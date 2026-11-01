"""Command-line interface for the sender."""

import argparse
import sys
from collections.abc import Callable, Sequence
from typing import Final

from camlab.config import EncoderKind, SenderConfig
from camlab.errors import InvalidConfigError, PipelineError
from camlab.pipeline import build_sender_pipeline
from camlab.ports import PipelineRunner
from camlab.runner import GstLaunchRunner
from camlab.sender import EXIT_OK, run_sender

EXIT_PIPELINE_ERROR: Final = 1
EXIT_BAD_ARGUMENTS: Final = 2

RunnerFactory = Callable[[str], PipelineRunner]


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser; defaults come from SenderConfig."""
    defaults = SenderConfig(host="")
    parser = argparse.ArgumentParser(description="Send camera video over RTP/UDP.")
    parser.add_argument("--host", required=True, help="IP address of the receiver")
    parser.add_argument("--port", type=int, default=defaults.port)
    parser.add_argument("--device", default=defaults.device_path)
    parser.add_argument("--width", type=int, default=defaults.width_px)
    parser.add_argument("--height", type=int, default=defaults.height_px)
    parser.add_argument("--fps", type=int, default=defaults.frame_rate_hz)
    parser.add_argument("--bitrate", type=int, default=defaults.bitrate_kbps)
    parser.add_argument(
        "--dry-run", action="store_true", help="print the pipeline and exit"
    )
    return parser


def config_from_args(args: argparse.Namespace) -> SenderConfig:
    """Turn parsed arguments into a validated SenderConfig."""
    return SenderConfig(
        host=args.host,
        port=args.port,
        device_path=args.device,
        width_px=args.width,
        height_px=args.height,
        frame_rate_hz=args.fps,
        bitrate_kbps=args.bitrate,
    )


def main(
    argv: Sequence[str] | None = None,
    runner_factory: RunnerFactory = GstLaunchRunner,
) -> int:
    """Run the sender and return the process exit code."""
    args = build_parser().parse_args(argv)
    try:
        pipeline = build_sender_pipeline(config_from_args(args))
    except InvalidConfigError as error:
        print(f"Bad settings: {error}", file=sys.stderr)
        return EXIT_BAD_ARGUMENTS
    if args.dry_run:
        print(pipeline)
        return EXIT_OK
    try:
        return run_sender(runner_factory(pipeline))
    except PipelineError as error:
        print(f"Pipeline error: {error}", file=sys.stderr)
        return EXIT_PIPELINE_ERROR