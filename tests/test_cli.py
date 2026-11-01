import pytest

from camlab.cli import EXIT_BAD_ARGUMENTS, EXIT_PIPELINE_ERROR, main
from camlab.errors import PipelineError


class FakeRunner:
    def __init__(self, pipeline: str) -> None:
        self.pipeline = pipeline

    def start(self) -> None:
        pass

    def wait(self) -> int:
        return 0

    def stop(self) -> None:
        pass


class BrokenRunner(FakeRunner):
    def start(self) -> None:
        msg = "no camera"
        raise PipelineError(msg)


def test_dry_run_prints_pipeline(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--host", "10.0.0.5", "--dry-run"]) == 0
    assert "udpsink host=10.0.0.5 port=5000" in capsys.readouterr().out


def test_bad_port_is_reported(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["--host", "10.0.0.5", "--port", "80", "--dry-run"])
    assert code == EXIT_BAD_ARGUMENTS
    assert "Bad settings" in capsys.readouterr().err


def test_runs_pipeline_with_injected_runner() -> None:
    assert main(["--host", "10.0.0.5"], runner_factory=FakeRunner) == 0


def test_pipeline_error_gives_exit_code(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["--host", "10.0.0.5"], runner_factory=BrokenRunner)
    assert code == EXIT_PIPELINE_ERROR
    assert "no camera" in capsys.readouterr().err

def test_hardware_encoder_flag(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--host", "10.0.0.5", "--encoder", "hardware", "--dry-run"]) == 0
    assert "v4l2h264enc" in capsys.readouterr().out


def test_unknown_encoder_is_rejected_by_argparse() -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--host", "10.0.0.5", "--encoder", "magic"])
    assert exit_info.value.code == EXIT_BAD_ARGUMENTS