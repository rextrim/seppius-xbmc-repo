#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2011 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
# Writer (c) 2011, Kostynoy S.A., E-mail: seppius2@gmail.com

import sys, xbmc, xbmcgui, xbmcplugin, xbmcaddon
import os, urllib, urllib2, cookielib, base64
import sha
import xml.dom.minidom

addon_id       = 'plugin.video.xbmc.rus'
addon_name     = 'unknown addon'
addon_version  = '0.0.0'
addon_provider = 'unknown'

addon_xml = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'addon.xml'))
if os.path.isfile(addon_xml):
	af = open(addon_xml, 'r')
	adom = xml.dom.minidom.parseString(af.read())
	af.close()
	areg = adom.getElementsByTagName('addon')
	addon_id       = areg[0].getAttribute('id')
	addon_name     = areg[0].getAttribute('name')
	addon_version  = areg[0].getAttribute('version')
	addon_provider = areg[0].getAttribute('provider-name')

__settings__ = xbmcaddon.Addon(id = addon_id)
__language__ = __settings__.getLocalizedString
icon   = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'icon.png'))
h = int(sys.argv[1])

try:
	import json
except ImportError:
	print '[%s]: Error import json. Uses module demjson2.' % addon_id
	import demjson2 as json
try:
	import io, gzip
	AcceptEncoding = 'gzip'
except ImportError:
	print '[%s]: Error import io, gzip. Setting plain accept encoding.' % addon_id
	AcceptEncoding = 'plain'

stimeout = [5,10,15,20,30,45,60,100][int(__settings__.getSetting('timeout'))]
import socket
socket.setdefaulttimeout(stimeout)

def showMessage(heading, message, times = 3000, pics = icon):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading.encode('utf-8'), message.encode('utf-8'), times, pics))
	except:
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, pics))
		except: pass

class TextReader(xbmcgui.Window):
	def __init__(self, txt_data):
		self.bgread = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'resources', 'img', 'background.png'))
		self.setCoordinateResolution(1) # 0 for 1080
		self.addControl(xbmcgui.ControlImage(0, 0, 1280, 720, self.bgread))
		self.NewsTextBox = xbmcgui.ControlTextBox(10,10,1260,700)
		self.addControl(self.NewsTextBox)
		self.NewsTextBox.setText(txt_data)
		self.scroll_pos = 0
	def onAction(self, action):
		aID = action.getId()
		if aID in [1,3,5]:
			self.scroll_pos -= 5
			self.NewsTextBox.scroll(self.scroll_pos)
		elif aID in [2,4,6]:
			self.scroll_pos += 5
			self.NewsTextBox.scroll(self.scroll_pos)
		elif aID in [9,10]: self.close()

def directshowtext(params):
	TextReader(txt_data = params['text']).doModal()

def showtext(params):
	http = GET(params['href'])
	TextReader(txt_data = http).doModal()

def builtin(params):
	try: xbmc.executebuiltin(urllib.unquote_plus(params['href']))
	except: pass

def GET(href, post=None):
	username = __settings__.getSetting('username')
	password = __settings__.getSetting('password')
	token0 = __settings__.getSetting('token0')
	token1 = __settings__.getSetting('token1')
	try:
		sendpw = False
		based = base64.b64decode(__language__(30000))
		if href.startswith('http://') or href.startswith('https://'): target = href
		else:
			target = based + href
			sendpw = True
		CJ = cookielib.CookieJar()
		CP = urllib2.HTTPCookieProcessor(CJ)
		BO = urllib2.build_opener(CP)
		urllib2.install_opener(BO)
		aUA = 'XBMC/%s (%s; %s; %s; http://xbmc.ru)' % (addon_id, urllib.quote_plus(addon_name), addon_version, addon_provider)
		headers = {'Accept-Encoding':AcceptEncoding, 'User-Agent':aUA}
		if sendpw:
			reqhash = sha.new(':%s:%s:%s:%s:'%(token0, token1, password, target)).hexdigest()
			cooks = {'token0':token0, 'token1':token1, 'user':username, 'hash':reqhash}
		else: cooks = {'token0':token0}
		cookstr = urllib.urlencode(cooks)
		headers['Cookie'] = cookstr.replace('&','; ')
		req = urllib2.Request(url = target, data = post, headers = headers)
		resp = urllib2.urlopen(req)
		CE = resp.headers.get('content-encoding')
		if CE == 'bz2':
			import bz2
			http = bz2.decompress(resp.read())
		elif (CE == 'gzip'):
			bindata = io.BytesIO(resp.read())
			gzipf = gzip.GzipFile(fileobj = bindata, mode='rb')
			http = gzipf.read()
		else:
			print '[%s]: Unknown Content-Encoding [%s]' % (addon_id, CE)
			http = resp.read()
		for Cook in CJ:
			#resp.headers.get('set-cookie')
			if   Cook.name == 'token0': __settings__.setSetting('token0', Cook.value)
			elif Cook.name == 'token1': __settings__.setSetting('token1', Cook.value)
		resp.close()
		return http
	except:
		showMessage('HTTP ERROR', href, 5000)

