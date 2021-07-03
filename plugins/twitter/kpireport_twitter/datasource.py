from time import sleep

import pandas as pd
from TwitterAPI import TwitterAPI, TwitterRequestError, TwitterConnectionError

from kpireport.datasource import Datasource, DatasourceError

import logging

LOG = logging.getLogger(__name__)


class TwitterDatasource(Datasource):
    """A datasource that can fetch metrics from Twitter's V2 API.

    Currently the following queries are supported:

    * ``tweets``: request a list of the user's latest Tweets via the `Timeline API
      <https://developer.twitter.com/en/docs/twitter-api/tweets/timelines/api-reference/get-users-id-tweets>`_.
      If requesting the authenticated user's own timeline, "non-public" metrics such
      as impression counts are included in the output table result. Otherwise, only
      public metrics such as like, reply, and retweet counts are retrieved. The text
      and ID of the Tweet are also included in the output table.

    Attributes:
        consumer_key (str): The Twitter application consumer public key.
        consumer_secret (str): The Twitter application consumer secret.
        access_token_key (str): The user-scoped access token public key.
        access_token_secret (str): The user-scoped access token secret.
        pagination_delay_s (int): The number of seconds to wait before fetching the
            next page of results from Twitter's API. It is recommended to set this to
            at least 1 to avoid rate limits or downstream errors from the API.
            (Default 5)
    """

    def init(
        self,
        consumer_key=None,
        consumer_secret=None,
        access_token_key=None,
        access_token_secret=None,
        pagination_delay_s=5,
    ):
        self._user_context = access_token_key is not None
        auth_type = "oAuth2"
        self.twitter = TwitterAPI(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token_key=access_token_key,
            access_token_secret=access_token_secret,
            auth_type=auth_type,
            api_version="2",
        )
        self.twitter_v1 = TwitterAPI(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token_key=access_token_key,
            access_token_secret=access_token_secret,
            auth_type=auth_type,
            api_version="1.1",
        )
        self.pagination_delay_s = pagination_delay_s

    def query(self, query: str, **kwargs) -> pd.DataFrame:
        if query == "tweets":
            return self.query_tweets(**kwargs)
        else:
            raise ValueError(f"Invalid query '{query}'")

    def query_tweets(self, username=None, fields=None) -> pd.DataFrame:
        user_id = self._get_user_id(username)
        fields = [
            "created_at",
            "text",
            "public_metrics",
        ]

        if self._user_context:
            fields.append("non_public_metrics")

        page_counter = 1
        tweets, pagination_token = self._fetch_tweets(user_id, fields)
        while pagination_token:
            page_counter += 1
            LOG.info(f"Fetching page {page_counter} of Tweets...")
            if self.pagination_delay_s:
                sleep(self.pagination_delay_s)
            _tweets, pagination_token = self._fetch_tweets(
                user_id, fields, pagination_token=pagination_token
            )
            tweets.extend(_tweets)

        df = pd.json_normalize(tweets)
        # Convert timestamps to report timezone
        df["created_at"] = pd.to_datetime(df["created_at"])
        df["created_at"] = df["created_at"].dt.tz_convert(self.report.timezone)

        def _rename_column(col):
            # Rename time column for easier integration with e.g., plot plugin
            if col == "created_at":
                return "time"
            for prefix in ["public_metrics.", "non_public_metrics."]:
                if col.startswith(prefix):
                    return col.replace(prefix, "")
            return col

        df = df.rename(_rename_column, axis="columns")
        df["retweet_and_quote_count"] = df["retweet_count"] + df["quote_count"]
        df = df.drop(["retweet_count", "quote_count"], axis="columns")

        def _sort_cols(col):
            count_ordering = [
                "like_count",
                "retweet_and_quote_count",
                "reply_count",
                "impression_count",
            ]
            # Time column goes first
            if col == "time":
                return -1
            # Try to order count columns by highest to lowest, generally
            elif col in count_ordering:
                return count_ordering.index(col) / len(count_ordering)
            else:
                return 1

        df = df[sorted(df.columns, key=_sort_cols)]
        LOG.debug(df)
        return df

    def _fetch_tweets(self, user_id, fields, pagination_token=None):
        query_args = {
            "start_time": self.report.start_date.isoformat(),
            "tweet.fields": ",".join(fields),
            # Show only direct tweets
            "exclude": "retweets,replies",
        }
        if pagination_token:
            query_args["pagination_token"] = pagination_token
        res = self.twitter.request(f"users/:{user_id}/tweets", query_args)
        res_json = res.json()
        if "errors" in res_json:
            details = set(err["detail"] for err in res_json["errors"])
            raise DatasourceError(f"Twiter API responded with errors: {details}")
        # Handle empty pages; "data" is not present in such cases.
        return res_json.get("data", []), res_json["meta"].get("next_token")

    def _get_user_id(self, username) -> str:
        if not username:
            res = self.twitter_v1.request(f"account/verify_credentials")
            if res.status_code == 200:
                user = res.json()
                LOG.info(f"Auto-detected username of {user['screen_name']}")
                return user["id"]
            else:
                raise ValueError(
                    (
                        "No username specified, and provided credentials are not valid "
                        "for any user. Verify the access_token_key/secret if "
                        "authenticating as a user, or specify a username explicitly."
                    )
                )

        res = self.twitter.request(f"users/by/username/:{username}")
        payload = res.json()
        if res.status_code != 200:
            if "errors" in payload:
                message = payload["errors"][0]["detail"]
            else:
                message = res.text
            raise ValueError(f"Failed to get user {username}: {message}")
        return payload["data"]["id"]
