# mpc1k-seq
AKAI MPC 1000 sequence file command line utility

I often use my MPC1000 as a backing track loop player. For example I export the same drum loop in different speeds out of a DAW. Creating all the sequence files on the MPC itself is a very tedious task, This utility shows meta information of sequence files and helps doing repititive tasks like replacing the filename in the Audio tracks or replace BPM values.

```
usage: seq.py [-h] [--search SEARCHTERM] [--replace REPLACETERM]
              [--correct-wav] [--correct-wav-bpm] [--bpm BPM_LIST]
              [--correct-bpm] [--hex] [--verbose]
              path

positional arguments:
  path                  path of *.SEQ files to be processed

optional arguments:
  -h, --help            show this help message and exit
  --search SEARCHTERM, -s SEARCHTERM
                        search for given string in file contents
  --replace REPLACETERM, -r REPLACETERM
                        replace SEARCHTERM with REPLACETERM
  --correct-wav, -w     sets basename of .SEQ file to the place where
                        SEARCHTERM is found. Use this if your seq and wav
                        files are named identically
  --correct-wav-bpm, -p
                        replace BPM in found SEARCHTERM with BPM found in
                        filename
  --bpm BPM_LIST, -b BPM_LIST
                        space seperated BPM list (actually any string in
                        filename will be searched for)
  --correct-bpm, -c     set BPM to the same as in filename
  --hex, -x             show hex values next to decimal and strings
  --verbose, -v         also show border markers and not yet studied header
                        information
```

## examples

just show meta information of all seq files in current folder
```
seq.py .
```

show info of all seqfile that have 64 and 512 in the filename (usually BPM values)
```
seq.py -b "64 512" .
```
also display values in hex
```
seq.py -b "64 512" -x .
```
search for a string
```
seq.py -b "64 512" -x -s "FunkBG" .
```
replace SEARCHTERM with REPLACETERM
```
seq.py -b "64 512" -x -s "FunkBG" -r "Blues01" .
```


## output example

show all SEQ files in current directory that have 80 in the filename and search for the term FunkBG

```
seq.py -b "80" -s FunkBG .
```

output:

```
```
