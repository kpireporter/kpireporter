from unittest import mock

import pytest
from kpireport.report import Content, Report
from kpireport_slack import SlackOutputDriver


def test_render_output(report: "Report", content: "Content", mocker: "mock"):
    web_client = mocker.patch("kpireport_slack.output.WebClient")()
    web_client.chat_postMessage.return_value = None
    expected_blocks = [
        {
            "text": {
                "text": (
                    "*Fake report*\n\nReport for: <!date^1588327872^{date_short}"
                    "|2020-05-01> to <!date^1588846272^{date_short}|2020-05-07>"
                ),
                "type": "mrkdwn",
            },
            "type": "section",
        },
        {
            "text": {
                "text": "*First block*\n\nFirst block output",
                "type": "mrkdwn",
            },
            "type": "section",
        },
        {
            "elements": [
                {"text": "The first block in the rendered layout", "type": "mrkdwn"}
            ],
            "type": "context",
        },
        {"type": "divider"},
        {
            "text": {
                "text": "*Second block*\n\nSecond block output",
                "type": "mrkdwn",
            },
            "type": "section",
        },
        {
            "elements": [
                {
                    "text": "The second block in the rendered layout",
                    "type": "mrkdwn",
                }
            ],
            "type": "context",
        },
    ]

    slack = SlackOutputDriver(report, channels=["#general"], api_token="fake-api-token")
    slack.render_output(content, [])
    web_client.chat_postMessage.assert_called_with(
        channel="#general",
        attachments=[],
        blocks=expected_blocks,
        mrkdwn=True,
    )


def test_missing_args(report: "Report"):
    with pytest.raises(ValueError):
        SlackOutputDriver(report, channels=[], api_token="fake-api-token")
    with pytest.raises(ValueError):
        SlackOutputDriver(report, channels=["#general"], api_token=None)
