TYPE=$1
IHOME=`pwd`
UI_URL="https://releases.hashicorp.com/consul/0.7.5/consul_0.7.5_web_ui.zip"
CONSUL_URL="https://releases.hashicorp.com/consul/0.7.5/consul_0.7.5_linux_amd64.zip"
CONSUL_HOME="/var/consul"
if [ "$TYPE" = "gen" ]; then
        keyvalue=`/usr/local/bin/consul keygen`
        echo $keyvalue > $IHOME/shared_encrypt
        echo "Shared key generated"
        exit
fi
# Download dependencies
apt-get -q update
apt-get -y install unzip
mkdir -p $CONSUL_HOME/dist
cd $CONSUL_HOME/dist
wget $UI_URL
unzip *.zip
rm *.zip
cd /usr/local/bin
wget $CONSUL_URL
unzip *.zip
rm *.zip


useradd -d $CONSUL_HOME consul
mkdir -p /etc/consul.d/{bootstrap,server,client}
chown -R consul:consul /var/consul

if [ "$TYPE" = "server" ]; then
        cp $IHOME/consul.server.conf /etc/init/consul.conf
        printf "{\n\"bootstrap\": false,\n\"server\": true,\n\"datacenter\": \"mydc\",\n\"da
ta_dir\": \"/var/consul\",\n\"ui_dir\": \"/var/consul/dist\",\n\"encrypt\": \"$keyvalue\",\n
\"log_level\": \"INFO\",\n\"enable_syslog\": true,\n\"start_join\": [\"162.243.94.138\",\"16
2.243.95.96\"]\n}" > /etc/consul.d/bootstrap/config.json
        cp /etc/consul.d/bootstrap/config.json /etc/consul.d/server
        #printf "consul agent -data-dir=/var/consul -config-dir=/etc/consul.d/server -bind=1
62.243.96.42" > /usr/local/bin/start_con
elif [ "$TYPE" = "client" ]; then
        cp $IHOME/consul.client.conf /etc/init/consul.conf
        printf "{\n\"server\": false,\n\"datacenter\": \"mydc\",\n\"data_dir\": \"/var/consu
l\",\n\"ui_dir\": \"/var/consul/dist\",\n\"encrypt\": \"$keyvalue\",\n\"log_level\": \"INFO\
",\n\"enable_syslog\": true,\n\"start_join\": [\"162.243.94.138\",\"162.243.95.96\"]\n}" > /
etc/consul.d/bootstrap/config.json
        cp /etc/consul.d/bootstrap/config.json /etc/consul.d/client
fi

echo "To start consul, run: service consul start"
