#!/usr/bin/python
import os, sys

def GetHWAddr():
	MAC = None
	def GetHWAddr_Linux():
		MAC = None
		try:
			import fcntl, struct, socket
			def getHwAddr(ifname):
				s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
				return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]
			for cif in os.listdir('/sys/class/net'):
				if 'eth' in cif:
					MAC = getHwAddr(cif).replace(':','').replace('-','').upper()
					if len(MAC) == 12:
						return MAC
					else:
						MAC = None
		except:
			MAC = None
		return MAC

	def ExecPopenMAC(fname):
		try:
			import re, subprocess, sys, popen2
			fin, fout = popen2.popen2(fname, mode='b')
			for line in fin.readlines():
				macrow = re.compile('(?i)(.[0-9a-f]+)[:-](.[0-9a-f]+)[:-](.[0-9a-f]+)[:-](.[0-9a-f]+)[:-](.[0-9a-f]+)[:-](.[0-9a-f]+)').findall(line)
				for cmr in macrow:
					ssrow = cmr[0] + cmr[1] + cmr[2] + cmr[3] + cmr[4] + cmr[5]
					MAC = ssrow.replace(' ','').replace(':','').replace('-','')
					if len(MAC) == 12:
						return MAC
					else:
						MAC = None
		except:
			return None
	if 'darwin' in sys.platform.lower() :
		MAC = ExecPopenMAC('/sbin/ifconfig')
	elif 'win' in sys.platform.lower() :
		MAC = ExecPopenMAC('ipconfig /all')


	if MAC == None:
		MAC = GetHWAddr_Linux()
	if MAC == None:
		MAC = ExecPopenMAC('ifconfig')
	if MAC == None:
		MAC = ExecPopenMAC('/sbin/ifconfig')
	if MAC == None:
		MAC = ExecPopenMAC('ipconfig /all')
	return MAC




def adIO(adName, adHandle, adPath):
	import urllib, socket
	socket.setdefaulttimeout(10)
	SHMAC = ''
	MAC_ADDR = GetHWAddr()
	if MAC_ADDR != None:
		import sha
		SHMAC = sha.new(MAC_ADDR).hexdigest().upper()

	def addElement(Doc, pChild, keyname, keyval):
		newNode = Doc.createElement(keyname)
		newNode.appendChild(Doc.createTextNode(urllib.quote_plus(str(keyval))))
		pChild.appendChild(newNode)

	import xml.dom.minidom, platform
	doc = xml.dom.minidom.Document()

	rootelem = doc.createElement('analytics')

	PyChild = doc.createElement('platform_python')
	addElement(doc, PyChild, 'build', platform.python_build())
	addElement(doc, PyChild, 'compiler', platform.python_compiler())
	addElement(doc, PyChild, 'version', platform.python_version())
	rootelem.appendChild(PyChild)

	SyChild = doc.createElement('platform_system')
	addElement(doc, SyChild, 'architecture', platform.architecture())
	addElement(doc, SyChild, 'machine', platform.machine())
	addElement(doc, SyChild, 'node', platform.node())
	addElement(doc, SyChild, 'platform', platform.platform())
	addElement(doc, SyChild, 'processor', platform.processor())
	addElement(doc, SyChild, 'release', platform.release())
	addElement(doc, SyChild, 'system', platform.system())
	addElement(doc, SyChild, 'version', platform.version())
	addElement(doc, SyChild, 'uname', platform.uname())
	rootelem.appendChild(SyChild)

	AdChild = doc.createElement('addon')
	addElement(doc, AdChild, 'name', adName)
	addElement(doc, AdChild, 'handle', adHandle)
	addElement(doc, AdChild, 'path', adPath)
	addElement(doc, AdChild, 'shmac', SHMAC)
	rootelem.appendChild(AdChild)

	doc.appendChild(rootelem)

	import httplib
	conn =   httplib.HTTPConnection(host='xbmcstat.co.cc', port=80)
	conn.request(method='POST', url='/cgi-bin/adc.py', body=doc.toxml(encoding='utf-8'))
	#response = conn.getresponse()
	#hdrs = response.getheader('Set-Cookie')
	#if hdrs != None: print 'Save %s'%hdrs
	#print 'Set-Cookie %s'%hdrs
	#print 'status %d'%response.status
	#print 'reason %s'%response.reason
	#print 'DATA %s'%response.read()
	conn.close()

