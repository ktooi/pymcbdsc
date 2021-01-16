import unittest
from unittest import mock
import pymcbdsc
import re
import os
import shutil
from sys import version_info
from logging import getLogger


logger = getLogger(__name__)


os_name2root_dir = {"posix": "/var/lib/pymcbdsc",
                    "nt": "c:\\pymcbdsc"}


class TestCommon(unittest.TestCase):

    def _test_pymcbdsc_root_dir(self, os_name: str, exp: str) -> None:
        p = mock.patch('pymcbdsc.os_name', os_name)
        p.start()

        act = pymcbdsc.pymcbdsc_root_dir()
        self.assertEqual(act, exp)
        p.stop()

    def test_pymcbdsc_root_dir(self) -> None:
        for (os_name, exp_root_dir) in os_name2root_dir.items():
            self._test_pymcbdsc_root_dir(os_name, exp_root_dir)


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

    os_name2test_root_dir = {"posix": "/tmp/test/pymcbdsc",
                             "nt": "c:\\test\\pymcbdsc"}

    def setUp(self) -> None:
        test_dir = self.os_name2test_root_dir[os.name]
        os.makedirs(test_dir)
        self.test_dir = test_dir
        self.patcher_requests = mock.patch('pymcbdsc.requests')
        self.mock_requests = self.patcher_requests.start()
        self.mcbdsc = pymcbdsc.McbdscDownloader(pymcbdsc_root_dir=test_dir)

    def tearDown(self) -> None:
        stop_patcher(self.patcher_requests)
        shutil.rmtree(self.os_name2test_root_dir[os.name])

    def test_root_dir(self) -> None:
        # __init__() での初期値を試験。
        mcbdsc = pymcbdsc.McbdscDownloader()

        act = mcbdsc.root_dir()
        # OS 毎に初期値が異なるが、初期値は import した段階で決まってしまうので、
        # OS 毎の初期値を試験するのは難しい。
        # 初期値を決定する pymcbdsc.pymcbdsc_root_dir() 関数の試験は別途行っているので、
        # その試験結果を以て OS 毎の初期値は問題ないものとする。
        exp = os_name2root_dir[os.name]
        self.assertEqual(act, exp)

        # __init__() で pymcbdsc_root_dir を指定した場合の試験。
        exp = "/path/to/root"
        mcbdsc = pymcbdsc.McbdscDownloader(pymcbdsc_root_dir=exp)
        act = mcbdsc.root_dir()
        self.assertEqual(act, exp)

    def test_download_dir(self) -> None:
        mcbdsc = self.mcbdsc
        root_dir = self.test_dir

        # relative パラメータが False の場合の試験。
        act = mcbdsc.download_dir(relative=False)
        exp = os.path.join(root_dir, "downloads")
        self.assertEqual(act, exp)

        # relative パラメータが True の場合の試験。
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
        exp = os.path.join(self.test_dir, "downloads", "bedrock-server-1.0.0.0.zip")
        self.assertEqual(act, exp)

    def test_has_latest_version_zip_file(self) -> None:
        # "downloads" ディレクトリが存在しない場合に、 False となる試験。
        mcbdsc = self.mcbdsc
        self._set_dummy_attr(mcbdsc=mcbdsc)

        act = mcbdsc.has_latest_version_zip_file()
        exp = False
        self.assertEqual(act, exp)

        # "downloads" ディレクトリが存在するが、ファイルがない場合に False となる試験。
        downloads_dir = os.path.join(self.test_dir, "downloads")
        os.makedirs(downloads_dir)

        act = mcbdsc.has_latest_version_zip_file()
        exp = False
        self.assertEqual(act, exp)

        # "downloads" ディレクトリが存在し、ファイルが存在する場合に True となる試験。
        with open(os.path.join(downloads_dir, "bedrock-server-1.0.0.0.zip"), "w") as f:
            f.write('')

        act = mcbdsc.has_latest_version_zip_file()
        exp = True
        self.assertEqual(act, exp)

    def test_download(self) -> None:
        pass

    def test_download_latest_version_zip_file(self) -> None:
        pass

    def test_download_latest_version_zip_file_if_needed(self) -> None:
        pass
