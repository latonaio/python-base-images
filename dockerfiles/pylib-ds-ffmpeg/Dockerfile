FROM nvcr.io/nvidia/deepstream-l4t:4.0.2-19.12-base

# Install Dependencies
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections
RUN apt-get update -y && apt-get upgrade -y && apt-get install -y \
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
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

ENV PATH=/usr/local/cuda-10.0/bin:$PATH \
    LD_LIBRARY_PATH=/usr/local/cuda-10.0/lib64:$LD_LIBRARY_PATH

RUN git clone https://github.com/FFmpeg/nv-codec-headers -b n10.0.26.0 && \
    cd ./nv-codec-headers && \
    make -j && \
    sudo make install -j && \
    cd .. && rm -rf nv-codec-headers

RUN git clone https://git.ffmpeg.org/ffmpeg.git && \
    cd ./ffmpeg && \
    git checkout f95dac666caea27c && \
    ./configure \
    --enable-nonfree \
    --disable-shared \
    --enable-nvenc \
    --enable-cuda \
    --enable-cuvid \
    --extra-cflags=-I/usr/local/cuda/include \
    --extra-cflags=-I/usr/local/include \
    --extra-ldflags=-L/usr/local/cuda/lib64 && \
    make -j && make install && \
    cd .. && rm -rf ffmpeg

# Dependencies about mysqlclient
RUN git clone https://github.com/edenhill/librdkafka && \
    cd librdkafka && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd ../ && \
    rm -rf librdkafka

ADD dist .
ENV GRPC_PYTHON_BUILD_EXT_COMPILER_JOBS 8
RUN python3 -m pip install ./aion-*.tar.gz