# テスト実行結果エビデンス

## サマリ

- 実行開始: 2026-07-14 20:37:48
- 実行終了: 2026-07-14 20:37:48
- 合計: 279件
- 成功: 279件
- 失敗: 0件
- エラー: 0件
- スキップ: 0件

## テスト結果

### binary_string_codec

| テストメソッド名 | 結果 | 実行時間(秒) |
|---|---|---|
| test_単体正常系_encode_bytesとdecode_bytesが_任意のバイト列を受け取った場合_元のバイト列に復元する[] | 成功 | 0.001 |
| test_単体正常系_encode_bytesとdecode_bytesが_任意のバイト列を受け取った場合_元のバイト列に復元する[hello world] | 成功 | 0.000 |
| test_単体正常系_encode_bytesとdecode_bytesが_任意のバイト列を受け取った場合_元のバイト列に復元する[\x00\x01\x02\xff\xfe] | 成功 | 0.000 |
| test_単体正常系_encode_bytesとdecode_bytesが_任意のバイト列を受け取った場合_元のバイト列に復元する[aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa] | 成功 | 0.000 |
| test_単体正常系_encode_bytesとdecode_bytesが_任意のバイト列を受け取った場合_元のバイト列に復元する[\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff] | 成功 | 0.000 |
| test_単体正常系_encode_bytesが_バイナリデータを受け取った場合_印字可能なASCII文字のみの文字列を返す | 成功 | 0.000 |
| test_境界_encode_bytesが_空バイト列を受け取った場合_有効な文字列を返す | 成功 | 0.000 |
| test_異常系_encode_bytesが_bytes型以外を受け取った場合_TypeErrorを送出する | 成功 | 0.000 |
| test_異常系_decode_bytesが_str型以外を受け取った場合_TypeErrorを送出する | 成功 | 0.000 |
| test_境界_compress_if_smallerが_空データを受け取った場合_圧縮せずそのまま返す | 成功 | 0.000 |
| test_単体正常系_compress_if_smallerが_非圧縮性のランダムデータを受け取った場合_元データのまま返す | 成功 | 0.000 |
| test_単体正常系_compress_if_smallerが_高圧縮率のテキストデータを受け取った場合_圧縮済みデータを返す | 成功 | 0.000 |
| test_単体正常系_compress_if_smallerが_任意のデータを受け取った場合_圧縮結果が元データ長を超えない | 成功 | 0.000 |
| test_結合_encode_bytesが_繰り返しテキストデータを受け取った場合_base64エンコードよりも短い文字列を返す | 成功 | 0.000 |
| test_結合_encode_bytesが_日本語文章データを受け取った場合_base64エンコードよりも短い文字列を返す | 成功 | 0.000 |
| test_結合_encode_bytesが_非圧縮性のランダムデータを受け取った場合_非圧縮時のbase85サイズと一致する | 成功 | 0.000 |
| test_単体正常系_packとunpackが_任意のペイロード_圧縮有無_種別を受け取った場合_元のペイロードと圧縮フラグを復元する[0-True-] | 成功 | 0.000 |
| test_単体正常系_packとunpackが_任意のペイロード_圧縮有無_種別を受け取った場合_元のペイロードと圧縮フラグを復元する[0-True-hello world] | 成功 | 0.000 |
| test_単体正常系_packとunpackが_任意のペイロード_圧縮有無_種別を受け取った場合_元のペイロードと圧縮フラグを復元する[0-True-\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff] | 成功 | 0.000 |
| test_単体正常系_packとunpackが_任意のペイロード_圧縮有無_種別を受け取った場合_元のペイロードと圧縮フラグを復元する[0-False-] | 成功 | 0.000 |
| test_単体正常系_packとunpackが_任意のペイロード_圧縮有無_種別を受け取った場合_元のペイロードと圧縮フラグを復元する[0-False-hello world] | 成功 | 0.000 |
| test_単体正常系_packとunpackが_任意のペイロード_圧縮有無_種別を受け取った場合_元のペイロードと圧縮フラグを復元する[0-False-\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff] | 成功 | 0.000 |
| test_単体正常系_packとunpackが_任意のペイロード_圧縮有無_種別を受け取った場合_元のペイロードと圧縮フラグを復元する[1-True-] | 成功 | 0.000 |
| test_単体正常系_packとunpackが_任意のペイロード_圧縮有無_種別を受け取った場合_元のペイロードと圧縮フラグを復元する[1-True-hello world] | 成功 | 0.000 |
| test_単体正常系_packとunpackが_任意のペイロード_圧縮有無_種別を受け取った場合_元のペイロードと圧縮フラグを復元する[1-True-\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff] | 成功 | 0.000 |
| test_単体正常系_packとunpackが_任意のペイロード_圧縮有無_種別を受け取った場合_元のペイロードと圧縮フラグを復元する[1-False-] | 成功 | 0.000 |
| test_単体正常系_packとunpackが_任意のペイロード_圧縮有無_種別を受け取った場合_元のペイロードと圧縮フラグを復元する[1-False-hello world] | 成功 | 0.000 |
| test_単体正常系_packとunpackが_任意のペイロード_圧縮有無_種別を受け取った場合_元のペイロードと圧縮フラグを復元する[1-False-\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff] | 成功 | 0.000 |
| test_単体正常系_packが_空ペイロードを受け取った場合_ヘッダー長以上のバイト列を返す | 成功 | 0.000 |
| test_異常系_unpackが_マジックバイトが不一致のデータを受け取った場合_BinaryStringDecodeErrorを送出する | 成功 | 0.000 |
| test_異常系_unpackが_バージョンが不一致のデータを受け取った場合_BinaryStringDecodeErrorを送出する | 成功 | 0.000 |
| test_異常系_unpackが_予約済みフラグビットが非ゼロのデータを受け取った場合_BinaryStringDecodeErrorを送出する | 成功 | 0.000 |
| test_異常系_unpackが_期待する種別と異なるデータを受け取った場合_BinaryStringDecodeErrorを送出する | 成功 | 0.000 |
| test_単体正常系_BinaryStringDecodeErrorが_定義された場合_ValueErrorのサブクラスである | 成功 | 0.000 |
| test_単体正常系_BinaryStringDecodeErrorが_値を受け取った場合_メッセージに値のrepr表現を含む | 成功 | 0.000 |
| test_単体正常系_BinaryStringDecodeErrorが_送出された場合_ValueErrorとして捕捉できる | 成功 | 0.000 |
| test_単体正常系_ObjectPickleErrorが_定義された場合_ValueErrorのサブクラスである | 成功 | 0.000 |
| test_単体正常系_ObjectPickleErrorが_値を受け取った場合_メッセージに値のrepr表現を含む | 成功 | 0.000 |
| test_単体正常系_ObjectPickleErrorが_送出された場合_ValueErrorとして捕捉できる | 成功 | 0.000 |
| test_結合_decode_bytesが_encode_objectの出力を受け取った場合_BinaryStringDecodeErrorを送出する | 成功 | 0.000 |
| test_結合_decode_objectが_encode_bytesの出力を受け取った場合_BinaryStringDecodeErrorを送出する | 成功 | 0.000 |
| test_異常系_decode_bytesが_base85として不正な文字列を受け取った場合_BinaryStringDecodeErrorを送出する | 成功 | 0.000 |
| test_異常系_decode_objectが_base85として不正な文字列を受け取った場合_BinaryStringDecodeErrorを送出する | 成功 | 0.000 |
| test_異常系_decode_bytesが_ヘッダーが欠損した切り詰めデータを受け取った場合_BinaryStringDecodeErrorを送出する | 成功 | 0.000 |
| test_異常系_decode_objectが_ヘッダーが欠損した切り詰めデータを受け取った場合_BinaryStringDecodeErrorを送出する | 成功 | 0.000 |
| test_単体正常系_encode_objectとdecode_objectが_dataclassインスタンスを受け取った場合_eq比較で等しい値を復元する | 成功 | 0.000 |
| test_単体正常系_encode_objectとdecode_objectが_通常クラスインスタンスを受け取った場合_型と属性値が一致する値を復元する | 成功 | 0.000 |
| test_単体正常系_encode_objectが_オブジェクトを受け取った場合_str型を返す | 成功 | 0.000 |
| test_異常系_decode_objectが_str型以外を受け取った場合_TypeErrorを送出する | 成功 | 0.000 |
| test_異常系_encode_objectが_pickle不可能なオブジェクトを受け取った場合_ObjectPickleErrorを送出し元例外を保持する | 成功 | 0.000 |
| test_単体正常系_binary_string_codecパッケージが_公開APIとして_主要シンボルをルートからインポート可能にする | 成功 | 0.000 |
| test_結合_パッケージルートからインポートしたencode_bytesとdecode_bytesが_バイト列を受け取った場合_元のバイト列に復元する | 成功 | 0.000 |
| test_結合_パッケージルートからインポートしたencode_objectとdecode_objectが_辞書オブジェクトを受け取った場合_元の辞書に復元する | 成功 | 0.000 |

