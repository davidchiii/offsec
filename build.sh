#!/bin/bash

cd ~/offsec-materials
#git pull

cd chals
for dir in `find -type f -name Dockerfile | xargs -n1 dirname`; do
    if [ "${dir:0:6}" = "./week" ]; then
	echo $dir
	name=`python -c "import json; print json.loads(open('$dir/challenge.json').read())['container_name']"`
	docker build -t $name $dir &> /dev/null
    fi
done
