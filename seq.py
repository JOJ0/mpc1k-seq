#!/usr/bin/env python
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

def read_and_tell(to_byte, fileobj):
  """read up to specific byte number, set bytedec+bytehex to current position"""
  global bytedec_beg, bytehex_beg, bytedec_end, bytehex_end
  chunk = fileobj.read(to_byte)
  bytedec_end=fileobj.tell()
  bytehex_end="{0:#0{1}x}".format(bytedec_end,6)
  bytedec_beg = bytedec_end - to_byte
  bytehex_beg="{0:#0{1}x}".format(bytedec_beg,6)
  return chunk

def print_chunk(chunk, data,  descr, hexflag=0):
  """print properly formated chunk data"""
  data_list=""
  data_list=" ".join(map(str,data))
  hexgroup=""
  if hexflag==1: hexgroup="| "+chunk2hexgroups(chunk)+" |"
  # for now set position output to decimal and include end position
  # FIXME should this be configurable?
  #return str(bytedec_beg)+"\t"+descr+data_list+"\t"+hexgroup
  return str(bytedec_beg)+":"+str(bytedec_end)+"\t"+descr+data_list+"\t"+hexgroup

def writeseqfile(currentfile, seqheader, rest_of_file, searchterm="", replaceterm="", bpm_new=0,
                 foundindex=0, looplength=0):
  # strip possible .SEQ ending
  replaceterm=replaceterm.replace(".SEQ", "") 
  # replace string
  if replaceterm:
    if len(replaceterm) > 16:
      print 'replaceterm ("{}") too long, max chars: 16, truncating!\n'.format(replaceterm)
      replaceterm=replaceterm[0:16]
    if replaceterm=="wav_bpm_replace":
      replaceterm=string_bpm_replace(args.searchterm, seqfile)
      print "!!! replacing FIRST occurence of \""+searchterm+"\" with \""+replaceterm+"\", "
      #print "!!! RUN AGAIN if you have more than 1 Audio track where this should be replaced!"
      rest_of_file=rest_of_file.replace(searchterm, replaceterm, 1)
    elif len(replaceterm) > 8:
      #print "DEBUG: we need to cut REPLACETERM, it's between 8 and 16 chars"
      #print "DEBUG: index:\t"+str(foundindex)
      print "!!! putting \""+term_split(replaceterm)["first"]\
        +"\" where \""+get_wav_first(rest_of_file, foundindex)+"\", "
      rest_of_file=rest_of_file.replace(get_wav_first(rest_of_file, foundindex),\
        term_split(replaceterm)["first"], 1)
      print "!!! putting \""+term_split(replaceterm)["second"]+"\" where \""\
        +get_wav_second(rest_of_file, foundindex)+"\", "
      rest_of_file=rest_of_file.replace(get_wav_second(rest_of_file, foundindex),\
        term_split(replaceterm)["second"], 1)
    else:
      #print "DEBUG: replaceterm is max 8 chars long, just replacing"
      print "!!! replacing FIRST occurence of \""+searchterm+"\" with \""+replaceterm+"\", "
      rest_of_file=rest_of_file.replace(searchterm, replaceterm, 1)
  bytestring=""
  bytestring+=struct.pack("<1H", *seqheader['some_number01'])
  bytestring+=struct.pack("<1H", *seqheader['some_number02'])
  bytestring+=struct.pack("16s", *seqheader['version'])
  bytestring+=struct.pack("<4H", *seqheader['some_number03'])
  if looplength > 0:
    print "!!! replacing looplength (bars) value, "
    bytestring+=struct.pack("<1H", looplength)
  else:
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
  #print "DEBUG: \n"+chunk2hexgroups(bytestring)
  # attach rest of seq file
  bytestring+=rest_of_file
  # close file-read handle, create writable one and (over)write
  currentfile.close()
  print "!!! and overwriting "+currentfile.name+" ..."
  #print "DEBUG: not really writing"
  with open(currentfile.name, "wb") as fw:
    fw.write(bytestring)
    fw.close()

def term_split(term):
  #print "DEBUG: replaceterm before splitting: "+term
  dict={}
  if len(term) > 16: termlength=16
  else: termlength=len(term)
  dict={"first": str(term[0:8]).ljust(8, "\x00"),
        "second": str(term[8:termlength]).ljust(8, "\x00")}
  return dict 

def get_wav_first(buf, index):
  #if str(0000) in binascii.hexlify(buf[index:index+8]):
  #  print "WARNING: there are binary zeroes at wav file position, something wrong?"
  return buf[index:index+8]