### logging

| テストメソッド名 | 結果 | 実行時間(秒) |
|---|---|---|
| test_単体正常系_load_configが_pyproject_tomlが見つからない場合_デフォルト設定を返す | 成功 | 0.003 |
| test_単体正常系_load_configが_toolテーブルが存在しない場合_デフォルト設定を返す | 成功 | 0.001 |
| test_単体正常系_load_configが_完全な設定テーブルを受け取った場合_全項目を解析する | 成功 | 0.001 |
| test_異常系_load_configが_TOML構文エラーを含む場合_警告を出しデフォルト設定にフォールバックする | 成功 | 0.001 |
| test_単体正常系_load_configが_UTF8の非ASCII文字を含む場合_ロケールに依存せず解析する | 成功 | 0.001 |
| test_異常系_load_configが_UTF8として不正なバイト列を含む場合_警告を出しデフォルト設定にフォールバックする | 成功 | 0.005 |
| test_異常系_load_configが_未知のログレベル文字列を受け取った場合_警告を出しデフォルト設定にフォールバックする | 成功 | 0.001 |
| test_単体正常系_load_configが_rotationテーブルを受け取った場合_有効フラグと保持日数を解析する | 成功 | 0.001 |
| test_単体正常系_load_configが_rotationテーブルが存在しない場合_ローテーション有効かつ保持7日を既定とする | 成功 | 0.001 |
| test_異常系_load_configが_retention_daysに不正値を受け取った場合_警告を出しデフォルト設定にフォールバックする[\u30bc\u30ed] | 成功 | 0.001 |
| test_異常系_load_configが_retention_daysに不正値を受け取った場合_警告を出しデフォルト設定にフォールバックする[\u8ca0\u6570] | 成功 | 0.001 |
| test_異常系_load_configが_retention_daysに不正値を受け取った場合_警告を出しデフォルト設定にフォールバックする[bool\u5024] | 成功 | 0.001 |
| test_異常系_load_configが_retention_daysに不正値を受け取った場合_警告を出しデフォルト設定にフォールバックする[\u6587\u5b57\u5217] | 成功 | 0.001 |
| test_異常系_load_configが_retention_daysに不正値を受け取った場合_警告を出しデフォルト設定にフォールバックする[\u6d6e\u52d5\u5c0f\u6570\u70b9\u6570] | 成功 | 0.001 |
| test_異常系_load_configが_rotation_enabledに非bool値を受け取った場合_警告を出しデフォルト設定にフォールバックする | 成功 | 0.001 |
| test_単体正常系_load_configが_子ディレクトリから開始した場合_親ディレクトリのpyproject_tomlを探索する | 成功 | 0.001 |
| test_境界_load_configが_複数階層にpyproject_tomlが存在する場合_最初に見つかったもののみを考慮する | 成功 | 0.001 |
| test_単体正常系_resolve_logger_overrideが_複数のプレフィックスに一致する場合_最長一致のオーバーライドを返す | 成功 | 0.000 |
| test_単体正常系_resolve_logger_overrideが_一致するロガー名がない場合_Noneを返す | 成功 | 0.000 |
| test_単体正常系_get_loggerが_名前を省略された場合_呼び出し元モジュール名を使用する | 成功 | 0.006 |
| test_単体正常系_get_loggerが_名前を指定された場合_指定された名前を使用する | 成功 | 0.000 |
| test_単体正常系_get_loggerが_設定なしで呼び出された場合_デフォルトでコンソールハンドラを付与する | 成功 | 0.000 |
| test_単体正常系_get_loggerが_ファイル出力が設定された場合_ファイルハンドラを付与する | 成功 | 0.003 |
| test_単体正常系_get_loggerが_コンソールとファイル両方が設定された場合_両方へ同時に出力する | 成功 | 0.001 |
| test_単体正常系_get_loggerが_複数回呼び出された場合_設定読み込みは一度だけ行う | 成功 | 0.000 |
| test_単体正常系_get_loggerが_パッケージ公開APIとして_エクスポートされている | 成功 | 0.000 |
| test_単体正常系_get_loggerが_同じ名前で繰り返し呼び出された場合_ハンドラを重複させない | 成功 | 0.000 |
| test_境界_get_loggerが_同じ名前で並行アクセスされた場合_ハンドラを一度だけ登録する | 成功 | 0.024 |
| test_単体正常系_get_loggerが_既存ロガーを再取得した場合_同一のハンドラ一覧を保持する | 成功 | 0.000 |
| test_単体正常系_get_loggerが_設定レベル未満のメッセージを受け取った場合_出力から除外する[20-10] | 成功 | 0.001 |
| test_単体正常系_get_loggerが_設定レベル未満のメッセージを受け取った場合_出力から除外する[30-20] | 成功 | 0.001 |
| test_単体正常系_get_loggerが_設定レベル未満のメッセージを受け取った場合_出力から除外する[40-30] | 成功 | 0.001 |
| test_単体正常系_get_loggerが_設定レベル未満のメッセージを受け取った場合_出力から除外する[50-40] | 成功 | 0.001 |
| test_単体正常系_コンソールとファイルが_異なるレベルで設定された場合_それぞれ独立にフィルタする | 成功 | 0.001 |
| test_結合_get_loggerが_pyproject_tomlが存在しない場合_コンソール出力のみにフォールバックする | 成功 | 0.001 |
| test_異常系_get_loggerが_TOML構文エラーが存在する場合_警告を出しデフォルト設定にフォールバックする | 成功 | 0.001 |
| test_異常系_get_loggerが_未知のログレベル文字列が設定された場合_警告を出しデフォルトレベルにフォールバックする | 成功 | 0.001 |
| test_異常系_get_loggerが_ログディレクトリ作成に失敗した場合_警告を出しコンソール出力のみを継続する | 成功 | 0.001 |
| test_単体正常系_build_console_handlerが_ログレベルを受け取った場合_整形済みのRichHandlerを返す | 成功 | 0.000 |
| test_単体正常系_build_file_handlerが_出力先ディレクトリが存在しない場合_ディレクトリを作成する | 成功 | 0.001 |
| test_単体正常系_build_file_handlerが_ログ出力を受け取った場合_時刻レベル名メッセージ形式で追記する | 成功 | 0.001 |
| test_単体正常系_build_file_handlerが_非ASCII文字を出力した場合_ロケールに依存せずUTF8で書き込む | 成功 | 0.001 |
| test_異常系_build_file_handlerが_ディレクトリ作成に失敗した場合_警告を出しNoneを返す | 成功 | 0.001 |
| test_単体正常系_コンソールハンドラとファイルハンドラが_異なるレベルで構築された場合_互いに独立したレベルを保持する | 成功 | 0.001 |
| test_結合_複数モジュールが_同一ファイル設定を共有する場合_単一のログファイルへ集約される | 成功 | 0.002 |
| test_結合_特定ロガーにファイルオーバーライドが設定された場合_出力ファイルが分離される | 成功 | 0.002 |
| test_結合_ロガーが_コンソールとファイル両方に設定された場合_両方が同一メッセージを受け取る | 成功 | 0.001 |
| test_結合_ログレベルが設定された場合_ファイル出力にもレベルフィルタが適用される | 成功 | 0.001 |
| test_単体正常系_python_util_loggingパッケージが_インポートされた場合_モジュールを取得できる | 成功 | 0.000 |
| test_単体正常系_loggingサブモジュール群が_インポートされた場合_いずれも取得できる | 成功 | 0.000 |
| test_単体正常系_LoggingConfigが_デフォルト生成された場合_既定値を保持する | 成功 | 0.000 |
| test_単体正常系_LoggingConfigが_設定なしで生成された場合_ローテーション有効かつ保持7日となる | 成功 | 0.000 |
| test_異常系_LoggingConfigが_属性変更を試みられた場合_FrozenInstanceErrorを送出する | 成功 | 0.000 |
| test_単体正常系_LoggingConfigが_フィールド定義された場合_明示的な型ヒントを持つ | 成功 | 0.000 |
| test_単体正常系_LoggerOverrideが_デフォルト生成された場合_既定値を保持する | 成功 | 0.000 |
| test_異常系_LoggerOverrideが_属性変更を試みられた場合_FrozenInstanceErrorを送出する | 成功 | 0.000 |
| test_単体正常系_LoggerOverrideが_フィールド定義された場合_明示的な型ヒントを持つ | 成功 | 0.000 |

