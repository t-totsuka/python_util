"""公開API（__init__.py）のテスト。"""


def test_単体正常系_binary_string_codecパッケージが_公開APIとして_主要シンボルをルートからインポート可能にする():
    from python_util.binary_string_codec import (
        BinaryStringDecodeError,
        ObjectPickleError,
        decode_bytes,
        decode_object,
        encode_bytes,
        encode_object,
    )

    assert encode_bytes is not None
    assert decode_bytes is not None
    assert encode_object is not None
    assert decode_object is not None
    assert BinaryStringDecodeError is not None
    assert ObjectPickleError is not None


def test_結合_パッケージルートからインポートしたencode_bytesとdecode_bytesが_バイト列を受け取った場合_元のバイト列に復元する():
    from python_util.binary_string_codec import decode_bytes, encode_bytes

    original = b"binary string codec"
    assert decode_bytes(encode_bytes(original)) == original


def test_結合_パッケージルートからインポートしたencode_objectとdecode_objectが_辞書オブジェクトを受け取った場合_元の辞書に復元する():
    from python_util.binary_string_codec import decode_object, encode_object

    original = {"key": "value", "count": 3}
    assert decode_object(encode_object(original)) == original
