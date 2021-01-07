import unittest
from unittest import mock
import pymsbre
import re
import os


class TestMsbreDownloader(unittest.TestCase):

    os_name2root_dir = {"posix": "/var/lib/pymsbre",
                        "nt": "c:\\pymsbre"}

    def setUp(self) -> None:
        self.patcher_docker = mock.patch('pymsbre.docker')
        self.patcher_requests = mock.patch('pymsbre.requests')
        self.mock_docker = self.patcher_docker.start()
        self.mock_requests = self.patcher_requests.start()
        self.msbre = pymsbre.MsbreDownloader()

    def tearDown(self) -> None:
        self.patcher_docker.stop()
        self.patcher_requests.stop()

    def _test_root_dir(self, os_name, exp):
        p = mock.patch('pymsbre.os_name', os_name)
        p.start()

        act = pymsbre.pymsbre_root_dir()
        self.assertEqual(act, exp)
        p.stop()

    def test_root_dir(self):
        for (os_name, exp_root_dir) in self.os_name2root_dir.items():
            self._test_root_dir(os_name, exp_root_dir)

    def test_download_dir(self):
        msbre = self.msbre
        root_dir = self.os_name2root_dir[os.name]

        act = msbre.download_dir(relative=False)
        exp = os.path.join(root_dir, "downloads")
        self.assertEqual(act, exp)

        act = msbre.download_dir(relative=True)
        exp = "downloads"
        self.assertEqual(act, exp)

    def _set_dummy_attr(self, msbre=None) -> None:
        if msbre is None:
            msbre = self.msbre

        msbre._zip_url = "https://example.com/bedrock-server-1.0.0.0.zip"
        msbre._latest_version = "1.0.0.0"

    def test_zip_url(self) -> None:
        msbre = self.msbre

        # 実際にリクエストを飛ばした際の挙動を確認する為、 requests のパッチを停止する。
        self.patcher_requests.stop()

        act = msbre.zip_url()
        exp = re.match("https?://.*[^/]/bedrock-server-([0-9.]+)+\\.zip", act)
        self.assertIsNotNone(exp)
        self.assertIsNotNone(msbre._zip_url)
        self.assertIsNotNone(msbre._latest_version)

    def test_latest_version(self) -> None:
        msbre = self.msbre

        # 実際にリクエストを飛ばした際の挙動を確認する為、 requests のパッチを停止する。
        self.patcher_requests.stop()

        act = msbre.latest_version()
        exp = re.match("([0-9.]+)", act)
        self.assertIsNotNone(exp)

    def test_latest_filename(self) -> None:
        msbre = self.msbre

        self._set_dummy_attr()

        act = msbre.latest_filename()
        exp = "bedrock-server-1.0.0.0.zip"
        self.assertEqual(act, exp)

    def test_latest_version_zip_filepath(self) -> None:
        msbre = self.msbre

        self._set_dummy_attr(msbre)

        act = msbre.latest_version_zip_filepath()
        exp = os.path.join(self.os_name2root_dir[os.name], "downloads", "bedrock-server-1.0.0.0.zip")
        self.assertEqual(act, exp)
