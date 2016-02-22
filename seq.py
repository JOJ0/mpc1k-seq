#!/usr/bin/python
import sys
import string
import pprint
import subprocess
import binascii
#if len(sys.argv) > 1:
#  filename = sys.argv[1]
#  print ("file used: " + str(filename))
#else:
#  print "please provide zip or csv file!"
#  raise sys.exit() 

# set default value here!!
asciireplace="n"
PATH="/Users/jojo/Music/klavier/0-MIDI & Audio Drums, Backing Tracks/drumloops_jojo/FunkBG1_SEQ/learn from/"
# wav file name consisting of TWO 8 char strings, !not in a row!
FILEPRE="FunkBG_"
FILESUF="_8bar.SEQ"
BPM_LIST=[]
#BPM_LIST=["55","60"]
#BPM_LIST+=["60","65","70","74","78","80","84"]
#BPM_LIST+=["092","096"]
#BPM_LIST+=["100","102","106","110"]
BPM_LIST+=["088","088.1","089.2"]
#FIND="Funk2"+BPM
FIND="88acTght"
#REPL="FunkBG__"
REPL="acTgh" # BPM is added in for-loop below
#asciireplace="y"

for BPM in BPM_LIST:
  BPMREPL=BPM+REPL
  seqfile=PATH+FILEPRE+BPM+FILESUF
  ## ASCIIREPLACER START ##
  #print "file: "+FILEPRE+BPM+FILESUF+", find: "+FIND+", repl: "+BPMREPL
  #shellhexdump = subprocess.Popen(['hexdump', '-C', seqfile], stdout=subprocess.PIPE)
  #hexdumpout = shellhexdump.stdout.read()
  #assert shellhexdump.wait() == 0
  #print hexdumpout 
  #search_line = hexdumpout.split("Funk")
  #print search_line
  #print ""
  if asciireplace == "y":
    print "now really replacing ascii data..."
    #perl -pi -e 's/$ENV{FIND}/$ENV{REPL}/g' FunkBG_${BPM}_8bar.SEQ;
  ## ASCIIREPLACER END ##
  ##
  ## SHOW/REPLACE binary data at specific byte ##
  print "file: "+FILEPRE+BPM+FILESUF
  bars=04
  bpm=100.0
  with open(seqfile, "rb") as f:
    chunknr=1
    while True:
      chunk = f.read(8)
      if not chunk:
        break
      if chunknr==4:
        for idx,byte in enumerate(chunk):
           if idx == 4:
             #print "bars: ", binascii.b2a_uu(byte)
             print "bars: ", binascii.hexlify(byte)
      if chunknr==3:
        print "bpm i guess?: ", binascii.hexlify(chunk)
      if chunknr==5:
        print "bpm komma: ", binascii.hexlify(chunk)
      chunknr=chunknr+1
  print ""



