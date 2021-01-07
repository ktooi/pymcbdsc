#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest
from argparse import ArgumentParser


def test(args):
    runner = unittest.TextTestRunner()
    test_suite = unittest.defaultTestLoader.discover(start_dir="tests", top_level_dir=os.getcwd())
    test_result = runner.run(test_suite)
    return test_result.wasSuccessful()


def parse_args():
    parser = ArgumentParser()
    subparser = parser.add_subparsers()

    parser_test = subparser.add_parser('test')
    parser_test.set_defaults(func=test)

    return parser.parse_args()


def main():
    args = parse_args()
    return args.func(args)


if __name__ == "__main__":
    exit(not main())
