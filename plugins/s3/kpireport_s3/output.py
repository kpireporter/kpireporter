import boto3
import tempfile
import os

from kpireport_static import StaticOutputDriver

import logging

LOG = logging.getLogger(__name__)


class S3OutputDriver(StaticOutputDriver):
    """
    Attributes:
        bucket (str): the S3 bucket to upload to.
        prefix (str): the key prefix.
        kwargs: any additional keyword arguments are passed in to the
            :class:`boto3.client` constructor.
    """
    def init(self, **kwargs):
        self.bucket = kwargs.pop("bucket", None)
        self.prefix = kwargs.pop("prefix", None)
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html#boto3.session.Session.client
        self.s3 = boto3.client("s3", **kwargs)

        if not self.bucket:
            raise ValueError("'bucket' is required")

        self.tmp_dir = tempfile.TemporaryDirectory()

        super(S3OutputDriver, self).init(output_dir=self.tmp_dir.name)

    def render_output(self, content, blobs):
        super(S3OutputDriver, self).render_output(content, blobs)

        with self.tmp_dir as tmp_dir:
            for root, _, files in os.walk(tmp_dir):
                path = root.replace(tmp_dir, "").lstrip("/")
                prefix = self.prefix or ""
                for f in files:
                    key = f"{prefix}{path}/{f}"
                    self.s3.upload_file(f"{root}/{f}", self.bucket, key)
