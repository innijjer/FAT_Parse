#!/usr/bin/python3

import os
import sys
import re

off = str(sys.argv[1])
filen = str(sys.argv[2])

cmd1 = "dd if="+filen+" bs=512 count=1 status=none | xxd -g1 | sed -n '28,32p' > /root/Desktop/hexd.txt"
os.system(cmd1)
hexdfile = open("/root/Desktop/hexd.txt", 'r').readlines()
regex = re.compile("000001f0:.*55 aa")
if re.search(regex, str(hexdfile)) :
   LittleE = True
else :
   LittleE = False

def Endian(bytes):
   if (LittleE):
      LE_val = str()
      bytes = bytes[::-1]
      bytes = ''.join(bytes)
      return bytes
   else :
      bytes = ''.join(bytes)
      return bytes

def Cluster_To_Sector(Clus):
   sec = (Clus - 2) * (SecClus) + Clus2
   return sec
def Sector_To_Cluster(sec):
   clus = ((sec - Clus2) / (SecClus)) + 2
   return clus

cmd1 = "dd if=" + filen + " count=1 status=none | xxd -p > /root/Desktop/hexd.txt"
os.system(cmd1)
line = open("/root/Desktop/hexd.txt", 'r').readlines()
hexlist = list()
for data in line :
   hextemp = list(([data[i:i+2] for i in range(0,len(data), 2)]))
   hexlist += hextemp
   hexlist.remove('\n')


if int(Endian(hexlist[17:19]),16) == 0 :
   Type = "FAT32"
   print("FAT32")
else:
   print("FAT12/16")
   Type = "FAT12/16"
print("Bytes per sector:", int(Endian(hexlist[11:13]),16))
BytesSec = int(Endian(hexlist[11:13]),16)
ReservedArea = int(Endian(hexlist[14:16]),16)
SecClus = int(hexlist[13],16)
print("Sectors per Cluster:", int(hexlist[13],16))
print("Number of FATs:", int(hexlist[16],16))
DirEntry = int(Endian(hexlist[17:19]),16)
print("Max num in root Dir (0 for FAT32):", DirEntry)
if DirEntry == 0:
   print("Size of each FAT:", int(Endian(hexlist[36:40]),16))
   rootdir = int(Endian(hexlist[44:48]),16)
   FatSize = int(Endian(hexlist[36:40]),16)
   print("Cluster Address of Root Dir:", int(Endian(hexlist[44:48]),16))
   print("Volume Label:", bytearray.fromhex(''.join(hexlist[71:82])).decode('utf-8'))
   Clus2 = (FatSize*2)+ReservedArea
   print("Cluster 2 Sector Address:", Clus2)
   print("Root Directory Sector Address:", Cluster_To_Sector(rootdir))
   rootdir = Cluster_To_Sector(rootdir)
else:
   print("Size of each FAT (Sectors):", int(Endian(hexlist[22:24]),16))
   FatSize = int(Endian(hexlist[22:24]),16)
   #print("Volume Label:", bytearray.fromhex(''.join(hexlist[43:54])).decode('utf-8'))   
   rootdir = (FatSize*2)+ReservedArea
   Clus2 = rootdir + 32 
print("\n----------------------------------------------------------------------------")

bs = BytesSec
cmd1 = "dd if=" + filen + " bs="+str(bs)+" skip="+str(rootdir)+" count=32 status=none | xxd -p > /root/Desktop/hexd.txt"
os.system(cmd1)
line2 = open("/root/Desktop/hexd.txt", 'r').readlines()
hexlist2 = list()
for data in line2 :
   hextemp = list(([data[i:i+2] for i in range(0,len(data), 2)]))
   hexlist2 += hextemp
   hexlist2.remove('\n')


entries = list()
for i in range(0,len(hexlist2), 32) :
   entries.append(i)

entryList = list()
for i in entries :
   entryList.append(hexlist2[i:i+32])


AttribType = {'01':'Read-only','02':'Hidden file','04':'System file','08':'Valume Label','0f':'Long File name','10':'Directory','20':'Archive'}

#RootDir parse
def Root_Dir_Parse(entry):
   #print("Byte 1:",entry[0])
   #Char1 = bytearray.fromhex(''.join(entry[1:11])).decode('utf-8')
   Attrib = entry[11]
   if Attrib in AttribType:
      AID = AttribType[Attrib]
      print("File Attribute:",AID)
      if Attrib == '0f' : 
         #char2 = bytearray.fromhex(''.join(entry[14:26])).decode('utf-8')
         #char3 = bytearray.fromhex(''.join(entry[28:32])).decode('utf-8')         
         #print("Name: "+Char1+char2+char3)
         print("Convert to Ascii (hex):",''.join(entry[1:11]),''.join(entry[14:26]),''.join(entry[28:32]))
      else:
         print("Name in hex: ", ''.join(entry[1:11]))
         if Type == "FAT32" :
            HiOrder2Bytes = int(Endian(entry[20:22]),16)
            print("Address of first Cluster",Cluster_To_Sector(HiOrder2Bytes))
         else:
            LowOrder2Bytes = int(Endian(entry[26:28]),16)
            print("Address of first Cluster",Cluster_To_Sector(LowOrder2Bytes))
      print("\n")
   else:
      None


for entry in entryList :
   Root_Dir_Parse(entry)


   