#!/usr/bin/python
import sys
import os
import string
import pprint
import subprocess
import binascii
import argparse
import struct

bytedec_begin=0
bytehex_beg=0x0
bytedec_end=0
bytehex_end=0x0

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

def read_and_tell(to_byte):
  """read up to specific byte number, set bytedec+bytehex to current position"""
  global bytedec_begin, bytehex_beg, bytedec_end, bytehex_end
  chunk = f.read(to_byte)
  bytedec_end=f.tell()
  bytehex_end="{0:#0{1}x}".format(bytedec_end,6)
  bytedec_begin = bytedec_end - to_byte
  bytehex_beg="{0:#0{1}x}".format(bytedec_begin,6)
  return chunk

def print_chunk(chunk, data,  descr, hexflag=0):
  """print properly formated chunk data"""
  global bytedec_begin, bytehex_beg, bytedec_end, bytehex_end, chunk2hexgroups
  hexgroup=""
  if hexflag==1: hexgroup="| "+chunk2hexgroups(chunk)+" |"
  return str(bytehex_beg)+"\t"+descr+str(data[0])+"\t"+hexgroup

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path of *.seq files to be processed")
parser.add_argument("--replace", "-r", help="really replace ascii in seq file", action="store_true")
parser.add_argument("--bpm", "-b", help="space separated BPM list", type=str, dest="bpm_list")
args = parser.parse_args()

PATH=args.path
print "\nPATH used:\t" + PATH + "\n"

if args.replace:
  print "asciireplacer is enabled\n"

if args.bpm_list:
  bpm_list = args.bpm_list.split(' ')
  print "bpm_list:\t",  bpm_list , "\n"

