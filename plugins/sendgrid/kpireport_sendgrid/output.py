from base64 import b64encode
from jinja2 import Markup
import json
import os
from premailer import transform
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Attachment, Mail, MailSettings, SandBoxMode

from kpireport.output import OutputDriver

import logging

LOG = logging.getLogger(__name__)


class SendGridOutputDriver(OutputDriver):
    """Email a report via SendGrid.

    .. note::

        When testing, you can set a ``SENDGRID_SANDBOX_ENABLED=1`` environment
        variable, which will only verify the mail payload on SendGrid, but
        will not actually send it.

    Attributes:
        email_from (str): the sender email address.
        email_to (List[str]): a list of target email addresses.
        api_key (str): a SendGrid API key authorized to send mail on behalf of
            the sending address.
    """
    def init(self, email_from=None, email_to=None, api_key=None):
        if not (email_from and email_to):
            raise ValueError("Both 'from' and 'to' addresses are required")

        self.api_key = api_key or os.getenv("SENDGRID_API_KEY")

        if not self.api_key:
            raise ValueError(
                (
                    "Could not find SendGrid API key. Either provide it as the "
                    "'api_key' argument, or set the SENDGRID_API_KEY environment "
                    "variable."
                )
            )

        self.email_from = email_from
        self.email_to = email_to

    def _parse_sendgrid_error(self, err):
        if getattr(err, "body", None):
            errors = json.loads(err.body).get("errors", [])
            if errors:
                message = errors[0].get("message")
                if message:
                    return message
        return "Unknown error"

    @property
    def _sandbox_mode(self):
        flag = os.getenv("SENDGRID_SANDBOX_ENABLED", "").lower()
        return flag in ["1", "y", "yes", "true"]

    def render_blob_inline(self, blob, fmt=None):
        return Markup(f"""<img src="cid:{blob["id"]}" />""")

    def render_output(self, content, blobs):
        msg = Mail(
            from_email=self.email_from,
            to_emails=self.email_to,
            subject=self.report.title,
            html_content=transform(content.get_format("html")),
        )

        if self._sandbox_mode:
            LOG.warn(
                (
                    "Sandbox mode is enabled. Mails can only be verified, not "
                    "delivered."
                )
            )
            msg.mail_settings = MailSettings()
            msg.mail_settings.sandbox_mode = SandBoxMode(True)

        attachment = []
        for blob in blobs:
            encoded_content = b64encode(blob["content"].getvalue()).decode()
            attachment.append(
                Attachment(
                    file_content=encoded_content,
                    file_name=blob["id"],
                    file_type=blob.get("mime_type"),
                    content_id=blob["id"],
                    disposition="inline",
                )
            )
        msg.attachment = attachment

        try:
            sg = SendGridAPIClient(self.api_key)
            res = sg.send(msg)

            LOG.debug(res.body)
            LOG.debug(res.headers)

            if res.status_code != 202:
                raise ValueError(f"Unexpected HTTP response: {res.status_code}")
        except Exception as e:
            raise ValueError("Error sending mail", self._parse_sendgrid_error(e))
