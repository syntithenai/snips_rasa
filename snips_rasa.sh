#!/bin/bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
#echo "$DIR"
docker-compose -f $DIR/docker-compose.yml down &&  pasuspender -- docker-compose -f $DIR/docker-compose.yml up 
