#!/bin/bash

ipt="/sbin/iptables"

MapPort="222222"
Sshport="22"
WebPort="80,443"
net1="91.191.183.0/24"
net2="185.141.237.0/24"
net3="185.165.120.0/24"
InputPort="9000:10000"
ip1="8.9.10.11"
ip2="12.13.14.15"


$ipt -X -F
$ipt -t nat -X -F
