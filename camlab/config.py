"""Settings for the video sender."""

from dataclasses import dataclass
from enum import Enum
from typing import Final

from camlab.errors import InvalidConfigError

MIN_PORT: Final = 1024  # ports below this are reserved for system services
MAX_PORT: Final = 65535


class EncoderKind(str, Enum):
    """Which H.264 encoder compresses the video."""

    SOFTWARE = "software"  # runs on the CPU (x264enc), works everywhere
    HARDWARE = "hardware"  # dedicated chip of the Raspberry Pi 4 (v4l2h264enc)


def _require_positive(name: str, value: int) -> None:
    if value <= 0:
        msg = f"{name} must be positive, got {value}"
        raise InvalidConfigError(msg)


@dataclass(frozen=True, slots=True)
class SenderConfig:
    """Everything the sender needs to know.

    Attributes:
        host: IP address of the laptop that receives the video.
        port: UDP port the receiver listens on.
        device_path: Camera file, for example "/dev/video0".
        width_px: Frame width in pixels.
        height_px: Frame height in pixels.
        frame_rate_hz: Frames per second.
        bitrate_kbps: Target video bit rate in kilobits per second.
        key_interval_frames: Frames between two I-frames.
        encoder: Which H.264 encoder to use.
    """

    host: str
    port: int = 5000
    device_path: str = "/dev/video0"
    width_px: int = 1280
    height_px: int = 720
    frame_rate_hz: int = 30
    bitrate_kbps: int = 2000
    key_interval_frames: int = 30
    encoder: EncoderKind = EncoderKind.SOFTWARE

    def __post_init__(self) -> None:
        """Reject impossible values as early as possible."""
        if not MIN_PORT <= self.port <= MAX_PORT:
            msg = f"port must be {MIN_PORT}-{MAX_PORT}, got {self.port}"
            raise InvalidConfigError(msg)
        _require_positive("width_px", self.width_px)
        _require_positive("height_px", self.height_px)
        _require_positive("frame_rate_hz", self.frame_rate_hz)
        _require_positive("bitrate_kbps", self.bitrate_kbps)