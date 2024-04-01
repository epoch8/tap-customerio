"""CustomerIo tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_customerio import streams


class TapCustomerIo(Tap):
    """CustomerIo tap class."""

    name = "tap-customerio"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "auth_token",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="The token to authenticate against the API service",
        ),

    ).to_dict()

    def discover_streams(self) -> list[streams.CustomerIoStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.CampaignsStream(self),
            streams.CampaignsActionsStream(self),
            streams.CampaignsMessagesStream(self),
            streams.SegmentsStream(self),
            streams.NewslettersStream(self),
            streams.CampaignsMetricsStream(self),
            streams.NewslettersMetricsStream(self),
        ]


if __name__ == "__main__":
    TapCustomerIo.cli()
