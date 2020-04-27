from jinja2 import Markup
import json
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Attachment, Mail, MailSettings, SandBoxMode

from reportcard.output import OutputDriver

import logging
LOG = logging.getLogger(__name__)


class SendGridOutputDriver(OutputDriver):
    def init(self, email_from=None, email_to=None, api_key=None):
        if not (email_from and email_to):
            raise ValueError("Both 'from' and 'to' addresses are required")

        self.api_key = api_key or os.getenv("SENDGRID_API_KEY")

        if not self.api_key:
            raise ValueError((
                "Could not find SendGrid API key. Either provide it as the "
                "'api_key' argument, or set the SENDGRID_API_KEY environment "
                "variable."))

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
        print(flag)
        return flag in ["1", "y", "yes", "true"]

    def render_blob_inline(self, blob):
        return Markup(f"""<img src="cid:{blob["id"]}" />""")

    def render_output(self, content, blobs):
        msg = Mail(
            from_email=self.email_from,
            to_emails=self.email_to,
            subject=self.report.title,
            html_content=content.get("html")
        )

        if self._sandbox_mode:
            LOG.warn((
                "Sandbox mode is enabled. Mails can only be verified, not "
                "delivered."))
            msg.mail_settings = MailSettings()
            msg.mail_settings.sandbox_mode = SandBoxMode(True)

        msg.attachment = []
        for blob in blobs:
            msg.attachment.append(
                Attachment(file_content=blob["content"].getvalue(),
                           file_name=blob["id"],
                           file_type=blob.get("mime_type"),
                           content_id=blob["id"],
                           disposition="inline"))

        try:
            sg = SendGridAPIClient(self.api_key)
            res = sg.send(msg)
            print(res.status_code)
            print(res.body)
            print(res.headers)
        except Exception as e:
            raise ValueError("Error sending mail",
                             self._parse_sendgrid_error(e))

