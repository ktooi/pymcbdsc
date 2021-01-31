from typing import List, Optional
import os.path
from os import listdir
import re
from logging import getLogger
import docker
from docker.models.containers import Container
from docker.client import DockerClient
from .constants import bds_version_pat, bds_zip_file_pat
from .utils import pymcbdsc_root_dir


logger = getLogger(__name__)


class McbdscDockerManager(object):
    """ Bedrock Server のコンテナとコンテナイメージの作成・管理を行うクラス。

    このクラスが持つ責任範囲は、ローカルに保存されている BDS ファイルを用いて Docker Image を作成し、
    McbdsDockerContainer インスタンスを管理・制御することです。
    """

    bds_version_pat_compile = re.compile(bds_version_pat)

    def __init__(self,
                 containers_param: List[dict] = None,
                 pymcbdsc_root_dir: str = pymcbdsc_root_dir(),
                 docker_client: DockerClient = None,
                 dockerfile: str = "Dockerfile",
                 bds_zip_dir: str = "downloads",
                 repository: str = "bedrock") -> None:
        """[summary]

        Args:
            containers_param (List[dict], optional): 管理する全コンテナのパラメータ.
                                                     None の場合は、空のリストになる. Defaults to None.
            pymcbdsc_root_dir (str, optional): pymcbdsc が利用するディレクトリ(フォルダ).
                                               Defaults to pymcbdsc_root_dir().
            docker_client (DockerClient, optional): Docker ホストに接続する DockerClient インスタンス.
                                                    None の場合は `docker.from_env()` の戻り値を利用する. Defaults to None.
            dockerfile (str, optional): Dockerfile のファイル名. pymcbdsc_root_dir の配下にあるこのファイルを読み込む.
                                        Defaults to "Dockerfile".
            bds_zip_dir (str, optional): BDS Zip ファイルが保存されているディレクトリの名前.
                                         pymcbdsc_root_dir の配下にあるこの名前のディレクトリ内の BDS Zip ファイルを利用する。
                                         Defaults to "downloads".
            repository (str, optional): [description]. Defaults to "bedrock".

        Examples:

        >>> import docker
        >>> from pymcbdsc import McbdscDownloader, McbdscDockerManager
        >>>
        >>> downloader = McbdscDownloader()
        >>> docker_client = docker.from_env()
        >>> manager = McbdscDockerManager(docker_client=docker_client, bds_zip_dir=downloader.download_dir(relative=True))
        """
        self._containers_param = containers_param if containers_param is not None else []
        self._root_dir = pymcbdsc_root_dir
        # 引数のデフォルト値を下記のようにすると、 unittest で import した際に docker.from_env() がコールされてしまい
        # import することも patch することもできない。
        # docker_client: DockerClient = docker.from_env()
        # このため、デフォルト値を None としておき、 None の場合に docker.from_env() をコールする。
        self._docker_client = docker.from_env() if docker_client is None else docker_client
        self._dockerfile = os.path.join(self._root_dir, dockerfile)
        self._bds_zip_dir = bds_zip_dir
        self._repository = repository

    def factory_containers(self) -> list:
        """ McbdscDockerContainer インスタンスを初期化しリストで戻すメソッド。

        Returns:
            list: McbdscDockerContainer インスタンスのリスト。
        """
        if not hasattr(self, "_containers"):
            dc_containers = self._docker_client.containers
            exist_containers = dc_containers.list(all=True)
            # name から container インスタンスを取得できる dict を作成。
            name2container = {c.name: c for c in exist_containers}
            containers_param = self._containers_param
            mcbdsc_containers = []
            for container_param in containers_param:
                name = container_param["name"]
                if name in name2container:
                    # コンテナが作成済みあればそのインスタンスを指定。
                    container = name2container[name]
                else:
                    # コンテナが未作成であれば作成。
                    container = dc_containers.create(**container_param)
                # start 時に処理が停止してしまうため、 detach オプションを強制的に有効。
                # container_param["detach"] = True
                container_param["stdin_open"] = True
                container_param["tty"] = True
                mcbdsc_container = McbdscDockerContainer(name=name, container=container)
                mcbdsc_containers.append(mcbdsc_container)
            self._containers = mcbdsc_containers
        return self._containers

    def build_image(self, version: str = None, extra_buildargs: dict = None, **extra_build_opt):
        """ Minecraft Bedrock Server の Docker Image を Build するメソッド。

        This method build the Docker Image of the Minecraft Bedrock Server.

        Args:
            version (str, optional): Build する Docker Image の Minecraft のバージョン. None の場合は、最新バージョンとなる. Defaults to None.
            extra_buildargs (dict, optional): Docker Image を Build する際の、追加の引数. Defaults to None.

        Returns:
            [type]: Build した Docker Image.
        """
        dc_images = self._docker_client.images
        root_dir = self._root_dir
        dockerfile = self._dockerfile
        if version is None:
            version = self.get_bds_latest_version_from_local_file()
        buildargs = {"BEDROCK_SERVER_VER": version,
                     "BEDROCK_SERVER_DIR": self._bds_zip_dir}
        if extra_buildargs is not None:
            buildargs.update(extra_buildargs)
        tag = "{repository}:{version}".format(repository=self._repository, version=version)
        logger.info("Build image: {tag}".format(tag=tag))
        return dc_images.build(path=root_dir, dockerfile=dockerfile, buildargs=buildargs, tag=tag, **extra_build_opt)

    def get_image(self, version: str = None):
        """ Minecraft Bedrock Server の、指定されたバージョンの Docker Image を戻すメソッド。

        This method returns the Docker Image of the Minecraft Bedrock Server that you specified version.

        Args:
            version (str, optional): 取得する Docker Image の Minecraft のバージョン. None の場合は、最新バージョンとなる. Defaults to None.

        Returns:
            [type]: 指定されたバージョンの Docker Image.
        """
        dc_images = self._docker_client.images
        if version is None:
            version = self.get_bds_latest_version_from_local_file()
        tag = "{repository}:{version}".format(repository=self._repository, version=version)
        return dc_images.get(name=tag)

    def list_images(self):
        dc_images = self._docker_client.images
        repository = self._repository
        return dc_images.list(repository)

    def set_tag(self, version, tag) -> bool:
        logger.info("Set tag \"{tag}\" to version: {version}".format(tag=tag, version=version))
        image = self.get_image(version=version)
        return image.tag(repository=self._repository, tag=tag)

    def set_latest_tag_to_latest_image(self) -> bool:
        latest_version = self.get_bds_versions_from_container_image(sort=True, reverse=False)[-1]
        return self.set_tag(version=latest_version, tag="latest")

    def set_minor_tags(self):
        """ 各マイナーバージョン毎のタグを作成し、それぞれのマイナーバージョンの最新バージョンのコンテナイメージに付与するメソッド。

        このメソッドは、 BDS のバージョンを取得する為に Docker Image の一覧を使用するので、
        あらかじめ必要な Docker Image が Build されている必要があります。

        BDS のバージョニングは次のようになっています。

        major.minor.patch.revision

        このうち、 minor 部までのタグ(e.g., 1.16)を各マイナーバージョンごとに作成し、
        それぞれのマイナーバージョンの最新バージョンの Docker Image にそのタグを付与します。

        これにより、コンテナ作成時にマイナーバージョンまでを指定してコンテナを起動することが可能となります。
        例えば 1.16 のマイナーバージョンの Docker Image を使用するように指定されたコンテナは、
        1.16 の最新バージョンで動作し続けますが、バージョン 1.17 以上に更新されることはありません。
        """
        bds_versions = self.get_bds_versions_from_container_image(sort=True, reverse=False)
        # マイナーバージョンと、その最新パッチ(またはリビジョン)の組み合わせを作る。
        d = {}
        for bds_version in bds_versions:
            # version が "1.2.3.4" なら major_minor には "1.2" が入る。
            major_minor = ".".join(bds_version.split(".")[0:2])
            # versions は昇順なので、特に条件式を入れなくても
            # マイナーバージョンとその最新パッチ(またはリビジョン)の組み合わせになる。
            d[major_minor] = bds_version
        for (major_minor, bds_version) in d.items():
            self.set_tag(version=bds_version, tag=major_minor)

    def get_bds_versions_from_container_image(self, sort=True, reverse=False) -> List[str]:
        images = self.list_images()
        versions = []
        for image in images:
            for tag in image.tags:
                version = tag.split(":")[1]
                m = self.bds_version_pat_compile.fullmatch(version)
                if not m:
                    continue
                versions.append(version)
        if sort:
            self.sort_bds_versions(versions, reverse)
        return versions

    def get_bds_versions_from_local_file(self, sort=True, reverse=False) -> List[str]:
        """ ローカルに保存されている BDS Zip ファイルからバージョンの一覧を戻すメソッド。

        sort パラメータを指定しなかった場合は、このメソッドが戻すリストの順番については保証されず、同じ順序であるとも限らない。

        Args:
            sort (bool, optional): バージョン番号をソートします. reverse が False の場合は昇順でソートします. Defaults to True.
            reverse (bool, optional): sort が True の場合に、降順でソートします. Defaults to False.

        Returns:
            List[str]: ローカルに保存されている BDS Zip ファイルから取得したバージョンのリスト.
        """
        root_dir = self._root_dir
        bds_zip_dir = os.path.join(root_dir, self._bds_zip_dir)
        dir_contents = listdir(bds_zip_dir)
        files = [c for c in dir_contents if os.path.isfile(os.path.join(bds_zip_dir, c))]
        if not files:
            return []
        bds_zip_file_re = re.compile(bds_zip_file_pat)
        versions = []
        for file in files:
            m = bds_zip_file_re.fullmatch(file)
            if m:
                versions.append(m.group(1))
        if sort:
            self.sort_bds_versions(versions, reverse)
        return versions

    @classmethod
    def sort_bds_versions(cls, versions: List[str], reverse: bool = False) -> None:
        """

        Args:
            versions (list): [description]

        Examples:

            >>> from pymcbdsc import McbdscDockerManager
            >>>
            >>> versions = [
            ...     '1.2.3.4',
            ...     '1.1.1.1',
            ...     '4.3.2.1',
            ...     '1.10.3.4',
            ...     '1.10.3.05'
            ... ]
            >>> McbdscDockerManager.sort_bds_versions(versions=versions)
            >>> versions
            ['1.1.1.1', '1.2.3.4', '1.10.3.4', '1.10.3.05', '4.3.2.1']

        See Also:
            https://stackoverflow.com/questions/2574080/sorting-a-list-of-dot-separated-numbers-like-software-versions/2574090
        """
        versions.sort(key=lambda s: list(map(int, s.split('.'))), reverse=reverse)

    def get_bds_latest_version_from_local_file(self) -> Optional[str]:
        """ ローカルに保存されている BDS Zip ファイルの中で最も新しいバージョンを戻すメソッド。

        Returns:
            str: ローカルに保存されている BDS Zip ファイルの中で最も新しいバージョン.
            None: ローカルに保存されている BDS Zip ファイルが存在しない場合は None.
        """
        versions = self.get_bds_versions_from_local_file()
        if versions:
            return self.get_bds_versions_from_local_file()[-1]
        else:
            return None

    def backup(self):
        client = self._docker_client
        containers = self.factory_containers()
        params = {'stdin': 1, 'stream': 1}
        for container in containers:
            s = client.api.attach_socket(container._container.name, params=params)
            logger.info("send command: save hold")
            s.send("save hold\n".encode('utf-8'))
            s.close()


class McbdscDockerContainer(object):
    """[summary]
    """

    def __init__(self,
                 name: str,
                 container: Container) -> None:
        self._name = name
        self._container = container

    def start(self, **kwargs):
        container = self._container
        container.start(**kwargs)

    def stop(self, **kwargs):
        container = self._container
        container.stop(**kwargs)

    def restart(self, **kwargs):
        container = self._container
        container.restart(**kwargs)

    def remove(self):
        pass

    def stats(self, **kwargs):
        container = self._container
        container.stats(**kwargs)

    def backup(self, online=False):
        """container = client.api.create_container(
    image="debian",
    command="cat",
    stdin_open=True)
client.api.start(container)
s = client.api.attach_socket(container, params={'stdin': 1, 'stream': 1})
s._sock.send("Hello, world! This is on stdin!")
s.close()"""
        container = self._container
        s = container.attach_socket(stdin=True, stream=True)
        s._sock.send("save hold")
        s.close()

    def restore(self):
        pass
