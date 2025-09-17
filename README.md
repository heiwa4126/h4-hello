# h4-hello

0. uv でパッケージを作る(build backend も uv)
1. testPyPI で公開する
2. GitHub Actions 経由で、testPyPI に公開する
   - その過程で suzuki-shunsuke/pinact, rhysd/actionlint, nektos/act などを使う (あと aqua)
3. Sigstore 署名をつけて testPyPI に公開する

## 参考

- [Building and publishing a package | uv](https://docs.astral.sh/uv/guides/package/)
- [Build backend | uv](https://docs.astral.sh/uv/concepts/build-backend/)
- [build\-backend](https://docs.astral.sh/uv/reference/settings/#build-backend)
