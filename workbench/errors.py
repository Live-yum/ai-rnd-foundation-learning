"""Recoverable control states retain both user data and workflow checkpoints."""


class PausedLimit(RuntimeError):
    pass


class UnsupportedScope(RuntimeError):
    pass
