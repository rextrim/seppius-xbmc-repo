#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *	  Copyright (C) 2010 Kostynoy S. aka Seppius
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# */




import urllib, urllib2, re, sys, os
import xbmcplugin, xbmcgui, xbmcaddon
import base64, popen2

__settings__ = xbmcaddon.Addon(id='plugin.program.ifconfig')
__language__ = __settings__.getLocalizedString

icon	= xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))
img_dns = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'resources','Crystal_128_yast_dns.png'))
img_eth = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'resources','ethernet-card-Vista-icon.png'))

iFile = '/etc/network/interfaces'
#iFile = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'resources', 'interfaces'))
lsNet = '/sys/class/net'
Names = '/etc/resolv.conf'

h = int(sys.argv[1])

def showMessage(heading, message, times = 3000):
	#heading = heading.encode('utf-8')
	#message = message.encode('utf-8')
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))



# # # # # # # # ПОЛУЧЕНИЕ ПАРОЛЯ # # # # # # # #
def GetSudoPass():
	savep = __settings__.getSetting('savep')
	if savep == 'false': __settings__.setSetting('sp','')
	digest_key = __settings__.getSetting('sp')
	if len(digest_key) == 0:
		kbd = xbmc.Keyboard()
		kbd.setHiddenInput(True)
		kbd.setHeading('Sudo password')
		kbd.doModal()
		if (kbd.isConfirmed()):
			SudoPass = kbd.getText()
			if savep == 'true': __settings__.setSetting('sp', base64.b64encode(SudoPass))
		else:
			return False
	else:
		SudoPass =  base64.b64decode(digest_key)
	return SudoPass


# # # # # # # # ВЫПОЛНЕНИЕ CMD # # # # # # # #
def SudoExec(cmd):
	xbmc.output('def SudoExec(%s):'%cmd)
	RetA = []
	fin, fout = popen2.popen2('echo %s|sudo -Sk "%s"'%(GetSudoPass(), cmd))
	for line in fin.readlines():
		line = line.replace('\t',' ')
		line = ' '.join(line.split())
		if len(line) > 0:
			xbmc.output('[SudoExec] %s'%line)
			RetA.append(line)
	fin.close()
	fout.close()
	return RetA

# # # # # # # # ЧТЕНИЕ ФАЙЛА (убирает пробелы, табуляции и комменты) # # # # # # # #
def ReadFile(fname):
	RetA = []
	try:
		f = open(fname, 'r')
		for line in f:
			line = line.replace('\t',' ')
			line = ' '.join(line.split())
			if len(line) > 0:
				if line[0] != '#':
					RetA.append(line)
	except:
		showMessage('ПЛОХОЙ ФАЙЛ', fname, 5000)
	return RetA




def ifconfig_root():
	lst = SudoExec('ifconfig')
	ifdata = ''
	for l in lst:
		if 'Link encap' in l: l = '\n' + l
		ifdata += l+'\n'
	ifdata += '\n'

	for cif in os.listdir(lsNet):

		info = ' '
		r1 = re.compile('%s\s(.+?)\n\n'%cif, re.DOTALL).findall(ifdata)
		if len(r1) == 1:
			#print r1[0]

			r2 = re.compile('inet addr:\s*(.[0-9|:|.|/]*)').findall(r1[0])
			if len(r2) > 0:
				info += 'IPv4 Addr: %s '%r2[0]

			#r3 = re.compile('Mask:\s*(.[0-9|:|.|/]*)').findall(r1[0])
			#if len(r3) > 0:
			#	info += 'IPv4 Mask: %s '%r3[0]

			r4 = re.compile('inet6 addr:\s*(.[a-z0-9:./]*)').findall(r1[0])
			if len(r4) > 0:
				info += 'IPv6 Addr: %s '%r4[0]
		#

		if len(info) > 2:
			txt = '%s (%s)'%(cif,info)
		else:
			txt = txt = '%s (%s)'%(cif,'DOWN')
		info = ''

		i = xbmcgui.ListItem(txt, iconImage=img_eth, thumbnailImage=img_eth)
		u = sys.argv[0] + '?mode=IFOPEN'
		u += "&ifac="		+ urllib.quote_plus(cif)
		xbmcplugin.addDirectoryItem(h, u, i, True)

	i = xbmcgui.ListItem('Настройка DNS', iconImage=img_dns, thumbnailImage=img_dns)
	u = sys.argv[0] + '?mode=DNS'
	xbmcplugin.addDirectoryItem(h, u, i, True)

	xbmcplugin.endOfDirectory(h)


def open_dns():
	data = ReadFile(Names)
	for line in data:
		print line
		r1 = re.compile('nameserver (.*?)#').findall(line + '#')
		i = xbmcgui.ListItem(r1[0], iconImage=img_dns, thumbnailImage=img_dns)
		u = sys.argv[0] + '?mode=EditDNS'
		u += "&LastIP=" + urllib.quote_plus(r1[0])
		xbmcplugin.addDirectoryItem(h, u, i)
	xbmcplugin.endOfDirectory(h)


def open_ifac(ifac):
	data = ReadFile(iFile)

	for row in data:
		if 'auto %s'%ifac in row:
			i = xbmcgui.ListItem('auto %s'%ifac, iconImage=img_eth, thumbnailImage=img_eth)
			u = sys.argv[0] + '?mode=EditETH'
			xbmcplugin.addDirectoryItem(h, u, i)

	isFin = False
	StEed = False
	for row in data:
		print row
		if (('iface' in row) and (ifac in row.split(' '))): isFin = True
		if (isFin and StEed and ('iface ' in row)): isFin = False
		if isFin and not ('auto' in row):
			i = xbmcgui.ListItem(row, iconImage=img_eth, thumbnailImage=img_eth)
			u = sys.argv[0] + '?mode=EditETH'
			xbmcplugin.addDirectoryItem(h, u, i)
			StEed = True


	xbmcplugin.endOfDirectory(h)




def get_params(paramstring):
	param=[]
	if len(paramstring)>=2:
		params=paramstring
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	return param

params=get_params(sys.argv[2])

mode = None
ifac = None

try:	mode = urllib.unquote_plus(params['mode'])
except: pass

try:	ifac = urllib.unquote_plus(params['ifac'])
except: pass

xbmc.output('# Initial params mode = %s' % mode)
xbmc.output('# Initial params ifac = %s' % ifac)


if mode == None:
	ifconfig_root()

if mode == 'DNS':
	open_dns()

if mode == 'IFOPEN':
	open_ifac(ifac)
