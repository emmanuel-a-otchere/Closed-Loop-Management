"""Authentication router (Slice 3 PR1).

Token management endpoints:

- ``POST /api/v1/auth/tokens`` -- issue a new token. Requires ADMIN
  scope (only callable when auth is enabled, otherwise auth is bypassed
  and this endpoint always works for dev convenience).
- ``GET /api/v1/auth/tokens`` -- list active tokens (ADMIN scope).
- ``DELETE /api/v1/auth/tokens/{tokenId}`` -- revoke a token (ADMIN).
- ``GET /api/v1/auth/whoami`` -- return the current principal; useful
  for clients to confirm their token is valid.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Path, Request, status

from ..auth import Principal, Scope, auth_enabled, require_scope
from ..errors import ErrorCode, error_response
from ..models import (
    AuditAction,
    AuditActor,
    AuthTokenCreate,
    AuthTokenDetail,
    AuthTokenInfo,
    AuthTokenIssued,
)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)


def _store(request: Request):
    return getattr(request.app.state, "token_store", None)


def _admin_required(request: Request) -> Principal:
    return request.state.principal


async def _reject_if_unauthed(request: Request):
    """Reject unauthenticated requests when auth is enabled.

    When auth is bypassed (CLAM_AUTH_ENABLED=false), the principal is
    anonymous but the request is permitted -- the auth subsystem is
    not enforcing anything.
    """
    principal = request.state.principal
    if not auth_enabled():
        return None
    # The token-issuance endpoint on a fresh install is the bootstrap
    # path; it must be reachable without an existing token. The
    # application middleware permits the request through; we mirror
    # that here so the route handler does not double-reject.
    store = _store(request)
    if (
        request.method == "POST"
        and request.url.path == "/api/v1/auth/tokens"
        and store is not None
    ):
        # Async count of tokens (covers both in-memory and durable).
        if getattr(store, "is_durable", False):
            current = await store.list_tokens_async()
        else:
            current = store.list_tokens()
        if not current:
            return None
    denial = require_scope(principal, Scope.ADMIN)
    if denial is not None:
        return denial
    return None


@router.post(
    "/tokens",
    response_model=AuthTokenIssued,
    status_code=status.HTTP_201_CREATED,
    summary="Issue a new auth token (admin scope required when auth is enabled)",
)
async def issue_token(
    request: Request, payload: AuthTokenCreate
) -> AuthTokenIssued | object:
    denial = await _reject_if_unauthed(request)
    if denial is not None:
        return denial
    scopes: list[Scope] = []
    for raw in payload.scopes:
        try:
            scopes.append(Scope(raw))
        except ValueError:
            return error_response(
                status_code=422,
                code=ErrorCode.VALIDATION_ERROR,
                message=(
                    f"Unknown scope {raw!r}. Valid scopes: "
                    + ", ".join(s.value for s in Scope)
                    + "."
                ),
                details={"scopes": payload.scopes},
            )
    store = _store(request)
    if store is None:
        return error_response(
            status_code=503,
            code=ErrorCode.INTERNAL_ERROR,
            message="Auth subsystem is not initialised.",
        )
    issued = await store.issue(name=payload.name, scopes=scopes)
    # PR2: audit hook.
    clam_store = getattr(request.app.state, "store", None)
    if clam_store is not None:
        # Token ids are URL-safe tokens, not UUIDs; derive a stable
        # UUID5 audit entity_id from the token id so the audit_log
        # entity_id column type (UUID) holds.
        audit_id = uuid.uuid5(
            uuid.NAMESPACE_URL, f"token:{issued.token_id}"
        )
        await clam_store.record_audit(
            actor=AuditActor.USER,
            action=AuditAction.AUTH_TOKEN_ISSUE,
            entity_kind="AuthToken",
            entity_id=audit_id,
            after=AuthTokenInfo(
                tokenId=issued.token_id,
                name=issued.name,
                scopes=[s.value for s in issued.scopes],
                issuedAt=issued.issued_at,
            ),
        )
        # PR4: update the active token count.
        clam_store.set_token_total(len(store.list_tokens()))
    return AuthTokenIssued(
        tokenId=issued.token_id,
        plaintext=issued.plaintext,
        name=issued.name,
        scopes=[s.value for s in issued.scopes],
        issuedAt=issued.issued_at,
    )


@router.get(
    "/tokens",
    response_model=list[AuthTokenInfo],
    summary="List active auth tokens (admin scope required when auth is enabled)",
)
async def list_tokens(request: Request):
    denial = await _reject_if_unauthed(request)
    if denial is not None:
        return denial
    store = _store(request)
    if store is None:
        return []
    return [
        AuthTokenInfo(**row) for row in store.list_tokens()
    ]


@router.delete(
    "/tokens/{tokenId}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke an auth token (admin scope required when auth is enabled)",
)
async def revoke_token(
    request: Request,
    tokenId: str = Path(..., description="Token id to revoke"),
):
    denial = await _reject_if_unauthed(request)
    if denial is not None:
        return denial
    store = _store(request)
    if store is None:
        return error_response(
            status_code=503,
            code=ErrorCode.INTERNAL_ERROR,
            message="Auth subsystem is not initialised.",
        )
    if not await store.revoke(tokenId):
        return error_response(
            status_code=404,
            code=ErrorCode.NOT_FOUND,
            message=f"Token {tokenId!r} not found.",
        )
    # PR2: audit hook.
    clam_store = getattr(request.app.state, "store", None)
    if clam_store is not None:
        audit_id = uuid.uuid5(uuid.NAMESPACE_URL, f"token:{tokenId}")
        await clam_store.record_audit(
            actor=AuditActor.USER,
            action=AuditAction.AUTH_TOKEN_REVOKE,
            entity_kind="AuthToken",
            entity_id=audit_id,
        )
        # PR4: update the active token count.
        clam_store.set_token_total(len(store.list_tokens()))


@router.get(
    "/tokens/{tokenId}",
    response_model=AuthTokenDetail,
    summary="Get a single auth token (PR3, ADMIN scope)",
)
async def get_token(request: Request, tokenId: str = Path(...)):
    """Return the full view of an issued token (expiresAt + revokedAt)."""
    denial = await _reject_if_unauthed(request)
    if denial is not None:
        return denial
    store = _store(request)
    if store is None:
        return error_response(
            status_code=503,
            code=ErrorCode.INTERNAL_ERROR,
            message="Auth subsystem is not initialised.",
        )
    row = await store.get_token(tokenId)
    if row is None:
        return error_response(
            status_code=404,
            code=ErrorCode.NOT_FOUND,
            message=f"Token {tokenId!r} not found.",
        )
    return AuthTokenDetail(
        tokenId=str(row["tokenId"]),
        name=str(row["name"]),
        scopes=list(row["scopes"]),
        issuedAt=row["issuedAt"],
        expiresAt=row["expiresAt"],
        revokedAt=row["revokedAt"],
    )


@router.post(
    "/tokens/{tokenId}/rotate",
    response_model=AuthTokenIssued,
    status_code=status.HTTP_201_CREATED,
    summary="Rotate an auth token (PR3, ADMIN scope)",
)
async def rotate_token(request: Request, tokenId: str = Path(...)):
    """Issue a fresh plaintext secret, retire the old token.

    Writes an ``auth.token.rotate`` audit row tied to the old
    token's derived UUID5 entity_id. The response carries the
    new plaintext exactly once.
    """
    denial = await _reject_if_unauthed(request)
    if denial is not None:
        return denial
    store = _store(request)
    if store is None:
        return error_response(
            status_code=503,
            code=ErrorCode.INTERNAL_ERROR,
            message="Auth subsystem is not initialised.",
        )
    issued = await store.rotate(tokenId)
    if issued is None:
        return error_response(
            status_code=404,
            code=ErrorCode.NOT_FOUND,
            message=(
                f"Token {tokenId!r} not found or already revoked; "
                "rotation requires a live token."
            ),
        )
    clam_store = getattr(request.app.state, "store", None)
    if clam_store is not None:
        old_audit_id = uuid.uuid5(
            uuid.NAMESPACE_URL, f"token:{tokenId}"
        )
        await clam_store.record_audit(
            actor=AuditActor.USER,
            action=AuditAction.AUTH_TOKEN_ROTATE,
            entity_kind="AuthToken",
            entity_id=old_audit_id,
            after=AuthTokenDetail(
                tokenId=issued.token_id,
                name=issued.name,
                scopes=[s.value for s in issued.scopes],
                issuedAt=issued.issued_at,
                expiresAt=None,
                revokedAt=None,
            ),
        )
        clam_store.set_token_total(
            await clam_store.count_active_auth_tokens()
        )
    return AuthTokenIssued(
        tokenId=issued.token_id,
        plaintext=issued.plaintext,
        name=issued.name,
        scopes=[s.value for s in issued.scopes],
        issuedAt=issued.issued_at,
    )


@router.get(
    "/whoami",
    summary="Return the principal resolved for the current request",
)
async def whoami(request: Request) -> dict[str, object]:
    principal = request.state.principal
    return {
        "name": principal.name,
        "scopes": sorted(s.value for s in principal.scopes),
        "isAnonymous": principal.is_anonymous,
        "authEnabled": _auth_enabled(),
    }


def _auth_enabled() -> bool:
    from ..auth import auth_enabled

    return auth_enabled()


__all__ = ["router"]
