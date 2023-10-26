
class CreateError(Exception):
    """Base Create tool exception."""

class NoExecuteCmd(CreateError):
    """Can't find execute command."""

