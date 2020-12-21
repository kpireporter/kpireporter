from datetime import datetime
import json
import os
from slack import WebClient
from slack.errors import SlackApiError
from slack.web.classes import messages, blocks, objects

from kpireport.output import OutputDriver

import logging

LOG = logging.getLogger(__name__)


class SlackOutputDriver(OutputDriver):
    """Send a report to one or more Slack channel(s).

    Attributes:
        api_token (str): a Slack API token with authorization to publish a
            message to the target channel.
        channels (List[str]): a list of Slack channels to publish the report to.
        image_remote_base_url (str): a base URL where blob assets (images etc.)
            are served. It is highly recommended to use another plugin, such as
            the :ref:`s3-plugin` or :ref:`scp-plugin` plugin, in order to place
            the assets in the expected folder structure.
    """

    # Slack has its own Markdown language
    supported_formats = ["slack"]

    def init(self, api_token=None, channels=[], image_remote_base_url=None):
        if not channels:
            raise ValueError("'channels' is required")

        self.channels = channels
        self.image_remote_base_url = image_remote_base_url

        if not self.image_remote_base_url:
            LOG.warn(
                "'image_remote_base_url' is not defined. Slack does not "
                "support attaching multiple files as blobs on a single "
                "post; any blobs attached to report Views will be "
                "ignored. If you would like image blobs rendered in "
                "your Slack message, specify a base URL and "
                "additionally publish your report to some remote URL "
                "via, e.g., the 's3' plugin."
            )
        else:
            self.image_remote_base_url = image_remote_base_url.format(
                **self.report.__dict__
            )

        api_token = api_token or os.getenv("SLACK_API_TOKEN")

        if not api_token:
            raise ValueError(
                (
                    "Could not find Slack API token. Either provide it as the "
                    "'api_token' argument, or set the SLACK_API_TOKEN "
                    "environment variable."
                )
            )

        self.slack = WebClient(token=api_token)

    def _parse_slack_error(self, err):
        assert err.response["ok"] is False
        err_message = err.response.get("error", "Unknown error")
        err_detailed_messages = err.response.get("response_metadata", {}).get(
            "messages", []
        )
        if err_detailed_messages:
            err_message += f": {json.dumps(err_detailed_messages)}"
        return err_message

    def _format_slack_date(self, dateobj):
        fallback = datetime.strftime(dateobj, "%Y-%m-%d")
        date_format = "{date_short}"

        link = objects.DateLink(
            date=dateobj, date_format=date_format, fallback=fallback
        )

        if "!date" not in str(link):
            # Bug in older versions of Slack client where dates were not
            # properly rendered; hack in the !date^ part of the URL.
            # TODO [2020-05-16]: remove this hack in ~6 months
            link = objects.DateLink(
                date=f"!date^{int(dateobj.timestamp())}",
                date_format=date_format,
                fallback=fallback,
            )

        return str(link)

    def render_output(self, content, blobs):
        views = content.get_views("slack", [])

        blks = []

        start_date = self._format_slack_date(self.report.start_date)
        end_date = self._format_slack_date(self.report.end_date)
        title_lines = [
            f"*{self.report.title}*",
            f"Report for: {start_date} to {end_date}",
        ]
        blks.append(
            blocks.SectionBlock(
                text=objects.MarkdownTextObject(text="\n\n".join(title_lines))
            )
        )

        for i, view in enumerate(views):
            title = view.get("title")
            output_lines = [f"*{title}*" if title else None, view.get("output") or None]
            output = "\n\n".join(list(filter(None, output_lines)))

            if output:
                blks.append(
                    blocks.SectionBlock(text=objects.MarkdownTextObject(text=output))
                )

            if self.image_remote_base_url:
                for blob in view.get("blobs"):
                    image_url = f"{self.image_remote_base_url}/{blob.id}"
                    title = blob.title or blob.id
                    blks.append(
                        blocks.ImageBlock(
                            title=title, image_url=image_url, alt_text=title
                        )
                    )

            description = view.get("description")
            if description:
                blks.append(
                    blocks.ContextBlock(
                        elements=[blocks.MarkdownTextObject(text=description)]
                    )
                )

            if (i + 1) < len(views):
                blks.append(blocks.DividerBlock())

        msg = messages.Message(text="", blocks=blks)

        try:
            for channel in self.channels:
                self.slack.chat_postMessage(channel=channel, **msg.to_dict())
        except SlackApiError as e:
            LOG.error(f"Got an error: {self._parse_slack_error(e)}")
