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
- [GitHub Actions でビルドとパブリッシュ (uv 版)](#github-actions-でビルドとパブリッシュ-uv-版)
- [PyPI(testPyPI)で "Trusted Publisher Management" のページまで行く方法](#pypitestpypiで-trusted-publisher-management-のページまで行く方法)
	- [GitHub Actions 用の各フィールド](#github-actions-用の各フィールド)
		- [Owner (=リポジトリの所有者)](#owner-リポジトリの所有者)
		- [Repository name (=リポジトリ名)](#repository-name-リポジトリ名)
		- [Workflow name(=ワークフローファイルのパス)](#workflow-nameワークフローファイルのパス)
		- [Environment (任意)](#environment-任意)
		- [以上をまとめると](#以上をまとめると)
- [`uv deploy` は PEP740 はまだ駄目 (2025-09)](#uv-deploy-は-pep740-はまだ駄目-2025-09)

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

0. TestPyPI にアカウント作成\
   https://test.pypi.org で PyPI とは別のアカウントを作成します
1. 2 段階認証を有効化\
   アカウント設定から 2FA を設定(Google Authenticator など)
2. API トークンを発行
   - TestPyPI の右上メニュー → Account Settings → API tokens →「Add API token」
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

## GitHub Actions でビルドとパブリッシュ (uv 版)

- [Publishing to PyPI - Using uv in GitHub Actions | uv](https://docs.astral.sh/uv/guides/integration/github/#publishing-to-pypi)
- [Commands | uv build](https://docs.astral.sh/uv/reference/cli/#uv-build)
- [Commands | uv publish](https://docs.astral.sh/uv/reference/cli/#uv-publish)
- [Adding a Trusted Publisher to an Existing PyPI Project - PyPI Docs](https://docs.pypi.org/trusted-publishers/adding-a-publisher/)
- [Publishing with a Trusted Publisher - PyPI Docs](https://docs.pypi.org/trusted-publishers/using-a-publisher/)
- [Trusted publishing support for GitHub Actions + TestPyPI via \`uv publish\` · Issue #8584 · astral-sh/uv](https://github.com/astral-sh/uv/issues/8584)

## PyPI(testPyPI)で "Trusted Publisher Management" のページまで行く方法

(2025-09)

1. **PyPI(testPyPI)にログイン**\
   <https://pypi.org> (<https://test.pypi.org>) にアクセスし、アカウントでログインします
2. **対象プロジェクトを選択**\
   右上のメニューから「Your projects (自分のプロジェクト)」をクリックし、設定したいプロジェクトを選びます
3. **「Manage」ページへ移動**\
   プロジェクト一覧で対象プロジェクトの「Manage (管理)」ボタンをクリック
4. **「Publishing」メニューを開く**\
   左サイドバーの「Publishing」をクリックします
5. **"Trusted Publisher Management"に着いたので Trusted Publisher を追加**\
   GitHub タブを選択すると、必要な入力フィールドが表示されます

### GitHub Actions 用の各フィールド

参照: [warehouse/docs/user/trusted-publishers/adding-a-publisher.md at main · pypi/warehouse · GitHub](https://github.com/pypi/warehouse/blob/main/docs/user/trusted-publishers/adding-a-publisher.md)

#### Owner (=リポジトリの所有者)

**意味:** GitHub 上の組織またはユーザー名(リポジトリの最初の要素)。

例: `https://github.com/octo-org/sampleproject` の場合、
Owner = octo-org

**注意:**

- チーム名や表示名ではなく、オーナーのハンドル (org/ユーザー名)を入力します。
- フォークではなく本家の所有者を指定してください (PyPI が信頼するのは指定オーナー配下のワークフローです)
- リポジトリを別オーナーへ Transfer した場合は、この Owner も更新が必要です

#### Repository name (=リポジトリ名)

**例:** `octo-org/sampleproject` の `sampleproject` に相当

#### Workflow name(=ワークフローファイルのパス)

**例:** `.github/workflows/example.yml` だったら `example.yml` を指定。

#### Environment (任意)

GitHub Actions の Environment 名 (例:testpypi)。
PyPI の UI では任意ですが、セキュリティと運用上の理由で利用が強く推奨されています。

#### 以上をまとめると

[publish-testpypi.yml](.github/workflows/publish-testpypi.yml) の場合は

- Owner: heiwa4126
- Repository name: h4-hello
- Workflow name: publish-testpypi.yml
- Environment: testpypi

## `uv deploy` は PEP740 はまだ駄目 (2025-09)

- [uv publish: create attestations · Issue #15618 · astral-sh/uv](https://github.com/astral-sh/uv/issues/15618)

`pypa/gh-action-pypi-publish`を使う。
