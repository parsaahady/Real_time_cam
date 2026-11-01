"""H.264 encoder choices (Strategy pattern)."""

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final, Protocol

from camlab.config import EncoderKind, SenderConfig

BITS_PER_KILOBIT: Final = 1000
H264_LEVEL: Final = 4  # level 4 covers up to 1080p at 30 Hz


class H264Encoder(Protocol):
    """Builds the pipeline stages that turn raw video into H.264."""

    def build_stages(self, config: SenderConfig) -> list[str]:
        """Return GStreamer stages from raw video in to H.264 out."""
        ...


class SoftwareEncoder:
    """x264 running on the CPU; works on any computer."""

    def build_stages(self, config: SenderConfig) -> list[str]:
        """Return the stages for CPU encoding."""
        encoder = (
            "x264enc tune=zerolatency speed-preset=ultrafast "
            f"bitrate={config.bitrate_kbps} key-int-max={config.key_interval_frames}"
        )
        return ["videoconvert", encoder, "video/x-h264,profile=baseline"]


class HardwareEncoder:
    """The H.264 chip of the Raspberry Pi 4, driven through V4L2."""

    def build_stages(self, config: SenderConfig) -> list[str]:
        """Return the stages for chip encoding."""
        bitrate_bps = config.bitrate_kbps * BITS_PER_KILOBIT
        controls = (
            "controls,repeat_sequence_header=1,"
            f"video_bitrate={bitrate_bps},"
            f"h264_i_frame_period={config.key_interval_frames}"
        )
        return [
            "videoconvert",
            "video/x-raw,format=I420",
            f'v4l2h264enc extra-controls="{controls}"',
            f"video/x-h264,level=(string){H264_LEVEL}",
        ]


ENCODERS: Final[Mapping[EncoderKind, H264Encoder]] = MappingProxyType(
    {
        EncoderKind.SOFTWARE: SoftwareEncoder(),
        EncoderKind.HARDWARE: HardwareEncoder(),
    }
)


def get_encoder(kind: EncoderKind) -> H264Encoder:
    """Return the encoder strategy registered for ``kind``."""
    return ENCODERS[kind]