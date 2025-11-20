# Plan: Goodbye機能の追加

現在の`hello()`関数と同様のパターンで`goodbye()`関数を実装し、CLIから`-g|--goodbye`オプションで呼び出せるようにします。既存のシンプルな設計を維持しつつ、後方互換性を保ちます。

## Steps
1. `src/h4_hello/_core.py`に`goodbye()`関数を追加（`hello()`と同じパターンで`"Goodbye!"`を返す）
2. `src/h4_hello/__init__.py`の`__all__`に`"goodbye"`を追加してエクスポート
3. `src/h4_hello/_core_test.py`に`test_goodbye()`を追加（戻り値が`"Goodbye!"`であることを検証）
4. `src/h4_hello/__main__.py`に`-g|--goodbye`オプションを追加（指定時は`goodbye()`、未指定時は従来通り`hello()`を表示）
5. `examples/ex1.py`に`goodbye()`の使用例を追加

## Further Considerations
1. **後方互換性**: `-g|--goodbye`なしの場合は従来通り`Hello!`を表示するため、既存の動作を維持
2. **相互排他性**: `-V`と`-g`は同時指定可能か？現在`-V`は`action="version"`で即終了するため問題なし
