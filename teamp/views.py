"""views.py"""

from __future__ import print_function

from flask import render_template, request

import sys
import libvirt

from teamp import app, db

class Domaininf:
    OStype = ""
    response = ""
    uuid = ""
    name = ""
    flag = ""
    state = ""
    persistent = ""
    hw = []

#main page
@app.route("/")
def main():

    conn = libvirt.open('qemu://192.168.122.109/system')
    if conn == None:
        return "Connection Failed"

    #all domains, including not running ones
    domains = conn.listAllDomains(0)

    domname = []

    for domain in domains:
        domname.append(domain.name())

    conn.close()

    #connect to proj/teamp/templates/main.html
    return render_template("main.html", alldomainsname = domname)

#response to search
@app.route("/", methods=['POST'])
def response():

    conn = libvirt.open('qemu://192.168.122.109/system')
    if conn == None:
        return "Connection Failed"

    inputname = request.form['domn']

    inf = Domaininf()
    inf.name = inputname

    dom = conn.lookupByName(inputname)

    if dom == None:
        inf.response = "Failed to find the domain" + inputname
    else:
        id = dom.ID()
        if id == -1:
            inf.response = "The domain is not running"
        else:
            inf.response = "The ID of the domain is " + str(id)

        inf.uuid = dom.UUIDString()
        inf.OStype = dom.OSType()
        inf.flag = dom.hasManagedSaveImage()

        #hardware informations
        inf.hw = dom.info()

        if inf.hw[0] == libvirt.VIR_DOMAIN_NOSTATE:
            inf.state = "nostate"
        elif inf.hw[0] == libvirt.VIR_DOMAIN_RUNNING:
            inf.state = "running"
        elif inf.hw[0] == libvirt.VIR_DOMAIN_BLOCKED:
            inf.state = "blocked"
        elif inf.hw[0] == libvirt.VIR_DOMAIN_PAUSED:
            inf.state = "paused"
        elif inf.hw[0] == libvirt.VIR_DOMAIN_SHUTOFF:
            inf.state = "shutoff"
        elif inf.hw[0] == libvirt.VIR_DOMAIN_CRASHED:
            inf.state = "crashed"
        elif inf.hw[0] == libvirt.VIR_DOMAIN_PMSUSPENDED:
            inf.state = "pmsuspended"
        else:
            inf.state = "unknown"

        temp = dom.isPersistent()
        if temp == 0:
            inf.persistent = "not persistent"
        if temp == 1:
            inf.persistent = "persistent"
        else:
            inf.persistent = "error occured"

    conn.close()

    return render_template("search.html", domain = inf)


@app.route("/boot", methods=['POST'])
def boot():
    conn = libvirt.open('qemu://192.168.122.109/system')
    if conn == None:
        return "Connection Failed"

    name = request.form['domainname']

    dom = conn.lookupByName(name)
    if dom.create() < 0:
        return "cannot boot"

    return "Booted!"


@app.route("/createform", methods=['POST'])
def createform():
    return render_template("createform.html")


@app.route("/create", methods=['POST'])
def create():

    name = request.form['name']
    ncpu = request.form['ncpu']
    ostype = request.form['ostype']
    mem = request.form['mem']
    persist = request.form['pers']

    #source: source file to make configuration
    #file: new conf file
    source = open('/home/ncloud/proj/teamp/conf.xml','r')
    file = open('/home/ncloud/proj/teamp/newconf.xml', 'w')

    lines = source.readlines()
    i = 1

    nameconf = "\t<name>" + name + "</name>\n"
    ncpuconf = "\t<vcpu placement='static'>"+ncpu+"</vcpu>\n"
    ostypeconf = "\t\t<type arch='"+ostype+"' machine='pc-i440fx-xenial'>hvm</type>\n"
    memconf = "\t<memory unit='KiB'>"+mem+"</memory>"
    currmemconf = "\t<currentmemory unit='KiB'>"+mem+"</currentmemory>"

    for line in lines:
        if i == 2:
            file.write(nameconf)
        elif i == 3:
            file.write(memconf)
        elif i == 4:
            file.write(currmemconf)
        elif i == 5:
            file.write(ncpuconf)
        elif i == 10:
            file.write(ostypeconf)
        else:
            file.write(line)
        i = i+1

    source.close()
    file.close()

    file = open('/home/ncloud/proj/teamp/newconf.xml', 'r')
    xmlconfig = file.read()

    conn = libvirt.open('qemu://192.168.122.109/system')
    if conn == None:
        return "Connection Failed"

    if persist == 1:
        dom = conn.defineXML(xmlconfig)
        if dom == None:
            return "Failed to create a domain."

        if dom.create(dom) < 0:
            return "Can not boot guest domain."
    else:
        dom = conn.createXML(xmlconfig)
        if dom == None:
            return "Faile to create a domain."

    return "Created!"


#stop and save
@app.route("/save", methods=['POST'])
def save():

    name = request.form['domainname']

    filename = "/home/ncloud/test/"+str(name) + ".img"

    conn = libvirt.open('qemu://192.168.122.109/system')
    if conn == None:
        return "Connection Failed"

    dom = conn.lookupByName(name)
    if dom == None:
        return ("Cannot find guest to be saved")

    info = dom.info()
    if info == None:
        return ("Cannot check domain state")

    if info[0] == libvirt.VIR_DOMAIN_SHUTOFF:
        return ("Cannot save guest that is not running")

    if dom.save(filename) < 0:
        return ("Unable to save guest")

    return ("Guest saved")
