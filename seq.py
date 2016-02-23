#!/usr/bin/python
import sys
import string
import pprint
import subprocess
import binascii

def hex2dec(s):
  """return the integer value of a hexadecimal string s"""
  return int(s, 16)

#if len(sys.argv) > 1:
#  filename = sys.argv[1]
#  print ("file used: " + str(filename))
#else:
#  print "please provide zip or csv file!"
#  raise sys.exit() 

# set default value here!!
asciireplace="n"
PATH="/Users/jojo/Music/klavier/0-MIDI & Audio Drums, Backing Tracks/drumloops_jojo/FunkBG1_SEQ/fertig und auf mpc/"
# wav file name consisting of TWO 8 char strings, !not in a row!
FILEPRE="FunkBG_"
FILESUF="_8bar.SEQ"
BPM_LIST=[]
BPM_LIST=["055","060"]
BPM_LIST+=["060","065","070","074","078","080","084"]
BPM_LIST+=["092","096"]
BPM_LIST+=["100","102","106","110"]
#BPM_LIST+=["064","128","256"]
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
             #print "bars:", binascii.b2a_uu(byte)
             print "bars:          ", binascii.hexlify(byte)
      if chunknr==3:
        print "what's chunk 3:", binascii.hexlify(chunk)
      if chunknr==5:
        tempo = (ord(chunk[1:2]) << 8 | ord(chunk[:1])) / 10
        print "bpm hex:       ", binascii.hexlify(chunk)
        print "bpm dec:       ", tempo
      #if chunk.find('Funk') != -1:
      if chunknr==904:
        print "WAV File P1:   ", chunk
      if chunknr==906:
        print "WAV File P2:   ", chunk
      if chunknr==907:
        print "WAV File Err:   ", chunk
        
      chunknr=chunknr+1
  print ""

#print "hex2dec: ", hex2dec("2c0101000a") 
#print "hex2dec: ", hex2dec("002c0101") 
#print '70 03 -> 88bpm'
#print '7a 03 -> 89bpm'
#text88='\x70\x03'
#text89='\x7a\x03'
#print '88 part1: ', binascii.hexlify(text88[0:1])
#print '88 part2: ', binascii.hexlify(text88[1:2])
#print '89 part1: ', binascii.hexlify(text89[0:1])
#print '89 part2: ', binascii.hexlify(text89[1:2])