def advt_show(jsdata):
	try:    adv = jsdata['advt']
	except: return
	if adv['type'] == 'showmessage': showMessage(adv['heading'], adv['message'], adv['delay'], adv['picture'])
	elif adv['type'] == 'dialogOK':  xbmcgui.Dialog().ok(adv['heading'],adv['lines'])
	elif adv['type'] == 'textbox':  TextReader(txt_data = adv['text']).doModal()
	else: print '[%s]: Unsupported adv type' % addon_id

def getitems(params):
	vquality = int(__settings__.getSetting('quality'))
	listsize = [10,25,50,100,150,200,250,300][int(__settings__.getSetting('size'))]
	try: href = '%s&size=%s&grade=%s' % (params['href'], listsize, vquality)
	except: href = ''
	try:
		usreq = params['usreq'].lower()
		if usreq == 'keyboard':
			kbd = xbmc.Keyboard()
			kbd.setDefault(params['kbtext'])
			kbd.setHeading(params['kbhead'])
			kbd.setHiddenInput(eval(params['kbmask']))
			kbd.doModal()
			if kbd.isConfirmed():
				answer = kbd.getText()
			else:
				return False
		elif usreq == 'numeric':
			nutype = int(params['nutype'])
			nuhead = params['nuhead']
			nutext = params['nutext']
			answer = xbmcgui.Dialog().numeric(nutype, nuhead, nutext)
			if nutext == answer:
				return False
		elif usreq == 'select':
			sehead = params['sehead']
			selist = params['selist'].split('\n')
			answer = xbmcgui.Dialog().select(sehead, selist)
			if answer == -1:
				return False
		elif usreq == 'yesno':
			ynhead = params['ynhead']
			yntext = params['yntext'].split('\n')
			answer = xbmcgui.Dialog().yesno(addon_name, ynhead, '', '', yntext[0], yntext[1])
		else:
			return False
		href += '&answer=%s' % urllib.quote_plus(answer)
	except: pass

	http = GET(href)
	if http == None: return False
	jsdata = json.loads(http)
	dispitem = 0
	for item in jsdata:
		isitem = False
		try:
			title = item['title']
			uri   = item['uri']
			del item['uri']
			uri = '%s?%s'%(sys.argv[0], uri)
			isitem = True
		except: pass
		if isitem:
			try:
				item_type = item['type']
				del item['type']
			except: item_type = 'video'
			try:
				IsPlayable = item['playable']
				del item['playable']
			except: IsPlayable = False
			try:
				IsFolder = item['folder']
				del item['folder']
			except: IsFolder = False
			try:    ico_img = item['icons'][0]
			except: ico_img = ''
			try:    thu_img = item['icons'][1]
			except: thu_img = ''
			i = xbmcgui.ListItem(title, iconImage = ico_img, thumbnailImage = thu_img)
			try: i.setProperty('fanart_image', item['icons'][2])
			except: pass
			try: del item['icons']
			except: pass
			try:
				conmenu = item['conmenu']
				del item['conmenu']
				cm = []
				for curcm in conmenu:
					cm.append((curcm['name'], 'xbmc.runPlugin(%s?%s)' % (sys.argv[0], curcm['uri'])))
				i.addContextMenuItems(items=cm, replaceItems=True)
			except: pass
			try:
				i.setProperty('mimetype', item['mimetype'])
				del item['mimetype']
			except: pass
			workitem = {}
			for citem in item:
				if item[citem] != None: workitem[citem] = item[citem]
			i.setInfo(type = item_type, infoLabels = workitem)
			if IsPlayable: i.setProperty('IsPlayable', 'true')
			xbmcplugin.addDirectoryItem(h, uri, i, IsFolder)
			dispitem += 1
		else:
			advt_show(item)

	if dispitem > 0:
		xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_UNSORTED)
		xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DATE)
		xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DURATION)
		xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_GENRE)
		xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_TITLE)
		xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_RATING)
		xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
		xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_TITLE)
		xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
		xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_LABEL)
		xbmcplugin.endOfDirectory(h)
	else: return False

