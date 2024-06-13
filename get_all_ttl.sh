#!/bin/bash

if [ $# -ne 2 ]; then
	echo 'src_dir dest_dir must be provided'
	exit
fi

src_dir=$1
dest_dir=$2

i=1
find "$src_dir" -name '*.ttl' -type f -print0 | while IFS= read -r -d '' file; do
	cp -- "$file" "$dest_dir/file_$((i++)).ttl"
done
