# h4-hello

**Table of Contents**

- [Installation](#installation)
- [License](#license)
- [---ここまではテンプレ、以下メモ---](#---ここまではテンプレ以下メモ---)
- [これは何か](#これは何か)
- [参考](#参考)
	- [ビルド関連](#ビルド関連)
	- [パブリッシュ関連](#パブリッシュ関連)
- [testPyPI のトークン取得](#testpypi-のトークン取得)
- [testPyPI への手動パブリッシュ](#testpypi-への手動パブリッシュ)

## Installation

```console
pip install h4-hello
```

## License

`h4-hello` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## ---ここまではテンプレ、以下メモ---

(本当は別ページにする)

## これは何か

練習プロジェクト

0. uv でパッケージを作る(build backend も uv)
1. testPyPI で公開する(手動)。publish も `uv publish`で。twine を使わない
2. GitHub Actions 経由で、testPyPI に公開する
   - その過程で suzuki-shunsuke/pinact, rhysd/actionlint, nektos/act などを使う (あと aqua)
3. Sigstore 署名をつけて testPyPI に公開する

## 参考

### ビルド関連

- [Building and publishing a package | uv](https://docs.astral.sh/uv/guides/package/)
- [Build backend | uv](https://docs.astral.sh/uv/concepts/build-backend/)
- [build\-backend](https://docs.astral.sh/uv/reference/settings/#build-backend)

### パブリッシュ関連

- [Publishing your package](https://docs.astral.sh/uv/guides/package/#publishing-your-package)

## testPyPI のトークン取得

0. TestPyPI にアカウント作成  
   https://test.pypi.org で PyPI とは別のアカウントを作成します
1. 2 段階認証を有効化  
   アカウント設定から 2FA を設定(Google Authenticator など)
2. API トークンを発行
   - TestPyPI の右上メニュー → Account Settings → API tokens → 「Add API token」
   - トークン名を入力し、Create token をクリック
   - **表示されたトークンは一度しか表示されないので必ずコピーして保存**
     　ここでは .env に保存

## testPyPI への手動パブリッシュ

例:

```sh
uv version --bump patch  # このへんはアレンジ
git commit -am 'v9.9.9'  # 上で表示されたやつ
git tag -a 'v9.9.9' -m 'v9.9.9'
rm dist/* -f
uv build
poe testpypi
```

なんかめんどくさいね。自動化する。

パブリッシュできたら別環境でテストする。

```sh
mkdir tmp1 && cd $!
uv init --python 3.12
uv sync
uv add --index-url https://test.pypi.org/simple/ h4-hello
. .venv/bin/activate
h4-hello
# -> hello!
```
