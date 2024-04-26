#!/usr/bin/bash

# Upload all ttl files in a directory (recursively) to a named graph in graphdb.

gdb_host="gdb.dev.example.com"
upload_from="mydir"
graph_name='mygraph'

# get auth token
gdb_token=$(curl -X POST -s -H "X-GraphDB-Password: $GDB_PASSWORD" -I "https://anufnp.dev.kurrawong.ai/rest/login/$GDB_USER" |
    grep "authorization" | awk '{print $3}')

# upload files to named graph. [204 = uploaded successfully]
find "$upload_from" -name '*.ttl' |
    parallel "
        echo -n 'uploading {0}:  '
        curl -X POST -s -D - \
            -H 'Authorization: GDB $gdb_token' \
            -H 'Content-Type: application/x-turtle' \
            -T '{0}' \
            'https://$gdb_host/repositories/anu-publications/rdf-graphs/$graph_name' |
        grep 'HTTP/2'
    "
