import unittest
from unittest import mock
import pymcdbsc
import re
import os


class TestMcdbscDownloader(unittest.TestCase):

    os_name2root_dir = {"posix": "/var/lib/pymcdbsc",
                        "nt": "c:\\pymcdbsc"}

    def setUp(self) -> None:
        self.patcher_docker = mock.patch('pymcdbsc.docker')
        self.patcher_requests = mock.patch('pymcdbsc.requests')
        self.mock_docker = self.patcher_docker.start()
        self.mock_requests = self.patcher_requests.start()
        self.mcdbsc = pymcdbsc.McdbscDownloader()

    def tearDown(self) -> None:
        self.patcher_docker.stop()
        self.patcher_requests.stop()

    def _test_root_dir(self, os_name, exp):
        p = mock.patch('pymcdbsc.os_name', os_name)
        p.start()

        act = pymcdbsc.pymcdbsc_root_dir()
        self.assertEqual(act, exp)
        p.stop()

    def test_root_dir(self):
        for (os_name, exp_root_dir) in self.os_name2root_dir.items():
            self._test_root_dir(os_name, exp_root_dir)

    def test_download_dir(self):
        mcdbsc = self.mcdbsc
        root_dir = self.os_name2root_dir[os.name]

        act = mcdbsc.download_dir(relative=False)
        exp = os.path.join(root_dir, "downloads")
        self.assertEqual(act, exp)

        act = mcdbsc.download_dir(relative=True)
        exp = "downloads"
        self.assertEqual(act, exp)

    def _set_dummy_attr(self, mcdbsc=None) -> None:
        if mcdbsc is None:
            mcdbsc = self.mcdbsc

        mcdbsc._zip_url = "https://example.com/bedrock-server-1.0.0.0.zip"
        mcdbsc._latest_version = "1.0.0.0"

    def test_zip_url(self) -> None:
        mcdbsc = self.mcdbsc

        # 実際にリクエストを飛ばした際の挙動を確認する為、 requests のパッチを停止する。
        self.patcher_requests.stop()

        act = mcdbsc.zip_url()
        exp = re.match("https?://.*[^/]/bedrock-server-([0-9.]+)+\\.zip", act)
        self.assertIsNotNone(exp)
        self.assertIsNotNone(mcdbsc._zip_url)
        self.assertIsNotNone(mcdbsc._latest_version)

    def test_latest_version(self) -> None:
        mcdbsc = self.mcdbsc

        # 実際にリクエストを飛ばした際の挙動を確認する為、 requests のパッチを停止する。
        self.patcher_requests.stop()

        act = mcdbsc.latest_version()
        exp = re.match("([0-9.]+)", act)
        self.assertIsNotNone(exp)

    def test_latest_filename(self) -> None:
        mcdbsc = self.mcdbsc

        self._set_dummy_attr()

        act = mcdbsc.latest_filename()
        exp = "bedrock-server-1.0.0.0.zip"
        self.assertEqual(act, exp)

    def test_latest_version_zip_filepath(self) -> None:
        mcdbsc = self.mcdbsc

        self._set_dummy_attr(mcdbsc)

        act = mcdbsc.latest_version_zip_filepath()
        exp = os.path.join(self.os_name2root_dir[os.name], "downloads", "bedrock-server-1.0.0.0.zip")
        self.assertEqual(act, exp)
