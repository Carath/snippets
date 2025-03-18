#!/bin/sh

#############################################
# Building an image, and running a container
# from it. Run this script as sudoer.
#############################################

DEFAULT_SETTINGS_FILE=app.env

# Choice of settings file:
if [ $# -ge 1 ]; then
	FILE=$1
elif [ -e "$DEFAULT_SETTINGS_FILE" ]; then
	FILE=$DEFAULT_SETTINGS_FILE
else
	printf "\n-> %s %s\n\n" "No custom settings file given, and default file" \
		"'$DEFAULT_SETTINGS_FILE' not found."
	exit 1
fi

printf "\n-> Using settings from: '$FILE'\n"

# Loading the settings. Exits on failure:
. ./$FILE

# Checking if necessary files, e.g build results are present:
if [ "$TARGET" = "" ]; then
	printf "\n-> Target check disabled.\n"
elif [ ! -d "$TARGET" ]; then # no directory matching TARGET.
	if [ ! -e "$TARGET" ]; then # no file matching TARGET.
		printf "\n-> Not running the container: missing '$TARGET' resource.\n\n"
		exit 1
	fi
elif [ ! -n "$(ls -A $TARGET)" ]; then
	printf "\n-> Not running the container: empty directory '$TARGET'.\n\n"
	exit 1
fi

ERROR_MESSAGE="\n-> Are you sure docker is installed, and this script is run as sudoer?\n\n"

PREVIOUS_INSTANCES=$(docker ps -aq --filter name=$NAME) || { printf "$ERROR_MESSAGE"; exit 1; }

if [ ! "$PREVIOUS_INSTANCES" = "" ]; then # do not check the version!
	printf "\n-> Removing any previous instance of the container:\n\n"
	docker rm -f $PREVIOUS_INSTANCES
fi

printf "\n-> Building the new image:\n\n"
docker build -t $NAME:$VERSION .

DANGLING_IMAGES=$(docker images -aq --filter "dangling=true" --no-trunc)

if [ $ENABLE_DANGLING_CLEANING = true -a "$DANGLING_IMAGES" != "" ]; then
	printf "\n-> Removing dangling images:\n\n"
	docker rmi -f $DANGLING_IMAGES
fi

printf "\n-> Running the new container:\n\n"
docker run \
	$LIFETIME \
	$DETACHED \
	$INTERACTIVE \
	-p $HOST_PORT:$CONTAINER_PORT \
	--name $NAME \
	$NAME:$VERSION

if [ ''$DETACHED = -d ]; then
	CONTAINER_ID=$(docker ps -aqf "name=$NAME")
	printf "\n-> Container '$NAME:$VERSION' (id = $CONTAINER_ID) is running.\n\n"
fi

exit 0
