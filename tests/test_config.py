import dataclasses
from typing import Any

import pytest

from camlab.config import SenderConfig
from camlab.errors import InvalidConfigError


def test_defaults_are_valid() -> None:
    config = SenderConfig(host="192.168.1.20")
    assert config.port == 5000
    assert config.width_px == 1280


def test_config_is_frozen() -> None:
    config = SenderConfig(host="192.168.1.20")
    with pytest.raises(dataclasses.FrozenInstanceError):
        config.port = 6000  # type: ignore[misc]


@pytest.mark.parametrize(
    "bad_values",
    [
        {"width_px": 0},
        {"height_px": 0},
        {"frame_rate_hz": 0},
        {"bitrate_kbps": -5},
    ],
)
def test_non_positive_value_is_rejected(bad_values: dict[str, Any]) -> None:
    with pytest.raises(InvalidConfigError, match="must be positive"):
        SenderConfig(host="192.168.1.20", **bad_values)


@pytest.mark.parametrize("port", [80, 70000])
def test_port_out_of_range_is_rejected(port: int) -> None:
    with pytest.raises(InvalidConfigError, match="port"):
        SenderConfig(host="192.168.1.20", port=port)
