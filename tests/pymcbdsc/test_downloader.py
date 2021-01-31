from typing import Optional
import unittest
from unittest import mock
import os
import shutil
import pymcbdsc
# os_name2root_dir: os.name で取得できる OS の名前と、各 OS のデフォルトとなる pymbdsc_root_dir のデフォルト値のペア。
# os_name2test_root_dir: os.name で取得できる OS の名前と、各 OS でのテストケース実行時に利用するテスト用ディレクトリパスのペア。
from .test_utils import os_name2root_dir, os_name2test_root_dir
from . import stop_patcher, create_empty_files


class TestMcbdscDownloader(unittest.TestCase):

    mocked_response_bds_ver = "9.99.999.99"
    mocked_response_bds_file = "bedrock-server-{bds_ver}.zip".format(bds_ver=mocked_response_bds_ver)
    mocked_response_url = ("https://minecraft.azureedge.net/bin-linux/{bds_file}"
                           .format(bds_file=mocked_response_bds_file))
    mocked_response_content = b'TEST FILE'

    def setUp(self) -> None:
        test_dir = os_name2test_root_dir[os.name]
        os.makedirs(test_dir, exist_ok=True)
        self.test_dir = test_dir
        self.patcher_requests = mock.patch('pymcbdsc.downloader.requests')
        self.mock_requests = self.patcher_requests.start()
        self.mcbdsc = self.gen_downloader()

    def tearDown(self) -> None:
        stop_patcher(self.patcher_requests)
        shutil.rmtree(self.test_dir)
        if hasattr(self, "_response"):
            # response モックが生成されていたら、削除する。
            delattr(self, "_response")

    # 以下、テスト用サポートメソッドの定義。

    @property
    def response(self):
        # requests.get() の戻り値をモックする MagicMock を戻すメソッド。
        if not hasattr(self, "_response"):
            response = mock.MagicMock()
            self.mock_requests.get.return_value = response
            self._response = response
        return self._response

    def gen_downloader(self, **kwargs) -> pymcbdsc.McbdscDownloader:
        test_dir = self.test_dir
        return pymcbdsc.McbdscDownloader(pymcbdsc_root_dir=test_dir, **kwargs)

    def _set_dummy_attr(self, mcbdsc: Optional[pymcbdsc.McbdscDownloader] = None) -> None:
        if mcbdsc is None:
            mcbdsc = self.mcbdsc

        mcbdsc._zip_url = "https://example.com/bedrock-server-1.0.0.0.zip"
        mcbdsc._latest_version = "1.0.0.0"

    def _set_dummy_url_response(self) -> None:
        response = self.response
        text = mock.PropertyMock()
        text.return_value = ('<a href="{url}"'
                             ' class="btn btn-disabled-outline mt-4 downloadlink" role="button"'
                             ' data-platform="serverBedrockLinux" tabindex="-1">Download </a>'
                             .format(url=self.mocked_response_url))
        type(response).text = text

    def _set_dummy_file_response(self, response=None) -> None:
        response = self.response
        content = mock.PropertyMock()
        content.return_value = self.mocked_response_content
        type(response).content = content

    # 以下、テストメソッドの定義。

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

    def test_zip_url(self) -> None:
        mcbdsc = self.mcbdsc

        self._set_dummy_url_response()

        # mock 済み response に含まれる url が戻されることを確認。
        act = mcbdsc.zip_url()
        exp = self.mocked_response_url
        self.assertEqual(act, exp)

    def test_latest_version(self) -> None:
        mcbdsc = self.mcbdsc

        self._set_dummy_url_response()

        # mock 済み response に含まれるバージョンが戻されることを確認。
        act = mcbdsc.latest_version()
        exp = self.mocked_response_bds_ver
        self.assertEqual(act, exp)

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
        mcbdsc = self.mcbdsc

        self._set_dummy_file_response()

        # 指定した URL の内容がファイルとして保存されることを確認する。
        testurl = "https://example.com/dummy_file"
        testfile = os.path.join(self.test_dir, "download_test")
        mcbdsc.download(url=testurl, filepath=testfile)
        # testurl を get しているか確認する。
        act = self.mock_requests.get.call_args
        exp = unittest.mock.call(testurl)
        self.assertEqual(act, exp)
        # ファイルが意図したとおりの内容で保存されているか確認する。
        with open(testfile, 'rb') as f:
            act = f.read()
        exp = self.mocked_response_content
        self.assertEqual(act, exp)

    def _test_download_latest_version_zip_file(self, mcbdsc, params) -> None:
        os.makedirs(mcbdsc.download_dir(), exist_ok=True)
        mcbdsc.download_latest_version_zip_file(**params)
        # 最新のファイルパスが意図したとおりになっているか確認する。
        act_path = mcbdsc.latest_version_zip_filepath()
        exp_path = os.path.join(self.test_dir, "downloads", self.mocked_response_bds_file)
        self.assertEqual(act_path, exp_path)
        # _set_dummy_url_response により戻されたダミーの URL に対して get しているか確認する。
        act = self.mock_requests.get.call_args
        exp = unittest.mock.call(self.mocked_response_url)
        self.assertEqual(act, exp)
        # ファイルが意図したとおりの内容で保存されているか確認する。
        with open(act_path, 'rb') as f:
            act = f.read()
        exp = self.mocked_response_content
        self.assertEqual(act, exp)

    def test_download_latest_version_zip_file(self) -> None:
        mcbdsc = self.mcbdsc

        # agree_to_meula_and_pp が False の場合に
        # FailureAgreeMeulaAndPpError が Raise されることを確認する。
        with self.assertRaises(pymcbdsc.exceptions.FailureAgreeMeulaAndPpError):
            mcbdsc.download_latest_version_zip_file(agree_to_meula_and_pp=False)

        # McbdscDownloader の初期化時に agree_to_meula_and_pp が未指定で、
        # 且つ download_latest_version_zip_file メソッドでも未指定の場合に
        # FailureAgreeMeulaAndPpError が Raise されることを確認する。
        with self.assertRaises(pymcbdsc.exceptions.FailureAgreeMeulaAndPpError):
            mcbdsc.download_latest_version_zip_file()

        self._set_dummy_file_response()
        self._set_dummy_url_response()
        # ダウンロードディレクトリが存在しない場合に FileNotFoundError が Raise されることを確認する。
        with self.assertRaises(FileNotFoundError):
            mcbdsc.download_latest_version_zip_file(agree_to_meula_and_pp=True)

        # agree_to_meula_and_pp が True の場合に FailureAgreeMeulaAndPpError が Raise されず、
        # ファイルがダウンロードされることを確認する。
        self._test_download_latest_version_zip_file(mcbdsc=mcbdsc, params={"agree_to_meula_and_pp": True})

    def test_download_latest_version_zip_file_second(self) -> None:
        mcbdsc = self.gen_downloader(agree_to_meula_and_pp=True)

        # McbdscDownloader の初期化時に agree_to_meula_and_pp を True とした場合に
        # download_latest_version_zip_file に agree_to_meula_and_pp を渡さなくても
        # ファイルがダウンロードされることを確認する。

        self._set_dummy_file_response()
        self._set_dummy_url_response()
        self._test_download_latest_version_zip_file(mcbdsc=mcbdsc, params={})

    def test_download_latest_version_zip_file_if_needed(self) -> None:
        mcbdsc = self.mcbdsc

        self._set_dummy_url_response()

        # ファイルが存在せず、 agree_to_meula_and_pp も未指定の場合に
        # FailureAgreeMeulaAndPpError が Raise されることを確認する。
        with self.assertRaises(pymcbdsc.exceptions.FailureAgreeMeulaAndPpError):
            mcbdsc.download_latest_version_zip_file_if_needed()

        self._set_dummy_file_response()
        os.makedirs(mcbdsc.download_dir(), exist_ok=True)
        mcbdsc.download_latest_version_zip_file_if_needed(agree_to_meula_and_pp=True)
        path = os.path.join(mcbdsc.download_dir(), self.mocked_response_bds_file)
        # ファイルが意図したとおりの内容で保存されているか確認する。
        with open(path, 'rb') as f:
            act = f.read()
        exp = self.mocked_response_content
        self.assertEqual(act, exp)
