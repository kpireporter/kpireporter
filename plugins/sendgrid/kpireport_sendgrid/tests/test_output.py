from unittest import mock

import pytest
from kpireport.report import Content, Report
from kpireport.tests.fixtures import FakeResponse
from kpireport_sendgrid import SendGridOutputDriver

FAKE_API_KEY = "fake-api-key"


def test_missing_something(report: "Report"):
    with pytest.raises(ValueError):
        SendGridOutputDriver(report)


def test_bad_status_code(report: "Report", content: "Content", mocker: "mock"):
    sg = SendGridOutputDriver(
        report,
        api_key=FAKE_API_KEY,
        email_from="fake-from@example.com",
        email_to="fake-to@example.com",
    )
    FakeAPIClient = mocker.patch("kpireport_sendgrid.output.SendGridAPIClient")
    FakeAPIClient().send.return_value = FakeResponse(200, "")
    with pytest.raises(ValueError):
        sg.render_output(content, [])


def test_good_status_code(report: "Report", content: "Content", mocker: "mock"):
    sg = SendGridOutputDriver(
        report,
        api_key=FAKE_API_KEY,
        email_from="fake-from@example.com",
        email_to="fake-to@example.com",
    )
    FakeAPIClient = mocker.patch("kpireport_sendgrid.output.SendGridAPIClient")
    send = FakeAPIClient().send
    send.return_value = FakeResponse(202, "")
    sg.render_output(content, [])
    msg = send.call_args.args[0]
    assert msg.from_email.email == "fake-from@example.com"
    assert msg.personalizations[0].tos[0]["email"] == "fake-to@example.com"
    assert msg.subject.subject == report.title
    assert msg.contents[0].content
