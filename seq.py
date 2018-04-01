#!/usr/bin/python
import sys
import os
import string
import pprint
import subprocess
import binascii
import argparse
import struct

bytedec_beg=0
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
  """the file objects name is hardcoded *grauslich*"""
  global bytedec_beg, bytehex_beg, bytedec_end, bytehex_end
  chunk = f.read(to_byte)
  bytedec_end=f.tell()
  bytehex_end="{0:#0{1}x}".format(bytedec_end,6)
  bytedec_beg = bytedec_end - to_byte
  bytehex_beg="{0:#0{1}x}".format(bytedec_beg,6)
  return chunk

def print_chunk(chunk, data,  descr, hexflag=0):
  """print properly formated chunk data"""
  global bytedec_beg, bytehex_beg, bytedec_end, bytehex_end, chunk2hexgroups
  data_list=""
  data_list=" ".join(map(str,data))
  hexgroup=""
  if hexflag==1: hexgroup="| "+chunk2hexgroups(chunk)+" |"
  return bytehex_beg+"\t"+descr+data_list+"\t"+hexgroup

def writeseqfile(currentfile, seqheader, rest_of_file, searchterm=None, replaceterm=None, bpm_new=0):
  # replace string
  if replaceterm:
    if len(replaceterm) > 8:
      sys.stderr.write('replaceterm too long, max chars: 8, may support 16 in the future, exiting.\n')
      raise SystemExit(4)
    print "!!! replacing first occurence of \""+searchterm+"\" with \""+replaceterm+"\", "
    rest_of_file=rest_of_file.replace(searchterm, replaceterm, 1)
  bytestring=""
  bytestring+=struct.pack("<1H", *seqheader['some_number01'])
  bytestring+=struct.pack("<1H", *seqheader['some_number02'])
  bytestring+=struct.pack("16s", *seqheader['version'])
  bytestring+=struct.pack("<4H", *seqheader['some_number03'])
  bytestring+=struct.pack("<1H", *seqheader['bars'])
  bytestring+=struct.pack("<1H", *seqheader['some_number07'])
  if bpm_new > 0:
    print "!!! replacing bpm value, "
    bytestring+=struct.pack("<1H", bpm_new*10)
  else:
    bytestring+=struct.pack("<1H", seqheader['bpm'][0]*10)
  bytestring+=struct.pack("<7H", *seqheader['some_number08']) # 3 ints
  bytestring+=struct.pack("<2H", *seqheader['tempo_map01'])
  bytestring+=struct.pack("<2H", *seqheader['tempo_map02'])
  #print chunk2hexgroups(bytestring)
  # attach rest of seq file
  bytestring+=rest_of_file
  # close file-read handle, create writable one and (over)write
  currentfile.close()
  print "!!! and overwriting "+currentfile.name+" ..."
  with open(currentfile.name, "wb") as fw:
    fw.write(bytestring)
    fw.close()

def stringsearch(rest_of_file, searchterm):
  length=len(searchterm)
  if length > 16:
    sys.stderr.write('searchterm too long, max chars: 16, exiting...\n')
    raise SystemExit(2)
  if length > 8:
    sys.stderr.write('searchterm too long, max chars: 8, may support 16 in the future, exiting.\n')
    raise SystemExit(3)
    firsthalf=searchterm[0:8]
    secondhalf=searchterm[8:length]
    print firsthalf
    print secondhalf
  index = rest_of_file.find(searchterm)
  if index != -1:
    print "Found first occurence of searchterm at index "+str(index)+", it's "+str(length)+" chars long"
    print "If your searchterm is the START of a filename in an Audio Track,"
    print "this would be the first half of the filename:\t"+rest_of_file[index:index+8]
    print "and this would be the second half:\t\t"+rest_of_file[index+8+8:index+8+8+8]
    if args.hex:
      print "first half hex:\t\t"+chunk2hexgroups(rest_of_file[index:index+8])
      print "second half hex:\t"+chunk2hexgroups(rest_of_file[index+8+8:index+8+8+8])
    print "(max chars in filename total is 16)"
    return True
  else:
    print "your SEARCHTERM \""+searchterm+"\" was not found!"
    return False

def bpmfind(filename):
  bpm=0
  splitted=filename.split("_")
  for i in splitted:
    if i.isdigit():
      bpm=int(i)
      print "found underscore seperated bpm value in filename: "+str(bpm)
  # if we still dont have a possible bpm value, continue with dash search
  if bpm==0:
    splitted=filename.split("-")
    for i in splitted:
      if i.isdigit():
        bpm=int(i)
        print "found dash seperated bpm value in filename: "+str(bpm)
  # if we still dont have a bpm value, give up!
  if bpm==0:
    print "didn't find a possible bpm value in filename, "
    print "use underscores or dashed as separating characters"
  return int(bpm)

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path of *.SEQ files to be processed")
parser.add_argument("--search", "-s", help="search for given string in file contents", type=str, dest="searchterm")
parser.add_argument("--replace", "-r", help="replace SEARCHTERM with REPLACETERM", type=str, dest="replaceterm")
parser.add_argument("--bpm", "-b", help="space seperated BPM list (actually any string in filename will be searched for)", type=str, dest="bpm_list")
parser.add_argument("--correct-bpm", "-c", help="set BPM to the same as in filename", action="store_true")
parser.add_argument("--hex", "-x", help="show hex values next to decimal and strings", action="store_true")
args = parser.parse_args()

