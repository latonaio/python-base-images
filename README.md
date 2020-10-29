# python-base-images
AIONのマイクロサービスで利用するpythonライブラリ及びpython版のベースイメージです。

## 動作環境
### 前提条件
動作には以下の環境であることを前提とします。
* Ubuntu OS
* ARM CPU搭載のデバイス

## セットアップ
```
git clone https://github.com/latonaio/python-base-images.git
cd python-base-images
make docker-build-pylib-lite
make docker-build-l4t
```

## Notes
aion-coreとprotoファイルを共有しているので、aion-core側でprotoファイルを変更した場合は変更内容を適用してください。

