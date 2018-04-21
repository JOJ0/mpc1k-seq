#!/bin/bash

BPM_LIST="090 100 110 120 130 140 150 160"

if [ "$1" == "doit" ]; then
  DOIT=""
else
  DOIT="echo"
fi

for SEQ in ./*SEQ; do
  for BPM in $BPM_LIST; do
    $DOIT cp $SEQ ${BPM}_`echo $SEQ | awk -F "_" '{ print $2 "_" $3 }'`;
  done
done