### progress_display

| テストメソッド名 | 結果 | 実行時間(秒) |
|---|---|---|
| test_単体正常系_load_configが_pyproject_tomlが見つからない場合_デフォルト設定を返す | 成功 | 0.001 |
| test_単体正常系_load_configが_設定テーブルが存在しない場合_デフォルト設定を返す | 成功 | 0.001 |
| test_単体正常系_load_configが_完全な設定テーブルを受け取った場合_値を解析して返す | 成功 | 0.001 |
| test_異常系_load_configが_TOML構文エラーを含む場合_警告を出しデフォルト設定にフォールバックする | 成功 | 0.001 |
| test_単体正常系_load_configが_UTF8の非ASCII文字を含む場合_ロケールに依存せず解析する | 成功 | 0.001 |
| test_異常系_load_configが_UTF8として不正なバイト列を含む場合_警告を出しデフォルト設定にフォールバックする | 成功 | 0.001 |
| test_異常系_load_configが_refresh_per_secondに0を指定された場合_警告を出しデフォルト設定にフォールバックする | 成功 | 0.001 |
| test_異常系_load_configが_refresh_per_secondに負数を指定された場合_警告を出しデフォルト設定にフォールバックする | 成功 | 0.001 |
| test_異常系_load_configが_auto_remove_finishedに不正な型を指定された場合_警告を出しデフォルト設定にフォールバックする | 成功 | 0.001 |
| test_単体正常系_load_configが_開始ディレクトリにpyproject_tomlがない場合_親ディレクトリを探索して設定を読み込む | 成功 | 0.001 |
| test_境界_load_configが_複数階層にpyproject_tomlが存在する場合_最初に見つかったファイルのみを考慮する | 成功 | 0.001 |
| test_単体正常系_load_configが_start_dirを省略された場合_カレントディレクトリを起点に探索する | 成功 | 0.001 |
| test_単体正常系_get_cached_configが_複数回呼び出された場合_設定読み込みは一度だけ行う | 成功 | 0.000 |
| test_単体正常系_reset_config_cacheが_呼び出された場合_次回取得時に設定を再読み込みする | 成功 | 0.000 |
| test_単体正常系_ProgressDisplayが_コンテキストに入る前の場合_開始状態でない | 成功 | 0.001 |
| test_単体正常系_ProgressDisplayが_withブロックに入った場合_表示を開始する | 成功 | 0.001 |
| test_単体正常系_ProgressDisplayが_withブロックを正常に抜けた場合_表示を停止する | 成功 | 0.002 |
| test_異常系_ProgressDisplayが_withブロック内で例外が発生した場合_表示を停止する | 成功 | 0.001 |
| test_単体正常系_ProgressDisplayが_カスタムカラムを渡された場合_カラムを保持する | 成功 | 0.000 |
| test_単体正常系_ProgressDisplayが_カラムを指定されなかった場合_デフォルトカラムを使用する | 成功 | 0.000 |
| test_異常系_add_taskが_表示開始前に呼び出された場合_DisplayNotStartedErrorを送出する | 成功 | 0.001 |
| test_異常系_add_taskが_totalに0を指定された場合_InvalidTotalErrorを送出する | 成功 | 0.001 |
| test_異常系_add_taskが_totalに負数を指定された場合_InvalidTotalErrorを送出する | 成功 | 0.001 |
| test_単体正常系_add_taskが_複数回呼び出された場合_一意なタスクIDを返す | 成功 | 0.003 |
| test_単体正常系_add_taskが_説明文とtotalとcompletedを指定された場合_タスクへ登録する | 成功 | 0.001 |
| test_単体正常系_add_taskが_複数回呼び出された場合_単一の表示に複数タスクを表示する | 成功 | 0.001 |
| test_単体正常系_add_taskが_completedがtotalに到達しauto_remove_finishedが無効な場合_タスクを表示し続ける | 成功 | 0.001 |
| test_単体正常系_add_taskが_completedがtotalに到達しauto_remove_finishedが有効な場合_タスクを自動的に削除する | 成功 | 0.001 |
| test_異常系_updateが_表示開始前に呼び出された場合_DisplayNotStartedErrorを送出する | 成功 | 0.001 |
| test_異常系_updateが_未知のタスクIDを指定された場合_UnknownTaskErrorを送出する | 成功 | 0.001 |
| test_単体正常系_updateが_completedを絶対値で指定された場合_即座に反映する | 成功 | 0.001 |
| test_単体正常系_updateが_advanceを指定された場合_即座に加算して反映する | 成功 | 0.001 |
| test_単体正常系_updateが_completedがtotalに到達した場合_タスクをfinished状態にする | 成功 | 0.001 |
| test_単体正常系_updateが_completedがtotalに到達しauto_remove_finishedが無効な場合_タスクを表示し続ける | 成功 | 0.001 |
| test_単体正常系_updateが_completedがtotalに到達しauto_remove_finishedが有効な場合_タスクを自動的に削除する | 成功 | 0.001 |
| test_異常系_remove_taskが_表示開始前に呼び出された場合_DisplayNotStartedErrorを送出する | 成功 | 0.000 |
| test_異常系_remove_taskが_未知のタスクIDを指定された場合_UnknownTaskErrorを送出する | 成功 | 0.005 |
| test_単体正常系_remove_taskが_既知のタスクIDを指定された場合_表示からタスクを削除する | 成功 | 0.001 |
| test_単体正常系_remove_taskが_一つのタスクを削除した場合_他のタスクに影響しない | 成功 | 0.001 |
| test_異常系_trackが_表示開始前に呼び出された場合_DisplayNotStartedErrorを送出する | 成功 | 0.001 |
| test_単体正常系_trackが_シーケンスを渡された場合_元の値をそのまま順に返す | 成功 | 0.001 |
| test_単体正常系_trackが_要素を消費するたびに_進捗を1ずつ進める | 成功 | 0.001 |
| test_単体正常系_trackが_totalを指定されなかった場合_シーケンスの長さをデフォルトのtotalとして使用する | 成功 | 0.001 |
| test_単体正常系_trackが_totalを明示的に指定された場合_デフォルト値より優先する | 成功 | 0.001 |
| test_単体正常系_trackが_auto_remove_finishedが有効な場合_完了後にタスクを自動的に削除する | 成功 | 0.001 |
| test_異常系_add_taskが_descriptionに文字列以外を指定された場合_TypeErrorを送出する | 成功 | 0.001 |
| test_異常系_add_taskが_totalに数値以外を指定された場合_TypeErrorを送出する | 成功 | 0.001 |
| test_異常系_add_taskが_completedに数値以外を指定された場合_TypeErrorを送出する | 成功 | 0.001 |
| test_異常系_updateが_task_idにTaskID以外を指定された場合_TypeErrorを送出する | 成功 | 0.001 |
| test_異常系_updateが_completedに数値以外を指定された場合_TypeErrorを送出する | 成功 | 0.001 |
| test_異常系_updateが_advanceに数値以外を指定された場合_TypeErrorを送出する | 成功 | 0.001 |
| test_異常系_updateが_descriptionに文字列以外を指定された場合_TypeErrorを送出する | 成功 | 0.001 |
| test_異常系_remove_taskが_task_idにTaskID以外を指定された場合_TypeErrorを送出する | 成功 | 0.001 |
| test_異常系_trackが_イテラブルでない値を指定された場合_TypeErrorを送出する | 成功 | 0.001 |
| test_異常系_trackが_descriptionに文字列以外を指定された場合_TypeErrorを送出する | 成功 | 0.001 |
| test_異常系_trackが_totalに数値以外を指定された場合_TypeErrorを送出する | 成功 | 0.001 |
| test_単体正常系_UnknownTaskErrorが_定義された場合_ValueErrorのサブクラスである | 成功 | 0.000 |
| test_単体正常系_UnknownTaskErrorが_タスクIDを渡されて送出された場合_メッセージにタスクIDを含む | 成功 | 0.000 |
| test_単体正常系_InvalidTotalErrorが_定義された場合_ValueErrorのサブクラスである | 成功 | 0.000 |
| test_単体正常系_InvalidTotalErrorが_不正なtotalを渡されて送出された場合_メッセージにtotalを含む | 成功 | 0.000 |
| test_単体正常系_DisplayNotStartedErrorが_定義された場合_ValueErrorのサブクラスである | 成功 | 0.000 |
| test_単体正常系_DisplayNotStartedErrorが_引数なしで送出された場合_例外として送出できる | 成功 | 0.000 |
| test_単体正常系_InvalidProgressDisplayConfigが_定義された場合_ValueErrorでないException派生である | 成功 | 0.000 |
| test_結合_ProgressDisplayが_複数タスクを同時に進行させた場合_完了したタスクのみ自動削除される | 成功 | 0.001 |
| test_結合_trackが_シーケンスを反復処理する場合_1要素ごとに進捗を進める | 成功 | 0.001 |
| test_結合_ProgressDisplayが_withブロック内で例外が発生した場合_表示を後片付けし再利用できる | 成功 | 0.002 |
| test_単体正常系_progress_displayパッケージが_公開APIとして_期待される名前をエクスポートする | 成功 | 0.000 |
| test_結合_progress_displayのトップレベルAPIのみを使用した場合_一連のワークフローが完結する | 成功 | 0.001 |
| test_結合_README記載の基本サンプルが_複数タスクを扱った場合_期待通りに動作する | 成功 | 0.002 |
| test_結合_README記載のtrackヘルパーサンプルが_シーケンスを処理した場合_期待通りに動作する | 成功 | 0.001 |
| test_結合_README記載のpyproject_toml設定サンプルが_読み込まれた場合_期待通りの設定値になる | 成功 | 0.001 |
| test_単体正常系_ProgressDisplayConfigが_デフォルト値で生成された場合_期待されるデフォルト値を持つ | 成功 | 0.000 |
| test_単体正常系_ProgressDisplayConfigが_生成された場合_フィールド変更不可なイミュータブルである | 成功 | 0.000 |
| test_単体正常系_ProgressDisplayConfigが_生成時に値を指定された場合_指定した値で上書きする | 成功 | 0.000 |

