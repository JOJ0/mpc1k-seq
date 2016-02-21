#!/usr/bin/python
import sys
import string
import pprint
import subprocess
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
#BPM_LIST+=["92","96"]
#BPM_LIST+=["100","102","106","110"]
BPM_LIST+=["88","88.2","89.2"]
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
    bytenr=0
    while True:
      byte = f.read(1)
      if not byte:
        break
      if bytenr==28:
        print "bars: ", ord(byte) 
      if bytenr==20:
        print "bpm p1: ", ord(byte) 
      if bytenr==21:
        print "bpm p2: ", ord(byte) 
      if bytenr==22:
        print "bpm p3: ", ord(byte) 
      if bytenr==23:
        print "bpm p4: ", ord(byte) 
      if bytenr==32:
        print "bpm komma: ", ord(byte) 
      bytenr=bytenr+1
  print ""



