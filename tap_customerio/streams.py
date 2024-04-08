"""Stream type classes for tap-customerio."""

from __future__ import annotations

import time
import typing as t
from pathlib import Path
from typing import Any, Dict, Iterable, Optional
import requests
import datetime

from singer_sdk.pagination import BaseHATEOASPaginator
from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_customerio.client import CustomerIoStream

# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.
import logging


class MyPaginator(BaseHATEOASPaginator):
    def get_next_url(self, response):
        data = response.json()
        return data.get("next")
    

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

class CampaignsActionsStream(CustomerIoStream):
    name = "campaigns_actions"
    parent_stream_type = CampaignsStream
    path = "/campaigns/{campaign_id}/actions"
    primary_keys = []
    replication_key = None
    schema_filepath = None
    schema = th.PropertiesList(
            th.Property("id", th.StringType),
            th.Property("campaign_id", th.IntegerType),
            th.Property("parent_action_id", th.IntegerType),
            th.Property("deduplicate_id", th.StringType),
            th.Property("name", th.StringType),
            th.Property("layout", th.StringType),
            th.Property("created", th.IntegerType),
            th.Property("updated", th.IntegerType),
            th.Property("body_amp", th.StringType),
            th.Property("language", th.StringType),
            th.Property("type", th.StringType),
            th.Property("sending_state", th.StringType),
            th.Property("from_email", th.StringType),
            th.Property("from_id", th.IntegerType),
            th.Property("reply_to", th.StringType),
            th.Property("reply_to_id", th.IntegerType),
            th.Property("preprocessor", th.StringType),
            th.Property("recipient", th.StringType),
            th.Property("subject", th.StringType),
            th.Property("bcc", th.StringType),
            th.Property("fake_bcc", th.BooleanType),
            th.Property("preheader_text", th.StringType),
    ).to_dict()

    def post_process(self, row: dict, context: dict) -> dict | None:
        row['campaign_id'] = context['campaign_id']
        return row
    
    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        data = response.json()
        actions = data.get("actions")

        if actions:
            for action in actions:
                result = {
                    "id": action.get("id"),
                    "campaign_id": action.get("campaign_id"),
                    "parent_action_id": action.get("parent_action_id"),
                    "deduplicate_id": action.get("deduplicate_id"),
                    "name": action.get("name"),
                    "layout": action.get("layout"),
                    "created": action.get("created"),
                    "updated": action.get("updated"),
                    "body_amp": action.get("body_amp"),
                    "language": action.get("language"),
                    "type": action.get("type"),
                    "sending_state": action.get("sending_state"),
                    "from_email": action.get("from"),
                    "from_id": action.get("from_id"),
                    "reply_to": action.get("reply_to"),
                    "reply_to_id": action.get("reply_to_id"),
                    "preprocessor": action.get("preprocessor"),
                    "recipient": action.get("recipient"),
                    "subject": action.get("subject", ""),
                    "bcc": action.get("bcc"),
                    "fake_bcc": action.get("fake_bcc"),
                    "preheader_text": action.get("preheader_text", ""),
                }
                for key, val in result.items():
                    if isinstance(val, str):
                        result[key] = val.encode("ascii", "ignore").decode('utf-8')
                yield result


class CampaignsMessagesStream(CustomerIoStream):
    name = "campaigns_messages"
    parent_stream_type = CampaignsStream
    path = "/campaigns/{campaign_id}/messages"
    primary_keys = []
    replication_key = None
    schema_filepath = None
    schema = th.PropertiesList(
            th.Property("id", th.StringType),
            th.Property("deduplicate_id", th.StringType),
            th.Property("msg_template_id", th.IntegerType),
            th.Property("action_id", th.IntegerType),
            th.Property("customer_id", th.StringType),
            th.Property("customer_identifiers", th.ObjectType(
                th.Property("id", th.StringType),
                th.Property("email", th.StringType),
                th.Property("cio_id", th.StringType),
            )),
            th.Property("recipient", th.StringType),
            th.Property("subject", th.StringType),
            th.Property("metrics", th.ObjectType(
                th.Property("delivered", th.IntegerType),
                th.Property("sent", th.IntegerType),
            )),
            th.Property("created", th.IntegerType),
            th.Property("failure_message", th.StringType),
            th.Property("newsletter_id", th.StringType),
            th.Property("content_id", th.IntegerType),
            th.Property("campaign_id", th.IntegerType),
            th.Property("broadcast_id", th.StringType),
            th.Property("type", th.StringType),
            th.Property("forgotten", th.BooleanType),
    ).to_dict()

    def post_process(self, row: dict, context: dict) -> dict | None:
        row['campaign_id'] = context['campaign_id']
        return row

    def get_new_paginator(self):
        return MyPaginator()

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        today = datetime.date.today()
        timedelta = datetime.timedelta(days=30)
        start_ts = int(time.mktime(today.timetuple()))
        end_ts = int(time.mktime((today - timedelta).timetuple()))
        params = {
            "limit": 1000,
            "start_ts": start_ts,
            "end_ts": end_ts,
        }
        if next_page_token:
            params["start"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key
        return params
    
    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        data = response.json()
        messages = data['messages']

        for message in messages:
            yield message


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
