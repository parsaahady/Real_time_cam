"""Settings the sender and the receiver must agree on.

Both sides import this file, so the values cannot drift apart.
"""

from typing import Final

RTP_PAYLOAD_TYPE: Final = 96
RTP_CLOCK_RATE_HZ: Final = 90_000
ENCODING_NAME: Final = "H264"

RECEIVER_CAPS: Final = (
    f"application/x-rtp,media=video,encoding-name={ENCODING_NAME},"
    f"payload={RTP_PAYLOAD_TYPE},clock-rate={RTP_CLOCK_RATE_HZ}"
)