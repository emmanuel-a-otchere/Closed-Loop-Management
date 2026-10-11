"""Authentication / authorization for the CLAM service.

The Slice 3 PR1 module wires a simple bearer-token auth scheme on top
of the Slice 1-2 endpoints. Slice 1-2 ships without auth; the slice-3
work adds an opt-in layer that defaults to *bypass* in dev so existing
scripts and tests do not break.

Modes (selected by ``CLAM_AUTH_ENABLED`` env var):

- ``CLAM_AUTH_ENABLED=false`` (default): no token required. A
  ``AnonymousPrincipal`` is attached to every request. This is the
  dev / CI default so contributors can iterate without juggling
  tokens.
- ``CLAM_AUTH_ENABLED=true``: every request must carry a
  ``Authorization: Bearer <token>`` header that resolves to a
  registered token in the in-memory ``TokenStore``. The token's
  scope is consulted for write endpoints.

Tokens are issued via ``POST /api/v1/auth/tokens`` (admin scope only)
and stored in a process-local ``TokenStore``. There is no persistence
yet; tokens are wiped on process restart. Production deployments
are expected to swap in a DB-backed store; the interface is shaped
to make that swap a one-line change.
"""

from __future__ import annotations

import hashlib
import os
import secrets
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from fastapi import Request
from fastapi.responses import JSONResponse


class Scope(StrEnum):
    """Capability scopes attached to a token.

    READ < WRITE < ADMIN. Higher scopes implicitly grant lower scopes.
    """

    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


_SCOPE_ORDER: dict[Scope, int] = {
    Scope.READ: 1,
    Scope.WRITE: 2,
    Scope.ADMIN: 3,
}


@dataclass(frozen=True)
class Principal:
    """Authenticated caller attached to ``request.state.principal``.

    ``is_anonymous`` is True when auth is bypassed (dev mode) or when
    the request was not authenticated despite auth being enabled.
    """

    name: str
    scopes: frozenset[Scope]
    is_anonymous: bool = False

    def has_scope(self, required: Scope) -> bool:
        """Return True iff this principal has at least the required scope."""
        if self.is_anonymous:
            return False
        required_level = _SCOPE_ORDER[required]
        return any(_SCOPE_ORDER[s] >= required_level for s in self.scopes)


@dataclass(frozen=True)
class IssuedToken:
    """A token record returned by the issuer endpoint.

    ``plaintext`` is shown exactly once in the response; only its SHA-256
    fingerprint is stored.
    """

    token_id: str
    plaintext: str
    name: str
    scopes: frozenset[Scope]
    issued_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class _StoredToken:
    token_id: str
    fingerprint: str
    name: str
    scopes: frozenset[Scope]
    issued_at: datetime


def _fingerprint(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class TokenStore:
    """In-memory token registry.

    Stores the SHA-256 fingerprint of each token rather than the raw
    plaintext. The interface is shaped to be swapped for a DB-backed
    implementation later.
    """

    def __init__(self) -> None:
        self._tokens: dict[str, _StoredToken] = {}

    def issue(self, *, name: str, scopes: Iterable[Scope]) -> IssuedToken:
        plaintext = secrets.token_urlsafe(32)
        token_id = secrets.token_urlsafe(8)
        fingerprint = _fingerprint(plaintext)
        scopes_set = frozenset(scopes)
        record = _StoredToken(
            token_id=token_id,
            fingerprint=fingerprint,
            name=name,
            scopes=scopes_set,
            issued_at=datetime.now(UTC),
        )
        self._tokens[fingerprint] = record
        return IssuedToken(
            token_id=token_id,
            plaintext=plaintext,
            name=name,
            scopes=scopes_set,
            issued_at=record.issued_at,
        )

    def revoke(self, token_id: str) -> bool:
        for record in self._tokens.values():
            if record.token_id == token_id:
                self._tokens.pop(record.fingerprint, None)
                return True
        return False

    def authenticate(self, plaintext: str) -> Principal | None:
        record = self._tokens.get(_fingerprint(plaintext))
        if record is None:
            return None
        return Principal(
            name=record.name,
            scopes=record.scopes,
            is_anonymous=False,
        )

    def list_tokens(self) -> list[dict[str, object]]:
        return [
            {
                "tokenId": r.token_id,
                "name": r.name,
                "scopes": sorted(s.value for s in r.scopes),
                "issuedAt": r.issued_at.isoformat(),
            }
            for r in self._tokens.values()
        ]


_ANONYMOUS = Principal(name="anonymous", scopes=frozenset(), is_anonymous=True)


def auth_enabled() -> bool:
    """Read the ``CLAM_AUTH_ENABLED`` env var."""
    val = os.environ.get("CLAM_AUTH_ENABLED", "false").strip().lower()
    return val in {"1", "true", "yes", "on"}


def _extract_bearer(request: Request) -> str | None:
    header = request.headers.get("Authorization") or request.headers.get(
        "authorization"
    )
    if header is None:
        return None
    parts = header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1]


