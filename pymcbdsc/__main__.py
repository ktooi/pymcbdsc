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
    subparsers = parser.add_subparsers(dest="subcommand")
    subparsers.required = True

    # 共通となる引数を定義。
    common_parser = ArgumentParser(add_help=False)
    common_parser.add_argument('-r', '--root-dir', default=pymcbdsc_root_dir(),
                               help="This directory is used for container management and storage of download files.")
    common_parser.add_argument('--i-agree-to-meula-and-pp', action='store_true',
                               help=("You have to agree to the MEULA and Privacy Policy at download the Bedrock Server. "
                                     "If you specify this argument, you agree to them."))

    # サブコマンドと、それぞれ特有の引数を定義。
    subcmd_install = subparsers.add_parser("install", parents=[common_parser], help="TODO")
    subcmd_install.set_defaults(func=install)

    subcmd_download = subparsers.add_parser("download", parents=[common_parser],
                                            help=("Download and storage latest version "
                                                  "of the Minecraft Bedrock Dedicated Server."))
    subcmd_download.set_defaults(func=download)

    subcmd_build = subparsers.add_parser("build", parents=[common_parser],
                                         help="Build the Docker Image of the Minecraft Bedrock Dedicated Server.")
    subcmd_build.add_argument('-V', '--bedrock-version')
    subcmd_build.set_defaults(func=build)

    # 以下、ヘルプコマンドの定義。

    # "help" 以外の subcommand のリストを保持する。
    # dict.keys() メソッドは list や tuple ではなく KeyView オブジェクトを戻す。
    # これは、対象となる dict の要素が変更されたときに、 KeyView オブジェクトの内容も変化してしまうので、
    # subparsers.choices の変更が反映されないように list 化したものを subcmd_list に代入しておく。
    subcmd_list = list(subparsers.choices.keys())

    subcmd_help = subparsers.add_parser("help", help="Help is shown.")
    # add_argument() の第一引数を "subcommand" としてはならない。
    # `mcbdsc help build` 等と実行した際に、
    # >>> args = parser.parse_args()
    # >>> args.subcommand
    # で "help" となってほしいが、この第一引数を "subcommand" にしてしまうとこの例では "build" となってしまう。
    # このため、ここでは第一引数を "subcmd" とし、 metavar="subcommand" とすることで
    # ヘルプ表示上は "subcommand" としたまま、 `args.subcommand` が "help" となるよう対応する。
    subcmd_help.add_argument("subcmd", metavar="subcommand", choices=subcmd_list, help="Command name which help is shown.")
    subcmd_help.set_defaults(func=lambda args: print(parser.parse_args([args.subcmd, '--help'])))

    return parser.parse_args()


def main():
    args = parse_args()
    if args.debug:
        logger.info("Set log level to DEBUG.")
        logger.setLevel(DEBUG)
    if args.subcommand in ["install", "download", "build"]:
        dl = McbdscDownloader(pymcbdsc_root_dir=args.root_dir, agree_to_meula_and_pp=args.i_agree_to_meula_and_pp)
        args.func(args, dl)
    else:
        args.func(args)


if __name__ == "__main__":
    main()
