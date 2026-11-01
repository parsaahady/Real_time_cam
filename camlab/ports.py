"""Interfaces (ports) that the outer code implements."""

from typing import Protocol


class PipelineRunner(Protocol):
    """Anything that can run a video pipeline until it ends."""

    def start(self) -> None:
        """Begin running the pipeline."""
        ...

    def wait(self) -> int:
        """Block until the pipeline ends and return its exit code."""
        ...

    def stop(self) -> None:
        """Shut the pipeline down cleanly; safe to call more than once."""
        ...