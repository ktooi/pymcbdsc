import docker
import requests
import re
import os.path
from os import getcwd as os_getcwd

# To can mock the os.name like below line:
# >>> p = mock.patch('pymsbre.os_name', os_name)
from os import name as os_name


def download_dir():
    """ OS 毎のデフォルトのダウンロードディレクトリ(フォルダ)を戻す関数。

    The function returns the default download directory each by OS. """
    r = None
    if os_name == 'nt':
        r = "c:\\pymsbre\\downloads"
    elif os_name == 'posix':
        r = "/var/lib/pymsbre/downloads"
    else:
        r = "/var/lib/pymsbre/downloads"
    return r


class MsbreDownloader(object):
    """
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
                 download_dir=download_dir(),
                 url="https://www.minecraft.net/en-us/download/server/bedrock/",
                 zip_url_pat=("https:\\/\\/minecraft\\.azureedge\\.net\\/bin-linux\\/"
                              "bedrock-server-([0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+)\\.zip"),
                 agree_to_meula_and_pp=False):
        self._download_dir = download_dir
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

    def latest_version_zip_filepath(self) -> str:
        """ ローカル上に保存されている(或いは保存するべき)最新の Bedrock Server の zip ファイルパスを戻すメソッド。

        The method returns the latest zip filepath of the Bedrock Server on the localhost.

        Examples:

            >>> downloader.latest_filepath()
            '/var/lib/pymsbre/downloads/bedrock-server-1.16.201.02.zip'
        """
        download_dir = self._download_dir
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
    def download(cls, url, filepath) -> None:
        res = requests.get(url)
        res.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(res.content)

    def download_latest_version_zip_file(self, agree_to_meula_and_pp=None) -> None:
        if agree_to_meula_and_pp is None:
            agree_to_meula_and_pp = self._agree_to_meula_and_pp
        if not agree_to_meula_and_pp:
            # TODO
            raise ValueError()
        self.download(url=self.zip_url(),
                      filepath=self.latest_version_zip_filepath())

    def download_latest_version_zip_file_if_needed(self, agree_to_meula_and_pp=None) -> None:
        if not self.has_latest_version_zip_file():
            self.download_latest_version_zip_file(agree_to_meula_and_pp=agree_to_meula_and_pp)


class MsbreDockerManager(object):

    def __init__(self, docker=docker.from_env(), downloader=MsbreDownloader(), dockerfile=os.path.join(os_getcwd, "Dockerfile"), repository="bedrock"):
        self._docker = docker
        self._dockerfile = dockerfile
        self._downloader = downloader
        self._repository = repository

    def download(self, agree_to_meula_and_pp):
        downloader = self._downloader
        downloader.download_latest_version_zip_file_if_needed(agree_to_meula_and_pp=agree_to_meula_and_pp)