def get_wav_second(buf, index):
  #if str(0000) in binascii.hexlify(buf[index+16:index+16+8]):
  #  print "WARNING: there are binary zeroes at wav file position, something wrong?"
  return buf[index+16:index+16+8]

def string_bpm_replace(term_one, term_two):
  """replaces term_ones bpm with bpm found in term_two"""
  if term_two == "0":
    print "no bpm to replace found!!!"
    return ""
  else:
    #print "DEBUG: string_replace_bpm term_one: "+term_one
    #print "DEBUG: string_replace_bpm term_two: "+term_two
    return term_one.replace(bpmfind(term_one, leading_zero=True), 
            bpmfind(term_two, leading_zero=True))

def stringsearch(rest_of_file, searchterm):
  length=len(searchterm)
  if length > 16:
    sys.stderr.write('searchterm too long, max chars: 16, exiting...\n')
    raise SystemExit(2)
  if length > 8:
    sys.stderr.write('searchterm too long, max chars: 8, may support 16 in the future, exiting.\n')
    raise SystemExit(3)
  index = rest_of_file.find(searchterm)
  if index != -1:
    print "Found first occurence of SEARCHTERM at index "+str(index)+", it's "+str(length)+" chars long"
    print "If SEARCHTERM is the START of a wav filename in an AUDIO track,"
    print "this would be the first half:\t\t\""+get_wav_first(rest_of_file, index)+"\""
    print "and this would be the second half:\t\""+get_wav_second(rest_of_file, index)+"\""
    if args.hex:
      print "first half hex:\t\t"+chunk2hexgroups(get_wav_first(rest_of_file, index))
      print "second half hex:\t"+chunk2hexgroups(get_wav_second(rest_of_file, index))
    return index
  else:
    print "your SEARCHTERM \""+searchterm+"\" was not found!"
    return 0

def bpmfind(sometext, leading_zero=False):
  """finds possible bpm values in strings"""
  """leading_zero=True returns string instead of int!"""
  #print "DEBUG: bpmfind looking for bpm in: "+sometext
  bpm=0
  splitted=sometext.split("_")
  for i in splitted:
    if i.isdigit():
      if int(i) > 49:
        bpm=int(i)
        if leading_zero==False:
          print "-> found underscore seperated bpm value in given term: "+str(bpm)
  # if we still dont have a possible bpm value, continue with dash search
  if bpm==0:
    #print "DEBUG: still no bpm, before - dash search"
    splitted=sometext.split("-")
    for i in splitted:
      #print "DEBUG: inside dash search loop: "+i
      if i.isdigit():
        if int(i) > 49:
          #print "DEBUG: bpm found, it's > 49: "+i
          bpm=int(i)
          if leading_zero==False:
            print "-> found dash seperated bpm value in given term: "+str(bpm)
  # if we still dont have a bpm value, give up!
  if bpm==0:
    print "?? didn't find a possible bpm value in given term ("+sometext+"),"
    print "?? use underscores or dashes as seperating characters!"
  if leading_zero==True:
    return str(bpm).zfill(3)
  else:
    return int(bpm)

def header_delimiter(position, seqfile):
  maxlength=50
  j=0
  delim=""
  if position=="end":
    seqfile="End of header"
  namelength=len(seqfile)
  missing=maxlength-namelength
  #print "missing to maxlength:", missing
  #print "half of missing:", missing/2
  while j < missing/2:
    delim=delim+"#"
    j+=1
  line=delim+" "+seqfile+" "+delim 
  if missing % 2 != 0:
    line=line+"#"
  return line

