import unittest
from unittest import mock
import pymcbdsc


# os.name で取得できる OS の名前と、各 OS のデフォルトとなる pymbdsc_root_dir のデフォルト値のペア。
os_name2root_dir = {"posix": "/var/lib/pymcbdsc",
                    "nt": "c:\\pymcbdsc",
                    "OTHERS": "/var/lib/pymcbdsc"}  # OTHERS は posix でも nt でもない OS.
# os.name で取得できる OS の名前と、各 OS でのテストケース実行時に利用するテスト用ディレクトリパスのペア。
os_name2test_root_dir = {"posix": "/tmp/test/pymcbdsc",
                         "nt": "c:\\test\\pymcbdsc"}


class TestCommon(unittest.TestCase):
    """ pymcbdsc モジュールに定義されている関数をテストするテストクラス。 """

    def _test_pymcbdsc_root_dir(self, os_name: str, exp: str) -> None:
        p = mock.patch('pymcbdsc.utils.os_name', os_name)
        p.start()

        act = pymcbdsc.pymcbdsc_root_dir()
        self.assertEqual(act, exp)
        p.stop()

    def test_pymcbdsc_root_dir(self) -> None:
        for (os_name, exp_root_dir) in os_name2root_dir.items():
            self._test_pymcbdsc_root_dir(os_name, exp_root_dir)
