import os
from logging import basicConfig, getLogger, DEBUG, INFO
from argparse import ArgumentParser, Namespace
from pymsbre import MsbreDownloader, pymsbre_root_dir


# これはメインのファイルにのみ書く
basicConfig(level=INFO)

# これはすべてのファイルに書く
logger = getLogger(__name__)


def mkdir_if_needed(dir):
    if not os.path.exists(dir):
        logger.info("Create a directory: {dir}".format(dir=dir))
        os.makedirs(dir)


def install(args: Namespace, downloader: MsbreDownloader):
    root_dir = args.root_dir
    dl_dir = downloader.download_dir()
    mkdir_if_needed(root_dir)
    mkdir_if_needed(dl_dir)


def download(args: Namespace, downloader: MsbreDownloader):
    downloader.download_latest_version_zip_file_if_needed()


def parse_args():
    parser = ArgumentParser(description=("This project provides very easier setup and management "
                                         "for Minecraft server (Bedrock Edition)."))
    parser.add_argument('-d', '--debug', action='store_true', help="Show verbose messages.")
    subparser = parser.add_subparsers()

    common_parser = ArgumentParser(add_help=False)
    common_parser.add_argument('-r', '--root-dir', default=pymsbre_root_dir(), help="")
    common_parser.add_argument('--i-agree-to-meula-and-pp', action='store_true',
                               help=("You have to agree to the MEULA and Privacy Policy at download the Bedrock Server. "
                                     "If you specify this argument, you agree to them."))

    subcmd_install = subparser.add_parser("install", parents=[common_parser])
    subcmd_install.set_defaults(func=install)

    subcmd_download = subparser.add_parser("download", parents=[common_parser])
    subcmd_download.set_defaults(func=download)

    return parser.parse_args()


def main():
    args = parse_args()
    if args.debug:
        logger.info("Set log level to DEBUG.")
        logger.setLevel(DEBUG)
    dl = MsbreDownloader(pymsbre_root_dir=args.root_dir, agree_to_meula_and_pp=args.i_agree_to_meula_and_pp)
    args.func(args, dl)


if __name__ == "__main__":
    main()
