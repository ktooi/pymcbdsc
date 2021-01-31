from typing import List
import unittest
from unittest import mock
import os
import random
import shutil
import pymcbdsc
# os_name2test_root_dir: os.name で取得できる OS の名前と、各 OS でのテストケース実行時に利用するテスト用ディレクトリパスのペア。
from .test_utils import os_name2test_root_dir
from . import stop_patcher, create_empty_files


class TestMcbdscDockerManager(unittest.TestCase):

    def setUp(self) -> None:
        test_dir = os_name2test_root_dir[os.name]
        os.makedirs(test_dir, exist_ok=True)
        self.test_dir = test_dir
        self.patcher_docker = mock.patch('pymcbdsc.docker.docker')
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

    def test_list_images(self) -> None:
        pass

    def test_set_tag(self) -> None:
        pass

    def test_set_latest_tag_to_latest_image(self) -> None:
        pass

    def test_set_minor_tags(self) -> None:
        pass

    def test_get_bds_versions_from_container_image(self) -> None:
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
