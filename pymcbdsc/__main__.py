""" このファイルは pymcbdsc モジュールをコマンドラインから使用できるようにするファイルです。

詳細な利用方法はヘルプを参照してください。

`python -m pymcbdsc -h`, `python -m pymcbdsc <subcommand> -h` 等で確認することができます。
また、 pip でインストールした場合には `mcdbsc -h`, `mcdbsc <subcommand> -h` 等で確認することもできます。
"""

import os
from logging import basicConfig, getLogger, DEBUG, INFO
from argparse import ArgumentParser, Namespace
from pymcbdsc import McbdscDownloader, McbdscDockerManager, pymcbdsc_root_dir


# これはメインのファイルにのみ書く
basicConfig(level=INFO)

# これはすべてのファイルに書く
logger = getLogger(__name__)


def mkdir_if_needed(dir: str) -> None:
    """ 必要があればディレクトリ(フォルダ)を作成する関数。

    指定されたディレクトリ(フォルダ)が既に存在すれば、作成しない。

    Args:
        dir (str): 作成するディレクトリ(フォルダ)のパス。
    """
    if not os.path.exists(dir):
        logger.info("Create a directory: {dir}".format(dir=dir))
        os.makedirs(dir)


def install(args: Namespace, downloader: McbdscDownloader) -> None:
    root_dir = args.root_dir
    dl_dir = downloader.download_dir()
    mkdir_if_needed(root_dir)
    mkdir_if_needed(dl_dir)


def uninstall(args: Namespace, downloader: McbdscDownloader) -> None:
    pass


def download(args: Namespace, downloader: McbdscDownloader) -> None:
    downloader.download_latest_version_zip_file_if_needed()


def build(args: Namespace, downloader: McbdscDownloader) -> None:
    manager = McbdscDockerManager(downloader=downloader)
    b_version = args.bedrock_version if args.bedrock_version else downloader.latest_version()
    manager.build_image(version=b_version)


def parse_args() -> Namespace:
    """ 引数の定義と、解析を行う関数。

    Returns:
        Namespace: 解析済み引数。
    """
    parser = ArgumentParser(description=("This project provides very easier setup and management "
                                         "for Minecraft Bedrock Dedicated Server."))
    parser.add_argument('-d', '--debug', action='store_true', help="Show verbose messages.")
    subparser = parser.add_subparsers()

    # 共通となる引数を定義。
    common_parser = ArgumentParser(add_help=False)
    common_parser.add_argument('-r', '--root-dir', default=pymcbdsc_root_dir(),
                               help="This directory is used for container management and storage of download files.")
    common_parser.add_argument('--i-agree-to-meula-and-pp', action='store_true',
                               help=("You have to agree to the MEULA and Privacy Policy at download the Bedrock Server. "
                                     "If you specify this argument, you agree to them."))

    subcmd_install = subparser.add_parser("install", parents=[common_parser])
    subcmd_install.set_defaults(func=install)

    subcmd_download = subparser.add_parser("download", parents=[common_parser])
    subcmd_download.set_defaults(func=download)

    subcmd_build = subparser.add_parser("build", parents=[common_parser])
    subcmd_build.add_argument('-V', '--bedrock-version')
    subcmd_build.set_defaults(func=build)

    return parser.parse_args()


def main():
    args = parse_args()
    if args.debug:
        logger.info("Set log level to DEBUG.")
        logger.setLevel(DEBUG)
    dl = McbdscDownloader(pymcbdsc_root_dir=args.root_dir, agree_to_meula_and_pp=args.i_agree_to_meula_and_pp)
    args.func(args, dl)


if __name__ == "__main__":
    main()
