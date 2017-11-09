#!/bin/bash

RESFILE=$1
if [ "$RESFILE" == "" ]
then
 echo "Usage:"
 echo "$0 report file to be analyzed"
 exit 0
fi

echo Total hosts scanned:
echo $(expr $(cat $RESFILE | wc -l) - 1)

echo Successful:
echo $(grep success $RESFILE |  wc -l)

echo Failed:
echo $(grep fail $RESFILE |  wc -l)

echo Failure reasons:
REASONS=$(grep fail $RESFILE | cut -f7- -d, | sort | uniq)

IFS=$'\n'
for REASON in $REASONS
do
 IFS=" "
 echo $REASON
 REASON=$(echo "$REASON" | sed -e 's/[][]/\\&/g')
 echo $(grep "$REASON" $RESFILE |  wc -l)
done
