from camlab.config import EncoderKind, SenderConfig
from camlab.encoders import HardwareEncoder, SoftwareEncoder, get_encoder
from camlab.pipeline import build_sender_pipeline


def test_registry_returns_matching_strategy() -> None:
    assert isinstance(get_encoder(EncoderKind.SOFTWARE), SoftwareEncoder)
    assert isinstance(get_encoder(EncoderKind.HARDWARE), HardwareEncoder)


def test_software_pipeline_uses_x264() -> None:
    pipeline = build_sender_pipeline(SenderConfig(host="10.0.0.5"))
    assert "x264enc" in pipeline
    assert "v4l2h264enc" not in pipeline


def test_hardware_pipeline_uses_chip_and_converts_kbps_to_bps() -> None:
    config = SenderConfig(
        host="10.0.0.5",
        bitrate_kbps=1500,
        key_interval_frames=15,
        encoder=EncoderKind.HARDWARE,
    )
    pipeline = build_sender_pipeline(config)
    assert "x264enc" not in pipeline
    assert "video_bitrate=1500000" in pipeline
    assert "h264_i_frame_period=15" in pipeline
    assert "repeat_sequence_header=1" in pipeline