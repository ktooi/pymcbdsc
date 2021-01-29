# To can mock the os.name like below line:
# >>> os_name = "posix"
# >>> p = mock.patch('pymcbdsc.utils.os_name', os_name)
from os import name as os_name


def pymcbdsc_root_dir():
    """ pymcbdsc が利用するディレクトリ(フォルダ)の OS 毎のデフォルトパスを戻す関数。

    The function returns the default root directory of pymcbdsc each by OS.

    Returns:
        str: pymcbdsc が利用するディレクトリ(フォルダ)の OS 毎のデフォルトパス。

    Examples:

        >>> import pymcbdsc
        >>>
        >>> s = pymcbdsc.utils.pymcbdsc_root_dir()
        >>> type(s)
        <class 'str'>

        実行環境によって、次のどちらかの値を戻します。

        '/var/lib/pymcbdsc', 'c:\\pymcbdsc'
    """
    r = None
    if os_name == 'nt':
        r = "c:\\pymcbdsc"
    elif os_name == 'posix':
        r = "/var/lib/pymcbdsc"
    else:
        r = "/var/lib/pymcbdsc"
    return r
