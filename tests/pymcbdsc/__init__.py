from typing import List
import unittest
from unittest import mock
import pymcbdsc
import re
import os
import shutil
import random
from sys import version_info
from logging import getLogger


logger = getLogger(__name__)

# os.name で取得できる OS の名前と、各 OS のデフォルトとなる pymbdsc_root_dir のデフォルト値のペア。
os_name2root_dir = {"posix": "/var/lib/pymcbdsc",
                    "nt": "c:\\pymcbdsc"}
# os.name で取得できる OS の名前と、各 OS でのテストケース実行時に利用するテスト用ディレクトリパスのペア。
os_name2test_root_dir = {"posix": "/tmp/test/pymcbdsc",
                         "nt": "c:\\test\\pymcbdsc"}


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


def create_empty_files(dir: str, files: List[str]) -> None:
    """ 空ファイルを作成する関数。 """
    for file in files:
        with open(os.path.join(dir, file), "w") as f:
            f.write('')


class TestCommon(unittest.TestCase):
    """ pymcbdsc モジュールに定義されている関数をテストするテストクラス。 """

    def _test_pymcbdsc_root_dir(self, os_name: str, exp: str) -> None:
        p = mock.patch('pymcbdsc.os_name', os_name)
        p.start()

        act = pymcbdsc.pymcbdsc_root_dir()
        self.assertEqual(act, exp)
        p.stop()

    def test_pymcbdsc_root_dir(self) -> None:
        for (os_name, exp_root_dir) in os_name2root_dir.items():
            self._test_pymcbdsc_root_dir(os_name, exp_root_dir)


class TestMcbdscDownloader(unittest.TestCase):

    def setUp(self) -> None:
        test_dir = os_name2test_root_dir[os.name]
        os.makedirs(test_dir, exist_ok=True)
        self.test_dir = test_dir
        self.patcher_requests = mock.patch('pymcbdsc.requests')
        self.mock_requests = self.patcher_requests.start()
        self.mcbdsc = pymcbdsc.McbdscDownloader(pymcbdsc_root_dir=test_dir)

    def tearDown(self) -> None:
        stop_patcher(self.patcher_requests)
        shutil.rmtree(os_name2test_root_dir[os.name])

    def test_root_dir(self) -> None:
        # __init__() での初期値を試験。
        mcbdsc = pymcbdsc.McbdscDownloader()

        act = mcbdsc.root_dir()
        # OS 毎に初期値が異なるが、初期値は import した段階で決まってしまうので、
        # OS 毎の初期値を試験するのは難しい。
        # 初期値を決定する pymcbdsc.pymcbdsc_root_dir() 関数の試験は別途行っているので、
        # その試験結果を以て OS 毎の初期値は問題ないものとする。
        # よって、ここではこのテストケースを実行した OS の初期値が戻ることのみを確認する。
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
        create_empty_files(downloads_dir, ["bedrock-server-1.0.0.0.zip"])

        act = mcbdsc.has_latest_version_zip_file()
        exp = True
        self.assertEqual(act, exp)

    def test_download(self) -> None:
        pass

    def test_download_latest_version_zip_file(self) -> None:
        pass

    def test_download_latest_version_zip_file_if_needed(self) -> None:
        pass


