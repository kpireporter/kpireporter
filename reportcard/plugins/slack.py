import json
import os
from slack import WebClient
from slack.errors import SlackApiError
from slack.web.classes import messages, blocks, elements, objects

from reportcard.output import OutputDriver

import logging
LOG = logging.getLogger(__name__)


class SlackOutputDriver(OutputDriver):
    def init(self, api_token=None, channels=[], image_remote_base_url=None):
        if not channels:
            raise ValueError("'channels' is required")

        self.channels = channels
        self.image_remote_base_url = image_remote_base_url

        if not self.image_remote_base_url:
            LOG.warn("'image_remote_base_url' is not defined. Slack does not "
                     "support attaching multiple files as blobs on a single "
                     "post; any blobs attached to report Views will be "
                     "ignored. If you would like image blobs rendered in "
                     "your Slack message, specify a base URL and "
                     "additionally publish your report to some remote URL "
                     "via, e.g., the 'html' plugin.")
        else:
            self.image_remote_base_url = (
                image_remote_base_url.format(**self.report.__dict__))

        api_token = api_token or os.getenv("SLACK_API_TOKEN")

        if not api_token:
            raise ValueError((
                "Could not find Slack API token. Either provide it as the "
                "'api_token' argument, or set the SLACK_API_TOKEN "
                "environment variable."))

        self.slack = WebClient(token=api_token)

    def _parse_slack_error(self, err):
        assert err.response["ok"] is False
        err_message = err.response.get("error", "Unknown error")
        err_detailed_messages = (
            err.response.get("response_metadata", {}).get("messages", []))
        if err_detailed_messages:
            err_message += f": {json.dumps(err_detailed_messages)}"
        return err_message

    def render_output(self, content, blobs):
        views = content.get("md_views", [])

        blks = []

        # TODO: description, start_date, end_date
        blks.append(blocks.SectionBlock(
            text=f"*{self.report.title}*"
        ))

        for i, view in enumerate(views):
            output_lines = [
                f"*{view.get('title')}*" if view.get("title") else None,
                view.get("output")
            ]
            output = "\n\n".join(list(filter(None, output_lines)))

            if output:
                blks.append(blocks.SectionBlock(
                    text=objects.MarkdownTextObject(text=output)
                ))

            if self.image_remote_base_url:
                for blob in view.get("blobs"):
                    image_url = f"{self.image_remote_base_url}/{blob['id']}"
                    title = blob.get("title", blob["id"])
                    blks.append(blocks.ImageBlock(
                        title=title,
                        image_url=image_url,
                        alt_text=title
                    ))

            description = view.get("description")
            if description:
                blks.append(blocks.ContextBlock(
                    elements=[blocks.MarkdownTextObject(
                        text=description
                    )]
                ))

            if (i + 1) < len(views):
                blks.append(blocks.DividerBlock())

        # TODO: put report date in here somehow
        report_title = self.report.title
        msg = messages.Message(text=report_title, blocks=blks)

        try:
            for channel in self.channels:
                self.slack.chat_postMessage(channel=channel, **msg.to_dict())
        except SlackApiError as e:
            LOG.error(f"Got an error: {self._parse_slack_error(e)}")
