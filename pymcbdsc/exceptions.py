
class FailureAgreeMeulaAndPpError(Exception):
    """ MEULA と Privacy Policy への未同意であることを示す例外。

    Minecraft Bedrock Edition のサーバをダウンロードする為には、 MEULA と Privacy Policy に同意する必要がありますが、
    同意せずにダウンロードしようとした場合にこの例外が Raise します。

    TODO:
        例外のメッセージに、 MEULA 及び Privacy Policy への同意が必要であるということがわかりやすいメッセージを追加する。
    """
    pass
