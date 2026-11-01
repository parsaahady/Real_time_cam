from camlab.sender import run_sender


class FakeRunner:
    def __init__(self, exit_code: int = 0, *, is_interrupted: bool = False) -> None:
        self._exit_code = exit_code
        self._is_interrupted = is_interrupted
        self.calls: list[str] = []

    def start(self) -> None:
        self.calls.append("start")

    def wait(self) -> int:
        self.calls.append("wait")
        if self._is_interrupted:
            raise KeyboardInterrupt
        return self._exit_code

    def stop(self) -> None:
        self.calls.append("stop")


def test_returns_pipeline_exit_code_and_stops() -> None:
    runner = FakeRunner(exit_code=7)
    assert run_sender(runner) == 7
    assert runner.calls == ["start", "wait", "stop"]


def test_ctrl_c_is_a_clean_exit_and_still_stops() -> None:
    runner = FakeRunner(is_interrupted=True)
    assert run_sender(runner) == 0
    assert runner.calls[-1] == "stop"