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
- [Sigstore なしで `uv deploy` で TestPyPI にデプロイする最後のバージョンの workflow](#sigstore-なしで-uv-deploy-で-testpypi-にデプロイする最後のバージョンの-workflow)
- [`uv deploy` は PEP740 はまだ駄目なので (2025-09)](#uv-deploy-は-pep740-はまだ駄目なので-2025-09)
- [Sigstore つける前と後の比較](#sigstore-つける前と後の比較)
	- [TestPyPI のパッケージを署名確認する](#testpypi-のパッケージを署名確認する)
- [TestPyPI 版から PyPI 版を作る](#testpypi-版から-pypi-版を作る)
- [あっさり PyPI に deploy できたので署名を確認](#あっさり-pypi-に-deploy-できたので署名を確認)
- [今後ローカルから直接 PyPI/TestPyPI に発行できないようにしたい](#今後ローカルから直接-pypitestpypi-に発行できないようにしたい)

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
# 統合ビルドタスク(lint, format, tests, build, smoke-test を全て実行)
poe build

# または個別に実行
poe check     # ruff linting
poe mypy      # 型チェック
poe test      # pytest実行
poe format    # コードフォーマット
poe lint      # 全てのlinter実行

uv build
# ./dist以下に .tar.gz と .whlができるので
# 中身を確認して(`tar tzvf` と zipinfo)、余計なものがあったら
# pyproject.toml の [tool.uv.build-backend] で調整

# 「パッケージをimportできるか」程度の簡単なテスト(smoke test)
poe smoke-test
# または手動で
uv run --isolated --no-project --refresh --no-cache --with "dist/*.whl" h4-hello -V
uv run --isolated --no-project --refresh --no-cache --with "dist/*.tar.gz" h4-hello --help
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
# pyproject.tomlのバージョンを手動で更新(例: 0.1.12b2)
git commit -am 'test-0.1.12b2'
git tag -a 'test-0.1.12b2' -m 'test-0.1.12b2'
git push
git push --tags
# GitHub Actionsが自動的にTestPyPIにデプロイ
```

または手動でローカルからデプロイ:

```sh
rm dist/* -f
uv build
poe testpypi  # .envにTEST_PYPI_TOKENが必要
```

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
   右上のメニューから「Your projects (自分のプロジェクト)」をクリック (ここからが[既存のプロジェクトの場合](#既存のプロジェクトの場合)と違う)
3. **「Publishing」メニューを開く**\
   左サイドバーの「Publishing」をクリックします
4. **"Trusted Publisher Management"に着いたので Trusted Publisher を追加**\
   GitHub タブを選択すると、必要な入力フィールドが表示されます

### GitHub Actions 用の各フィールド

参照: [warehouse/docs/user/trusted-publishers/adding-a-publisher.md at main · pypi/warehouse · GitHub](https://github.com/pypi/warehouse/blob/main/docs/user/trusted-publishers/adding-a-publisher.md)

#### PyPI Project Name (新プロジェクトの場合のみ存在する)

このパブリッシャーを使った時に
PyPI/TestPyPI で新しく作成されるプロジェクト名

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

## Sigstore なしで `uv deploy` で TestPyPI にデプロイする最後のバージョンの workflow

[h4-hello/.github/workflows/publish-testpypi.yml at c286e1706a4a0f6c5a52a11da62d1fafa47ddc18 · heiwa4126/h4-hello](https://github.com/heiwa4126/h4-hello/blob/c286e1706a4a0f6c5a52a11da62d1fafa47ddc18/.github/workflows/publish-testpypi.yml)

`ex*` というタグ付けると TestPyPI にデプロイする仕様。

## `uv deploy` は PEP740 はまだ駄目なので (2025-09)

update 2025-10: uv v0.9 でサポートされるといいなあ、と思ったけどまだダメみたい。まあ難しいのはわかる

- [uv publish: create attestations · Issue #15618 · astral-sh/uv](https://github.com/astral-sh/uv/issues/15618)

[pypa/gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish)
に入れ替える。

...あっさりできた。GitHub Actions のログがなんかえらいことに。
Docker イメージ `ghcr.io/pypa/gh-action-pypi-publish:release-v1` で実行されるらしい。

コンテナは GitHub Container Registry (GHCR) にあるこれ [Package gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish/pkgs/container/gh-action-pypi-publish)

## Sigstore つける前と後の比較

**前:**

- [h4-hello v0.1.3 · TestPyPI](https://test.pypi.org/project/h4-hello/0.1.3/) - Verified マークは過去のにも着くなあ..
- [h4_hello-0.1.0-py3-none-any.whl · TestPyPI](https://test.pypi.org/project/h4-hello/0.1.0/#h4_hello-0.1.0-py3-none-any.whl)

**後:**

- [h4-hello v0.1.4 · TestPyPI](https://test.pypi.org/project/h4-hello/0.1.4/)
- [h4_hello-0.1.4-py3-none-any.whl · TestPyPI](https://test.pypi.org/project/h4-hello/#h4_hello-0.1.4-py3-none-any.whl)

どうやら **"Verified details" の横のチェックマークは Sigstore 署名とは無関係に付くみたい**。(2025-09)

- [Security Model and Considerations - PyPI Docs](https://docs.pypi.org/attestations/security-model/)
- [Project Metadata - PyPI Docs](https://docs.pypi.org/project_metadata/#verified-details)

そのパッケージが Sigstore 署名されているかを確認するには、個別の tar.gz や whl のページに行って確認するしかない。

### TestPyPI のパッケージを署名確認する

公式のこれで [pypi-attestations · PyPI](https://pypi.org/project/pypi-attestations/)

TestPyPI だと URL で指定できない(本体も attestation も)。
ファイルをダウンロードする。

```sh
pip download --index-url https://test.pypi.org/simple/ h4-hello==0.1.4

curl -H "Accept: application/vnd.pypi.integrity.v1+json" \
  -o h4_hello-0.1.4-py3-none-any.whl.provenance.json \
  "https://test.pypi.org/integrity/h4-hello/0.1.4/h4_hello-0.1.4-py3-none-any.whl/provenance"
## 参考: https://docs.pypi.org/api/integrity/#get-provenance-for-file

pypi-attestations verify pypi \
  --repository https://github.com/heiwa4126/h4-hello \
  --provenance-file ./h4_hello-0.1.4-py3-none-any.whl.provenance.json \
  ./h4_hello-0.1.4-py3-none-any.whl

## -> OK: h4_hello-0.1.4-py3-none-any.whl
```

## TestPyPI 版から PyPI 版を作る

[publish-pypi.yml](.github/workflows/publish-pypi.yml)

- pypa/gh-action-pypi-publish を semver にし、pinact で pinned した
- TestPyPI と PyPI で共通の部分を別ファイルにした ([build-package.yml](.github/workflows/build-package.yml))
- PyPI 版は v9.9.9 式の semver 風タグで発動
- PyPI で Trusted publishing の設定した。[以上をまとめると](#以上をまとめると)を参照

## あっさり PyPI に deploy できたので署名を確認

[h4-hello v0.1.8 · PyPI](https://pypi.org/project/h4-hello/0.1.8/)

pypi-attestations で署名を確認する。

```sh
pypi-attestations verify pypi \
  --repository https://github.com/heiwa4126/h4-hello \
  pypi:h4_hello-0.1.8-py3-none-any.whl
## -> OK: h4_hello-0.1.8-py3-none-any.whl

pypi-attestations verify pypi \
  --repository https://github.com/heiwa4126/h4-hello \
  pypi:h4_hello-0.1.8.tar.gz
## -> OK: h4_hello-0.1.8.tar.gz
```

TestPyPI の時と比較してずーっと楽だなあ。

# 修正(2025-09-24)

TestPyPI のワークフロー([publish-testpypi.yml](.github/workflows/publish-testpypi.yml))で、タグを"ex*" から "test-*"にした。

手順はこんな感じ

```sh
git commit -am 'v0.1.11'
git tag 'test-0.1.11' -m ''
git push
git push --tags
# GitHub Actions と TestPyPI 確認
git tag 'v0.1.11' -m ''
git push --tags
# GitHub Actions と PyPI 確認
```

発行の workflow の実行ができるのはオーナーのみにした
(`if: github.repository_owner == github.actor` のところ)

あとセキュリティ関係で GitHub の設定を変更

Settings → Branches → Add rule:

- ☑️ Require signed commits (署名されたコミットを要求)
- ☑️ Restrict pushes that create files (これはきつすぎ.新しいファイルを作成するプッシュを制限する)

Settings → Environments → testpypi/pypi:

- ☑️ Required reviewers (自分を追加)
- ☑️ Wait timer (必要に応じて)

## 今後ローカルから直接 PyPI/TestPyPI に発行できないようにしたい

んだけど npmjs みたいに簡単な切り替えスイッチが無い。

まず 2024 年頭から 2FA 必須になってるのでこれはクリア
[2FA Required for PyPI - The Python Package Index Blog](https://blog.pypi.org/posts/2024-01-01-2fa-enforced/)

あとは `~/.pypirc` から pipy/testpypi のトークンを消す(twine)。
場合によっては AWS の codeartifact なんかに出してる可能性があるので、それは消さないように注意

`uv publish` は `~/.config/uv/config.toml` を確認。
