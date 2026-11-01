"""Errors raised by camlab."""


class InvalidConfigError(ValueError):
    """Raised when a setting has a value that cannot work."""


class PipelineError(RuntimeError):
    """Raised when the video pipeline cannot be started or controlled."""