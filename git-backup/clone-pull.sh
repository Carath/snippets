#!/bin/sh

# $1: path to current directory
# $2: git repository URL
# $3: 0: all history fetched, 1: only last commit.
# $4: 1: cleanup and cloning from scratch.

path=$1; url=$2; lastCommit=$3; ignoreCache=$4; currentDir=$PWD
directory=$(basename "$url" .git)
cd "$path"
if [ $? -ne 0 ] || [ -z "$path" ] || [ -z "$directory" ]; then
	exit 1
elif [ "$ignoreCache" = "1" ]; then
	echo "Removing $directory"
	rm -rf "$directory"
fi
if [ -d "$directory" ]; then
	cd "$directory"
	echo "Pulling $url"
	git pull
	cd ../
elif [ ! "$lastCommit" = "1" ]; then
	echo "Cloning $url"
	git clone "$url"
else
	echo "Cloning $url with depth 1"
	git clone "$url" --depth 1
fi
cd "$currentDir"
