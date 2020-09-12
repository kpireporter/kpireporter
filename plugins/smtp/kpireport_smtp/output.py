from datetime import datetime

from email.message import EmailMessage
from email.headerregistry import Address
from jinja2 import Markup
from premailer import transform
import smtplib

from kpireport.output import OutputDriver


class SMTPOutputDriver(OutputDriver):
    """Email a report's contents via SMTP to one or more recipients.

    Attributes:
        email_from (str): From email address.
        email_to (List[str]): Email addresses to send to.
        smtp_host (str): SMTP server to relay mail through. Defaults to
            "localhost".
        smtp_port (int): SMTP port to use. Defaults to 25.
        image_strategy (str): Strategy to use for including images in the mail
            contents. Two options are available:

            :embed: embed the image directly in the mail using Content-ID
                (`RFC2392 <https://tools.ietf.org/html/rfc2392>`_) linked
                resources. These should be compatible with most modern desktop
                and web mail clients.
            :remote: link the image to a remote resource. For this strategy
                to work, the image assets must exist on a server reachable via
                the public Internet (and not require authentication). Consider
                using the SMTP plugin in conjunction with e.g., the
                :ref:`S3 <s3-plugin>` or :ref:`SCP <scp-plugin>` plugins to
                accomplish this entirely within KPI reporter.

                .. note::

                   No tracking information is included when rendering remote
                   image URLs; if for some reason you need to track open rates,
                   consider using the :ref:`SendGrid <sendgrid-plugin>` plugin
                   to send the report instead.

        image_remote_base_url (str): When using the "remote" image strategy,
            the base URL for the image assets. Image blobs generated by Views
            are placed in folders named after the View ID; this base URL should
            point to the root path for all of these folders.
    """
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
        self.cache_buster = f'?_={datetime.now()}'

    def _parse_address(self, address):
        username, domain = address.split("@")
        return Address(username=username, domain=domain)

    def render_blob_inline(self, blob, fmt=None):
        if self.image_strategy == "embed":
            return Markup(f"""<img src="cid:{blob["id"]}" />""")
        elif self.image_strategy == "remote":
            path = "/".join([self.image_remote_base_url, blob["id"]])
            return Markup(f"""<img src="{path}{self.cache_buster}" />""")
        else:
            raise ValueError(
                f"Unsupported image strategy '{self.image_strategy}'")

    def render_output(self, content, blobs):
        msg = EmailMessage()
        msg["Subject"] = self.report.title
        msg["From"] = self.email_from
        msg["To"] = self.email_to

        msg.set_content(content.get_format("md"))
        html = transform(content.get_format("html"))
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
