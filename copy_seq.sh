#!/bin/bash

BPM_LIST="072 077 082 088 093 099 104"

if [ "$1" == "doit" ]; then
  DOIT=""
else
  DOIT="echo"
fi

for SEQ in ./*SEQ; do
  for BPM in $BPM_LIST; do
    #$DOIT cp $SEQ ${BPM}_`echo $SEQ | awk -F "_" '{ print $2 "_" $3 }'`;
    $DOIT cp $SEQ `echo $SEQ | awk -F "_" '{ print $1 }'`_${BPM}_`echo $SEQ | awk -F "_" '{ print $3 "_" $4 "_" $5 }'`;
  done
done