def resolve_principal(request: Request) -> Principal:
    """Resolve the principal for ``request``.

    When auth is disabled (default), returns the anonymous principal.
    When auth is enabled, looks up the bearer token in the app-scoped
    ``TokenStore``; returns None on missing / malformed header.
    """
    if not auth_enabled():
        return _ANONYMOUS
    store: TokenStore | None = getattr(request.app.state, "token_store", None)
    if store is None:
        return _ANONYMOUS
    token = _extract_bearer(request)
    if token is None:
        return Principal(name="", scopes=frozenset(), is_anonymous=True)
    principal = store.authenticate(token)
    if principal is None:
        return Principal(name="", scopes=frozenset(), is_anonymous=True)
    return principal


def require_scope(principal: Principal, required: Scope) -> JSONResponse | None:
    """Return a 401 / 403 response if the principal lacks the scope.

    Returns None when the principal satisfies the requirement.
    """
    from .errors import ErrorCode, error_envelope  # local to avoid cycle

    if principal.is_anonymous and auth_enabled():
        return JSONResponse(
            status_code=401,
            content=error_envelope(
                code=ErrorCode.UNAUTHORIZED,
                message="Authentication required.",
                details=None,
            ).model_dump(),
        )
    if not principal.has_scope(required):
        return JSONResponse(
            status_code=403,
            content=error_envelope(
                code=ErrorCode.FORBIDDEN,
                message=(
                    f"Token lacks the {required.value!r} scope required "
                    "for this endpoint."
                ),
                details={"requiredScope": required.value},
            ).model_dump(),
        )
    return None


class _AuthChallenge(Exception):
    """Raised by FastAPI dependencies when scope enforcement fails.

    The application's exception handler converts this into the structured
    error envelope (``auth.unauthorized`` or ``auth.forbidden``).
    """

    def __init__(self, response: JSONResponse) -> None:
        self.response = response
        super().__init__(response.body)


def require_read_scope(request: Request) -> Principal:
    """FastAPI dependency that requires READ scope when auth is enabled."""
    denial = require_scope(request.state.principal, Scope.READ)
    if denial is not None:
        raise _AuthChallenge(denial)
    return request.state.principal


def require_write_scope(request: Request) -> Principal:
    """FastAPI dependency that requires WRITE scope when auth is enabled."""
    denial = require_scope(request.state.principal, Scope.WRITE)
    if denial is not None:
        raise _AuthChallenge(denial)
    return request.state.principal


def require_admin_scope(request: Request) -> Principal:
    """FastAPI dependency that requires ADMIN scope when auth is enabled."""
    denial = require_scope(request.state.principal, Scope.ADMIN)
    if denial is not None:
        raise _AuthChallenge(denial)
    return request.state.principal


__all__ = [
    "ANONYMOUS",
    "IssuedToken",
    "Principal",
    "Scope",
    "TokenStore",
    "_ANONYMOUS",
    "auth_enabled",
    "require_read_scope",
    "require_scope",
    "require_write_scope",
    "resolve_principal",
]


# Alias used by the request middleware when auth is disabled.
ANONYMOUS = _ANONYMOUS
