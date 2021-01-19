#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
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
    from pymcbdsc import __version__ as pymcbdsc_version
    act_version = "v{version}".format(version=pymcbdsc_version)
    logger.info("Pymcbdsc version: {act_version}, Provided version: {exp_version}"
                .format(act_version=act_version, exp_version=version))
    return act_version == version


def parse_args() -> Namespace:
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()
    subparsers.required = True

    subcmd_test = subparsers.add_parser('test')
    subcmd_test.set_defaults(func=test)

    return parser.parse_args()


def main() -> bool:
    args = parse_args()
    return args.func(args)


if __name__ == "__main__":
    exit(not main())
