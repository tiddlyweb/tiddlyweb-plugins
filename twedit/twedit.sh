#/bin/sh

BAG=$1
TIDDLER=$2
URL="http://tiddlyweb.peermore.com/wiki/bags/$BAG/tiddlers/$TIDDLER"

AUTH=$3

curl -X GET -H 'Accept: text/plain' $URL > /tmp/twedit.$$ && \
$VISUAL /tmp/twedit.$$ && \
curl -X PUT -H "$AUTH" -H 'Content-Type: text/plain' --data-binary @/tmp/twedit.$$ $URL 

