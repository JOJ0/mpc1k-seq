# mpc1k-seq
AKAI MPC 1000 sequence file command line utility

I often use my MPC1000 as a backing track loop player. For example I export the same drum loop in different speeds out of a DAW. Creating all the sequence files on the MPC itself is a very tedious task, This utility shows meta information of sequence files and helps doing repititive tasks like replacing the filename in the Audio tracks or replace BPM values.

```
usage: seq.py [-h] [--search SEARCHTERM] [--replace REPLACETERM]
              [--correct-wav] [--correct-wav-bpm] [--filter BPM_LIST]
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
  --filter BPM_LIST, --bpm BPM_LIST, -b BPM_LIST
                        historically was used as a space seperated BPM list
                        but actually it is a simple filter: only filenames
                        containing one of the strings in the list, will be
                        processed
  --correct-bpm, -c     set BPM to the same as in filename
  --hex, -x             show hex values next to decimal and strings
  --verbose, -v         also show border markers and not yet studied header
                        information
```

## Simple usage examples

just show meta information of all seq files in current directory
```
seq.py .
```

show info of all seq files that have 64 or 512 in the filename (usually BPM values)
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
replace _first occurence_ of SEARCHTERM with REPLACETERM (run script again to replace next instance of SEARCHTERM)

FIXME - "replacecount" may be configurable in future releases
```
seq.py -b "64 512" -x -s "FunkBG" -r "Blues01" .
```


## A more detailed usage example

