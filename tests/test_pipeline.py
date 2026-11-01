from camlab.config import SenderConfig
from camlab.pipeline import build_receiver_pipeline, build_sender_pipeline


def test_sender_pipeline_uses_config_values() -> None:
    config = SenderConfig(host="10.0.0.5", port=6000, bitrate_kbps=1500)
    pipeline = build_sender_pipeline(config)
    assert "udpsink host=10.0.0.5 port=6000" in pipeline
    assert "bitrate=1500" in pipeline
    assert pipeline.startswith("v4l2src device=/dev/video0 ! image/jpeg")


def test_sender_pipeline_stages_are_in_order() -> None:
    pipeline = build_sender_pipeline(SenderConfig(host="10.0.0.5"))
    stages = ["jpegdec", "x264enc", "rtph264pay", "udpsink"]
    positions = [pipeline.index(stage) for stage in stages]
    assert positions == sorted(positions)


def test_receiver_pipeline_listens_on_port() -> None:
    pipeline = build_receiver_pipeline(port=5000, latency_ms=50)
    assert pipeline.startswith("udpsrc port=5000")
    assert "rtpjitterbuffer latency=50" in pipeline
