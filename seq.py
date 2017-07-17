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

def little2dec(byte1, byte2=None):
  """return the integer value of a little-endian hexadecimal string s"""
  if byte2==None:
    return int(binascii.hexlify(byte1[1:2]+byte1[0:1]), 16)
  else:
    return int(binascii.hexlify(byte2+byte1), 16)

def chunk2hexgroups(chunk):
  """return 2-byte-groups of binary chunk"""
  hexchunk=binascii.hexlify(chunk)
  #return  hexchunk
  #hexchunk2byte=hexchunk[0:4]+" "+hexchunk[4:8]+" "+hexchunk[8:12]+" "+hexchunk[12:16]+" "
  #return len(hexchunk), "\n"
  hexgroups=[hexchunk[i:i+4] for i in range (0, len(hexchunk), 4)]
  hexgroups_str=""
  for idx,group in enumerate(hexgroups):
    if idx==0: hexgroups_str=str(group)
    else: hexgroups_str=hexgroups_str+" "+str(group)
  return hexgroups_str

def chunk2bytearray(chunk):
  """return list containing bytes of chunk"""
  bytearray=[chunk[i:i+1] for i in range (0, len(chunk), 1)]
  return bytearray

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path of *.seq files to be processed")
parser.add_argument("--replace", "-r", help="really replace ascii in seq file", action="store_true")
#parser.add_argument("--bpm", "-b", help="space separated BPM list", type=str, nargs="*", dest="bpm_list")
parser.add_argument("--bpm", "-b", help="space separated BPM list", type=str, dest="bpm_list")
args = parser.parse_args()

PATH=args.path
print "\nPATH used:\t" + PATH + "\n"

if args.replace:
  print "asciireplacer is enabled\n"

if args.bpm_list:
  #print "bpm_list text:\t", args.bpm_list
  bpm_list = args.bpm_list.split(' ')
  print "bpm_list:\t",  bpm_list , "\n"


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
    print "file:\t\t\t\t"+seqfile
    #bars=04
    #bpm=100.0
    with open(PATH+"/"+seqfile, "rb") as f:
      chunknr=0
      while True:
        chunk = f.read(8) # each chunk is 8 bytes of binary data (\x00\x01...)
        if not chunk:
          break
        bytedec=chunknr*8
        bytehex="{0:#0{1}x}".format(bytedec,6)
        #print '0x%04x' % bytenr # DEBUG OUT ALL HEX CHUNK NUMBERS
        #print bytehex # DEBUG OUT ALL HEX CHUNK NUMBERS
        if chunknr==0:
          print bytehex,"\theader 1:\t\t", chunk
        if chunknr==1:
          print bytehex,"\theader 2:\t\t", chunk
        if chunknr==2:
          print bytehex, "\theader 3:\t\t", chunk
        if chunknr==3:
          print bytehex, "\tsome ints and bars HEX:\t", chunk2hexgroups(chunk)
          someint1 = little2dec(chunk[0:1], chunk[1:2])
          someint2 = little2dec(chunk[2:3], chunk[3:4])
          print bytehex, "\tsome ints:\t\t", someint1, " ", someint2  
          bars = little2dec(chunk[4:5], chunk[6:7]) 
          print bytehex, "\tbars DEC:\t\t", bars 
        if chunknr==4:
          print bytehex, "\tbpm HEX:\t\t", chunk2hexgroups(chunk)
          #tempo_rob = (ord(chunk[1:2]) << 8 | ord(chunk[:1])) / 10
          #print bytehex, "\tbpm DEC Robert:\t\t", tempo_rob
          #tempo_my_reord = chunk2bytearray(chunk)[1:2]+chunk2bytearray(chunk)[0:1]
          tempo_my = little2dec(chunk[0:1], chunk[1:2]) / 10
          print bytehex, "\tbpm DEC:\t\t", tempo_my
        #if chunk.find('Funk') != -1:
        # in file FunkBG__096ac8ba.SEQ chunk 901 is 2nd part of WAV name!?!
        #if chunknr==901:
        #  print bytehex, "\tchunk 901:\t\t", chunk
        # Track 1
        if chunknr==903:
          print bytehex, "\tWAV file Tr1 P1:\t", chunk
        if chunknr==905:
          print bytehex, "\tWAV file Tr1 P2:\t", chunk
        #if chunknr==906:
        #  print bytehex, "\tWAV file Tr1 Err:\t\t", binascii.hexlify(chunk)
        # Track 2
        #if chunknr==908:
        #  print bytehex, "\tWAV file Tr2 P1:\t", chunk
        #if chunknr==909:
        #  print bytehex, "\tWAV file Tr2 P2:\t", chunk
        #if chunknr==910:
        #  print bytehex, "\tWAV file Tr2 Err:\t", binascii.hexlify(chunk)

        # DEBUG findstr
        #if "070bsD1" in chunk:
        #  print "chunknr is ", chunknr
        #  print "chunk is ", chunk
        #if "070drTgh" in chunk:
        #  print "chunknr is ", chunknr
        #  print "chunk is ", chunk
        if bytehex=="0x0028": # actually 0x20f
          print bytehex, "\tLAST CHUNK BEFORE END OF HEADER (0x20f):"
        if bytehex=="0x0030":
          print bytehex, "\tTEMPO MAP STARTS: ", little2dec(chunk[0:2]), little2dec(chunk[2:4]),\
                                                 little2dec(chunk[4:6]), little2dec(chunk[6:8])
        if bytehex=="0x0fd0":
          print bytehex, "\tTRACK DATA STARTS: " 
          print "\t(64 chunks, 48 bytes each"
          print "\tname, midich, program, status)"
        # TRACK 01
        if bytehex=="0x1000":
          print bytehex, "\t1st track name:\t\t", chunk[0:8]
        if bytehex=="0x1010" or bytehex=="0x1018":
          print bytehex, "\tprogram:\t\t", chunk[0:8]
        if bytehex=="0x1020":
          print bytehex, "\tsomething no idea:\t",little2dec(chunk[0:1],chunk[1:2]), \
                                                  little2dec(chunk[4:7])
        if bytehex=="0x1028":
          print bytehex, "\tsome ints & midi ch:\t", little2dec(chunk[0:1], chunk[1:2]), \
                little2dec(chunk[2:3], chunk[3:4]),  little2dec(chunk[4:5], chunk[5:6]), \
                chunk[6:7], chunk[7:8]
        # TRACK 02
        if bytehex=="0x1030":
          print bytehex, "\t2nd track name:\t\t", chunk[0:8]
        if bytehex=="0x1040" or bytehex=="0x1048":
          print bytehex, "\tprogram:\t\t", chunk[0:8]
        if bytehex=="0x1050":
          print bytehex, "\tprogram and something:\t", chunk[0:2], little2dec(chunk[2:4]),\
                                                  little2dec(chunk[4:7])
        # TRACK 03
        if bytehex=="0x1060":
          print bytehex, "\t3rd track name:\t\t", chunk[0:8]
        if bytehex=="0x1070" or bytehex=="0x1078":
          print bytehex, "\tprogram:\t\t", chunk[0:8]
        if bytehex=="0x1080":
          print bytehex, "\tsomething no idea:\t",little2dec(chunk[0:1],chunk[1:2]), \
                                                  little2dec(chunk[4:7])
        # BOUNDARY
        if bytehex=="0x1c00":
          print bytehex, "\tBOUNDARY MARKER:\t", chunk2hexgroups(chunk) 
        if bytehex=="0x1c10":
          print bytehex, "\tDATA STARTS: " 
          print bytehex, "\t(ticks, track#, event): " 


        #print hex(chunknr)
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