Show all .SEQ files in the current directory (.) that have 80 in the filename (-b "80" or --filter "80" and search for the term "FunkBG" in the file:

```
seq.py -b "80" -s FunkBG .
```

Usually this is useful if we would like to search and replace a wav files name in an audio track, but certainly also could use it to replace the name of an MPC "program file" (.PGM) somewhere in the (binary) seq file.

The command's output is first showing us general meta data like the version of the sequence file, the number of bars and the bpm of the sequence.

After the "End of header" marker we see that it found our searchterm "FunkBG". If you are using the script like I do, you probably would like to replace the name of the wav file configured into the seq file (or only a part of it). The name of a wav file oddly is saved in two 8 Byte chunks in different places. The script is trying to help us with finding out if it just found part of a wav file name or something else (like a pgm file name or some other string).

Next are our possibilities to replace that string:

--replace (-r) is the simplest form of replacement and shoudld be self-explanatory.

--correct-wav (-w) is the option to use when our wav files are exactely identically named to our wav files (except the file ending of course). This is the option I use most. In case of the test seq file from the repo this wav and seq file names where identically already so this option currently also does not make much sense.

--correct-wav-bpm (-p) ist not applicable in this case. I'll show it in another example.

Each of the options exactely state what they would replace, so if we are happy with one of them we just rerun the script and additionally add the replace option to the command line.

```
* PATH used: .
* searching for "FunkBG" (after End of header)
* bpm_list: ['80']

################## FunkBG_080_8bar.SEQ ###################
4:20  version:    MPC1000 SEQ 4.40
28:30 bars:       8
32:34 bpm:        80
############### End of header ###############
Found first occurence of SEARCHTERM at index 7168, it's 6 chars long
If SEARCHTERM is the START of a wav filename in an Audio Track,
this would be the first half:       "FunkBG_0"
and this would be the second half:  "80_8bar"
** REPLACE OPTIONS: *************************************
** --replace simply replaces FunkBG with REPLACETERM.
** --correct-wav (-w) puts this files basename at found terms position,
**     it would replace "FunkBG_0" with "FunkBG_0",
**     and              "80_8bar" with "80_8bar".
** --correct-wav-bpm (-p) just replaces the bpm part in the found term,
?? didn't find a possible bpm value in given term (FunkBG),
?? use underscores or dashes as seperating characters!
?? replace options --bpm-correct and --correct-wav-bpm won't work!
**     it would replace "FunkBG" with "FunkBG".
** If this all looks like crap, don't do it! Existing files will be OVERWRITTEN!
```

For example if we choose -r to be the wanted option because we want to replace "FunkBG" with "Punk__", this would be the resulting output

```
seq.py -b "80" -s FunkBG -r "PunkBG" .

* PATH used: .
* searching for "FunkBG" (after End of header)
* replace is enabled! REPLACETERM is "PunkBG"
* bpm_list: ['80']

################## FunkBG_080_8bar.SEQ ###################
4:20  version:  MPC1000 SEQ 4.40
28:30 bars:     8
32:34 bpm:      80
############### End of header ###############
Found first occurence of SEARCHTERM at index 7168, it's 6 chars long
If SEARCHTERM is the START of a wav filename in an Audio Track,
this would be the first half:       "FunkBG_0"
and this would be the second half:  "80_8bar"
!!! replacing FIRST occurence of "FunkBG" with "PunkBG",
!!! and overwriting ./FunkBG_080_8bar.SEQ ...
```

If we now search for FunkBG again, we certainly won't find it anymore:

```
seq.py -b "80" -s "FunkBG" .

* PATH used: .
* searching for "FunkBG" (after End of header)
* bpm_list: ['80']

################## FunkBG_080_8bar.SEQ ###################
4:20  version:  MPC1000 SEQ 4.40
28:30 bars:     8
32:34 bpm:      80
############### End of header ###############
your SEARCHTERM "FunkBG" was not found!
```

PunkBG would instead be found and we would have similar options as with our first search above:

```
seq.py -b "80" -s "Punk" .

* PATH used: .
* searching for "Punk" (after End of header)
* bpm_list: ['80']

################## FunkBG_080_8bar.SEQ ###################
4:20  version:    MPC1000 SEQ 4.40
28:30 bars:       8
32:34 bpm:        80
############### End of header ###############
Found first occurence of SEARCHTERM at index 7168, it's 4 chars long
If SEARCHTERM is the START of a wav filename in an Audio Track,
this would be the first half:       "PunkBG_0"
and this would be the second half:  "80_8bar"
** REPLACE OPTIONS: *************************************
** --replace simply replaces Punk with REPLACETERM.
** --correct-wav (-w) puts this files basename at found terms position,
**     it would replace "PunkBG_0" with "FunkBG_0",
**     and              "80_8bar" with "80_8bar".
** --correct-wav-bpm (-p) just replaces the bpm part in the found term,
?? didn't find a possible bpm value in given term (Punk),
?? use underscores or dashes as seperating characters!
?? replace options --bpm-correct and --correct-wav-bpm won't work!
**     it would replace "Punk" with "Punk".
** If this all looks like crap, don't do it! Existing files will be OVERWRITTEN!
```


## Another more sophisticated example

This is the use case I actually wrote this script for. Let's take the file from above example where we had replaced Funk with Punk, but let's copy and _rename_ them. You can do the copy/renaming however you like, eg iOS X Finder has a nice mass renaming tool built-in. I do it directly on the commandline now, while we are at it:


```
cp FunkBG_080_8bar.SEQ PunkBG_080_8bar.SEQ
cp FunkBG_080_8bar.SEQ PunkBG_090_8bar.SEQ
cp FunkBG_080_8bar.SEQ PunkBG_100_8bar.SEQ
```

Ok now we'd like to set the wav files name in all of the 3 "Punk sequence files" to the same as the filename. We first search for Punk and see what we have. Probably there are other seq files in this folder so we particularily select our 3 files with the --filter (-b) option:


```
seq.py --filter Punk -s "PunkBG" .

* PATH used: .
* searching for "PunkBG" (after End of header)
* bpm_list:	['Punk']

################## PunkBG_080_8bar.SEQ ###################
4:20	version:  MPC1000 SEQ 4.40
28:30	bars:     8
32:34	bpm:      80
############### End of header ###############
Found first occurence of SEARCHTERM at index 7168, it's 6 chars long
If SEARCHTERM is the START of a wav filename in an Audio Track,
this would be the first half:       "PunkBG_0"
and this would be the second half:  "80_8bar"
** REPLACE OPTIONS: *************************************
** --replace simply replaces PunkBG with REPLACETERM.
** --correct-wav (-w) puts this files basename at found terms position,
**     it would replace "PunkBG_0" with "PunkBG_0",
**     and              "80_8bar" with "80_8bar".
** --correct-wav-bpm (-p) just replaces the bpm part in the found term,
?? didn't find a possible bpm value in given term (PunkBG),
?? use underscores or dashes as seperating characters!
?? replace options --bpm-correct and --correct-wav-bpm won't work!
**     it would replace "PunkBG" with "PunkBG".
** If this all looks like crap, don't do it! Existing files will be OVERWRITTEN!


################## PunkBG_090_8bar.SEQ ###################
4:20	version:  MPC1000 SEQ 4.40
28:30	bars:     8
32:34	bpm:      80
bpm in filename is different! correct with -c
############### End of header ###############
Found first occurence of SEARCHTERM at index 7168, it's 6 chars long
If SEARCHTERM is the START of a wav filename in an Audio Track,
this would be the first half:		"PunkBG_0"
and this would be the second half:	"80_8bar"
** REPLACE OPTIONS: *************************************
** --replace simply replaces PunkBG with REPLACETERM.
** --correct-wav (-w) puts this files basename at found terms position,
**     it would replace "PunkBG_0" with "PunkBG_0",
**     and              "80_8bar" with "90_8bar".
** --correct-wav-bpm (-p) just replaces the bpm part in the found term,
?? didn't find a possible bpm value in given term (PunkBG),
?? use underscores or dashes as seperating characters!
?? replace options --bpm-correct and --correct-wav-bpm won't work!
**     it would replace "PunkBG" with "PunkBG".
** If this all looks like crap, don't do it! Existing files will be OVERWRITTEN!


################## PunkBG_100_8bar.SEQ ###################
4:20	version:  MPC1000 SEQ 4.40
28:30	bars:     8
32:34	bpm:      80
bpm in filename is different! correct with -c
############### End of header ###############
Found first occurence of SEARCHTERM at index 7168, it's 6 chars long
If SEARCHTERM is the START of a wav filename in an Audio Track,
this would be the first half:		"PunkBG_0"
and this would be the second half:	"80_8bar"
** REPLACE OPTIONS: *************************************
** --replace simply replaces PunkBG with REPLACETERM.
** --correct-wav (-w) puts this files basename at found terms position,
**     it would replace "PunkBG_0" with "PunkBG_1",
**     and              "80_8bar" with "00_8bar".
** --correct-wav-bpm (-p) just replaces the bpm part in the found term,
?? didn't find a possible bpm value in given term (PunkBG),
?? use underscores or dashes as seperating characters!
?? replace options --bpm-correct and --correct-wav-bpm won't work!
**     it would replace "PunkBG" with "PunkBG".
** If this all looks like crap, don't do it! Existing files will be OVERWRITTEN!
```

If we closely look at the output for the 3 files we'd find these differencies

  * -c could correct the bpm of the sequence in files 2 and 3 (the copies)
  * --correct-wav (-w) could replace the name of the wav file so it's equal to the seq files name. Also in files 2 and 3 (the copies)

If we would now use options -w and -c option we would get the following output

```
seq.py --filter Punk -s "PunkBG" -w -c

* PATH used: .
* searching for "PunkBG" (after End of header)
* bpm_list: ['Punk']
* bpm-correct is enabled!
* correct-wav is enabled!

################## PunkBG_080_8bar.SEQ ###################
4:20  version:  MPC1000 SEQ 4.40
28:30 bars:     8
32:34 bpm:      80
############### End of header ###############
Found first occurence of SEARCHTERM at index 7168, it's 6 chars long
If SEARCHTERM is the START of a wav filename in an Audio Track,
this would be the first half:       "PunkBG_0"
and this would be the second half:  "80_8bar"
-> found underscore seperated bpm value in given term: 80
!!! putting "PunkBG_0" where "PunkBG_0",
!!! putting "80_8bar" where "80_8bar",
!!! replacing bpm value,
!!! and overwriting ./PunkBG_080_8bar.SEQ ...


################## PunkBG_090_8bar.SEQ ###################
4:20  version:  MPC1000 SEQ 4.40
28:30 bars:     8
32:34 bpm:      80
bpm in filename is different!  This will be fixed now!
############### End of header ###############
Found first occurence of SEARCHTERM at index 7168, it's 6 chars long
If SEARCHTERM is the START of a wav filename in an Audio Track,
this would be the first half:       "PunkBG_0"
and this would be the second half:  "80_8bar"
-> found underscore seperated bpm value in given term: 90
!!! putting "PunkBG_0" where "PunkBG_0",
!!! putting "90_8bar" where "80_8bar",
!!! replacing bpm value,
!!! and overwriting ./PunkBG_090_8bar.SEQ ...


################## PunkBG_100_8bar.SEQ ###################
4:20  version:  MPC1000 SEQ 4.40
28:30 bars:     8
32:34 bpm:      80
bpm in filename is different! This will be fixed now!
############### End of header ###############
Found first occurence of SEARCHTERM at index 7168, it's 6 chars long
If SEARCHTERM is the START of a wav filename in an Audio Track,
this would be the first half:       "PunkBG_0"
and this would be the second half:  "80_8bar"
-> found underscore seperated bpm value in given term: 100
!!! putting "PunkBG_1" where "PunkBG_0",
!!! putting "00_8bar" where "80_8bar",
!!! replacing bpm value,
!!! and overwriting ./PunkBG_100_8bar.SEQ ...
```

A last check shows us that the wav file name and also the bpm have been corrected 

```
seq.py --filter Punk -s "PunkBG" .

* PATH used: .
* searching for "PunkBG" (after End of header)
* bpm_list: ['Punk']

################## PunkBG_080_8bar.SEQ ###################
4:20  version:  MPC1000 SEQ 4.40
28:30 bars:     8
32:34 bpm:      80
############### End of header ###############
Found first occurence of SEARCHTERM at index 7168, it's 6 chars long
If SEARCHTERM is the START of a wav filename in an Audio Track,
this would be the first half:       "PunkBG_0"
and this would be the second half:  "80_8bar"
** REPLACE OPTIONS: *************************************
** --replace simply replaces PunkBG with REPLACETERM.
** --correct-wav (-w) puts this files basename at found terms position,
**     it would replace "PunkBG_0" with "PunkBG_0",
**     and    "80_8bar" with "80_8bar".
** --correct-wav-bpm (-p) just replaces the bpm part in the found term,
?? didn't find a possible bpm value in given term (PunkBG),
?? use underscores or dashes as seperating characters!
?? replace options --bpm-correct and --correct-wav-bpm won't work!
**     it would replace "PunkBG" with "PunkBG".
** If this all looks like crap, don't do it! Existing files will be OVERWRITTEN!


################## PunkBG_090_8bar.SEQ ###################
4:20  version:  MPC1000 SEQ 4.40
28:30 bars:     8
32:34 bpm:      90
############### End of header ###############
Found first occurence of SEARCHTERM at index 7168, it's 6 chars long
If SEARCHTERM is the START of a wav filename in an Audio Track,
this would be the first half:       "PunkBG_0"
and this would be the second half:  "90_8bar"
** REPLACE OPTIONS: *************************************
** --replace simply replaces PunkBG with REPLACETERM.
** --correct-wav (-w) puts this files basename at found terms position,
**     it would replace "PunkBG_0" with "PunkBG_0",
**     and    "90_8bar" with "90_8bar".
** --correct-wav-bpm (-p) just replaces the bpm part in the found term,
?? didn't find a possible bpm value in given term (PunkBG),
?? use underscores or dashes as seperating characters!
?? replace options --bpm-correct and --correct-wav-bpm won't work!
**     it would replace "PunkBG" with "PunkBG".
** If this all looks like crap, don't do it! Existing files will be OVERWRITTEN!


################## PunkBG_100_8bar.SEQ ###################
4:20  version:  MPC1000 SEQ 4.40
28:30 bars:     8
32:34 bpm:      100
############### End of header ###############
Found first occurence of SEARCHTERM at index 7168, it's 6 chars long
If SEARCHTERM is the START of a wav filename in an Audio Track,
this would be the first half:       "PunkBG_1"
and this would be the second half:  "00_8bar"
** REPLACE OPTIONS: *************************************
** --replace simply replaces PunkBG with REPLACETERM.
** --correct-wav (-w) puts this files basename at found terms position,
**     it would replace "PunkBG_1" with "PunkBG_1",
**     and    "00_8bar" with "00_8bar".
** --correct-wav-bpm (-p) just replaces the bpm part in the found term,
?? didn't find a possible bpm value in given term (PunkBG),
?? use underscores or dashes as seperating characters!
?? replace options --bpm-correct and --correct-wav-bpm won't work!
**     it would replace "PunkBG" with "PunkBG".
** If this all looks like crap, don't do it! Existing files will be OVERWRITTEN!
```

FIXME... example how to use --correct-wav-bpm


