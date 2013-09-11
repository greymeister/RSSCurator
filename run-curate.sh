#!/bin/bash

set -e
# Get the location of the script to make sure sqlite3 DB is in working dir
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

# Run script with first arg from STDIN
./curate.py $1
