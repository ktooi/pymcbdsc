import unittest
from unittest import mock
import pymcbdsc
import re
import os
from sys import version_info
from logging import getLogger


logger = getLogger(__name__)


def stop_patcher(patcher, patcher_name=None):
    """ mock.patch を停止する関数。

    Python3.5, 3.6, 3.7 では、既に `stop()` をコールした patch で再度 `stop()` をコールすると
    次のような Exception が Raise されてしまうので、その対処を行う。

    >>> patcher = mock.patch('hoge')
    >>> patcher.start()
    >>> patcher.stop()
    >>> patcher.stop()  # すでに `stop()` をコールした patch で再度 `stop()` をコールする。
    Traceback (most recent call last):
    ...snip...
    RuntimeError: stop called on unstarted patcher

    一度 `stop()` をコールした patch からは "is_local" 属性がなくなるので、 "is_local" 属性の有無で
    patch の `stop()` をコールするか否かを判断する。ハック的だがやり方として問題ないかは知らん。

    なお、 Python3.8, 3.9 では `stop()` をコールした patch で再度 `stop()` しても問題はないので、
    このハックは利用せずに、何も気にしないで `stop()` をコールする。
    """
    (major, minor) = version_info[0:2]
    if major == 3 and (minor >= 5 and minor <= 7):  # Python3.5, 3.6, 3.7 のみハックを利用。
        if hasattr(patcher, "is_local"):
            patcher.stop()
        else:
            if patcher_name is None:
                patcher_name = patcher.attribute
            logger.info("Trying stop a patcher named {name} but it was already stopped.".format(name=patcher_name))
    else:  # Python3.5, 3.6, 3.7 以外はハックを利用しない。
        patcher.stop()


class TestMcbdscDownloader(unittest.TestCase):

    os_name2root_dir = {"posix": "/var/lib/pymcbdsc",
                        "nt": "c:\\pymcbdsc"}

    def setUp(self) -> None:
        self.patcher_docker = mock.patch('pymcbdsc.docker')
        self.patcher_requests = mock.patch('pymcbdsc.requests')
        self.mock_docker = self.patcher_docker.start()
        self.mock_requests = self.patcher_requests.start()
        self.mcbdsc = pymcbdsc.McbdscDownloader()

    def tearDown(self) -> None:
        stop_patcher(self.patcher_docker)
        stop_patcher(self.patcher_requests)

    def _test_root_dir(self, os_name, exp):
        p = mock.patch('pymcbdsc.os_name', os_name)
        p.start()

        act = pymcbdsc.pymcbdsc_root_dir()
        self.assertEqual(act, exp)
        p.stop()

    def test_root_dir(self):
        for (os_name, exp_root_dir) in self.os_name2root_dir.items():
            self._test_root_dir(os_name, exp_root_dir)

    def test_download_dir(self):
        mcbdsc = self.mcbdsc
        root_dir = self.os_name2root_dir[os.name]

        act = mcbdsc.download_dir(relative=False)
        exp = os.path.join(root_dir, "downloads")
        self.assertEqual(act, exp)

        act = mcbdsc.download_dir(relative=True)
        exp = "downloads"
        self.assertEqual(act, exp)

    def _set_dummy_attr(self, mcbdsc=None) -> None:
        if mcbdsc is None:
            mcbdsc = self.mcbdsc

        mcbdsc._zip_url = "https://example.com/bedrock-server-1.0.0.0.zip"
        mcbdsc._latest_version = "1.0.0.0"

    def test_zip_url(self) -> None:
        mcbdsc = self.mcbdsc

        # 実際にリクエストを飛ばした際の挙動を確認する為、 requests のパッチを停止する。
        self.patcher_requests.stop()

        act = mcbdsc.zip_url()
        exp = re.match("https?://.*[^/]/bedrock-server-([0-9.]+)+\\.zip", act)
        self.assertIsNotNone(exp)
        self.assertIsNotNone(mcbdsc._zip_url)
        self.assertIsNotNone(mcbdsc._latest_version)

    def test_latest_version(self) -> None:
        mcbdsc = self.mcbdsc

        # 実際にリクエストを飛ばした際の挙動を確認する為、 requests のパッチを停止する。
        self.patcher_requests.stop()

        act = mcbdsc.latest_version()
        exp = re.match("([0-9.]+)", act)
        self.assertIsNotNone(exp)

    def test_latest_filename(self) -> None:
        mcbdsc = self.mcbdsc

        self._set_dummy_attr()

        act = mcbdsc.latest_filename()
        exp = "bedrock-server-1.0.0.0.zip"
        self.assertEqual(act, exp)

    def test_latest_version_zip_filepath(self) -> None:
        mcbdsc = self.mcbdsc

        self._set_dummy_attr(mcbdsc)

        act = mcbdsc.latest_version_zip_filepath()
        exp = os.path.join(self.os_name2root_dir[os.name], "downloads", "bedrock-server-1.0.0.0.zip")
        self.assertEqual(act, exp)
