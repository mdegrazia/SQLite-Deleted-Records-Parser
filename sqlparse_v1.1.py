#sqlparse.py
#
#This program parses an SQLite3 database for deleted entires and
#places the output into either and TSV file, or text file
#
#The SQLite file format, offsets etc is described at
#sqlite.org/fileformat.html
#
#
# Copyright (C) 2013 Mari DeGrazia (arizona4n6@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You can view the GNU General Public License at <http://www.gnu.org/licenses/>
#
# Version History:
# v1.1 2013-11-05
#	
#Find a bug???? Please let me know and I'll try to fix it (if you ask nicely....)
#

import struct
from optparse import OptionParser
import sys

#function to remove the non-printable characters, tabs and white spaces
def remove_ascii_non_printable(chunk):
    chunk = ' '.join(chunk .split())
    return ''.join([ch for ch in chunk if ord(ch) > 31 and ord(ch) < 126 or ord(ch) ==9])


usage = "Parse deleted records from an SQLite file into a TSV File or text file \n\
Examples:\n\
-f /home/sanforensics/smsmms.db -o report.tsv\n\
-f /home/sanforensics/smssms.db -r -o report.txt \n"

parser = OptionParser(usage=usage)

parser.add_option("-f", "--file", dest = "infile", help = "sqlite database file", metavar = "smsmms.db")
parser.add_option("-o", "--output", dest = "outfile", help = "Uutput to a tsv file. Strips white space, tabs and non-printable characters from data field", metavar = "output.tsv")
parser.add_option("-r", "--raw", action ="store_true", dest = "raw", help = "Optional. Will out put data field in a raw format and text file.", metavar = "output.tsv")

(options,args)=parser.parse_args()

#no arugments given by user,exit
if len(sys.argv) == 1:
    parser.print_help()
    exit(0)

#if input of output file missing, exit
if (options.infile == None) or (options.outfile == None):
    parser.print_help()
    print "Filename or Output file not given"
    exit(0)

#open file, confirm it is an SQLite DB
try:
    f=open(options.infile,"rb")
except:
    print ("File not Found")
    exit(0)
    
try:
    output = open(options.outfile, 'w')
except:
    print "Error opening output file"
    exit(0)


#write the column header if not outputting to text file
if options.raw !=True:
    output.write("Type\tOffset\tLength\tData\n")
    
#get the file size, we'll need this later
filesize = len(f.read())

#be kind, rewind (to the beginning of the file, that is)
f.seek(0)

#verify the file is an sqlite db; read the first 16 bytes for the header
header = f.read(16)

if "SQLite" not in header:
    print ("File does not appear to be an SQLite File")
    exit(0)


#OK, lets get started. The SQLite database is made up of multiple Pages. We need to get the size of each page.
#The pagesize this is stored at offset 16 at is 2 bytes long

pagesize = struct.unpack('>H', f.read(2))[0]


#According to SQLite.org/fileformat.html,  all the data is contained in the table-b-trees leaves.
#Let's go to each Page, read the B-Tree Header, and see if it is a table b-tree, which is designated by the flag 13

#set the offset to the pagesize, which will take us to the first page entry
offset = pagesize

#while the offset is less then the filesize, keep processing the pages

while offset < filesize: 
    
    #move to the beginning of the page and read the b-tree flag, if it's 13, its a leaf table b tree and we want to process it
    f.seek(offset)
    flag = struct.unpack('>b',f.read(1))[0]
    
    if flag == 13:
        
        #this is a table_b_tree - get the header information which is contained in the first 8 bytes
        
        freeblock_offset = struct.unpack('>h',f.read(2))[0] 
        num_cells = struct.unpack('>h',f.read(2))[0]
        cell_offset = struct.unpack('>h',f.read(2))[0]
        num_free_bytes = struct.unpack('>b',f.read(1))[0]
        
        
        #unallocated is the space after the header information and before the first cell starts 
        
        #start after the header (8 bytes) and after the cell pointer array. The cell pointer array will be the number of cells x 2 bytes per cell
        start = 8 + (num_cells * 2)
        
        # the length of the unallocated space will be the difference between the start and the cell offset
        length = cell_offset-start
        
        #move to start of unallocated, then read the data (if any) in unallocated - remember, we already read in the first 8 bytes, so now we just need to move past the cell pointer array
        f.read(num_cells*2)
        unallocated = f.read(length)
        
        if options.raw == True:
            output.write("Unallocated, Offset " + str(offset+start) + " Length " +  str(length) + "\n")
            output.write("Data:\n")
            output.write((unallocated))
            output.write("\n\n")
        
        else:
        #lets clean this up so its mainly the strings - remove white spaces and tabs too
            
            unallocated  = remove_ascii_non_printable(unallocated )
            if unallocated != "":
                output.write("Unallocated" + "\t" +  str(offset+start) + "\t" + str(length) + "\t" + str(unallocated) + "\n" )   
                
        #if there are freeblocks, lets pull the data
        
        while freeblock_offset != 0:
            
            #move to the freeblock offset
            f.seek(offset+freeblock_offset)
            
            #get next freeblock chain
            next_fb_offset = struct.unpack('>h',f.read(2))[0]
        
            #get the size of this freeblock
            free_block_size = struct.unpack('>hh',f.read(4))[0]
            
            #move to the offset so we can read the free block data
            f.seek(offset+freeblock_offset)
            
            #read in this freeblock
            free_block = f.read(free_block_size)
            
            if options.raw == True:
                output.write("Free Block, Offset " + str(offset+freeblock_offset) + ", Length " + str(free_block_size) + "\n")
                output.write("Data:\n")
                output.write((free_block))
                output.write( "\n\n")
            
            else:
                #lets clean this up so its mainly the strings - remove white spaces and tabs too
                free_block  = remove_ascii_non_printable(free_block)
                if unallocated != "":
                    output.write("Free Block" + "\t" +  str(offset+freeblock_offset) + "\t" + str(free_block_size) + "\t" + str(free_block) + "\n" )
            
            freeblock_offset = next_fb_offset
        
    
    #increase the offset by one pagesize and loop
    offset = offset + pagesize
    
#end

