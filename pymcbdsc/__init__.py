import docker
from docker.client import DockerClient
import requests
import re
import os.path
# To can mock the os.name like below line:
# >>> os_name = "posix"
# >>> p = mock.patch('pymcbdsc.os_name', os_name)
from os import name as os_name


__version__ = "0.1.0"


def pymcbdsc_root_dir():
    """ pymcbdsc が利用するディレクトリ(フォルダ)の OS 毎のデフォルトパスを戻す関数。

    The function returns the default root directory of pymcbdsc each by OS.

    Returns:
        str: pymcbdsc が利用するディレクトリ(フォルダ)の OS 毎のデフォルトパス。

    Examples:

        >>> import pymcbdsc
        >>>
        >>> pymcbdsc.pymcbdsc_root_dir()
        '/var/lib/pymcbdsc'
    """
    r = None
    if os_name == 'nt':
        r = "c:\\pymcbdsc"
    elif os_name == 'posix':
        r = "/var/lib/pymcbdsc"
    else:
        r = "/var/lib/pymcbdsc"
    return r


class McbdscDownloader(object):
    """ Bedrock Server の最新ファイルについてダウンロードし、管理するクラス。

    このクラスを利用するにあたっては、本モジュールのライセンスの他に Minecraft End User License Agreement
    及び Privacy Policy に同意する必要があります。

    This class is download and manage latest version of the Bedrock Server file.

    You have to agree to the Minecraft End User License Agreement and Privacy Policy to use this module.

    Examples:

        >>> from pymcbdsc import McbdscDownloader
        >>>
        >>> downloader = McbdscDownloader()
        >>> # You have to agree to the Minecraft End User License Agreement and Privacy Policy.
        >>> # See also:
        >>> #     * Minecraft End User License Agreement : https://account.mojang.com/terms
        >>> #     * Privacy Policy : https://privacy.microsoft.com/en-us/privacystatement
        >>> downloader.download_latest_version_zip_file_if_needed(agree_to_meula_and_pp=True)
        >>> downloader.latest_version_zip_filepath()
        '/var/lib/pymcbdsc/downloads/bedrock-server-1.16.201.02.zip'
    """

    def __init__(self,
                 pymcbdsc_root_dir: str = pymcbdsc_root_dir(),
                 url: str = "https://www.minecraft.net/en-us/download/server/bedrock/",
                 zip_url_pat: str = ("https:\\/\\/minecraft\\.azureedge\\.net\\/bin-linux\\/"
                                     "bedrock-server-([0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+)\\.zip"),
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

        Returns:
            str: Bedrock Server の最新バージョン番号.

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

        Returns:
            str: Bedrock Server の最新 zip ファイル名.

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
            relative (bool, optional): pymcbdsc_root_dir からの相対パスを戻すか否か。 Defaults to False.

        Returns:
            str: Bedrock Server の zip ファイルをダウンロードするディレクトリ(フォルダ)。

        Examples:

            >>> downloader.download_dir()
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

            >>> downloader.root_dir()
            '/var/lib/pymcbdsc'
        """
        return self._pymcbdsc_root_dir

    def latest_version_zip_filepath(self) -> str:
        """ ローカル上に保存されている(或いは保存するべき)最新の Bedrock Server の zip ファイルパスを戻すメソッド。

        The method returns the latest zip filepath of the Bedrock Server on the localhost.

        Returns:
            str: ローカル上に保存されている(或いは保存するべき)最新の Bedrock Server の zip ファイルパス.

        Examples:

            >>> downloader.latest_filepath()
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

            >>> downloader.has_latest_version_zip_file()
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


class FailureAgreeMeulaAndPpError(Exception):
    """ MEULA と Privacy Policy への未同意であることを示す例外。

    Minecraft Bedrock Edition のサーバをダウンロードする為には、 MEULA と Privacy Policy に同意する必要がありますが、
    同意せずにダウンロードしようとした場合にこの例外が Raise します。

    TODO:
        例外のメッセージに、 MEULA 及び Privacy Policy への同意が必要であるということがわかりやすいメッセージを追加する。
    """
    pass


class McbdscDockerManager(object):
    """ Bedrock Server のコンテナとコンテナイメージの作成・管理を行うクラス。
    """

    def __init__(self,
                 docker_client: DockerClient = None,
                 downloader: McbdscDownloader = McbdscDownloader(),
                 dockerfile: str = "Dockerfile",
                 repository: str = "bedrock") -> None:
        """[summary]

        Args:
            docker_client (DockerClient, optional): Docker ホストに接続する DockerClient インスタンス.
                                                    None の場合は `docker.from_env()` の戻り値を利用する. Defaults to None.
            downloader (McbdscDownloader, optional): [description]. Defaults to McbdscDownloader().
            dockerfile (str, optional): [description]. Defaults to "Dockerfile".
            repository (str, optional): [description]. Defaults to "bedrock".
        """
        # 引数のデフォルト値を下記のようにすると、 unittest で import した際に docker.from_env() がコールされてしまい
        # import することも patch することもできない。
        # docker_client: DockerClient = docker.from_env()
        # このため、デフォルト値を None としておき、 None の場合に docker.from_env() をコールする。
        self._docker_client = docker.from_env() if docker_client is None else docker_client
        self._dockerfile = os.path.join(downloader.root_dir(), dockerfile)
        self._downloader = downloader
        self._repository = repository

    def download(self, agree_to_meula_and_pp: bool) -> None:
        """ Bedrock Server の Zip ファイルをダウンロードするメソッド。

        This method downloads the Bedrock Server zip file.

        Args:
            agree_to_meula_and_pp (bool): MEULA 及び Privacy Policy に同意するか否か.
        """
        downloader = self._downloader
        downloader.download_latest_version_zip_file_if_needed(agree_to_meula_and_pp=agree_to_meula_and_pp)

    def build_image(self, version: str = None, extra_buildargs: dict = None, **extra_build_opt):
        """ Minecraft Bedrock Server の Docker Image を Build するメソッド。

        This method build the Docker Image of the Minecraft Bedrock Server.

        Args:
            version (str, optional): Build する Docker Image の Minecraft のバージョン. None の場合は、最新バージョンとなる. Defaults to None.
            extra_buildargs (dict, optional): Docker Image を Build する際の、追加の引数. Defaults to None.

        Returns:
            [type]: Build した Docker Image.
        """
        dl = self._downloader
        dc_images = self._docker_client.images
        path = dl.root_dir()
        dockerfile = self._dockerfile
        if version is None:
            version = dl.latest_version()
        buildargs = {"BEDROCK_SERVER_VER": version,
                     "BEDROCK_SERVER_DIR": dl.download_dir(relative=True)}
        if extra_buildargs is not None:
            buildargs.update(extra_buildargs)
        tag = "{repository}:{version}".format(repository=self._repository, version=version)
        return dc_images.build(path=path, dockerfile=dockerfile, buildargs=buildargs, tag=tag, **extra_build_opt)

    def get_image(self, version: str = None):
        """ Minecraft Bedrock Server の、指定されたバージョンの Docker Image を戻すメソッド。

        This method returns the Docker Image of the Minecraft Bedrock Server that you specified version.

        Args:
            version (str, optional): 取得する Docker Image の Minecraft のバージョン. None の場合は、最新バージョンとなる. Defaults to None.

        Returns:
            [type]: 指定されたバージョンの Docker Image.
        """
        dl = self._downloader
        dc_images = self._docker_client.images
        if version is None:
            version = dl.latest_version()
        tag = "{repository}:{version}".format(repository=self._repository, version=version)
        return dc_images.get(name=tag)


class McbdscDockerContainer(object):

    def __init__(self,
                 mcbdsc_manager: McbdscDockerManager) -> None:
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def run(self):
        pass

    def remove(self):
        pass

    def status(self):
        pass

    def backup(self):
        pass

    def restore(self):
        pass