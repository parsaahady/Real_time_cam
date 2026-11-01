"""Build GStreamer pipeline descriptions from settings."""

from camlab.config import SenderConfig
from camlab.contract import RECEIVER_CAPS, RTP_PAYLOAD_TYPE
from camlab.encoders import get_encoder


def build_sender_pipeline(config: SenderConfig) -> str:
    """Return the sender pipeline as one GStreamer description string."""
    camera_caps = (
        f"image/jpeg,width={config.width_px},"
        f"height={config.height_px},framerate={config.frame_rate_hz}/1"
    )
    encoder_stages = get_encoder(config.encoder).build_stages(config)
    parts = [
        f"v4l2src device={config.device_path}",
        camera_caps,
        "jpegdec",
        *encoder_stages,
        "h264parse",
        f"rtph264pay pt={RTP_PAYLOAD_TYPE} config-interval=1",
        f"udpsink host={config.host} port={config.port}",
    ]
    return " ! ".join(parts)


def build_receiver_pipeline(port: int, latency_ms: int) -> str:
    """Return the receiver pipeline for the laptop."""
    parts = [
        f'udpsrc port={port} caps="{RECEIVER_CAPS}"',
        f"rtpjitterbuffer latency={latency_ms}",
        "rtph264depay",
        "h264parse",
        "avdec_h264",
        "videoconvert",
        "autovideosink sync=false",
    ]
    return " ! ".join(parts)