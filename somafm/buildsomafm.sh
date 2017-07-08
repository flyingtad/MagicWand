#!/bin/bash

wget -O - http://somafm.com -o /dev/null | grep "href=\"/.*/\"" | sed 's/.*href="\//http:\/\/somafm.com\// ' | grep "\" >" | sed 's/" >//' > list.txt

rm radiostations.txt
while read p; do
  echo $p
  wget -O - $p -o /dev/null | grep ".pls" | sed 's/.*href="/http:\/\/somafm.com/' | sed 's/".*//' >> radiostations.txt
done <list.txt

cp radiostations.txt /home/pi/MagicWand/html
chmod 777 /home/pi/MagicWand/html/radiostations.txt