### test_evidence

| テストメソッド名 | 結果 | 実行時間(秒) |
|---|---|---|
| test_結合_pytest_runtest_logreportが_callが成功しteardownが失敗した場合_FAILEDとして記録する | 成功 | 0.020 |
| test_結合_pytest_runtest_logreportが_全フェーズ成功した場合_PASSEDとして記録する | 成功 | 0.016 |
| test_結合_pytest_runtest_logreportが_スキップされた場合_SKIPPEDとして記録する | 成功 | 0.016 |
| test_結合_pytest_runtest_logreportが_ネストしたpytesterセッション実行時_外側セッションの収集結果を汚染しない | 成功 | 0.016 |
| test_単体正常系_extract_subpackage_and_method_nameが_parametrizeされたnodeidを受け取った場合_接尾辞を保持したままmethod_nameを返す | 成功 | 0.000 |
| test_結合_pytest_sessionstartが_セッション開始時_開始時刻をUTC日時として記録する | 成功 | 0.018 |
| test_結合_pytest_sessionfinishが_セッション終了時_収集済みTestCaseResultからreports配下にMarkdownエビデンスを書き込む | 成功 | 0.015 |
| test_結合_pytest_runtest_logreportが_parametrizeされたテストを実行した場合_パラメータ接尾辞を含むmethod_nameで記録する | 成功 | 0.016 |
| test_結合_pytest_sessionfinishが_複数サブパッケージと失敗を含むスイート実行時_サブパッケージ別グルーピングと失敗一覧を含むMarkdownを生成する | 成功 | 0.021 |
| test_単体正常系_InvalidReportDestinationErrorが_ValueErrorを継承している場合_ValueErrorとして送出できる | 成功 | 0.000 |
| test_単体異常系_InvalidReportDestinationErrorが_不正な拡張子を受け取った場合_送出先を含むメッセージを保持する | 成功 | 0.000 |
| test_単体正常系_render_markdown_reportが_複数サブパッケージのケースを受け取った場合_サブパッケージ単位で見出しをグルーピングして出力する | 成功 | 0.000 |
| test_単体正常系_render_markdown_reportが_成功失敗スキップを含む場合_全体サマリに件数と実行開始終了時刻を出力する | 成功 | 0.000 |
| test_単体正常系_render_markdown_reportが_失敗ケースを含む場合_専用セクションに失敗内容とともに明示する | 成功 | 0.000 |
| test_単体境界_render_markdown_reportが_0件のTestRunReportを受け取った場合_有効なMarkdownを返す | 成功 | 0.000 |
| test_結合_pre_commit_config_yamlのフックentryが_pdm_run_pytestを疑似成功コマンドに置換した場合_reports_test_evidence_mdをステージする | 成功 | 0.043 |
| test_結合_pre_commit_config_yamlのフックentryが_pdm_run_pytestを疑似失敗コマンドに置換した場合_非0で終了しreports_test_evidence_mdをステージしない | 成功 | 0.033 |
| test_単体正常系_test_evidenceパッケージが_importされた場合_公開APIをall属性として保持する | 成功 | 0.000 |
| test_単体正常系_test_evidenceパッケージが_importされた場合_all属性に列挙した名前を実際に参照できる | 成功 | 0.000 |
| test_単体正常系_write_markdown_reportが_有効な出力先を受け取った場合_render結果をファイルへ書き込む | 成功 | 0.001 |
| test_単体正常系_write_markdown_reportが_親ディレクトリが存在しない場合_ディレクトリを作成してから書き込む | 成功 | 0.001 |
| test_単体正常系_write_markdown_reportが_再実行された場合_内容を上書きする | 成功 | 0.001 |
| test_単体異常系_write_markdown_reportが_md以外の拡張子を受け取った場合_InvalidReportDestinationErrorを送出する | 成功 | 0.001 |
| test_単体正常系_TestOutcomeが_4値を持つ場合_それぞれの値でアクセスできる | 成功 | 0.000 |
| test_単体正常系_TestCaseResultが_必須項目を受け取った場合_各属性を保持する | 成功 | 0.000 |
| test_単体正常系_TestCaseResultが_failure_messageを受け取った場合_属性に保持する | 成功 | 0.000 |
| test_単体正常系_TestCaseResultが_生成済みの場合_属性への再代入でFrozenInstanceErrorを送出する | 成功 | 0.000 |
| test_単体正常系_TestRunReportが_複数のTestCaseResultを受け取った場合_全件を保持する | 成功 | 0.000 |
| test_単体正常系_TestRunReportが_生成済みの場合_属性への再代入でFrozenInstanceErrorを送出する | 成功 | 0.000 |

