#!/bin/sh

tar xzf Net-WebSocket-Server-0.003004.tar.gz
cd Net-WebSocket-Server-0.003004/
mkdir websocket_perl
perl Makefile.PL PREFIX=./websocket_perl/
make
make install
mv websocket_perl/ ../
cd ../
rm -rf Net-WebSocket-Server-0.003004*
echo "------------------------------------------------------------------"
echo "Installation of perl dependencies are completed."
echo "------------------------------------------------------------------"