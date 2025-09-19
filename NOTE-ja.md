# h4-hello メモ

**目次**

- [これは何か](#これは何か)
- [作った手順](#作った手順)
- [参考リンク](#参考リンク)
	- [ビルド関連](#ビルド関連)
	- [パブリッシュ関連](#パブリッシュ関連)
- [ビルドとテスト](#ビルドとテスト)
- [testPyPI のトークン取得](#testpypi-のトークン取得)
- [TestPyPI への手動パブリッシュ](#testpypi-への手動パブリッシュ)
- [GitHub Actions でビルドとパブリッシュ (uv 版)](#github-actions-でビルドとパブリッシュ-uv-版)
- [PyPI(testPyPI)で "Trusted Publisher Management" のページまで行く方法](#pypitestpypiで-trusted-publisher-management-のページまで行く方法)
	- [既存のプロジェクトの場合](#既存のプロジェクトの場合)
	- [新プロジェクトの場合](#新プロジェクトの場合)
	- [GitHub Actions 用の各フィールド](#github-actions-用の各フィールド)
		- [PyPI Project Name (新プロジェクトの場合のみ存在する)](#pypi-project-name-新プロジェクトの場合のみ存在する)
		- [Owner (リポジトリの所有者)](#owner-リポジトリの所有者)
		- [Repository name (リポジトリ名)](#repository-name-リポジトリ名)
		- [Workflow name(ワークフローファイルのパス)](#workflow-nameワークフローファイルのパス)
		- [Environment (任意)](#environment-任意)
		- [以上をまとめると](#以上をまとめると)
- [`uv deploy` は PEP740 はまだ駄目 (2025-09)](#uv-deploy-は-pep740-はまだ駄目-2025-09)

## これは何か

uv で作った Python のプロジェクトを PEP740 の署名付きで PyPI に公開する練習プロジェクト。中身は "Hello!"を返す hello()関数だけ。

## 作った手順

1. uv でパッケージを作る (build backend も uv)
1. TestPyPI で公開する(手動)。publish も `uv publish`で。twine は使わない
   - 「すべてのプロジェクト」スコープのトークンを使う
1. GitHub Actions 経由で、testPyPI に公開する。
   - TestPyPI 上の既存プロジェクトに対して Trusted publishing 設定する
   - この段階では workflow でも `uv publish` を使う
   - suzuki-shunsuke/pinact, rhysd/actionlint, nektos/act などを使う (あと aquaproj/aqua)
1. Sigstore 署名をつけて testPyPI に公開する
   - workflow を `uv publish` から `pypa/gh-action-pypi-publish` に変更
1. Sigstore 署名をつけて PyPI に公開する
   - PyPI 上で新規プロジェクトとして Trusted publishing を設定
1. ドキュメントをまとめる

## 参考リンク

### ビルド関連

- [Building and publishing a package | uv](https://docs.astral.sh/uv/guides/package/)
- [Build backend | uv](https://docs.astral.sh/uv/concepts/build-backend/)
- [build\-backend](https://docs.astral.sh/uv/reference/settings/#build-backend)

### パブリッシュ関連

- [Publishing your package](https://docs.astral.sh/uv/guides/package/#publishing-your-package)

## ビルドとテスト

```sh
poe check
poe mypy
poe tests

uv build
# ./dist以下に .tar.gz と .whlができるので
# 中身を確認して(`tar tzvf` と zipinfo)、余計なものがあったら
# pyproject.toml の [tool.uv.build-backend] で調整

# 「パッケージをimportできるか」程度の簡単なテスト
uv run --isolated --no-project --with "dist/*.whl" src/h4_hello/main.py
uv run --isolated --no-project --with "dist/*.tar.gz" src/h4_hello/main.py
```

## testPyPI のトークン取得

0. TestPyPI にアカウント作成\
   https://test.pypi.org で PyPI とは別のアカウントを作成します
1. 2 段階認証を有効化\
   アカウント設定から 2FA を設定(Google Authenticator など)
2. API トークンを発行
   - TestPyPI の右上メニュー → Account Settings → API tokens →「Add API token」
   - トークン名を入力し、Create token をクリック
   - **表示されたトークンは一度しか表示されないので必ずコピーして保存**
     ここでは `.env` に保存
     ```sh
     cp .env.template .env
     vim .env # コピペする
     ```

## TestPyPI への手動パブリッシュ

例:

```sh
uv version --bump patch  # このへんはアレンジ
git commit -am 'v9.9.9'  # 上で表示されたやつ
git tag -a 'v9.9.9' -m 'v9.9.9'
rm dist/* -f
uv build
poe testpypi
```

TODO: なんかめんどくさいね。自動化する。

TestPyPI にパブリッシュできたら別環境でテストする。

```sh
cd ~
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

(2025-09) UI よく変わる

### 既存のプロジェクトの場合

すでに PyPI/TestPyPI 上にプロジェクトがあるとき。

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

### 新プロジェクトの場合

PyPI/TestPyPI には、「空のプロジェクトを作る」機能はない。でも Trusted Publishing の設定はできる。

1. **PyPI(testPyPI)にログイン**\
   <https://pypi.org> (<https://test.pypi.org>) にアクセスし、アカウントでログインします
2. **対象プロジェクトを選択**\
   右上のメニューから「Your projects (自分のプロジェクト)」をクリックし、設定したいプロジェクトを選びます
3. **「Publishing」メニューを開く**\
   左サイドバーの「Publishing」をクリックします
4. **"Trusted Publisher Management"に着いたので Trusted Publisher を追加**\
   GitHub タブを選択すると、必要な入力フィールドが表示されます

### GitHub Actions 用の各フィールド

参照: [warehouse/docs/user/trusted-publishers/adding-a-publisher.md at main · pypi/warehouse · GitHub](https://github.com/pypi/warehouse/blob/main/docs/user/trusted-publishers/adding-a-publisher.md)

#### PyPI Project Name (新プロジェクトの場合のみ存在する)

このパブリッシャーを使用すると PyPI/TestPyPI で作成されるプロジェクト名

#### Owner (リポジトリの所有者)

**意味:** GitHub 上の組織またはユーザー名(リポジトリの最初の要素)。

例: `https://github.com/octo-org/sampleproject` の場合、
Owner = octo-org

**注意:**

- チーム名や表示名ではなく、オーナーのハンドル (org/ユーザー名)を入力します。
- フォークではなく本家の所有者を指定してください (PyPI が信頼するのは指定オーナー配下のワークフローです)
- リポジトリを別オーナーへ Transfer した場合は、この Owner も更新が必要です

#### Repository name (リポジトリ名)

**例:** `octo-org/sampleproject` の `sampleproject` に相当

#### Workflow name(ワークフローファイルのパス)

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

[publish-pypi.yml](.github/workflows/publish-pypi.yml) の場合は (こっちは新規プロジェクト)

- PyPI Project Name: h4-hello
- Owner: heiwa4126
- Repository name: h4-hello
- Workflow name: publish-pypi.yml
- Environment: pypi

## `uv deploy` は PEP740 はまだ駄目 (2025-09)

- [uv publish: create attestations · Issue #15618 · astral-sh/uv](https://github.com/astral-sh/uv/issues/15618)

[pypa/gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish)
に入れ替える。

...あっさりできた。GitHub Actions のログがなんかえらいことに。
Docker イメージ `ghcr.io/pypa/gh-action-pypi-publish:release-v1` で実行されるらしい。
GitHub Container Registry (GHCR)
これ [Package gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish/pkgs/container/gh-action-pypi-publish)

比較

前:

- [h4-hello v0.1.3 · TestPyPI](https://test.pypi.org/project/h4-hello/0.1.3/) - Verified マークは過去のにも着くなあ..
- [h4_hello-0.1.0-py3-none-any.whl · TestPyPI](https://test.pypi.org/project/h4-hello/0.1.0/#h4_hello-0.1.0-py3-none-any.whl)

後:

- [h4-hello v0.1.4 · TestPyPI](https://test.pypi.org/project/h4-hello/0.1.4/)
- [h4_hello-0.1.4-py3-none-any.whl · TestPyPI](https://test.pypi.org/project/h4-hello/#h4_hello-0.1.4-py3-none-any.whl)

どうやら "Verified details" の横のチェックマークは Sigstore 署名とは無関係に付くみたい。

そのパッケージが Sigstore 署名されているかを確認するには、個別の tgz や whl のページに行って確認するしかない