### time_utility

| テストメソッド名 | 結果 | 実行時間(秒) |
|---|---|---|
| test_単体正常系_nowが_tzを指定せずに呼ばれた場合_JSTタイムゾーンのdatetimeを返す | 成功 | 0.001 |
| test_単体正常系_nowが_文字列でタイムゾーンを指定された場合_指定したタイムゾーンのdatetimeを返す | 成功 | 0.000 |
| test_単体正常系_nowが_tzinfoオブジェクトを指定された場合_同じtzinfoを返す | 成功 | 0.001 |
| test_異常系_nowが_サポート対象外の型を指定された場合_TypeErrorを送出する | 成功 | 0.000 |
| test_異常系_nowが_未知のタイムゾーン名を指定された場合_InvalidTimezoneErrorを送出する | 成功 | 0.001 |
| test_単体正常系_ensure_awareが_naive状態のdatetimeを受け取った場合_デフォルトでJSTを付与する | 成功 | 0.000 |
| test_単体正常系_ensure_awareが_aware状態のdatetimeを受け取った場合_変更せずそのまま返す | 成功 | 0.000 |
| test_単体正常系_ensure_awareが_naive状態のdatetimeとdefault_tzを指定された場合_指定したタイムゾーンを付与する | 成功 | 0.000 |
| test_単体正常系_ensure_awareが_aware状態のdatetimeとdefault_tzを指定された場合_default_tzを無視する | 成功 | 0.000 |
| test_異常系_ensure_awareが_datetime以外を受け取った場合_TypeErrorを送出する | 成功 | 0.000 |
| test_単体正常系_to_jstが_aware状態のdatetimeを受け取った場合_同一時刻を保ったままJSTへ変換する | 成功 | 0.000 |
| test_単体正常系_to_jstが_naive状態のdatetimeを受け取った場合_既にJSTとして扱う | 成功 | 0.000 |
| test_異常系_to_jstが_datetime以外を受け取った場合_TypeErrorを送出する | 成功 | 0.000 |
| test_単体正常系_to_utcが_naive状態のdatetimeを受け取った場合_JSTとして解釈しUTCへ変換する | 成功 | 0.000 |
| test_単体正常系_to_utcが_aware状態のdatetimeを受け取った場合_同一時刻を保ったままUTCへ変換する | 成功 | 0.000 |
| test_異常系_to_utcが_datetime以外を受け取った場合_TypeErrorを送出する | 成功 | 0.000 |
| test_単体正常系_to_timezoneが_文字列でタイムゾーンを指定された場合_指定したタイムゾーンへ変換する | 成功 | 0.000 |
| test_単体正常系_to_timezoneが_naive状態のdatetimeを受け取った場合_JSTとして解釈してから変換する | 成功 | 0.000 |
| test_異常系_to_timezoneが_未知のタイムゾーン名を指定された場合_InvalidTimezoneErrorを送出する | 成功 | 0.001 |
| test_異常系_to_timezoneが_datetime以外を受け取った場合_TypeErrorを送出する | 成功 | 0.000 |
| test_結合_to_utcとto_jstが_aware状態のdatetimeを往復変換した場合_元の値を保つ | 成功 | 0.000 |
| test_結合_to_utcとto_jstが_naive状態のdatetimeを往復変換した場合_元の時刻表記を保つ | 成功 | 0.000 |
| test_単体正常系_InvalidTimezoneErrorが_定義された場合_ValueErrorのサブクラスである | 成功 | 0.000 |
| test_単体正常系_InvalidTimezoneErrorが_不正な値を渡された場合_メッセージにその値を含む | 成功 | 0.000 |
| test_単体正常系_DateTimeParseErrorが_定義された場合_ValueErrorのサブクラスである | 成功 | 0.000 |
| test_単体正常系_DateTimeParseErrorが_不正な値を渡された場合_メッセージにその値を含む | 成功 | 0.000 |
| test_単体正常系_DateTimeFormatが_列挙型として定義された場合_全ての事前定義メンバーを持つ | 成功 | 0.000 |
| test_単体正常系_format_datetimeが_ISO形式でaware状態のdatetimeを受け取った場合_UTCオフセットを含む文字列を返す | 成功 | 0.000 |
| test_単体正常系_format_datetimeが_DATE形式を指定された場合_年月日形式の文字列を返す | 成功 | 0.000 |
| test_単体正常系_format_datetimeが_DATETIME形式を指定された場合_年月日時分秒形式の文字列を返す | 成功 | 0.000 |
| test_単体正常系_format_datetimeが_fmtを省略された場合_DATETIME形式の文字列を返す | 成功 | 0.000 |
| test_単体正常系_format_datetimeが_JAPANESE_DATE形式を指定された場合_ロケール非依存で曜日を含む文字列を返す | 成功 | 0.000 |
| test_単体正常系_format_datetimeが_JAPANESE_DATETIME形式を指定された場合_曜日と時刻を含む文字列を返す | 成功 | 0.000 |
| test_単体正常系_format_datetimeが_enum値と一致する文字列でfmtを指定された場合_対応する形式の文字列を返す | 成功 | 0.000 |
| test_単体正常系_format_datetimeが_enumにないstrftime書式文字列を指定された場合_その書式で文字列を返す | 成功 | 0.000 |
| test_異常系_format_datetimeが_datetime以外を受け取った場合_TypeErrorを送出する | 成功 | 0.000 |
| test_単体正常系_parse_datetimeが_ISO形式の文字列を受け取った場合_aware状態のdatetimeへ往復変換する | 成功 | 0.000 |
| test_単体正常系_parse_datetimeが_DATETIME形式の文字列を受け取った場合_aware状態のdatetimeへ往復変換する | 成功 | 0.000 |
| test_単体正常系_parse_datetimeが_DATE形式の文字列を受け取った場合_aware状態のdatetimeへ往復変換する | 成功 | 0.000 |
| test_単体正常系_parse_datetimeが_JAPANESE_DATETIME形式の文字列を受け取った場合_aware状態のdatetimeへ往復変換する | 成功 | 0.002 |
| test_単体正常系_parse_datetimeが_JAPANESE_DATE形式の文字列を受け取った場合_aware状態のdatetimeへ往復変換する | 成功 | 0.000 |
| test_単体正常系_parse_datetimeが_タイムゾーン情報のない文字列を受け取った場合_デフォルトでJSTを付与する | 成功 | 0.000 |
| test_単体正常系_parse_datetimeが_タイムゾーン情報のない文字列とtzを指定された場合_指定したタイムゾーンを付与する | 成功 | 0.000 |
| test_単体正常系_parse_datetimeが_fmtにenumを明示指定された場合_その形式のみで解析する | 成功 | 0.000 |
| test_単体正常系_parse_datetimeが_fmtに文字列値を明示指定された場合_その形式のみで解析する | 成功 | 0.000 |
| test_単体正常系_parse_datetimeが_enumにないstrptime書式文字列を指定された場合_その書式で解析する | 成功 | 0.000 |
| test_異常系_parse_datetimeが_いずれの形式にも一致しない文字列を受け取った場合_DateTimeParseErrorを送出する | 成功 | 0.000 |
| test_異常系_parse_datetimeが_指定した形式に一致しない文字列を受け取った場合_DateTimeParseErrorを送出する | 成功 | 0.000 |
| test_結合_nowとformat_datetimeとparse_datetimeが_ISO形式で往復変換した場合_元の値を保つ | 成功 | 0.000 |
| test_結合_nowとformat_datetimeとparse_datetimeが_fmtを指定せず往復変換した場合_ISO形式を優先して元の値を保つ | 成功 | 0.000 |
| test_結合_nowとformat_datetimeとparse_datetimeが_DATETIME形式で往復変換した場合_秒精度で一致する | 成功 | 0.000 |
| test_結合_nowとformat_datetimeとparse_datetimeが_JAPANESE_DATETIME形式で往復変換した場合_秒精度で一致する | 成功 | 0.000 |
| test_結合_nowとformat_datetimeとparse_datetimeが_明示的なタイムゾーンで往復変換した場合_UTCオフセットを保つ | 成功 | 0.000 |
| test_結合_to_utcとto_jstが_nowの結果を往復変換した場合_元の値を保つ | 成功 | 0.000 |
| test_異常系_now_to_timezone_parse_datetimeが_未知のタイムゾーン名を指定された場合_一貫してInvalidTimezoneErrorを送出する[<lambda>0] | 成功 | 0.000 |
| test_異常系_now_to_timezone_parse_datetimeが_未知のタイムゾーン名を指定された場合_一貫してInvalidTimezoneErrorを送出する[<lambda>1] | 成功 | 0.000 |
| test_異常系_now_to_timezone_parse_datetimeが_未知のタイムゾーン名を指定された場合_一貫してInvalidTimezoneErrorを送出する[<lambda>2] | 成功 | 0.000 |
| test_単体正常系_time_utilityパッケージが_インポートされた場合_モジュールとして取得できる | 成功 | 0.000 |
| test_単体正常系_time_utilityパッケージの公開APIが_ルートからインポートされた場合_全てのシンボルを取得できる | 成功 | 0.000 |
| test_結合_time_utilityパッケージの再エクスポートされたシンボルが_往復変換に使用された場合_元の値を保つ | 成功 | 0.000 |
| test_単体正常系_JSTが_定義された場合_Asia_TokyoのZoneInfoと一致する | 成功 | 0.000 |
| test_単体正常系_resolve_timezoneが_Noneを受け取った場合_JSTを返す | 成功 | 0.000 |
| test_単体正常系_resolve_timezoneが_有効なタイムゾーン名を受け取った場合_対応するZoneInfoを返す | 成功 | 0.000 |
| test_単体正常系_resolve_timezoneが_tzinfoオブジェクトを受け取った場合_同じtzinfoを返す | 成功 | 0.000 |
| test_異常系_resolve_timezoneが_未知のタイムゾーン名を受け取った場合_InvalidTimezoneErrorを送出する | 成功 | 0.000 |
| test_異常系_resolve_timezoneが_サポート対象外の型を受け取った場合_InvalidTimezoneErrorを送出する | 成功 | 0.000 |
