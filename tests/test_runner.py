import signal
import subprocess
from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest

from camlab.errors import PipelineError
from camlab.pipeline import build_receiver_pipeline
from camlab.runner import GstLaunchRunner


@pytest.fixture
def popen() -> Iterator[MagicMock]:
    with patch("camlab.runner.subprocess.Popen") as mocked:
        yield mocked


def test_start_builds_command_with_eos_flag(popen: MagicMock) -> None:
    GstLaunchRunner("a ! b").start()
    command = popen.call_args.args[0]
    assert command == ["gst-launch-1.0", "-e", "a", "!", "b"]
    assert popen.call_args.kwargs["start_new_session"] is True


def test_quoted_caps_stay_one_argument(popen: MagicMock) -> None:
    GstLaunchRunner(build_receiver_pipeline(5000, 50)).start()
    command = popen.call_args.args[0]
    caps_args = [part for part in command if part.startswith("caps=")]
    assert len(caps_args) == 1
    assert "payload=96" in caps_args[0]


@pytest.mark.usefixtures("popen")
def test_start_twice_is_rejected() -> None:
    runner = GstLaunchRunner("a ! b")
    runner.start()
    with pytest.raises(PipelineError, match="already running"):
        runner.start()


def test_missing_gstreamer_gives_clear_error(popen: MagicMock) -> None:
    popen.side_effect = FileNotFoundError
    with pytest.raises(PipelineError, match="not found"):
        GstLaunchRunner("a ! b").start()


def test_wait_returns_exit_code(popen: MagicMock) -> None:
    popen.return_value.wait.return_value = 3
    runner = GstLaunchRunner("a ! b")
    runner.start()
    assert runner.wait() == 3


def test_wait_before_start_is_rejected() -> None:
    with pytest.raises(PipelineError, match="not started"):
        GstLaunchRunner("a ! b").wait()


def test_stop_sends_sigint_and_waits(popen: MagicMock) -> None:
    runner = GstLaunchRunner("a ! b")
    runner.start()
    runner.stop()
    process = popen.return_value
    process.send_signal.assert_called_once_with(signal.SIGINT)
    process.kill.assert_not_called()


def test_stop_kills_a_stuck_process(popen: MagicMock) -> None:
    process = popen.return_value
    process.wait.side_effect = [subprocess.TimeoutExpired("gst", 5.0), 0]
    runner = GstLaunchRunner("a ! b")
    runner.start()
    runner.stop()
    process.kill.assert_called_once()


def test_stop_without_start_does_nothing() -> None:
    GstLaunchRunner("a ! b").stop()