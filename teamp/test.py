
from __future__ import print_function
import sys
import libvirt

file = open('conf.xml', 'r')
xmlconfig = file.read()

conn = libvirt.open('qemu://192.168.122.109/system')
if conn == None:
    print ("Failed");
    exit(1)

dom = conn.createXML(xmlconfig)
if dom == None:
        print('Falied to create')
        exit(1)
print("created")

conn.close()
exit(0)
