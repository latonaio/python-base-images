# python-base-images
AIONのマイクロサービスで利用するpythonライブラリ及びpython版のベースイメージです。

## セットアップ
```
git clone https://github.com/latonaio/python-base-images.git
cd python-base-images
make docker-build-pylib-lite
make docker-build-l4t
```

## Notes
aion-coreとprotoファイルを共有しているので、aion-core側でprotoファイルを変更した場合は変更内容を適用してください。

