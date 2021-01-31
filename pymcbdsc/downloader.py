import os
import re
import requests
from .constants import bds_zip_file_pat
from .utils import pymcbdsc_root_dir
from .exceptions import FailureAgreeMeulaAndPpError


class McbdscDownloader(object):
    """ Bedrock Server の最新ファイルについてダウンロードし、管理するクラス。

    このクラスを利用するにあたっては、本モジュールのライセンスの他に Minecraft End User License Agreement
    及び Privacy Policy に同意する必要があります。

    このクラスが持つ責任範囲は、 BDS の最新版のバージョン番号を取得することと、
    そのファイルをダウンロードしローカルに保存することです。

    This class is download and manage latest version of the Bedrock Server file.

    You have to agree to the Minecraft End User License Agreement and Privacy Policy to use this module.

    Examples:

        >>> import os
        >>> from pymcbdsc import McbdscDownloader
        >>>
        >>> downloader = McbdscDownloader()
        >>> # ダウンロード先ディレクトリを作成。
        >>> os.makedirs(downloader.download_dir(), exist_ok=True)  # doctest: +SKIP
        >>>
        >>> # You have to agree to the Minecraft End User License Agreement and Privacy Policy.
        >>> # See also:
        >>> #     * Minecraft End User License Agreement : https://account.mojang.com/terms
        >>> #     * Privacy Policy : https://privacy.microsoft.com/en-us/privacystatement
        >>> downloader.download_latest_version_zip_file_if_needed(agree_to_meula_and_pp=True) # doctest: +SKIP
        >>> downloader.latest_version_zip_filepath()  # doctest: +SKIP
        '/var/lib/pymcbdsc/downloads/bedrock-server-1.16.201.02.zip'
    """

    def __init__(self,
                 pymcbdsc_root_dir: str = pymcbdsc_root_dir(),
                 url: str = "https://www.minecraft.net/en-us/download/server/bedrock/",
                 zip_url_pat: str = "https:\\/\\/minecraft\\.azureedge\\.net\\/bin-linux\\/" + bds_zip_file_pat,
                 agree_to_meula_and_pp: bool = False) -> None:
        """ McbdscDownloader インスタンスの初期化メソッド。

        Args:
            pymcbdsc_root_dir (str, optional): pymcbdsc が利用するディレクトリ(フォルダ). Defaults to pymcbdsc_root_dir().
            url (str, optional): Bedrock Server のダウンロードリンクが掲載されているページへの URL.
                                 Defaults to "https://www.minecraft.net/en-us/download/server/bedrock/".
            zip_url_pat (str, optional): `url` に掲載されているダウンロードリンクのパターン.
                                         Defaults to ("https:\\/\\/minecraft\\.azureedge\\.net\\/bin-linux\\/"
                                                      "bedrock-server-([0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+)\\.zip").
            agree_to_meula_and_pp (bool, optional): MEULA 及び Privacy Policy に同意するか否か. Defaults to False.
        """
        self._pymcbdsc_root_dir = pymcbdsc_root_dir
        self._url = url
        self._zip_url_pat = re.compile(zip_url_pat)
        self._agree_to_meula_and_pp = agree_to_meula_and_pp

    def zip_url(self) -> str:
        """ Bedrock Server の zip ファイルをダウンロードできる URL を取得し戻すメソッド。

        The method get and return the URL of zip file of the Bedrock Server.

        Returns:
            str: Bedrock Server の zip ファイルをダウンロードできる URL.

        Examples:

            >>> from pymcbdsc import McbdscDownloader
            >>>
            >>> downloader = McbdscDownloader()
            >>> downloader.zip_url()  # doctest: +SKIP
            'https://minecraft.azureedge.net/bin-linux/bedrock-server-1.16.201.02.zip'
        """
        if not hasattr(self, "_zip_url"):
            url = self._url
            zip_url_pat = self._zip_url_pat

            res = requests.get(url)
            res.raise_for_status()

            m = zip_url_pat.search(res.text)
            zip_url = m.group(0)
            latest_version = m.group(1)
            self._zip_url = zip_url
            self._latest_version = latest_version
        return self._zip_url

    def latest_version(self) -> str:
        """ Bedrock Server の最新バージョン番号を戻すメソッド。

        The method returns the latest version number of the Bedrock Server.

        Returns:
            str: Bedrock Server の最新バージョン番号.

        Examples:

            >>> from pymcbdsc import McbdscDownloader
            >>>
            >>> downloader = McbdscDownloader()
            >>> downloader.latest_version()  # doctest: +SKIP
            '1.16.201.02'
        """
        if not hasattr(self, "_latest_version"):
            self.zip_url()
        return self._latest_version

    def latest_filename(self) -> str:
        """ Bedrock Server の最新 zip ファイル名を戻すメソッド。

        The method returns the latest zip filename of the Bedrock Server.

        Returns:
            str: Bedrock Server の最新 zip ファイル名.

        Examples:

            >>> from pymcbdsc import McbdscDownloader
            >>>
            >>> downloader = McbdscDownloader()
            >>> downloader.latest_filename()  # doctest: +SKIP
            'bedrock-server-1.16.201.02.zip'
        """
        if not hasattr(self, "_latest_filename"):
            zip_url = self.zip_url()
            self._latest_filename = os.path.basename(zip_url)
        return self._latest_filename

    def download_dir(self, relative=False) -> str:
        """ Bedrock Server の zip ファイルをダウンロードするディレクトリ(フォルダ)を戻すメソッド。

        The method returns the download directory of the Bedrock Server file.

        Args:
            relative (bool, optional): pymcbdsc_root_dir からの相対パスを戻すか否か。 Defaults to False.

        Returns:
            str: Bedrock Server の zip ファイルをダウンロードするディレクトリ(フォルダ)。

        Examples:

            >>> from pymcbdsc import McbdscDownloader
            >>>
            >>> downloader = McbdscDownloader()
            >>> downloader.download_dir()  # doctest: +SKIP
            '/var/lib/pymcbdsc/downloads'
            >>>
            >>> downloader.download_dir(relative=True)
            'downloads'
        """
        downloads = "downloads"
        return downloads if relative else os.path.join(self._pymcbdsc_root_dir, downloads)

    def root_dir(self) -> str:
        """ Pymcbdsc が利用するディレクトリ(フォルダ)のパスを戻すメソッド。

        Dockerfile や env-file, ダウンロードした Bedrock Server の Zip ファイルなどはこの配下に配置される。

        This method returns the directory path used by the pymcbdsc.

        The directory will contains Dockerfile, env-files and downloaded the Bedrock Server Zip file.

        Returns:
            str: Pymcbdsc が利用するディレクトリ(フォルダ)のパス.

        Examples:

            >>> from pymcbdsc import McbdscDownloader
            >>>
            >>> downloader = McbdscDownloader()
            >>> downloader.root_dir()  # doctest: +SKIP
            '/var/lib/pymcbdsc'
        """
        return self._pymcbdsc_root_dir

    def latest_version_zip_filepath(self) -> str:
        """ ローカル上に保存されている(或いは保存するべき)最新の Bedrock Server の zip ファイルパスを戻すメソッド。

        The method returns the latest zip filepath of the Bedrock Server on the localhost.

        Returns:
            str: ローカル上に保存されている(或いは保存するべき)最新の Bedrock Server の zip ファイルパス.

        Examples:

            >>> from pymcbdsc import McbdscDownloader
            >>>
            >>> downloader = McbdscDownloader()
            >>> downloader.latest_version_zip_filepath()  # doctest: +SKIP
            '/var/lib/pymcbdsc/downloads/bedrock-server-1.16.201.02.zip'
        """
        download_dir = self.download_dir()
        latest_filename = self.latest_filename()
        return os.path.join(download_dir, latest_filename)

    def has_latest_version_zip_file(self) -> bool:
        """ ローカルホスト上に既に最新の Bedrock Server の zip ファイルが保存されているか否かを戻すメソッド。

        The method returns whether or not the localhost has the latest zip file of the Bedrock Server.

        Returns:
            bool: ローカルホスト上に既に最新の Bedrock Server の zip ファイルが保存されているか否か.

        Examples:

            >>> from pymcbdsc import McbdscDownloader
            >>>
            >>> downloader = McbdscDownloader()
            >>> downloader.has_latest_version_zip_file()  # doctest: +SKIP
            False
        """
        return os.path.exists(self.latest_version_zip_filepath())

    @classmethod
    def download(cls, url: str, filepath: str) -> None:
        """ `url` で指定されたファイルを、ダウンロードして `filepath` に保存するクラスメソッド。

        This classmethod download and save file from the `url` argument.

        Args:
            url (str): ダウンロードするファイルの URL.
            filepath (str): ダウンロードしたファイルを保存するファイルパス.
        """
        res = requests.get(url)
        res.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(res.content)

    def download_latest_version_zip_file(self, agree_to_meula_and_pp: bool = None) -> None:
        """ Bedrock Server の最新版の Zip ファイルをダウンロードするメソッド。

        This method download the latest version of the Bedrock Server Zip file.

        Args:
            agree_to_meula_and_pp (bool, optional): MEULA 及び Privacy Policy に同意するか否か. Defaults to None.

        Raises:
            FailureAgreeMeulaAndPpError: MEULA と Privacy Policy に同意していない場合に raise.
        """
        if agree_to_meula_and_pp is None:
            agree_to_meula_and_pp = self._agree_to_meula_and_pp
        if not agree_to_meula_and_pp:
            raise FailureAgreeMeulaAndPpError()
        self.download(url=self.zip_url(),
                      filepath=self.latest_version_zip_filepath())

    def download_latest_version_zip_file_if_needed(self, agree_to_meula_and_pp: bool = None) -> None:
        """ Bedrock Server の最新版の Zip ファイルがローカルになかった場合にのみ、ダウンロードするメソッド。

        This method will download the Bedrock Server Zip file if the downloads directory does not already contain it.

        Args:
            agree_to_meula_and_pp (bool, optional): MEULA 及び Privacy Policy に同意するか否か. Defaults to None.
        """
        if not self.has_latest_version_zip_file():
            self.download_latest_version_zip_file(agree_to_meula_and_pp=agree_to_meula_and_pp)
