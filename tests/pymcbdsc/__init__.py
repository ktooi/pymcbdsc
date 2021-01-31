from typing import List
import os
from sys import version_info
from logging import getLogger


logger = getLogger(__name__)


def stop_patcher(patcher, patcher_name=None):
    """ mock.patch を停止する関数。

    Python3.5, 3.6, 3.7 では、既に `stop()` をコールした patch で再度 `stop()` をコールすると
    次のような Exception が Raise されてしまうので、その対処を行う。

    >>> from unittest import mock
    >>>
    >>> patcher = mock.patch('pymcbdsc.downloader.requests')
    >>> mock_requests = patcher.start()
    >>> patcher.stop()  # doctest: +SKIP
    >>> # すでに `stop()` をコールした patch で再度 `stop()` をコールする。
    >>> patcher.stop()  # doctest: +SKIP
    Traceback (most recent call last):
    ...
    RuntimeError: stop called on unstarted patcher

    一度 `stop()` をコールした patch からは "is_local" 属性がなくなるので、 "is_local" 属性の有無で
    patch の `stop()` をコールするか否かを判断する。ハック的だがやり方として問題ないかは知らん。

    なお、 Python3.8, 3.9 では `stop()` をコールした patch で再度 `stop()` しても問題はないので、
    このハックは利用せずに、何も気にしないで `stop()` をコールする。
    """
    (major, minor) = version_info[0:2]
    if major == 3 and (minor >= 5 and minor <= 7):  # Python3.5, 3.6, 3.7 のみハックを利用。
        if hasattr(patcher, "is_local"):
            patcher.stop()
        else:
            if patcher_name is None:
                patcher_name = patcher.attribute
            logger.info("Trying stop a patcher named {name} but it was already stopped.".format(name=patcher_name))
    else:  # Python3.5, 3.6, 3.7 以外はハックを利用しない。
        patcher.stop()


def create_empty_files(dir: str, files: List[str]) -> None:
    """ 空ファイルを作成する関数。 """
    for file in files:
        with open(os.path.join(dir, file), "w") as f:
            f.write('')
