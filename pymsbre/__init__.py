import docker
from docker.client import DockerClient
import requests
import re
import os.path
from os import getcwd as os_getcwd

# To can mock the os.name like below line:
# >>> os_name = "posix"
# >>> p = mock.patch('pymsbre.os_name', os_name)
from os import name as os_name


__version__ = "0.1.0"


def pymsbre_root_dir():
    """ pymsbre が利用するディレクトリ(フォルダ)の OS 毎のデフォルトパスを戻す関数。

    The function returns the default root directory of pymsbre each by OS.

    Returns:
        str: pymsbre が利用するディレクトリ(フォルダ)の OS 毎のデフォルトパス。
    """
    r = None
    if os_name == 'nt':
        r = "c:\\pymsbre"
    elif os_name == 'posix':
        r = "/var/lib/pymsbre"
    else:
        r = "/var/lib/pymsbre"
    return r


class MsbreDownloader(object):
    """ Bedrock Server の最新ファイルについてダウンロードし、管理するクラス。

    このクラスを利用するにあたっては、本モジュールのライセンスの他に Minecraft End User License Agreement
    及び Privacy Policy に同意する必要があります。

    This class is download and manage latest version of the Bedrock Server file.

    You have to agree to the Minecraft End User License Agreement and Privacy Policy to use this module.

    Examples:

        >>> from pymsbre import MsbreDownloader
        >>>
        >>> downloader = MsbreDownloader()
        >>> # You have to agree to the Minecraft End User License Agreement and Privacy Policy.
        >>> # See also:
        >>> #     * Minecraft End User License Agreement : https://account.mojang.com/terms
        >>> #     * Privacy Policy : https://privacy.microsoft.com/en-us/privacystatement
        >>> downloader.download_latest_version_zip_file_if_needed(agree_to_meula_and_pp=True)
        >>> downloader.latest_version_zip_filepath()
        '/var/lib/pymsbre/downloads/bedrock-server-1.16.201.02.zip'
    """

    def __init__(self,
                 pymsbre_root_dir: str = pymsbre_root_dir(),
                 url: str = "https://www.minecraft.net/en-us/download/server/bedrock/",
                 zip_url_pat: str = ("https:\\/\\/minecraft\\.azureedge\\.net\\/bin-linux\\/"
                                     "bedrock-server-([0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+)\\.zip"),
                 agree_to_meula_and_pp: bool = False) -> None:
        """ MsbreDownloader インスタンスの初期化メソッド。

        Args:
            pymsbre_root_dir (str, optional): pymsbre が利用するディレクトリ(フォルダ). Defaults to pymsbre_root_dir().
            url (str, optional): Bedrock Server のダウンロードリンクが掲載されているページへの URL.
                                 Defaults to "https://www.minecraft.net/en-us/download/server/bedrock/".
            zip_url_pat (str, optional): `url` に掲載されているダウンロードリンクのパターン.
                                         Defaults to ("https:\\/\\/minecraft\\.azureedge\\.net\\/bin-linux\\/"
                                                      "bedrock-server-([0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+)\\.zip").
            agree_to_meula_and_pp (bool, optional): MEULA 及び Privacy Policy に同意するか否か. Defaults to False.
        """
        self._pymsbre_root_dir = pymsbre_root_dir
        self._url = url
        self._zip_url_pat = re.compile(zip_url_pat)
        self._agree_to_meula_and_pp = agree_to_meula_and_pp

    def zip_url(self) -> str:
        """ Bedrock Server の zip ファイルをダウンロードできる URL を取得し戻すメソッド。

        The method get and return the URL of zip file of the Bedrock Server.

        Examples:

            >>> downloader.zip_url()
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

        Examples:

            >>> downloader.latest_version()
            '1.16.201.02'
        """
        if not hasattr(self, "_latest_version"):
            self.zip_url()
        return self._latest_version

    def latest_filename(self) -> str:
        """ Bedrock Server の最新 zip ファイル名を戻すメソッド。

        The method returns the latest zip filename of the Bedrock Server.

        Examples:

            >>> downloader.latest_filename()
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
            relative (bool, optional): pymsbre_root_dir からの相対パスを戻すか否か。 Defaults to False.

        Returns:
            str: Bedrock Server の zip ファイルをダウンロードするディレクトリ(フォルダ)。
        """
        downloads = "downloads"
        return downloads if relative else os.path.join(self._pymsbre_root_dir, downloads)

    def root_dir(self) -> str:
        return self._pymsbre_root_dir

    def latest_version_zip_filepath(self) -> str:
        """ ローカル上に保存されている(或いは保存するべき)最新の Bedrock Server の zip ファイルパスを戻すメソッド。

        The method returns the latest zip filepath of the Bedrock Server on the localhost.

        Examples:

            >>> downloader.latest_filepath()
            '/var/lib/pymsbre/downloads/bedrock-server-1.16.201.02.zip'
        """
        download_dir = self.download_dir()
        latest_filename = self.latest_filename()
        return os.path.join(download_dir, latest_filename)

    def has_latest_version_zip_file(self) -> bool:
        """ ローカルホスト上に既に最新の Bedrock Server の zip ファイルが保存されているか否かを戻すメソッド。

        The method returns whether or not the localhost has the latest zip file of the Bedrock Server.

        Examples:

            >>> downloader.has_latest_version_zip_file()
            False
        """
        return os.path.exists(self.latest_version_zip_filepath())

    @classmethod
    def download(cls, url: str, filepath: str) -> None:
        """ `url` で指定されたファイルを、ダウンロードして `filepath` に保存するクラスメソッド。

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

        Args:
            agree_to_meula_and_pp (bool, optional): MEULA 及び Privacy Policy に同意するか否か. Defaults to None.
        """
        if not self.has_latest_version_zip_file():
            self.download_latest_version_zip_file(agree_to_meula_and_pp=agree_to_meula_and_pp)


class FailureAgreeMeulaAndPpError(Exception):
    """ MEULA と Privacy Policy への未同意であることを示す例外。

    Minecraft Bedrock Edition のサーバをダウンロードする為には、 MEULA と Privacy Policy に同意する必要がありますが、
    同意せずにダウンロードしようとした場合にこの例外が Raise します。
    """
    pass


class MsbreDockerManager(object):

    def __init__(self,
                 docker_client: DockerClient = None,
                 downloader: MsbreDownloader = MsbreDownloader(),
                 dockerfile: str = os.path.join(os_getcwd(), "Dockerfile"),
                 repository: str = "bedrock") -> None:
        """[summary]

        Args:
            docker_client (DockerClient, optional): [description]. Defaults to None.
            downloader (MsbreDownloader, optional): [description]. Defaults to MsbreDownloader().
            dockerfile (str, optional): [description]. Defaults to os.path.join(os_getcwd(), "Dockerfile").
            repository (str, optional): [description]. Defaults to "bedrock".
        """
        self._docker_client = docker.from_env() if docker_client is None else docker_client
        self._dockerfile = dockerfile
        self._downloader = downloader
        self._repository = repository

    def download(self, agree_to_meula_and_pp: bool) -> None:
        """ Bedrock Server の Zip ファイルをダウンロードするメソッド。

        Args:
            agree_to_meula_and_pp (bool): MEULA 及び Privacy Policy に同意するか否か.
        """
        downloader = self._downloader
        downloader.download_latest_version_zip_file_if_needed(agree_to_meula_and_pp=agree_to_meula_and_pp)
