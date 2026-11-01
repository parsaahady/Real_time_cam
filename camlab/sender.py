"""Run a pipeline until it ends or the user presses Ctrl+C."""

from typing import Final

from camlab.ports import PipelineRunner

EXIT_OK: Final = 0


def run_sender(runner: PipelineRunner) -> int:
    """Start the runner, wait for it, and always shut it down afterwards.

    Returns:
        Exit code: 0 after Ctrl+C, otherwise the pipeline's own exit code.
    """
    runner.start()
    try:
        return runner.wait()
    except KeyboardInterrupt:
        return EXIT_OK
    finally:
        runner.stop()