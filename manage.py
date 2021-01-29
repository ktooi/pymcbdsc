#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import unittest
from logging import basicConfig, getLogger, INFO
from argparse import ArgumentParser, Namespace


# これはメインのファイルにのみ書く
basicConfig(level=INFO)

# これはすべてのファイルに書く
logger = getLogger(__name__)


def test(args: Namespace) -> bool:
    runner = unittest.TextTestRunner()
    test_suite = unittest.defaultTestLoader.discover(start_dir="tests", top_level_dir=os.getcwd())
    test_result = runner.run(test_suite)
    return test_result.wasSuccessful()


def vercheck(args: Namespace) -> bool:
    version = os.environ[args.environment] if args.environment else args.version
    from pymcbdsc.constants import version as pymcbdsc_version
    act_version = "v{version}".format(version=pymcbdsc_version)
    logger.info("Pymcbdsc version: {act_version}, Provided version: {exp_version}"
                .format(act_version=act_version, exp_version=version))
    return act_version == version


def requires(args: Namespace) -> bool:
    import configparser
    cini = configparser.ConfigParser()
    cini.read(args.setupcfg, encoding=args.encoding)
    output = args.output
    requires = cini['options']['install_requires']
    if output is None or output == "-":
        sys.stdout.write(requires)
    else:
        with open(output, "w") as f:
            f.write(requires)
    return True


def parse_args() -> Namespace:
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()
    subparsers.required = True

    subcmd_test = subparsers.add_parser('test')
    subcmd_test.set_defaults(func=test)

    subcmd_vercheck = subparsers.add_parser('vercheck')
    subcmd_vercheck_ver_grp = subcmd_vercheck.add_mutually_exclusive_group()
    subcmd_vercheck_ver_grp.add_argument("-V", "--version", dest="version", type=str)
    subcmd_vercheck_ver_grp.add_argument("-e", "--environment", dest="environment", type=str)
    subcmd_vercheck.set_defaults(func=vercheck)

    subcmd_req = subparsers.add_parser('requires')
    subcmd_req.add_argument("-s", "--setupcfg", dest="setupcfg", type=str, default="setup.cfg")
    subcmd_req.add_argument("-e", "--encoding", dest="encoding", type=str, default="utf-8")
    subcmd_req.add_argument("-o", "--output", dest="output", type=str)
    subcmd_req.set_defaults(func=requires)

    return parser.parse_args()


def main() -> bool:
    args = parse_args()
    return args.func(args)


if __name__ == "__main__":
    exit(not main())
