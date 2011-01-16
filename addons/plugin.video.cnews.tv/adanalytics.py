#!/usr/bin/python
import platform, httplib, xml.dom.minidom, socket, os, fcntl, struct, sys, sha, urllib
#, urllib2
import thread

def getHwAddr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]

def clean(name):
	remove=[('\n',''),('"',''),('\'',''),('(',''),(')','')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name


def adIO(adName='plugin.video.none', adHandle=0, adPath=''):

	try:
		for cif in os.listdir('/sys/class/net'):
			if 'eth' in cif:
				shmac = sha.new(getHwAddr(cif).replace(':','').upper()).hexdigest().upper()
				break
	except:
		shmac = ''
	if shmac == '':
		try:
			for line in os.popen('/sbin/ifconfig'):
				if line.find('Ether') > -1:
					mac = line.split()[4]
					break
			shmac = sha.new(mac.replace(':','').upper()).hexdigest().upper()
		except:
			shmac = ''
	if shmac == '':
		try:
			if 'win' in sys.platform:
				for line in os.popen('ipconfig /all'):
					if line.lstrip().startswith('Physical Address'):
						mac = line.split(':')[1].strip().replace('-',':')
						break
			shmac = sha.new(mac.replace(':','').upper()).hexdigest().upper()
		except:
			shmac = ''

	def addElement(Doc, pChild, keyname, keyval):
		newNode = Doc.createElement(keyname)
		newNode.appendChild(Doc.createTextNode(urllib.quote_plus(str(keyval))))
		pChild.appendChild(newNode)

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
	addElement(doc, AdChild, 'shmac', shmac)
	rootelem.appendChild(AdChild)

	doc.appendChild(rootelem)

	#req = urllib2.Request('http://xbmcstat.co.cc/cgi-bin/adc.py', doc.toxml(encoding='utf-8'))
	#f = urllib2.urlopen(req)
	#a = f.read()
	#f.close()

	conn =   httplib.HTTPConnection(host='xbmcstat.co.cc', port=80)
	conn.request(method='POST', url='/cgi-bin/adc.py', body=doc.toxml(encoding='utf-8'))
	#response = conn.getresponse()
	#hdrs = response.getheader('Set-Cookie')
	#if hdrs != None:
	#	print 'Save %s'%hdrs
	#print 'Set-Cookie %s'%hdrs
	#print 'status %d'%response.status
	#print 'reason %s'%response.reason
	#print 'DATA %s'%response.read()
	conn.close()

	print platform.processor()

def main(adName='', adHandle=0, adPath=''):
	try:
		thread.start_new_thread(adIO, (adName, adHandle, adPath))
	except Exception, e:
		print(e)