class TestMcbdscDockerManager(unittest.TestCase):

    def setUp(self) -> None:
        test_dir = os_name2test_root_dir[os.name]
        os.makedirs(test_dir, exist_ok=True)
        self.test_dir = test_dir
        self.patcher_docker = mock.patch('pymcbdsc.docker')
        self.mock_docker = self.patcher_docker.start()
        self.manager = pymcbdsc.McbdscDockerManager(pymcbdsc_root_dir=test_dir, containers_param=[])

    def tearDown(self) -> None:
        stop_patcher(self.patcher_docker)
        shutil.rmtree(os_name2test_root_dir[os.name])

    def test_factory_containers(self) -> None:
        pass

    def test_build_image(self) -> None:
        pass

    def test_get_image(self) -> None:
        pass

    def _dummy_bds(self) -> List:
        return (["bedrock-server-1.0.0.0.zip",
                 "bedrock-server-1.1.1.1.zip",
                 "bedrock-server-1.2.3.4.zip",
                 "bedrock-server-1.10.3.4.zip",
                 "bedrock-server-1.10.3.05.zip",
                 "bedrock-server-4.3.2.1.zip"],
                # 上記 bedrock-server-*.zip のバージョンを昇順でリスト化。
                ["1.0.0.0",
                 "1.1.1.1",
                 "1.2.3.4",
                 "1.10.3.4",
                 "1.10.3.05",
                 "4.3.2.1"])

    def test_get_bds_versions_from_local_file(self) -> None:
        manager = self.manager

        downloads_dir = os.path.join(self.test_dir, "downloads")
        os.makedirs(downloads_dir)
        (test_files, versions) = self._dummy_bds()
        create_empty_files(downloads_dir, test_files)

        # _dummy_bds() メソッドの戻り値通りのバージョンが戻ることを確認する。
        # (順不同なので sorted() した結果で比較する。)
        act = sorted(manager.get_bds_versions_from_local_file())
        exp = sorted(versions)
        self.assertEqual(act, exp)

        # バージョンが昇順であることを確認する。
        act = manager.get_bds_versions_from_local_file(sort=True)
        exp = versions
        self.assertEqual(act, exp)

        # バージョンが降順であることを確認する。
        act = manager.get_bds_versions_from_local_file(sort=True, reverse=True)
        exp = list(reversed(versions))
        self.assertEqual(act, exp)

        # BDS Zip ファイル名のパターンと一致するディレクトリが存在しても、それを無視する事を確認する。
        os.makedirs(os.path.join(downloads_dir, "bedrock-server-9.9.9.9.zip"))  # 無視していない場合、 "9.9.9.9" がリストに紛れ込む。
        act = sorted(manager.get_bds_versions_from_local_file())
        exp = sorted(versions)
        self.assertEqual(act, exp)

        # BDS Zip ファイル名のパターンと部分一致するファイルが存在しても、それを無視する事を確認する。
        create_empty_files(downloads_dir, ["bedrock-server-8.8.8.8.zip.bak"])  # 無視していない場合、 "8.8.8.8" がリストに紛れ込む。
        act = sorted(manager.get_bds_versions_from_local_file())
        exp = sorted(versions)
        self.assertEqual(act, exp)

        shutil.rmtree(downloads_dir)
        # ディレクトリが存在しない場合に FileNotFoundError が Raise されることを確認する。
        with self.assertRaises(FileNotFoundError):
            act = manager.get_bds_versions_from_local_file()

        # ディレクトリが存在するが、 BDS Zip ファイルが存在しない場合に空リストが戻ることを確認する。
        os.makedirs(downloads_dir)
        act = manager.get_bds_versions_from_local_file()
        exp = []
        self.assertEqual(act, exp)

    def test_sort_bds_versions(self) -> None:
        versions = self._dummy_bds()[1]

        # ランダムにシャッフルされた test_versions が昇順ソートされたことを確認する。
        test_versions = random.sample(versions, len(versions))
        pymcbdsc.McbdscDockerManager.sort_bds_versions(versions=test_versions)
        act = test_versions
        exp = versions
        self.assertEqual(act, exp)

        # ランダムにシャッフルされた test_versions が降順ソートされたことを確認する。
        test_versions = random.sample(versions, len(versions))
        pymcbdsc.McbdscDockerManager.sort_bds_versions(versions=test_versions, reverse=True)
        act = test_versions
        exp = list(reversed(versions))
        self.assertEqual(act, exp)

        # 空リストでも問題ないことを確認する。
        test_versions = []
        pymcbdsc.McbdscDockerManager.sort_bds_versions(versions=test_versions)
        act = test_versions
        exp = []
        self.assertEqual(act, exp)

    def test_get_bds_latest_version_from_local_file(self) -> None:
        manager = self.manager

        downloads_dir = os.path.join(self.test_dir, "downloads")
        os.makedirs(downloads_dir)
        (test_files, versions) = self._dummy_bds()
        create_empty_files(downloads_dir, test_files)

        # _dummy_bds() メソッドから取得した中で、最もバージョンが高いもの一つと一致することを確認する。
        act = manager.get_bds_latest_version_from_local_file()
        exp = versions[-1]
        self.assertEqual(act, exp)

        shutil.rmtree(downloads_dir)
        # ディレクトリが存在しない場合に FileNotFoundError が Raise されることを確認する。
        with self.assertRaises(FileNotFoundError):
            manager.get_bds_latest_version_from_local_file()

        # ディレクトリが存在するが、 BDS Zip ファイルが存在しない場合は None となることを確認する。
        os.makedirs(downloads_dir)
        act = manager.get_bds_latest_version_from_local_file()
        exp = None
        self.assertEqual(act, exp)
