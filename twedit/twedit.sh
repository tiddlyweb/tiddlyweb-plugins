#/bin/sh -x

BAG=$1
TIDDLER=$2
URL="http://tiddlyweb.peermore.com/wiki/bags/$BAG/tiddlers/$TIDDLER"

AUTH='Cookie: tiddlyweb_user="put your cookie info here"'

echo $URL
echo $AUTH

curl -X GET -H 'Accept: text/plain' $URL > /tmp/twedit.$$
vim /tmp/twedit.$$
cat /tmp/twedit.$$ 
curl -v -X PUT -H "$AUTH" -H 'Content-Type: text/plain' --data-binary @/tmp/twedit.$$ $URL 

