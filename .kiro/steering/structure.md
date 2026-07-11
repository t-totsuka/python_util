# プロジェクト構成

## 組織方針

機能ごとにモジュールを分割する、単一パッケージのフラットな構成を想定（src レイアウト）。

## ディレクトリパターン

### パッケージ本体
**場所**: `src/python_util/<subpackage>/`
**用途**: 機能単位のサブパッケージとして分割する。各サブパッケージは `__init__.py` で公開APIを `__all__` に限定してエクスポートし、内部実装は責務ごとにモジュールを分ける（例: `types.py` に値オブジェクト、`exceptions.py` に例外、機能固有の処理をその他のモジュールに配置）
**例**: `src/python_util/logging/`（`factory.py`, `types.py`, `handlers.py`, `config_loader.py`）、`src/python_util/time_utility/`（`clock.py`, `convert.py`, `formatting.py`, `timezones.py`, `exceptions.py`）

### テスト
**場所**: `tests/<subpackage>/`
**用途**: pytest ベースのテストコード。`src/python_util/` の構成をミラーリングし、各ディレクトリに `__init__.py` を置く

## 命名規則

- **ファイル**: snake_case
- **関数・変数**: snake_case
- **クラス**: PascalCase

## インポート方針

パッケージルートからの絶対インポートを基本とする。

```python
from python_util.logging import get_logger
```

## コード組織の原則

- モジュール非公開のヘルパー関数・内部例外は先頭アンダースコアを付ける（例: `_configure_logger`, `_InvalidLoggingConfig`）
- サブパッケージの公開APIは `__init__.py` に集約し、内部モジュールを利用側に直接インポートさせない

---
_2026-07-11: `logging`, `time_utility` の実装を踏まえて同期。サブパッケージ構成と公開APIパターンを実コードから反映。_
