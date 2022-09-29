from email.message import EmailMessage
from unittest import mock

from kpireport.report import Content, Report
from kpireport_smtp import SMTPOutputDriver


def test_report_output(report: "Report", content: "Content", mocker: "mock"):
    def send_message(msg: "EmailMessage"):
        assert msg["Subject"] == report.title
        assert msg["To"] == "to@example.com"
        assert msg["From"] == "from@example.com"
        payload = msg.get_payload()
        assert len(payload) == 2
        assert payload[0].get_payload() == content.get_format("md")

    fake_smtp = mocker.patch("kpireport_smtp.output.smtplib.SMTP")()
    # Need to also tell the __enter__ context mgr function to return the same mock,
    # by default it wants to create a new mock as the return value.
    fake_smtp.__enter__.return_value = fake_smtp
    fake_smtp.send_message.side_effect = send_message

    smtp = SMTPOutputDriver(
        report, email_from="from@example.com", email_to="to@example.com"
    )
    smtp.render_output(content, [])

    fake_smtp.send_message.assert_called_once()
