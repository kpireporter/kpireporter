from unittest import mock

import pytest
from kpireport.report import Content, Report
from kpireport_scp import SCPOutputDriver


def test_missing_remote_path(report: "Report", content: "Content"):
    with pytest.raises(ValueError):
        SCPOutputDriver(report, host="fake-host", remote_path=None)
    with pytest.raises(ValueError):
        SCPOutputDriver(report, host=None, remote_path="/fake-remote-path")


def test_render_output(report: "Report", content: "Content", mocker: "mock"):
    scp = SCPOutputDriver(report, host="localhost", remote_path="/fake-remote-path")
    conn = mocker.patch.object(scp, "connection")
    scp.render_output(content, [])
    conn.put.assert_called_with(
        f"{scp._scp_tmp_dir.name}/{report.id}.tar.gz", remote="/tmp/kpireport.tar.gz"
    )
    conn.run.assert_any_call(
        f"tar -xf /tmp/kpireport.tar.gz -C /fake-remote-path --strip-components=1"
    )
