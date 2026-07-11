# Research & Design Decisions Template

---
**Purpose**: Capture discovery findings, architectural investigations, and rationale that inform the technical design.

**Usage**:
- Log research activities and outcomes during the discovery phase.
- Document design decision trade-offs that are too detailed for `design.md`.
- Provide references and evidence for future audits or reuse.
---

## Summary
- **Feature**: `binary-string-codec`
- **Discovery Scope**: New Feature（既存サブパッケージに同種機能なし。`src/python_util/` に新規サブパッケージを追加）
- **Key Findings**:
  - `bytes`⇔`str` の相互変換・圧縮・`pickle` はすべて標準ライブラリ（`base64`, `zlib`, `bz2`, `lzma`, `pickle`）で実現可能。新規外部依存は不要（`tech.md` の「外部依存最小限」方針に合致）
  - Base85（`base64.b85encode`）は Base64 比で約6%程度エンコード後サイズが小さい（情報密度が高い）ことを実測で確認
  - 圧縮＋Base85は、テキスト系・繰り返しの多いデータで無圧縮Base64比 90%超のサイズ削減を達成する一方、ランダムデータや小サイズ・既圧縮データでは圧縮がむしろサイズを増加させるため、Requirement 3 AC3（圧縮が有効でない場合は無圧縮にフォールバック）の判定ロジックが必須
  - `logging` / `time_utility` に、本機能がそのまま踏襲できる例外設計・公開API集約・テスト配置の確立済みパターンが存在する
  - `pickle` を用いたオブジェクトデコードは任意コード実行のリスクを伴うため、設計フェーズで「信頼できる入力のみを対象とする」制約をAPIドキュメントと設計判断の両方に明記する必要がある

## Research Log

### 圧縮アルゴリズム・エンコード方式の比較（Requirement 3 対応）
- **Context**: ユーザーより「RAWデータをBase64にしたものと比べてどのくらいの圧縮率になるのかを比較検討が必要」との明示的な要望があった（Requirement 3 AC5/AC6）
- **Sources Consulted**: 標準ライブラリ `base64`, `zlib`, `bz2`, `lzma` を用いた実測ベンチマーク（本セッション内で実行、5種類のサンプルデータ）
- **Findings**:

  | サンプル | raw bytes | Base64(無圧縮) | Base85(無圧縮) | zlib+Base85 | bz2+Base85 | lzma+Base85 |
  |---|---:|---:|---:|---:|---:|---:|
  | text_repeat（JSON風・繰り返し多） | 1212 | 1616 | 1515 | **120** | 179 | 190 |
  | prose（日本語自然文） | 3510 | 4680 | 4388 | **168** | 257 | 235 |
  | random（非圧縮性バイナリ） | 2000 | 2668 | **2500** | 2514 | 3007 | 2575 |
  | small（5 bytes） | 5 | 8 | **7** | 17 | 52 | 80 |
  | pre_compressed（既に圧縮済み） | 134 | 180 | **168** | 182 | 265 | 245 |

- **Implications**:
  - Base85は常にBase64より短い（無圧縮時で約6%削減）ため、Requirement 3 AC1（Base64より情報密度が高い方式の採用）の基準を満たす
  - 圧縮が効くデータでは `zlib` が最も高い圧縮率とエンコード後サイズの小ささを示した。`lzma` は理論上の圧縮率は高いが、ヘッダ・辞書オーバーヘッドが大きく、本ベンチマークの数KB程度のデータでは `zlib` に劣った（`bz2` も同様にオーバーヘッドが大きい）
  - ランダムデータ・小サイズデータ・既圧縮データでは、圧縮を適用すると無圧縮Base85より**大きく**なる（例: small は 7→17、pre_compressed は 168→182）。Requirement 3 AC3 の「圧縮なしへのフォールバック」は必須要件であり、単純に「常に圧縮する」実装では要件を満たせない
  - 設定ファイル・小〜中規模データという想定用途（`product.md`「個人用の Python ユーティリティ集」）を踏まえると、`zlib` をデフォルト候補とし、`lzma`/`bz2` は採用しない、または将来の拡張候補として保留するのが妥当
  - 本ベンチマークはサンプルサイズが小〜中規模（〜3.5KB）に限定されるため、より大きなペイロード（数百KB〜MB）における `lzma` の優位性は未検証（Research Needed として設計フェーズに繰り越し）

