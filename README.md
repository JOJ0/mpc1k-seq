# mpc1k-seq
AKAI MPC 1000 sequence file command line utility

I often use MPC1000 as a backing track loop player. I have the same drum loops in different speeds. This utility shows meta information of sequence files and helps to do tedious tasks like replacing parts of the filename in the Audio tracks.

```
usage: seq.py [-h] [--search SEARCHTERM] [--replace REPLACETERM]
              [--bpm BPM_LIST] [--hex]
              path

positional arguments:
  path                  path of *.seq files to be processed

optional arguments:
  -h, --help            show this help message and exit
  --search SEARCHTERM, -s SEARCHTERM
                        search for given string in file contents, show in
                        output when found
  --replace REPLACETERM, -r REPLACETERM
                        replace SEARCHTERM with REPLACETERM in seq file
  --bpm BPM_LIST, -b BPM_LIST
                        space separated BPM list (actually any string in
                        filename will be searched for
  --hex, -x             show hex values next to decimal and strings
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

command:

```
seq.py -b "64" -s FunkBG .
```

output:

```
* PATH used: .
* searching for "FunkBG" (only in the part after the header)
* bpm_list:	['64']

############### FunkBG_064_512b.SEQ ################
0x0000	first 2 bytes		8464
0x0002	zero:			0
0x0004	version:		MPC1000 SEQ 4.40
0x0014	some shorts:		5120 1 1 1000
0x001c	bars:			512
0x001e	zero:			0
0x0020	bpm:			64
0x0022	some zeroes:		0 0 0 0 0 0 0
0x0030	tempo map 01:		0 24576
0x0034	tempo map 02:		384 24576
############### End of Header ###############
Found first occurence of searchterm at index 7168, it's 6 chars long
If your searchterm is the START of a filename in an Audio Track,
this would be the first half of the filename:	FunkBG__
and this would be the second half:		88acTght
(max chars in filename total is 16)
run script again with --replace 'replaceterm' to replace 'searchterm'
If this all looks like crap, don't do it! Existing files will be OVERWRITTEN!


############### FunkBG_064_8bar.SEQ ################
0x0000	first 2 bytes		8464
0x0002	zero:			0
0x0004	version:		MPC1000 SEQ 4.40
0x0014	some shorts:		10752 257 1 1000
0x001c	bars:			8
0x001e	zero:			0
0x0020	bpm:			64
0x0022	some zeroes:		0 0 0 0 0 0 0
0x0030	tempo map 01:		0 24576
0x0034	tempo map 02:		384 24576
############### End of Header ###############
Found first occurence of searchterm at index 7168, it's 6 chars long
If your searchterm is the START of a filename in an Audio Track,
this would be the first half of the filename:	FunkBG__
and this would be the second half:		88acTght
(max chars in filename total is 16)
run script again with --replace 'replaceterm' to replace 'searchterm'
If this all looks like crap, don't do it! Existing files will be OVERWRITTEN!
```