def Play_Exec(jsdata):
	#print 'jsdata = ' + jsdata
	selects = []
	jsdata = json.loads(jsdata)
	for item in jsdata:
		try:    title = item['title']
		except: title = 'No title'
		selects.append(title)
	if   len(selects) == 0: return False
	elif len(selects) == 1: s = 0
	else:
		s = xbmcgui.Dialog().select('XBMC-Russia', selects)
		if s < 0: return False
	sjs = jsdata[s]
	advt_show(sjs) # advt
	playables = []

	def parse_plist_section(arrs):
		if len(arrs) == 0: return
		for carr in arrs:
			vid_url = carr['url']
			pappends = ''
			try:
				vproto = carr['proto']
				try:
					vparam = carr['params']
					if vproto == 'rtmp':
						for pkeys in vparam: pappends += ' %s=%s' % (pkeys, vparam[pkeys])
					elif vproto == 'http':
						for pkeys in vparam: pappends += '&%s=%s' % (pkeys, urllib.quote_plus(vparam[pkeys]))
						if pappends != '':   pappends = '|' + pappends[1:]
					else: print '[%s]: Unsupported protocol [%s]' % (addon_id, vproto)
				except: pass
			except: pass
			playables.append(vid_url + pappends)

	try:    parse_plist_section(sjs['video'])
	except: pass
	if len(playables) == 0: return False

	play_path = ''

	if len(playables) > 1:
		play_path = 'stack://'
		for pitem in playables: play_path += pitem.replace(',',',,') + ' , '
		play_path = play_path[:-3]
	elif len(playables) == 1:
		play_path = playables[0]

	i = xbmcgui.ListItem(path=play_path)
	try:    i.setProperty('mimetype', sjs['mimetype'])
	except: pass
	xbmcplugin.setResolvedUrl(h, True, i)

def directplay(params):
	Play_Exec(params['href'])

def play(params):
	http = GET(urllib.unquote_plus(params['href']))
	if http == None: return False
	Play_Exec(http)

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
	if len(param) > 0:
		for cur in param:
			param[cur] = urllib.unquote_plus(param[cur])
	return param

def licenseshow(params):
	LICENSE = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'LICENSE.UTF8.TXT'))
	if os.path.isfile(LICENSE):
		af = open(LICENSE, 'r')
		TextReader(txt_data = af.read()).doModal()
		af.close()
	answer = xbmcgui.Dialog().yesno(addon_name, 'Вы прочитали, принимаете и обязуетесь', 'выполнять условия соглашения?', 'Без этого дополнение не будет работать.', 'Отказаться', 'Принять')
	if answer:
		__settings__.setSetting('LicenseApproved', 'true')
		xbmc.executebuiltin('Container.Refresh')

def addon_main():
	params = get_params(sys.argv[2])
	try:
		func = params['func']
	except:
		LicApp = __settings__.getSetting('LicenseApproved')
		if LicApp == 'true':
			getitems(params)
			func = None
		else:
			xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], 'func=licenseshow'), xbmcgui.ListItem('Читать соглашение'), False)
			xbmcplugin.endOfDirectory(h)
			func = None
	if func != None:
		try: pfunc = globals()[func]
		except:
			pfunc = None
			print '[%s]: Function "%s" not found' % (addon_id, func)
			showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
		if pfunc: pfunc(params)
