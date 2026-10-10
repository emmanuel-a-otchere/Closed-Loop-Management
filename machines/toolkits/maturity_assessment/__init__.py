"""CLAM maturity assessment toolkit.

Questionnaire and CSV scoring template for assessing a closed-loop
deployment's maturity level. No runtime code -- this toolkit ships the
questionnaire markdown, the CSV scoring template, and a static scoring
rubric. CLI: ``clam-maturity-assessment``.
"""

from .cli import main

__all__ = ["main"]