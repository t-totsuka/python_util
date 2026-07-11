"""pickle化可能なPythonオブジェクトと文字列を相互変換するエンコード/デコード関数を提供する。"""

from __future__ import annotations

import base64
import pickle
import zlib

from python_util.binary_string_codec.compression import compress_if_smaller
from python_util.binary_string_codec.envelope import _PayloadKind, pack, unpack
from python_util.binary_string_codec.exceptions import BinaryStringDecodeError, ObjectPickleError


def encode_object(obj: object) -> str:
    """pickle化可能なオブジェクトをJSON/TOMLに安全に埋め込める印字可能ASCII文字列に変換する。"""
    try:
        data = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
    except (pickle.PicklingError, TypeError, AttributeError) as exc:
        raise ObjectPickleError(obj) from exc
    payload, compressed = compress_if_smaller(data)
    envelope = pack(payload, compressed=compressed, kind=_PayloadKind.OBJECT)
    return base64.b85encode(envelope).decode("ascii")


def decode_object(text: str) -> object:
    """encode_objectが生成した文字列を元のオブジェクトに復元する。

    内部で pickle.loads 相当の処理を行うため、信頼できない発信元の文字列を
    デコードすると任意コード実行のリスクがある。本コーデックが生成した
    信頼できる文字列のみをデコード対象とすること。
    """
    if not isinstance(text, str):
        raise TypeError(f"textはstr型である必要があります: {text!r}")
    try:
        envelope = base64.b85decode(text)
    except ValueError as exc:
        raise BinaryStringDecodeError(text) from exc
    payload, compressed = unpack(envelope, expected_kind=_PayloadKind.OBJECT)
    data = zlib.decompress(payload) if compressed else payload
    try:
        return pickle.loads(data)  # noqa: S301
    except Exception as exc:
        raise BinaryStringDecodeError(text) from exc
