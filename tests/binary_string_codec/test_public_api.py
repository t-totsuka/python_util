"""公開API（__init__.py）のテスト。"""


def test_public_api_symbols_are_importable_from_package_root():
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


def test_public_api_bytes_round_trip_uses_reexported_symbols():
    from python_util.binary_string_codec import decode_bytes, encode_bytes

    original = b"binary string codec"
    assert decode_bytes(encode_bytes(original)) == original


def test_public_api_object_round_trip_uses_reexported_symbols():
    from python_util.binary_string_codec import decode_object, encode_object

    original = {"key": "value", "count": 3}
    assert decode_object(encode_object(original)) == original
