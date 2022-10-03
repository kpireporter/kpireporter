from unittest import mock

from kpireport.report import Report
from kpireport.tests.fixtures import FakeResponse
from kpireport_twitter import TwitterDatasource


def test_query(report: "Report", mocker: "mock"):
    pages_served = 0

    def mock_request(resource, params=None, **kwargs):
        if resource == "users/by/username/:fake-username":
            return FakeResponse(200, {"data": {"id": "fake-id"}})
        elif resource == "users/:fake-id/tweets":
            nonlocal pages_served
            if pages_served == 1:
                assert params["pagination_token"] == "fake-page-token"
            pages_served += 1
            return FakeResponse(
                200,
                {
                    "data": [
                        {
                            "created_at": "2020-05-02T12:13:14Z",
                            "retweet_count": 1,
                            "like_count": 2,
                            "quote_count": 3,
                            "text": "fake-text",
                        }
                    ],
                    "meta": {
                        "next_token": "fake-page-token" if pages_served <= 1 else None
                    },
                },
            )
        raise ValueError("did not match expected mock")

    mocker.patch(
        "kpireport_twitter.datasource.sleep"
    )  # Will delay b/w making page requests
    mock_twitter = mocker.patch("kpireport_twitter.datasource.TwitterAPI")()
    mock_twitter.request.side_effect = mock_request
    ds = TwitterDatasource(
        report, consumer_key="fake-consumer-key", consumer_secret="fake-consumer-secret"
    )
    ds.query("tweets", username="fake-username")
    assert mock_twitter.request.call_count == 3