def looplength_find(sometext, leading_zero=False, silent=False):
  """finds possible looplength (bars) values in strings"""
  """leading_zero=True returns string instead of int!"""
  #print "DEBUG: looplength_find looking for looplength in: "+sometext
  looplength=0
  marker="b"
  def _finder(text, seperator, marker):
    splitted=text.split(seperator)
    for i in splitted:
      #print "DEBUG: looplength_find: this is i: "+i
      if i.isalnum():
        #print "DEBUG: looplength_find: found alnum in: "+i
        if i.endswith(marker):
          i_without_marker=i.replace(marker, "")
          if i_without_marker.isdigit():
            return int(i_without_marker)
    return 0

  looplength=_finder(sometext, "_", marker)
  if looplength > 0:
    if leading_zero==False:
      if not silent:
        print "-> found underscore seperated looplength value in given term: "+str(looplength)
  # if we still dont have a possible looplength value, continue with dash search
  elif looplength==0:
    looplength=_finder(sometext, "-", marker)
    if looplength > 0:
      #print "DEBUG: still no looplength, before - dash search"
      if leading_zero==False:
        if not silent:
          print "-> found dash seperated looplength value in given term: "+str(looplength)

  # if we still dont have a looplength value, give up!
  if looplength==0:
    if not silent:
      print "?? didn't find a possible looplength value in given term ("+sometext+"),"
      print "?? use underscores or dashes as seperating characters!"
      return 0
  if leading_zero==True:
    return str(looplength).zfill(3)
  else:
    return int(looplength)

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path of *.SEQ files to be processed")
parser.add_argument("--search", "-s", help="search for given string in file contents", type=str, dest="searchterm")
parser.add_argument("--replace", "-r", help="replace SEARCHTERM with REPLACETERM", type=str, dest="replaceterm")
parser.add_argument("--correct-wav", "-w", help="sets basename of .SEQ file to the place where SEARCHTERM is found. Use this if your seq and wav files are named identically", action="store_true")
parser.add_argument("--correct-wav-bpm", "-p", help="replace BPM in found SEARCHTERM with BPM found in filename", action="store_true")
parser.add_argument("--filter", "--bpm", "-b", help="historically was used as a space seperated BPM list but actually it is a simple filter: only filenames containing one of the strings in the list, will be processed", type=str, dest="bpm_list")
parser.add_argument("--correct-bpm", "-c", help="set BPM to the same as in filename", action="store_true")
parser.add_argument("--correct-length", "-l", help="set the sequences looplength (bars) to the same as in filename. Assumes value in filename is marked with trailing \"b\" (eg 8b)", action="store_true")
parser.add_argument("--hex", "-x", help="show hex values next to decimal and strings", action="store_true")
parser.add_argument("--verbose", "-v", help="also show border markers and not yet studied header information", action="store_true")
args = parser.parse_args()

if args.replaceterm and not args.searchterm:
  parser.error("--replace (-r) does not make sense without --search (-s)")
if args.correct_wav and not args.searchterm:
  parser.error("--correct-wav (-w) does not make sense without --search (-s)")
if args.correct_wav_bpm and not args.searchterm:
  parser.error("--correct-wav-bpm (-p) does not make sense without --search (-s)")
if ((args.replaceterm and args.correct_wav)
    or (args.replaceterm and args.correct_wav_bpm)
    or (args.correct_wav and args.correct_wav_bpm)):
  parser.error("you can either --replace (-r) or --correct-wav (-w) or correct-wav-bpm (-p)")
PATH=args.path
print "\n* PATH used: " + PATH + ""
if args.searchterm:
  print "* searching for \""+args.searchterm+"\" (after End of header)"
if args.replaceterm:
  print "* replace is enabled! REPLACETERM is \""+args.replaceterm+"\""
if args.hex:
  print "* show hex values is enabled"
if args.verbose:
  print "* verbose mode is enabled"
if args.bpm_list:
  bpm_list = args.bpm_list.split(' ')
  print "* bpm_list (filter_list):\t",  bpm_list
if args.correct_bpm:
  print "* correct-bpm is enabled!"
if args.correct_wav:
  print "* correct-wav is enabled!"
if args.correct_wav_bpm:
  print "* correct-wav-bpm is enabled!"
if args.correct_length:
  print "* correct-length is enabled!"
print "" # just some space


