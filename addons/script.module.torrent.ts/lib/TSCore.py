#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib
import urllib
import urllib2
import re
import sys
import os
import socket
import threading
import time
import random
import json


import xbmcgui
import xbmc
import xbmcaddon

import TSEProgress as progress

print sys.argv[0]

_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Addon = xbmcaddon.Addon(id='script.module.torrent.ts')
language = Addon.getLocalizedString
addon_icon    = Addon.getAddonInfo('icon')

prt_file=Addon.getSetting('port_path')
if Addon.getSetting('pausable')=='true': pausable=True
else: pausable=False
if Addon.getSetting('autoexit')=='true': autoexit=True
else: autoexit=False
if Addon.getSetting('autobuf')=='true': autobuf=True
else: autobuf=False
server_ip=Addon.getSetting('ip_addr')
aceport=62062

class TSengine(xbmc.Player):

	def onPlayBackStarted( self ):
		try: self.duration= int(xbmc.Player().getTotalTime()*1000)
		except: self.duration=0
		comm='DUR '+self.link.replace('\r','').replace('\n','')+' '+str(self.duration)
		self._TSpush(comm)
		comm='PLAYBACK '+self.link.replace('\r','').replace('\n','')+' 0'
		self._TSpush(comm)
		self.loop()
	def onPlayBackResumed( self ):
		comm='EVENT play'
		self._TSpush(comm)
		self.paused = False
	def onPlayBackEnded( self ):
		comm='EVENT stop'
		self._TSpush(comm)
		comm='PLAYBACK '+self.link.replace('\r','').replace('\n','')+' 100'
		self._TSpush(comm)
		self.active = False
		if not self.isAd:
			self.end()
	def onPlayBackStopped( self ):
		comm='EVENT stop'
		self._TSpush(comm)
		comm='PLAYBACK '+self.link.replace('\r','').replace('\n','')+' 100'
		self._TSpush(comm)
		self.active = False
		if not self.isAd:
			self.end()
	def onPlayBackPaused( self ):
		comm='EVENT pause'
		self._TSpush(comm)
		self.paused=True
	def onPlayBackSeek(self, time, seekOffset):
		comm='EVENT seek position=%s'%(int(time/1000))
		self._TSpush(comm)
	
	def _TSpush(self,command):
		#print ">>%s"%command
		try:
			_sock.send(command+'\r\n')
		except: print 'send error'
	
	def __init__(self):
		self.files=None
		self.mode=self.url=''
		self.active=True
		self.r=None
		self.error=None
		self.link=None
		self.paused=False
		self.isAd=False
		self.isStream=False
		self.timeout=10
		self.title=''
	def loop(self):
		visible=False
		pos=[25,50,75]
		if 'ad=1' in self.r.params: self.isAd=True
		else: self.isAd=False
		while self.active or self.isAd:
			if 'ad=1' in self.r.params: self.isAd=True
			else: self.isAd=False
			if self.isAd and not self.active:
				self.dialog2 = progress.dwprogress()
				self.dialog2.updater(0,language(1004))
				
				while not self.r.got_url and not self.dialog2.ui.isCanceled and not self.r.err:
					
					if self.r.last_com=='STATUS':
						try:
							if self.r.state: self.dialog2.updater(self.r.progress,self.r.state,self.r.label)
						except: pass
						xbmc.sleep(1000)
				self.dialog2.ui.showCancel=False
				if self.dialog2.ui.isCanceled or self.r.err: 
					self.dialog2.close()
					break
				self.dialog2.close()
				lit= xbmcgui.ListItem(self.title)
				self.play(self.r.got_url,lit)
				self.r.params=[]
				self.r.got_url=None
				self.active=True
			if self.isPlaying() and not self.isStream:
				if self.getTotalTime()>0: cpos= int((1-(self.getTotalTime()-self.getTime())/self.getTotalTime())*100)
				else: cpos=0
				if cpos in pos: 
					print cpos
					pos.remove(cpos)
					comm='PLAYBACK '+self.link.replace('\r','').replace('\n','')+' %s'%cpos
					self._TSpush(comm)
			if pausable:
				if self.r.pause==1 and not self.paused:
					self.pause()
					self.r.pause=None
					xbmc.sleep(1000)
				if self.r.pause==0 and self.paused:
					self.pause()
					self.r.pause=None
			else:
				if autobuf:
					if self.r.status==3 and not self.paused:
						self.dialog = progress.dwprogress()
						self.dialog.ui.showCancel=False
						self.dialog.updater(self.r.progress,self.r.state,self.r.label)
						visible=True
					elif visible and not self.paused:
						self.dialog.close()
						visible=False
			if self.paused: 
				if not visible: 
					self.dialog = progress.dwprogress()
					self.dialog.ui.showCancel=False
					self.dialog.updater(self.r.progress,self.r.state,self.r.label)
					visible=True
				else: self.dialog.updater(self.r.progress,self.r.state,self.r.label)
			elif visible:
				self.dialog.close()
				visible=False
			#if self.isPlaying(): print self.getTime()
			xbmc.sleep(1000)
	def __del__(self):
		#print "destroyed"
		pass
	
	def ace_init(self,host,port):
				
		if Addon.getSetting('ip_addr'):
			server_ip=Addon.getSetting('ip_addr')
		else: server_ip='127.0.0.1'
		
		try:
			aceport=int(Addon.getSetting('aceport'))
		except: aceport=62062
		
		try:
			_sock.connect((server_ip, aceport))
			print aceport
		except:
			aceport=62062
			if (sys.platform == 'win32') or (sys.platform == 'win64'):
				try:
					import _winreg
					t = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'Software\\TorrentStream')
					needed_value =  _winreg.QueryValueEx(t , 'EnginePath')[0]
					path= needed_value.replace('tsengine.exe','')
					print path
					pfile= os.path.join( path,'acestream.port')
					gf = open(pfile, 'r')
					aceport=int(gf.read())
				except: pass

			try:
				_sock.connect((server_ip, aceport))
			except:
				_tsMessage('AceStream','Try to start TSEngine')
				if (sys.platform == 'win32') or (sys.platform == 'win64'):
					try:
						import _winreg
						t = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'Software\\TorrentStream')
						needed_value =  _winreg.QueryValueEx(t , 'EnginePath')[0]
						path= needed_value.replace('tsengine.exe','')
						print path
						try: 
						#	subprocess.Popen(needed_value,startupinfo=st)
							os.startfile(needed_value)
						except: 
							_tsMessage('AceStream','Cant start TSEngine')
							self.error=1
							return "Cant start TSEngine"
						_tsMessage('AceStream','Starting TSEngine')
						xbmc.sleep(8000)
						pfile= os.path.join( path,'acestream.port')
						gf = open(pfile, 'r')
						aceport=int(gf.read())
					except: 
						_tsMessage('AceStream','TSEngine not Installed')
						self.error=1
						return "TSEngine not Installed"
				else:
					needed_value='acestreamengine-client-console'
					
					import subprocess
					st = None
					try: subprocess.Popen(needed_value)
					except: 
						try: 
							#os.startfile(Addon.getSetting('prog'))
							subprocess.Popen(Addon.getSetting('prog'))
						except: 
							_tsMessage('AceStream','TSEngine not Installed')
							self.error=1
							return "Cant start TSEngine"
					
					_tsMessage('AceStream','Starting TSEngine')
					xbmc.sleep(8000)
					aceport=62062
				try:
					_sock.connect((server_ip, aceport))
				except:
					_tsMessage('AceStream','Cant start TSEngine')
					self.error=1
					return "Cant start TSEngine"
		self.r = _ASpull(1)
		self.r.start()
		comm="HELLOBG"# version=3"
		self._TSpush(comm)
		timeout=self.timeout
		while not self.r.version:
			timeout=timeout-1
			if timeout==0: break
			time.sleep(1)
		if timeout==0: 
			xbmc.sleep(2000)
			self.error=1
			return 'Load Failed'	
		comm='READY'
		self._TSpush(comm)
		Addon.setSetting('aceport',str(aceport))
		return "ok"
	
	def load_torrent(self, torrent, mode, host=server_ip, port=aceport ):
		host=server_ip
		port=aceport
		print self.ace_init(host,port)
		if self.error: return False
		self.mode=mode
		self.url=torrent
		self.dialog = progress.dwprogress()
		self.dialog.updater(0,language(1001))
		spons=''
		if mode!='PID': spons=' 0 0 0'
		
		comm='LOADASYNC '+ str(random.randint(0, 0x7fffffff)) +' '+mode+' ' + torrent + spons
		self._TSpush(comm)

		
		print 'send ok'
		
		timeout=self.timeout
		while not self.r.files:
			timeout=timeout-1
			if timeout==0: break
			time.sleep(1)
		if timeout==0: 
			self.dialog.updater(100,language(1012))
			xbmc.sleep(2000)
			self.dialog.close()
			return 'Load Failed'	
		self.filelist=self.r.files
		self.file_count = self.r.count
		self.files={}
		self.dialog.updater(89)
		if self.file_count>1:
			flist=json.loads(self.filelist)
			for list in flist['files']:
				self.files[urllib.unquote_plus(urllib.quote(list[0]))]=list[1]
		elif self.file_count==1:
			flist=json.loads(self.filelist)
			list=flist['files'][0]
			self.files[urllib.unquote_plus(urllib.quote(list[0]))]=list[1]
		self.dialog.close()
		return 'Ok'

	def play_url_ind(self, index=0, title='', icon=None, thumb=None):
		if not self.error:
			self.dialog2 = progress.dwprogress()
			self.dialog2.updater(0,language(1004))
			
			spons=''
			if self.mode!='PID': spons=' 0 0 0'
			comm='START '+self.mode+ ' ' + self.url + ' '+ str(index) + spons
			self._TSpush(comm)

			while not self.r.got_url and not self.dialog2.ui.isCanceled and not self.r.err:
				
				if self.r.last_com=='STATUS':
					try:
						if self.r.state: self.dialog2.updater(self.r.progress,self.r.state,self.r.label)
					except: pass
					xbmc.sleep(1000)
			self.dialog2.ui.showCancel=False
			if self.dialog2.ui.isCanceled or self.r.err: 
				self.dialog2.close()
				return False
			else:
				self.dialog2.ui.showCancel=False
				self.link=self.r.got_url
				self.dialog2.close()
				self.title=title
				lit= xbmcgui.ListItem(title, iconImage = thumb, thumbnailImage =thumb)
				self.play(self.r.got_url,lit)
				self.r.got_url=None
				self.r.params=[]
				self.loop()
				return 'Ok'

	def get_url_ind(self, index=0, title='', icon=None, thumb=None):
		if self.error: return False
		self.dialog2 = progress.dwprogress()
		self.dialog2.updater(0,language(1004))
		addstr=''
		if self.mode != 'PID': addstr= ' 0 0 0'
		comm='START ' + self.mode + ' ' + self.url + ' ' + str(index) + addstr
		self._TSpush(comm)
		
		while not self.r.got_url and not self.dialog2.ui.isCanceled and not self.r.err:
			
			if self.r.last_com=='STATUS':
				try:
					if self.r.state: self.dialog2.updater(self.r.progress,self.r.state,self.r.label)
				except: pass
				xbmc.sleep(1000)
		self.dialog2.ui.showCancel=False
		if self.dialog2.ui.isCanceled or self.r.err:
			self.dialog2.close()
			return False
		else:
			self.dialog2.ui.showCancel=False
			self.link=self.r.got_url
			self.dialog2.close()
			return self.r.got_url
	

		
		
	def end(self):
		if not self.error:
			comm="SHUTDOWN"
			self._TSpush(comm)
		if self.r:
			self.r.active=False
			self.r.join(500)
			self.r=None
		_sock.close()
		if autoexit:
			if (sys.platform == 'win32') or (sys.platform == 'win64'):
				

				import subprocess
				st = subprocess.STARTUPINFO()
				st.dwFlags |= 1
				try: 
					#os.startfile('taskkill /F /IM tsengine.exe')
					subprocess.Popen('taskkill /F /IM tsengine.exe', stdin= subprocess.PIPE, stdout= subprocess.PIPE, stderr= subprocess.PIPE,shell= False,startupinfo=st)
				except: 
					_tsMessage('AceStream','Cant stop TSEngine')

				
		#print "ended"
		
