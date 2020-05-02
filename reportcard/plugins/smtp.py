from email.message import EmailMessage
from email.headerregistry import Address
from jinja2 import Markup
from premailer import transform
import smtplib

from reportcard.output import OutputDriver


class SMTPOutputDriver(OutputDriver):
    def init(self, email_from=None, email_to=[], smtp_host="localhost",
             smtp_port=25, image_strategy="embed",
             image_remote_base_url=None):
        if not (email_from and email_to):
            raise ValueError("Both 'from' and 'to' addresses are required")

        self.email_from = self._parse_address(email_from)
        self.email_to = [self._parse_address(to) for to in email_to]
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.image_strategy = image_strategy
        if image_remote_base_url:
            self.image_remote_base_url = (
                image_remote_base_url.format(**self.report.__dict__))
        else:
            self.image_remote_base_url = None

    def _parse_address(self, address):
        username, domain = address.split("@")
        return Address(username=username, domain=domain)

    def render_blob_inline(self, blob):
        if self.image_strategy == "embed":
            return Markup(f"""<img src="cid:{blob["id"]}" />""")
        elif self.image_strategy == "remote":
            path = "/".join([self.image_remote_base_url, blob["id"]])
            return Markup(f"""<img src="{path}" />""")
        else:
            raise ValueError(
                f"Unsupported image strategy '{self.image_strategy}'")

    def render_output(self, content, blobs):
        msg = EmailMessage()
        msg["Subject"] = self.report.title
        msg["From"] = self.email_from
        msg["To"] = self.email_to

        msg.set_content(content.get("md"))
        html = transform(content.get("html"))
        msg.add_alternative(html, subtype="html")

        if self.image_strategy == "embed":
            payload = msg.get_payload()[1]
            for blob in blobs:
                mime_type = blob.get("mime_type")
                if not mime_type:
                    raise ValueError(
                        f"No mime type specified for blob {blob['id']}")
                maintype, subtype = mime_type.split("/")
                payload.add_related(blob["content"].getvalue(),
                                    maintype, subtype, cid=blob["id"])

        # Send the message via local SMTP server.
        with smtplib.SMTP(self.smtp_host, port=self.smtp_port) as s:
            s.send_message(msg)
