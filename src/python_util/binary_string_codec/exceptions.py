"""binary_string_codec パッケージ固有の例外定義。"""

from __future__ import annotations


class BinaryStringDecodeError(ValueError):
    """本コーデックの生成物ではない、または破損した文字列をデコードしようとした場合に送出される。"""

    def __init__(self, value: object) -> None:
        super().__init__(f"不正または破損したエンコード文字列です: {value!r}")


class ObjectPickleError(ValueError):
    """オブジェクトの pickle 化に失敗した場合に送出される。"""

    def __init__(self, value: object) -> None:
        super().__init__(f"オブジェクトのpickle化に失敗しました: {value!r}")
