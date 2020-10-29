apt update -y 
apt install -y libmariadb-dev-compat libmariadb-dev
apt install -y libssl-dev zlib1g-dev gcc g++ make
apt clean 
rm -rf /var/lib/apt/lists/*
git clone https://github.com/edenhill/librdkafka
cd librdkafka
./configure --prefix=/usr
make
make install
cd ..
rm -rf librdkafka
pip3 install mysqlclient
