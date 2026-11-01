"""Run a GStreamer pipeline as a child process and stop it cleanly."""

import shlex
import signal
import subprocess
from typing import Final

from camlab.errors import PipelineError

GST_LAUNCH: Final = "gst-launch-1.0"
STOP_TIMEOUT_S: Final = 5.0


class GstLaunchRunner:
    """Starts ``gst-launch-1.0`` and shuts it down with SIGINT (like Ctrl+C)."""

    def __init__(self, pipeline: str) -> None:
        self._command = [GST_LAUNCH, "-e", *shlex.split(pipeline)]
        self._process: subprocess.Popen[bytes] | None = None

    def start(self) -> None:
        """Launch the child process."""
        if self._process is not None:
            msg = "pipeline is already running"
            raise PipelineError(msg)
        try:
            # Own session: a terminal Ctrl+C reaches only Python, which then
            # stops the child in an orderly way (see stop).
            self._process = subprocess.Popen(self._command, start_new_session=True)
        except FileNotFoundError as error:
            msg = f"{GST_LAUNCH} not found; is GStreamer installed?"
            raise PipelineError(msg) from error

    def wait(self) -> int:
        """Block until the pipeline ends; return its exit code."""
        if self._process is None:
            msg = "pipeline was not started"
            raise PipelineError(msg)
        return self._process.wait()

    def stop(self) -> None:
        """Ask the pipeline to finish; kill it if it ignores the request."""
        if self._process is None:
            return
        self._process.send_signal(signal.SIGINT)
        try:
            self._process.wait(timeout=STOP_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait()
        self._process = None