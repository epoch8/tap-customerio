"""Stream type classes for tap-customerio."""

from __future__ import annotations

import typing as t
from pathlib import Path
from typing import Iterable
import requests

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_customerio.client import CustomerIoStream

# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.


class CampaignsStream(CustomerIoStream):

    name = "campaigns"
    path = "/campaigns"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None # type: ignore
    records_jsonpath = "$[campaigns][*]"

    def get_child_context(self, record: dict, context: t.Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "campaign_id": record["id"],
        }

class CampaignsMetricsStream(CustomerIoStream):

    name = "campaigns_metrics"
    parent_stream_type = CampaignsStream
    path = "/campaigns/{campaign_id}/metrics"
    primary_keys = [] # type: ignore
    replication_key = None # type: ignore
    records_jsonpath = "$"

    def post_process(self, row: dict, context: dict) -> dict | None:
        row['campaign_id'] = context['campaign_id']
        return row



class NewslettersStream(CustomerIoStream):

    name = "newsletters"
    path = "/newsletters"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None # type: ignore
    records_jsonpath = "$[newsletters][*]"

    def get_child_context(self, record: dict, context: t.Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "newsletter_id": record["id"],
        }

class NewslettersMetricsStream(CustomerIoStream):

    name = "newsletters_metrics"
    parent_stream_type = NewslettersStream
    path = "/newsletters/{newsletter_id}/metrics"
    primary_keys = [] # type: ignore
    replication_key = None # type: ignore
    records_jsonpath = "$"

    def post_process(self, row: dict, context: dict) -> dict | None:
        row['newsletter_id'] = context['newsletter_id']
        return row




class SegmentsStream(CustomerIoStream):

    name = "segments"
    path = "/segments"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None # type: ignore
    records_jsonpath = "$[segments][*]"