class _ASpull(threading.Thread):

	def _com_received(self,text):

		comm=text.split(' ')[0]
		if comm=="STATUS":
			ss=re.compile('main:[a-z]+',re.S)
			s1=re.findall(ss, text)[0]
			st=s1.split(':')[1]
			if st=='prebuf': 
				self.state=language(1100)
				self.progress=int(text.split(';')[1])+0.1
				self.label=language(1150)%(text.split(';')[8],text.split(';')[5])
				self.speed=int(text.split(';')[5])
			if st=='buf': 
				self.state=language(1101)
				self.progress=int(text.split(';')[1])+0.1
				self.label=language(1150)%(text.split(';')[8],text.split(';')[5])
			if st=='dl': 
				self.state=language(1102)
				self.progress=int(text.split(';')[1])+0.1
				self.label=language(1150)%(text.split(';')[6],text.split(';')[3])
			if st=='check': 
				self.state=language(1103)
				self.progress=int(text.split(';')[1])
				self.label=None
				self.speed=1
			if st=='idle': 
				self.state=language(1104)
				self.progress=0
			if st=='wait': 
				self.state=language(1105)
				self.label=language(1151)%(text.split(';')[1])
				self.progress=0
			if st=='err': 
				self.err=1
				#print 'error'
		return comm

	def __init__(self,interval):
		threading.Thread.__init__(self)
		self.daemon = True
		self.interval = interval	#Я не пользуюсь, возможно пригодится, если будет тормозить
		self.active = True			#Если пошлем False - поток остановится и перестанет принимать данные
		self.lastresolt=None		
		self.received = []			#Тут хранится все, что пришло от сервера ТС (пригодится, я думаю)
		self.last_received=None		#Последний ответ от ТССервера
		self.last_com=None			#Последняя команда от ТССервера
		self.got_url=None			#Будет ссылка на файл после буфферизации
		self.files=None				#Список файлов в json
		self.buffer=5000000			#размер буффера для приема нужен большой, если файлов много
		self.count=None
		self.state=''
		self.status=None
		self.label=''
		self.progress=0
		self.filestemp=None
		self.speed=0
		self.pause=None
		self.version=None
		self.ad=''
		self.err=None
		#self.params=[]
		self.temp=''
	def run(self):
		while self.active and not self.err:
			try:
				self.last_received=_sock.recv(self.buffer)
			except: self.last_received=''
			#print self.last_received
			ind=self.last_received.find('\r\n')
			cnt=self.last_received.count('\r\n')

			if ind!=-1 and cnt==1:
				self.last_received=self.temp+self.last_received[:ind]
				self.temp=''
				#print self.last_received
				self.exec_com()
			elif cnt>1:
				fcom=self.last_received
				ind=1
				while ind!=-1:
					ind=fcom.find('\r\n')
					self.last_received=fcom[:ind]
					#print self.last_received
					self.exec_com()
					fcom=fcom[(ind+2):]
			elif ind==-1: 
				self.temp=self.temp+self.last_received
				self.last_received=None
			
	
			xbmc.sleep(500)
		if self.err: print 'need to shut down'
			
	def exec_com(self):
		#print "<<%s"%(self.last_received)
		self.last_com = self._com_received(self.last_received)
		
		if self.last_com=='START' or self.last_com=='PLAY': 
			self.got_url=self.last_received.split(' ')[1].replace('127.0.0.1',server_ip) # если пришло PLAY URL, то забираем себе ссылку
			self.params=self.last_received.split(' ')[2:]
			if len(self.params)>0:
				if 'ad=1' in self.params: print 'Have Ad'
				if 'stream=1' in self.params: print 'Is Stream'
			#self.params.append('ad=1')
			#self.ad=self.last_received.split(' ')[2]

		elif self.last_com=='STATUS': pass
			
		elif self.last_com=='STATE': 
			self.status=int(self.last_received.split(' ')[1])
		elif self.last_com=='EVENT': pass
		elif self.last_com=='RESUME': self.pause=0
		elif self.last_com=='PAUSE': self.pause=1
		elif self.last_com=='HELLOTS': 
			try: self.version=self.last_received.split(' ')[1].split('=')[1]
			except: self.version='1.0.6'
		elif self.last_com=='LOADRESP': 
			fil = self.last_received
			ll= fil[fil.find('{'):len(fil)]
			self.fileslist=ll
		
			json_files=json.loads(self.fileslist)
			aa=json_files['infohash']
			if json_files['status']==2:
				self.count=len(json_files['files'])
			if json_files['status']==1:
				self.count=1
			if json_files['status']==0:
				self.count=None
			self.files=self.fileslist.split('\n')[0]
			self.fileslist=None
		#self.pause=None
	#except:
	#	pass

	def end(self):
		self.daemon = False
		
def _tsMessage(heading, message, times = 3000, pics = addon_icon):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), timeds, pics.encode('utf-8')))
	except Exception, e:
		xbmc.log( '_tsMessage: Transcoding UTF-8 failed [%s]' % (e), 2 )
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			xbmc.log( '_tsMessage: exec failed [%s]' % (e), 3 )