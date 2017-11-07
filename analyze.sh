#!/bin/bash

RESFILE=endpoint_scan_results.txt

echo Total hosts scanned:
echo $(cat $RESFILE | wc -l)

echo Successful:
echo $(grep successful $RESFILE |  wc -l)

echo Failed:
echo $(grep failed $RESFILE |  wc -l)

echo Failure reasons:
REASONS="$(grep "failed" $RESFILE | cut -f3 -d: | sort | uniq)"

IFS=$'\n'
for REASON in $REASONS
do
 IFS=" "
 echo "$REASON"
 REASON=$(echo "$REASON" | sed -e 's/[][]/\\&/g')
 echo $(grep "$REASON" $RESFILE |  wc -l)
done
