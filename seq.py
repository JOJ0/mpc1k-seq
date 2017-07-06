#!/usr/bin/python
import sys
import os
import string
import pprint
import subprocess
import binascii
import argparse

def hex2dec(s):
  """return the integer value of a hexadecimal string s"""
  return int(s, 16)

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path of *.seq files to be processed")
parser.add_argument("--replace", "-r", help="really replace ascii in seq file", action="store_true")
#parser.add_argument("--bpm", "-b", help="space separated BPM list", type=str, nargs="*", dest="bpm_list")
parser.add_argument("--bpm", "-b", help="space separated BPM list", type=str, dest="bpm_list")
args = parser.parse_args()

PATH=args.path
print "\nPATH used: " + PATH + "\n"

if args.replace:
  print "asciireplacer is enabled\n"

if args.bpm_list:
  print "bpm_list text:     ", args.bpm_list
  bpm_list = args.bpm_list.split(' ')
  print "bpm_list list:     ",  bpm_list , "\n"


# wav file name consisting of TWO 8 char strings, !not in a row!
FILEPRE="FunkBG_"
FILESUF="_8bar.SEQ"
BPM_LIST=["100","102","106","110"]
#FIND="Funk2"+BPM
FIND="88acTght"
#REPL="FunkBG__"
REPL="acTgh" # BPM is added in for-loop below

#for BPM in BPM_LIST:
for seqfile in os.listdir(PATH):
  if (".SEQ" in seqfile and args.bpm_list is None) or (".SEQ" in seqfile and any(bpm in seqfile for bpm in bpm_list)):
    #BPMREPL=BPM+REPL
    #seqfile=PATH+FILEPRE+BPM+FILESUF

    ## ASCIIREPLACER START ##
    #print "file: "+FILEPRE+BPM+FILESUF+", find: "+FIND+", repl: "+BPMREPL
    #shellhexdump = subprocess.Popen(['hexdump', '-C', seqfile], stdout=subprocess.PIPE)
    #hexdumpout = shellhexdump.stdout.read()
    #assert shellhexdump.wait() == 0
    #print hexdumpout 
    #search_line = hexdumpout.split("Funk")
    #print search_line
    #print ""
    if args.replace:
      print "now really replacing ascii data...\n"
      #perl -pi -e 's/$ENV{FIND}/$ENV{REPL}/g' FunkBG_${BPM}_8bar.SEQ;
    ## ASCIIREPLACER END ##
    ##
    ## SHOW/REPLACE binary data at specific byte ##
    #print "file: "+FILEPRE+BPM+FILESUF
    print "file:               "+seqfile
    #bars=04
    #bpm=100.0
    with open(PATH+"/"+seqfile, "rb") as f:
      chunknr=0
      while True:
        chunk = f.read(8)
        if not chunk:
          break
        if chunknr==3:
          print "bars HEX:          ", binascii.hexlify(chunk)
          for idx,byte in enumerate(chunk):
             if idx == 4:
               #print "bars ???:          ", binascii.b2a_uu(byte)
               print "bars DEC:          ", binascii.hexlify(byte)
        #if chunknr==2:
        #  print "what's chunk 2:    ", binascii.hexlify(chunk)
        if chunknr==4:
          tempo = (ord(chunk[1:2]) << 8 | ord(chunk[:1])) / 10
          print "bpm HEX:           ", binascii.hexlify(chunk)
          print "bpm DEC:           ", tempo
        #if chunk.find('Funk') != -1:
        # in file FunkBG__096ac8ba.SEQ chunk 901 is 2nd part of WAV name!?!
        #if chunknr==901:
        #  print "chunk 901:   ", chunk
        # Track 1
        if chunknr==903:
          print "WAV file Tr1 P1:   ", chunk
        if chunknr==905:
          print "WAV file Tr1 P2:   ", chunk
        #if chunknr==906:
        #  print "WAV file Tr1 Err:  ", binascii.hexlify(chunk)
        # Track 2
        #if chunknr==908:
        #  print "WAV file Tr2 P1:   ", chunk
        #if chunknr==909:
        #  print "WAV file Tr2 P2:   ", chunk
        #if chunknr==910:
        #  print "WAV file Tr2 Err:  ", binascii.hexlify(chunk)

        # DEBUG findstr
        #if "070bsD1" in chunk:
        #  print "chunknr is ", chunknr
        #  print "chunk is ", chunk
        #if "070drTgh" in chunk:
        #  print "chunknr is ", chunknr
        #  print "chunk is ", chunk

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
