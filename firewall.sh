#!/bin/bash

echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward
ipt="/sbin/iptables"

iface="enp0s3"
mapport="22222"
sshport="22"
webport="80,443"
net1="91.191.183.0/24"
net2="185.141.237.0/24"
net3="185.165.120.0/24"
inputport="9000:10000"
ip1="8.9.10.11"
ip2="12.13.14.15"
maxHost="192.168.21.49"


$ipt -X
$ipt -F

$ipt -t nat -X 
$ipt -t nat -F

#Default Policy
$ipt -P FORWARD DROP
$ipt -P OUTPUT ACCEPT
$ipt -P INPUT DROP

#INPUT
#back trafik
$ipt -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

#local
$ipt -A INPUT -i lo -j ACCEPT 
$ipt -A OUTPUT -o lo -j ACCEPT

#SSH
$ipt -A INPUT -i $iface -s $maxHost -p tcp --dport $sshport -j ACCEPT

#WEB
$ipt -A INPUT -i $iface -s $net1,$net2,$net3 -p tcp -m multiport --dport $webport -j ACCEPT

#APP
$ipt -A INPUT -i $iface -s $ip1,$ip2 -p tcp -m multiport --dport $inputport -j ACCEPT

#Ping
$ipt -A INPUT -p icmp --icmp-type echo-request -j ACCEPT

#PREROUTING
$ipt -t nat -A PREROUTING -p tcp --dport $mapport -j REDIRECT --to-port $sshport

$ipt -L
#$ipt -t nat -L