for seqfile in os.listdir(PATH):
  if (".SEQ" in seqfile and args.bpm_list is None) or (".SEQ" in seqfile and any(bpm in seqfile for bpm in bpm_list)):
    if args.replace:
      print "now really replacing ascii data...\n"
    print "############### "+seqfile+" ################"
    with open(PATH+"/"+seqfile, "rb") as f:
      #while True:
      #chunk = f.read(47) # read up to end of header 0x002f
      #chunk = f.read(4) # read first 4
      #if not chunk:
      #  break
      seqheader={}
      chunk = read_and_tell(2) # read next bytes
      seqheader['some_number01']=struct.unpack("<H",chunk)
      print print_chunk(chunk, seqheader['some_number01'], "first 2 bytes\t\t", 1)
      #
      chunk = read_and_tell(2) # read next bytes
      seqheader['some_number02']=struct.unpack("<H",chunk)
      print print_chunk(chunk, seqheader['some_number02'], "next 2 bytes\t\t", 1)
      #
      chunk = read_and_tell(16) # read next bytes
      seqheader['version']=struct.unpack("16s",chunk)
      print print_chunk(chunk, seqheader['version'], "version:\t\t", 0)
      #
      chunk = read_and_tell(2) # read next bytes
      seqheader['some_number03']=struct.unpack("<H",chunk)
      print print_chunk(chunk, seqheader['some_number03'], "some short:\t\t", 1)
      #
      chunk = read_and_tell(2) # read next bytes
      seqheader['some_number04']=struct.unpack("<H",chunk)
      print print_chunk(chunk, seqheader['some_number04'], "some short:\t\t", 1)
      #
      chunk = read_and_tell(2) # read next bytes
      seqheader['some_number05']=struct.unpack("<H",chunk)
      print print_chunk(chunk, seqheader['some_number05'], "some short:\t\t", 1)
      #
      chunk = read_and_tell(2) # read next bytes
      seqheader['some_number06']=struct.unpack("<H",chunk)
      print print_chunk(chunk, seqheader['some_number06'], "some short:\t\t", 1)
      #
      chunk = read_and_tell(2) # read next bytes
      seqheader['bars']=struct.unpack("<H",chunk)
      print print_chunk(chunk, seqheader['bars'], "bars:\t\t\t", 1)
      #
      chunk = read_and_tell(2)
      seqheader['some_number07']=struct.unpack("<H",chunk)
      print print_chunk(chunk, seqheader['some_number07'], "some short:\t\t", 1)
      #
      chunk = read_and_tell(4)
      seqheader['bpm']=struct.unpack("<I",chunk)
      seqheader['bpm']=(seqheader['bpm'][0]/10, ) # divde by 10 and create a tuple again
      print print_chunk(chunk, seqheader['bpm'], "bpm:\t\t\t", 1)
      #
      chunk = read_and_tell(8)
      seqheader['some_number08']=struct.unpack("<Q",chunk) # unsinged long long
      #print seqheader['some_number08']
      print print_chunk(chunk, seqheader['some_number08'], "some zeroes:\t\t", 1)
      #
      chunk = read_and_tell(4)
      seqheader['some_number09']=struct.unpack("<I",chunk)
      print print_chunk(chunk, seqheader['some_number09'], "some zeroes:\t\t", 1)
      #
      chunk = read_and_tell(2)
      seqheader['tempo_map01']=struct.unpack("<H",chunk)
      print print_chunk(chunk, seqheader['tempo_map01'], "tempo map 01:\t\t", 1)
      #
      chunk = read_and_tell(2)
      seqheader['tempo_map02']=struct.unpack("<H",chunk)
      print print_chunk(chunk, seqheader['tempo_map02'], "tempo map 02:\t\t", 1)
      #
      #seqheader['fileversion']=struct.unpack('B',didson_data[3:4])[0]
      #seqheader['numframes']=struct.unpack('l',didson_data[4:8])
      #print '0x%04x' % bytenr # DEBUG OUT ALL HEX CHUNK NUMBERS
      #print bytehex # DEBUG OUT ALL HEX CHUNK NUMBERS
      #
      ##if chunk.find('Funk') != -1:
      ## in file FunkBG__096ac8ba.SEQ chunk 901 is 2nd part of WAV name!?!
      ##if chunknr==901:
      ##  print bytehex, "\tchunk 901:\t\t", chunk
      ## Track 1
      #if chunknr==903:
      #  print bytehex, "\tWAV file Tr1 P1:\t", chunk
      #if chunknr==905:
      #  print bytehex, "\tWAV file Tr1 P2:\t", chunk
      #if chunknr==906:
      #  print bytehex, "\tWAV file Tr1 bound.?\t", binascii.hexlify(chunk)
      ## Track 2
      #if chunknr==908:
      #  print bytehex, "\tWAV file Tr2 P1:\t", chunk
      #if chunknr==909:
      #  print bytehex, "\tWAV file Tr2 P2:\t", chunk
      #if chunknr==910:
      #  print bytehex, "\tWAV file Tr2 bound.?\t", binascii.hexlify(chunk)
      #if chunknr==899:
      #  print bytehex, "\ttest:\t", chunk
      #if chunknr==900:
      #  print bytehex, "\ttest:\t", chunk
      #if chunknr==901:
      #  print bytehex, "\ttest:\t", chunk

      ## DEBUG findstr
      ##if "75_" in chunk:
      ##  print "chunknr is ", chunknr
      ##  print "chunk is ", chunk
      #if bytehex=="0x0028": # actually 0x20f
      #  print bytehex, "\tLAST CHUNK BEFORE END OF HEADER (0x20f): ", bytedec
      #if bytehex=="0x0030":
      #  print bytehex, "\tTEMPO MAP STARTS: ", little2dec(chunk[0:2]), little2dec(chunk[2:4]),\
      #                                         little2dec(chunk[4:6]), little2dec(chunk[6:8])
      #if bytehex=="0x0fd0":
      #  print bytehex, "\tTRACK DATA STARTS: " 
      #  print "\t(64 chunks, 48 bytes each"
      #  print "\tname, midich, program, status)"
      ## TRACK 01
      #if bytehex=="0x1000":
      #  print bytehex, "\t1st track name:\t\t", chunk[0:8]
      #if bytehex=="0x1010" or bytehex=="0x1018":
      #  print bytehex, "\tprogram:\t\t", chunk[0:8]
      #if bytehex=="0x1020":
      #  print bytehex, "\tsomething no idea:\t",little2dec(chunk[0:1],chunk[1:2]), \
      #                                          little2dec(chunk[4:7])
      #if bytehex=="0x1028":
      #  print bytehex, "\tsome ints & midi ch:\t", little2dec(chunk[0:1], chunk[1:2]), \
      #        little2dec(chunk[2:3], chunk[3:4]),  little2dec(chunk[4:5], chunk[5:6]), \
      #        chunk[6:7], chunk[7:8]
      ## TRACK 02
      #if bytehex=="0x1030":
      #  print bytehex, "\t2nd track name:\t\t", chunk[0:8]
      #if bytehex=="0x1040" or bytehex=="0x1048":
      #  print bytehex, "\tprogram:\t\t", chunk[0:8]
      #if bytehex=="0x1050":
      #  print bytehex, "\tprogram and something:\t", chunk[0:2], little2dec(chunk[2:4]),\
      #                                          little2dec(chunk[4:7])
      ## TRACK 03
      #if bytehex=="0x1060":
      #  print bytehex, "\t3rd track name:\t\t", chunk[0:8]
      #if bytehex=="0x1070" or bytehex=="0x1078":
      #  print bytehex, "\tprogram:\t\t", chunk[0:8]
      #if bytehex=="0x1080":
      #  print bytehex, "\tsomething no idea:\t",little2dec(chunk[0:1],chunk[1:2]), \
      #                                          little2dec(chunk[4:7])
      ## BOUNDARY
      #if bytehex=="0x1c00":
      #  print bytehex, "\tBOUNDARY MARKER:\t", chunk2hexgroups(chunk) 
      #if bytehex=="0x1c10":
      #  print bytehex, "\tDATA STARTS: " 
      #  print bytehex, "\t(ticks, track#, event): " 


      #print hex(chunknr)
    print ""
