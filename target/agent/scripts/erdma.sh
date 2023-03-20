#!/bin/sh
function hasERDMA() {
	ibv_devinfo
	# there is ERDMA device
	if [ $? == 0 ]; then
		# check if os support tcp2smc
		sysctl -q net.smc.tcp2smc
		#support
		if [ $? == 0 ]; then
			return 0
		fi
	fi
	return -1
} > /dev/null 2>&1

function isERDMA() {
	ret=`sysctl -q net.smc.tcp2smc | awk -F= '{print $2}' | xargs`
	if [ x"$ret" == x1 ]; then
		return 0
	fi
	return -1
} > /dev/null 2>&1

function toggleERDMA() {
	isERDMA

	current=$( [ $? == 0 ] && echo on || echo off )
	target=$(echo $1 | tr '[:upper:]' '[:lower:]')

	# already set
	if [ x"$target" == x"$current" ]; then
		exit 0
	fi
	if [ x"$target" == x'on' ]; then
		modprobe erdma
		modprobe smc
		sysctl -w net.smc.tcp2smc=1;
		sysctl -w net.smc.net.smc.limit_handshake=1;
	else
		sysctl -w net.smc.tcp2smc=0;
		sysctl -w net.smc.net.smc.limit_handshake=0;
	fi

	exit 0

} > /dev/null 2>&1

function="$1"
shift
${function} $@