if args.replaceterm and not args.searchterm:
  parser.error("--replace (-r) does not make sense without --search (-s)")
PATH=args.path
print "\n* PATH used: " + PATH + ""
if args.searchterm:
  print "* searching for \""+args.searchterm+"\" (after End of header)"
if args.replaceterm:
  print "* replacer is enabled! replaceterm is \""+args.replaceterm+"\""
if args.hex:
  print "* show hex values is enabled"
if args.bpm_list:
  bpm_list = args.bpm_list.split(' ')
  print "* bpm_list:\t",  bpm_list
if args.correct_bpm:
  print "* bpm-correct is enabled!"
print "" # just some space

for seqfile in os.listdir(PATH):
  if (seqfile.endswith(".SEQ") and args.bpm_list is None) or (seqfile.endswith(".SEQ") and any(bpm in seqfile for bpm in bpm_list)):
    print "############### "+seqfile+" ################"
    with open(PATH+"/"+seqfile, "rb") as f:
      #chunk = f.read(47) # read up to end of header 0x002f
      # header data will be written into this dictionary,
      # each element read from struct.unpack is a tuple!
      seqheader={}
      chunk = read_and_tell(2) # read next bytes
      seqheader['some_number01']=struct.unpack("<H",chunk)
      print print_chunk(chunk, seqheader['some_number01'], "first 2 bytes\t\t", args.hex)
      #
      chunk = read_and_tell(2) # read next bytes
      seqheader['some_number02']=struct.unpack("<H",chunk)
      print print_chunk(chunk, seqheader['some_number02'], "zero:\t\t\t", args.hex)
      #
      chunk = read_and_tell(16) # read next bytes
      seqheader['version']=struct.unpack("16s",chunk)
      print print_chunk(chunk, seqheader['version'], "version:\t\t", args.hex)
      #
      chunk = read_and_tell(8) # read next bytes
      seqheader['some_number03']=struct.unpack("<4H",chunk)
      print print_chunk(chunk, seqheader['some_number03'], "some shorts:\t\t", args.hex)
      #
      chunk = read_and_tell(2) # read next bytes
      seqheader['bars']=struct.unpack("<H",chunk)
      print print_chunk(chunk, seqheader['bars'], "bars:\t\t\t", args.hex)
      #
      chunk = read_and_tell(2)
      seqheader['some_number07']=struct.unpack("<H",chunk)
      print print_chunk(chunk, seqheader['some_number07'], "zero:\t\t\t", args.hex)
      #
      chunk = read_and_tell(2)
      seqheader['bpm']=struct.unpack("<H",chunk)
      seqheader['bpm']=(seqheader['bpm'][0]/10, ) # divide by 10 and create a tuple again
      print print_chunk(chunk, seqheader['bpm'], "bpm:\t\t\t", args.hex)
      if str(seqheader['bpm'][0]) not in seqfile:
        print "bpm in filename is different! correct with -c"
      #
      chunk = read_and_tell(14)
      seqheader['some_number08']=struct.unpack("<7H",chunk) # 3 ints
      # maybe this actually is the end of header boundary?
      print print_chunk(chunk, seqheader['some_number08'], "some zeroes:\t\t", args.hex)
      #
      chunk = read_and_tell(4)
      seqheader['tempo_map01']=struct.unpack("<2H",chunk)
      print print_chunk(chunk, seqheader['tempo_map01'], "tempo map 01:\t\t", args.hex)
      #
      chunk = read_and_tell(4)
      seqheader['tempo_map02']=struct.unpack("<2H",chunk)
      print print_chunk(chunk, seqheader['tempo_map02'], "tempo map 02:\t\t", args.hex)
      #
      print "############### End of header ###############"
      # read to end of file and store in ordinary var
      rest_of_file = f.read()
      # debug print binary
      #print print_chunk(chunk, chunk, "rest of file:\t\t", args.hex)
      # search for string in rest of file
      if args.searchterm:
        stringfound=stringsearch(rest_of_file, args.searchterm)
        # several possible write combinations:
        if args.replaceterm and args.correct_bpm:
          writeseqfile(f, seqheader, rest_of_file, args.searchterm, args.replaceterm, bpmfind(seqfile))
        elif args.replaceterm and stringfound==True:
          writeseqfile(f, seqheader, rest_of_file, args.searchterm, args.replaceterm, 0)
        # also write file if searching, but nothing is found and only correcting bpm
        elif stringfound==False and args.correct_bpm:
          writeseqfile(f, seqheader, rest_of_file, None, None, bpmfind(seqfile))
        else:
          # only print this if we found something but are NOT replacing it already
          if stringfound==True:
            print "run script again with --replace 'replaceterm' to replace 'searchterm'"
            print "If this all looks like crap, don't do it! Existing files will be OVERWRITTEN!"
      else:
        if args.correct_bpm:
          writeseqfile(f, seqheader, rest_of_file, None, None, bpmfind(seqfile))
        # only print this if NOT replacing string
        #print "run script again with --replace 'replaceterm' to replace 'searchterm'"
        #print "If this all looks like crap, don't do it! Existing files will be OVERWRITTEN!"
      print ""

      # keeping old version and other stuff for reference here:
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