for seqfile in os.listdir(PATH):
  if (seqfile.endswith(".SEQ") and args.bpm_list is None) or (seqfile.endswith(".SEQ") and any(bpm in seqfile for bpm in bpm_list)):
    print header_delimiter("start", seqfile)
    with open(PATH+"/"+seqfile, "rb") as f:
      seqfbase=seqfile.replace(".SEQ", "")
      #chunk = f.read(47) # read up to end of header 0x002f
      # header data will be written into this dictionary,
      # each element read from struct.unpack is a tuple!
      seqheader={}
      chunk = read_and_tell(2, f) # read next bytes
      seqheader['some_number01']=struct.unpack("<H",chunk)
      if args.verbose:
        print print_chunk(chunk, seqheader['some_number01'], "first 2 bytes\t\t", args.hex)
      chunk = read_and_tell(2, f) # read next bytes
      seqheader['some_number02']=struct.unpack("<H",chunk)
      if args.verbose:
        print print_chunk(chunk, seqheader['some_number02'], "zero:\t\t\t", args.hex)
      chunk = read_and_tell(16, f) # read next bytes
      seqheader['version']=struct.unpack("16s",chunk)
      print print_chunk(chunk, seqheader['version'], "version:\t\t", args.hex)
      chunk = read_and_tell(8, f) # read next bytes
      seqheader['some_number03']=struct.unpack("<4H",chunk)
      if args.verbose:
        print print_chunk(chunk, seqheader['some_number03'], "some shorts:\t\t", args.hex)
      chunk = read_and_tell(2, f) # read next bytes
      seqheader['bars']=struct.unpack("<H",chunk)
      print print_chunk(chunk, seqheader['bars'], "length (bars):\t\t", args.hex)
      #if str(seqheader['bars'][0])+"b" not in seqfbase and args.correct_length:
      looplength=looplength_find(seqfbase, leading_zero=False, silent=True)
      if (looplength is not 0) and (looplength is not seqheader['bars'][0]):
        #print looplength
        if args.correct_length:
          print "looplength in filename is different! This will be fixed now!"
        else:
          print "looplength in filename is different! Correct with --correct-length (-l)"
      chunk = read_and_tell(2, f)
      seqheader['some_number07']=struct.unpack("<H",chunk)
      if args.verbose:
        print print_chunk(chunk, seqheader['some_number07'], "zero:\t\t\t", args.hex)
      chunk = read_and_tell(2, f)
      seqheader['bpm']=struct.unpack("<H",chunk)
      seqheader['bpm']=(seqheader['bpm'][0]/10, ) # divide by 10 and create a tuple again
      print print_chunk(chunk, seqheader['bpm'], "bpm:\t\t\t", args.hex)
      if str(seqheader['bpm'][0]) not in seqfbase and args.correct_bpm:
        print "bpm in filename is different! This will be fixed now!"
      elif str(seqheader['bpm'][0]) not in seqfbase:
        print "bpm in filename is different! Correct with --correct-bpm (-c)"
      chunk = read_and_tell(14, f)
      seqheader['some_number08']=struct.unpack("<7H",chunk) # 3 ints
      if args.verbose:
        # maybe this actually is the end of header boundary?
        print print_chunk(chunk, seqheader['some_number08'], "some zeroes:\t\t", args.hex)
      chunk = read_and_tell(4, f)
      seqheader['tempo_map01']=struct.unpack("<2H",chunk)
      if args.verbose:
        print print_chunk(chunk, seqheader['tempo_map01'], "tempo map 01:\t\t", args.hex)
      chunk = read_and_tell(4, f)
      seqheader['tempo_map02']=struct.unpack("<2H",chunk)
      if args.verbose:
        print print_chunk(chunk, seqheader['tempo_map02'], "tempo map 02:\t\t", args.hex)
      print header_delimiter("end", seqfile)
      # read to end of file and store in ordinary var
      rest_of_file = f.read()
      # debug print binary
      #print print_chunk(chunk, chunk, "rest of file:\t\t", args.hex)
      # search for string in rest of file
      if args.searchterm:
        foundindex=stringsearch(rest_of_file, args.searchterm)
        # several possible write combinations:
        # write file if FOUND, CORRECT_WAV, BPM, LENGTH
        if foundindex >0 and args.correct_wav and args.correct_bpm and args.correct_length:
          writeseqfile(f, seqheader, rest_of_file, args.searchterm, seqfile, bpmfind(seqfile),
                       foundindex, looplength=looplength_find(seqfbase))
        # write file if FOUND, CORRECT_WAV, BPM
        elif foundindex >0 and args.correct_wav and args.correct_bpm:
          writeseqfile(f, seqheader, rest_of_file, args.searchterm, seqfile, bpmfind(seqfile),
                       foundindex)
        # write file if FOUND, REPLACE, BPM, LENGTH
        elif foundindex >0 and args.replaceterm and args.correct_bpm and args.correct_length:
          writeseqfile(f, seqheader, rest_of_file, args.searchterm, args.replaceterm, bpmfind(seqfile),
                       foundindex, looplength=looplength_find(seqfbase))
        # write file if FOUND, REPLACE, BPM
        elif foundindex >0 and args.replaceterm and args.correct_bpm:
          writeseqfile(f, seqheader, rest_of_file, args.searchterm, args.replaceterm, bpmfind(seqfile),
                       foundindex)
        # write file if FOUND, CORRECT_WAV_BPM, BPM, LENGTH
        elif foundindex >0 and args.correct_wav_bpm and args.correct_bpm and args.correct_length:
          writeseqfile(f, seqheader, rest_of_file, args.searchterm, "wav_bpm_replace",
                       bpmfind(seqfile), foundindex, looplength=looplength_find(seqfbase))
        # write file if FOUND, CORRECT_WAV_BPM, BPM
        elif foundindex >0 and args.correct_wav_bpm and args.correct_bpm:
          writeseqfile(f, seqheader, rest_of_file, args.searchterm, "wav_bpm_replace",
                       bpmfind(seqfile), foundindex)
        # write file if FOUND, REPLACE, LENGTH
        elif foundindex >0 and args.replaceterm and args.correct_length:
          writeseqfile(f, seqheader, rest_of_file, args.searchterm, args.replaceterm, 0, foundindex,
                       looplength=looplength_find(seqfbase))
        # write file if FOUND, REPLACE
        elif foundindex >0 and args.replaceterm:
          writeseqfile(f, seqheader, rest_of_file, args.searchterm, args.replaceterm, 0, foundindex)
        # write file if FOUND, CORRECT_WAV, LENGTH
        elif foundindex >0 and args.correct_wav and args.correct_length:
          writeseqfile(f, seqheader, rest_of_file, args.searchterm, seqfile, 0, foundindex,
                       looplength=looplength_find(seqfbase))
        # write file if FOUND and CORRECT_WAV
        elif foundindex >0 and args.correct_wav:
          writeseqfile(f, seqheader, rest_of_file, args.searchterm, seqfile, 0, foundindex)
        # write file if FOUND, CORRECT_WAV_BPM and LENGTH
        elif foundindex >0 and args.correct_wav_bpm and args.correct_length:
          writeseqfile(f, seqheader, rest_of_file, args.searchterm, "wav_bpm_replace", 0, foundindex,
                       looplength=looplength_find(seqfbase))
        # write file if FOUND and CORRECT_WAV_BPM
        elif foundindex >0 and args.correct_wav_bpm:
          writeseqfile(f, seqheader, rest_of_file, args.searchterm, "wav_bpm_replace", 0, foundindex)
        # write file if NOTHING is found, CORRECT_BPM, LENGTH
        elif foundindex==0 and args.correct_bpm and args.correct_length:
          writeseqfile(f, seqheader, rest_of_file, "", "", bpmfind(seqfile),
                       looplength=looplength_find(seqfbase))
        # write file if NOTHING is found, CORRECT_BPM
        elif foundindex==0 and args.correct_bpm:
          writeseqfile(f, seqheader, rest_of_file, "", "", bpmfind(seqfile))
        # only print this if we found something but are NOT replacing it already
        elif foundindex >0:
          print "** REPLACE OPTIONS: ********************************"
          print "** --replace simply replaces \""+args.searchterm+"\" with REPLACETERM." 
          print "** --correct-wav (-w) puts this files basename at found terms position,"
          print "**     it would replace \""+get_wav_first(rest_of_file, foundindex)\
            +"\" with \""+term_split(seqfbase)["first"]+"\","
          print "**     and \t\t\""+get_wav_second(rest_of_file, foundindex)\
            +"\" with \""+term_split(seqfbase)["second"]+"\"."
          print "** --correct-wav-bpm (-p) just replaces the bpm part in the found term," 
          print "**     it would replace \""+args.searchterm\
            +"\" with \""+string_bpm_replace(args.searchterm, seqfile)+"\"."
          print "** If this all looks like crap, don't do it! Existing files will be OVERWRITTEN!"
          if args.correct_bpm:
            writeseqfile(f, seqheader, rest_of_file, "", "", bpmfind(seqfile))
          if args.correct_length:
            writeseqfile(f, seqheader, rest_of_file, "", "", looplength=looplength_find(seqfbase))
      else: # whithout --search
        if args.correct_bpm and args.correct_length:
          writeseqfile(f, seqheader, rest_of_file, "", "", bpmfind(seqfile),
                       looplength=looplength_find(seqfbase))
        elif args.correct_length:
          writeseqfile(f, seqheader, rest_of_file, "", "", looplength=looplength_find(seqfbase))
        elif args.correct_bpm:
          writeseqfile(f, seqheader, rest_of_file, "", "", bpmfind(seqfile))
        # only print this if NOT replacing string
        #print "run script again with --replace 'replaceterm' to replace 'searchterm'"
        #print "If this all looks like crap, don't do it! Existing files will be OVERWRITTEN!"
      print ""

def old_code_for_reference():
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