### Base85エンコード後の文字集合とJSON/TOML安全性の検証（Requirement 1 AC2 対応）

- **Context**: 設計フェーズにて、Base85エンコード結果が本当にJSON/TOMLへエスケープ不要で埋め込めるかを実装前に確定する必要があった
- **Sources Consulted**: Python標準ライブラリ `base64` の実装調査（`base64.b85encode(bytes(range(256)))` を実行し、出力に現れる文字集合を網羅的に確認）
- **Findings**: Pythonの`base64.b85encode`が用いるアルファベットは`0-9A-Za-z!#$%&()*+-;<=>?@^_\`{|}~`の85文字であり、二重引用符（`"`）・バックスラッシュ（`\`）・単一引用符（`'`）・空白/改行を一切含まない
- **Implications**: エンコード結果はJSON文字列リテラル・TOML基本文字列（`"..."`）・TOMLリテラル文字列（`'...'`）のいずれにもエスケープなしでそのまま埋め込める。Requirement 1 AC2 は追加のエスケープ処理を実装せずに満たせることが確定した

### pickleベースのオブジェクトデコードにおけるセキュリティ調査（Requirement 5 対応）

- **Context**: Requirement 5 はpickle化可能な任意のPythonオブジェクトをデコード可能とする要件だが、`pickle.loads` は信頼できないデータに対して任意コード実行を許してしまう既知のリスクがあるため、設計判断としてリスク受容の方針を確定する必要があった
- **Sources Consulted**: Python公式ドキュメント（[pickle — Python object serialization](https://docs.python.org/3/library/pickle.html)）、[Python Pickle Risks and Safer Serialization Alternatives](https://arjancodes.com/blog/python-pickle-module-security-risks-and-safer-alternatives/)
- **Findings**:
  - `pickle.loads` は悪意あるデータから任意コード実行が可能であり、信頼できない発信元のデータをデコードしてはならない
  - 緩和策として「`find_class` をオーバーライドしたクラス許可リスト方式」があるが、許可リストにより復元可能なクラスが制限されるため Requirement 5 AC1（「pickle化可能な任意のオブジェクト」対応）と矛盾する。またこの方式は巧妙なopcode列によって回避された実例がある
  - HMAC等による署名検証も有効な緩和策として挙げられるが、暗号化・署名機能はRequirement範囲外（Boundary Context「Out of scope」）として明示的に除外されている
  - 信頼できないデータに対する根本的な対策は、JSON等の別フォーマットを使うことであり、pickle自体を安全に保つ方法は存在しない
- **Implications**: 本機能はクラス許可リストや署名検証を実装せず、Requirement 5 AC5 の通り「信頼できる発信元のみを対象とする」という運用上の制約をAPIドキュメント（docstring）に明記するにとどめる設計とする。これはユーザーの要求（任意のPythonオブジェクトへの対応）と要件のBoundary Context（暗号化・署名機能は対象外）の両方に整合する

### 既存サブパッケージの規約調査（Requirement 6 対応）
- **Context**: 新規サブパッケージが `logging` / `time_utility` と一貫した構成・命名・例外設計に従う必要がある（Requirement 6, `structure.md`, `tech.md`）
- **Sources Consulted**: `src/python_util/logging/`, `src/python_util/time_utility/` の実装、`tests/time_utility/test_public_api.py`
- **Findings**:
  - `__init__.py` は一行docstring＋公開シンボルのimport＋`__all__`（アルファベット順）という統一パターン
  - 例外は `exceptions.py` に集約し、`ValueError` を継承。コンストラクタで受け取った不正値を `f"...: {value!r}"` の形式で日本語メッセージ化する（`time_utility.exceptions.InvalidTimezoneError` 参照）
  - パッケージ内部限定の例外は先頭アンダースコア付きクラス名＋`Exception` 継承（`logging.config_loader._InvalidLoggingConfig`）として区別されている
  - 型チェックは `isinstance` による早期 `TypeError` 送出が一貫パターン（`time_utility.convert.to_timezone` 等）
  - 公開API網羅性は `tests/<subpackage>/test_public_api.py` でインポート＋往復動作を検証するテストが定石
- **Implications**: `binary_string_codec` も同一パターン（`exceptions.py`, `__init__.py` の `__all__`, `test_public_api.py` 相当のテスト）に揃えることで設計判断の多くを省略できる。新規に検討すべきなのはエンコード方式・圧縮方式・envelope形式（後述）のみ

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| A: 既存サブパッケージ拡張 | `logging`/`time_utility` のいずれかにバイナリ⇔文字列変換機能を追加 | 新規ファイル不要 | 責務が全く異なり両パッケージの凝集度を破壊する。両者ともバイナリ変換と無関係 | 非推奨。適用不可（拡張対象となる既存コーデック機能が存在しない） |
| B: 新規サブパッケージ作成 | `src/python_util/binary_string_codec/` を新規追加し、`encoding.py`（bytesエンコード/デコード＋圧縮選択）、`object_codec.py`（pickleベースのオブジェクトエンコード/デコード）、`exceptions.py`、`__init__.py` で構成 | 既存パターンに完全準拠、責務が明確、独立してテスト可能、外部依存追加なし | ファイル数がやや増える（許容範囲） | 推奨。`structure.md` のサブパッケージ構成方針とも合致 |
| C: ハイブリッド（段階導入） | Option B の中で bytes コーデック（Req1-4）を先行実装し、オブジェクトコーデック（Req5）を後続タスクとして分離 | 小さい単位でレビュー・テスト可能、pickleのセキュリティ考慮を独立して検討できる | フェーズ間でenvelope形式の後方互換を意識する必要 | Option B 採用を前提にタスク分解の指針として有効（設計・タスクフェーズで具体化） |

## Design Decisions

### Decision: エンコード方式は Base85（`base64.b85encode`/`b85decode`）を採用
- **Context**: Requirement 1 AC2（印字可能ASCIIのみ）、Requirement 3 AC1（Base64より高密度）
- **Alternatives Considered**:
  1. Base64 — 実装最も簡易だが情報密度で劣る（要件未達）
  2. Base85（RFC 1924 系 / Python標準の `b85encode`） — 標準ライブラリのみで完結し、印字可能ASCIIのみで構成される
  3. Base91等のサードパーティ実装 — 情報密度はさらに高い可能性があるが外部依存が必要で `tech.md` の方針（外部依存最小限）に反する
- **Selected Approach**: `base64.b85encode`/`b85decode`（標準ライブラリ）
- **Rationale**: 外部依存なしでRequirement 3 AC1を満たす。実測でBase64比約6%のサイズ削減を確認済み
- **Trade-offs**: Base91等よりは密度で劣るが、標準ライブラリのみで完結するメリットを優先
- **Follow-up**: 設計フェーズでenvelopeのバイト配置（圧縮フラグ等）とBase85エンコードの適用順序を確定する

### Decision: 圧縮アルゴリズムは `zlib` をデフォルト候補とし、無効時は無圧縮にフォールバックする
- **Context**: Requirement 3 AC2/AC3/AC5/AC6
- **Alternatives Considered**:
  1. `zlib` — 低オーバーヘッド、汎用データで高圧縮率
  2. `bz2` — 圧縮率はデータによるが本ベンチマークでは `zlib` に劣り、オーバーヘッドも大きい
  3. `lzma` — 大容量データでの圧縮率は理論上優位だが、小〜中規模データではヘッダオーバーヘッドが大きく本ベンチマークでは最下位
- **Selected Approach**: `zlib` を第一候補とし、`圧縮後Base85長 >= 無圧縮Base85長` の場合は無圧縮エンコードにフォールバックする（Requirement 3 AC3）
- **Rationale**: 本ユーティリティの主用途（設定ファイル・小〜中規模データのJSON/TOML埋め込み）において実測で最良の結果
- **Trade-offs**: 大容量データにおける `lzma` の優位性を放棄する可能性がある
- **Follow-up**: 大容量データ（数百KB〜MB）での再ベンチマークをResearch Neededとして設計フェーズに繰り越す

## Requirement-to-Asset Map

| Requirement | 必要な技術要素 | 既存資産 | ギャップ区分 |
|---|---|---|---|
| Req1: バイナリエンコード | Base85エンコード | なし（標準ライブラリ `base64.b85encode` で対応可） | Missing（実装要） |
| Req2: デコード・往復整合性 | Base85デコード | なし（標準ライブラリ `base64.b85decode` で対応可） | Missing（実装要） |
| Req3: 高圧縮率エンコーディング | 圧縮（zlib等）＋フォールバック判定＋envelope形式 | なし。ただし比較検証は本ドキュメントで実施済み | Missing（実装要）／envelope形式はResearch Needed |
| Req4: 入力検証・エラーハンドリング | 型チェック＋専用例外 | `time_utility.exceptions` / `time_utility.convert` の実装パターンを流用可 | Constraint（パターン踏襲） |
| Req5: オブジェクトのバイナリ化 | `pickle` によるシリアライズ＋envelope再利用＋セキュリティ注記 | なし（標準ライブラリ `pickle` で対応可） | Missing（実装要）／pickleプロトコルバージョン方針はResearch Needed |
| Req6: 公開API・規約準拠 | サブパッケージ構成、`__init__.py`、`exceptions.py`、テストミラーリング | `logging`/`time_utility` の確立済みパターンを完全流用可 | Constraint（パターン踏襲） |

## Risks & Mitigations
- **Risk**: envelope形式（圧縮有無・アルゴリズム種別・オブジェクト/バイナリ種別の判定情報）の設計を誤ると、Requirement 4 AC3/AC4（不正形式の検出）が正しく機能しない — **Mitigation**: 設計フェーズで固定長ヘッダ（マジックバイト＋バージョン＋フラグ）を明確に定義し、デコード時に検証する
- **Risk**: `pickle` ベースのオブジェクトデコードは任意コード実行のリスクを持つ — **Mitigation**: Requirement 5 AC5の通りdocstringで明記し、Boundary Contextで「信頼できる入力のみ」を前提とする設計判断を`design.md`にも明記する
- **Risk**: 圧縮アルゴリズムの選定が小〜中規模データのベンチマークに基づいており、大容量データでは異なる結果になる可能性 — **Mitigation**: Research Neededとして繰り越し、必要であれば設計フェーズでサイズ閾値による切り替えを検討する

## References
- 標準ライブラリドキュメント: `base64`, `zlib`, `bz2`, `lzma`, `pickle`（いずれもPython 3.11標準ライブラリ、`pyproject.toml` の `requires-python = ">=3.11"` で利用可能）
- 本リポジトリの既存実装: [src/python_util/time_utility/exceptions.py](../../../src/python_util/time_utility/exceptions.py)、[src/python_util/time_utility/convert.py](../../../src/python_util/time_utility/convert.py)、[src/python_util/logging/__init__.py](../../../src/python_util/logging/__init__.py) — 例外設計・公開API集約パターンの参照元

## Research Needed（設計フェーズへの引き継ぎ事項）
- envelopeフォーマットの具体的なバイト配置（マジックバイト、バージョン番号、圧縮フラグ、オブジェクト/バイナリ種別フラグ）の設計
- 大容量データ（数百KB〜MB）における `zlib` vs `lzma` の再評価要否
- `pickle` のプロトコルバージョン方針（`pickle.HIGHEST_PROTOCOL` 固定 or envelopeにバージョンを埋め込むか）
- 圧縮フォールバック判定の閾値（「圧縮後が無圧縮以上」の単純比較で十分か、一定のマージンを設けるか）
