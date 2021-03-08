# python-base-images
AIONのマイクロサービスで利用するpythonライブラリ及びpython版のベースイメージです。  
Pythonアプリケーション用のDockerイメージを構築する際には、既存のイメージの上に構築します。  
本イメージには、アプリケーションの実行に必要なすべてのもの（コード、バイナリ、ランタイム、およびその他の必要なファイルオブジェクト）が含まれています。  

# 動作環境
## 前提条件
動作には以下の環境であることを前提とします。 
AIONのプラットフォーム上での動作を前提としています。 使用する際は、事前にAIONの動作環境を用意してください。  
-　ARM CPU搭載のデバイス(NVIDIA Jetson シリーズ等)  
-　OS: Linux Ubuntu OS  
-　CPU: ARM64  
-　Kubernetes  
-　AION のリソース  
  
  
`python-base-images` には以下のものが含まれています。  
```
    build-essential \
    make \
    cmake \
    curl \
    git \
    g++ \
    gcc \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgtk-3-dev \
    libssl-dev \
    libgtk-3-dev \
    libcurl4-openssl-dev \
    libgirepository1.0-dev \
    libmysqlclient-dev \
    zlib1g-dev \
    python-pip \
    python3-pip \
    python3-dev \
    tzdata \
    grpc \
    redis \
    mongo-db \
    mysql \
    ffmpeg \
```
  
また、`python-base-images` に含まれるクライアントライブラリには、以下のようなものが含まれます。  
```
kanban：
    kanbanサーバーへの問い合わせ
    kanbanサーバーへの書き込み
    redisクライアントの生成
logger：
    k8sにログを吐き出せる
    k8s対応を行ったデバッグログのラッパー
microservice：
    内部で実装しているdecoratorを実装している。
    decoratorを呼び出したマイクロサービスをkanbanクライアント化する
mongo：
    mongoクライアントの生成
    mongoへの問い合わせ
    mongoへのデータ書き込み
mysql：
    mysqlクライアントの生成
    mysqlへの問い合わせ
    mysqlへのデータ書き込み
proto：
    自動生成されたgrpcのコードが入っている
    kanbanライブラリでのgrpcに使用
```

# セットアップ  
利用するマイクロサービスに記載されている必要な`python-base-image` をGit cloneします。  
`python-base-images` の一覧は、本リポジトリ内の `Makefile` ディレクトリにあります。  
  
```
git clone https://github.com/latonaio/python-base-images.git
cd python-base-images
make docker-build-pylib-lite
make docker-build-l4t
```
    
# Notes
aion-coreとprotoファイルを共有しているので、aion-core側でprotoファイルを変更した場合は変更内容を適用してください。  

