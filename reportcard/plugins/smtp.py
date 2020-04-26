from email.message import EmailMessage
from email.headerregistry import Address
from j2 import Markup
import smtplib

from reportcard.output import OutputDriver


class SMTPOutputDriver(OutputDriver):
    def init(self, email_from=None, email_to=[], smtp_host="localhost"):
        if not (email_from and email_to):
            raise ValueError("Both 'from' and 'to' addresses are required")

        self.email_from = self._parse_address(email_from)
        self.email_to = [self._parse_address(to) for to in email_to]
        self.smtp_host = smtp_host

    def _parse_address(self, address):
        username, domain = address.split("@")
        return Address(username=username, domain=domain)

    def render_blob_inline(self, blob):
        return Markup(f"""<img src="cid:{blob["id"]}" />""")

    def render_output(self, content, blobs):
        msg = EmailMessage()
        msg["Subject"] = self.report.title
        msg["From"] = self.email_from
        msg["To"] = self.email_to
        msg.set_content(content.get("md"))
        msg.add_alternative(content.get("html"), subtype="html")

        payload = msg.get_payload()[1]
        for blob in blobs:
            mime_type = blob.get("mime_type")
            if not mime_type:
                raise ValueError(
                    f"No mime type specified for blob {blob['id']}")
            maintype, subtype = mime_type.split("/")
            payload.add_related(blob["content"], maintype, subtype,
                                cid=blob["id"])

        # Send the message via local SMTP server.
        with smtplib.SMTP(self.smtp_host) as s:
            s.send_message(msg)
