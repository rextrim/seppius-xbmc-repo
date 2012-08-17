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

_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
addon_icon=None

import TSEProgress as progress

#Надо объедениить с TSengine!!!!!!!!!
class myPlayer(xbmc.Player):
	def __init__( self, *args, **kwargs ):
		self.active = True
		self.playl=xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		self.playl.clear()
		self.title='None'
		self.paused=None
		self.resume=None
		self.duration=None
	def playlist_add( self, url, it):
		self.playl.add(url=url, listitem= it)
		
	def play_start(self, ind=0):
		self.play(self.playl)
		self.playselected(ind)
	def onPlayBackStarted( self ):
		self.duration= int(xbmc.Player().getTotalTime()*1000)
	def onPlayBackResumed( self ):
		self.paused = False
	def onPlayBackEnded( self ):
		self.active = False
	def onPlayBackStopped( self ):
		self.active = False
	def onPlayBackPaused( self ):
		self.paused=True
	
class TSengine(object):
	
	def _TSpush(self,command):
		#print '>>'+command
		_sock.send(command+'\r\n')
	
	def __init__(self):
		self.addon_icon=None
		self.ready = False
		self.filelist = None
		self.files = {}
		self.file_count = None
		self.url=None
		self.player=None
		self.playing=False
		self.error_num=None
		self.dialog = progress.DownloadProgress()
		self.dialog.create('Инициализация TS Engine', "")
		self.timeout=10
		self.mode=''
	def load_torrent(self, torrent, mode, host='127.0.0.1', port=62062 ):
		self.dialog.update(0,'Соединяюсь с TS Engine')
		try:
			_sock.connect((host, port))
		except:
			self.dialog.close()
			return False
			exit
		self.mode=mode	
		self.r = _TSpull(1)
		self.r.start()
		comm="HELLOBG"
		self._TSpush(comm)
		self.dialog.update(0,'Жду ответа от TS Engine')
		timeout=self.timeout
		while not self.r.last_com:
			timeout=timeout-1
			if timeout==0: break
			time.sleep(1)
		if timeout==0: 
			self.dialog.update(100,'Ошибка загрузки торрента')
			xbmc.sleep(2000)
			self.dialog.close()
			return 'No responce'
		comm='READY'
		self._TSpush(comm)
		self.ready=True
		self.dialog.update(100,'Передаю торрент')
		self.url=torrent
		comm='LOADASYNC '+ str(random.randint(0, 0x7fffffff)) +' '+mode+' ' + torrent+ ' 0 0 0'
		self._TSpush(comm)
		timeout=self.timeout
		while not self.r.files:
			timeout=timeout-1
			if timeout==0: break
			time.sleep(1)
		if timeout==0: 
			self.dialog.update(100,'Ошибка загрузки торрента')
			xbmc.sleep(2000)
			self.dialog.close()
			return 'Load Failed'	
		self.filelist=self.r.files
		self.file_count = self.r.count
		self.files={}
		if self.file_count>1:
			flist=json.loads(self.filelist)
			for list in flist['files']:
				self.files[list[0]]=list[1]
		elif self.file_count==1:
			flist=json.loads(self.filelist)
			list=flist['files'][0]
			self.files[list[0]]=list[1]
		#print self.files
		#self.dialog.close()
		return 'Ok'
		

	def play_url_ind(self, index=0, title='', icon=None, thumb=None):
		self.dialog.update(0,'Получаю ссылку')
		comm='START '+self.mode+ ' ' + self.url + ' '+ str(index) +' 0 0 0'
		self._TSpush(comm)
		off_timer=180
		while not self.r.got_url:
			if self.r.last_com=='STATUS':
				try:
					if self.r.state: self.dialog.update(self.r.progress,self.r.state,self.r.label)
					#!!!!!!!!!тут буду использовать _com_received вместо ^^^
					
				except: pass
				#print r.last_received
				xbmc.sleep(1000)
				off_timer=off_timer-1
				if off_timer<=0: 
					
					break
		if self.r.got_url:
			plr=myPlayer()
			lit= xbmcgui.ListItem(title, iconImage = thumb, thumbnailImage =thumb)
			self.dialog.update(100,'Начинаю воспроизведение')
			plr.play(self.r.got_url, lit)
			while not plr.duration:
				self.dialog.update(self.r.progress,self.r.state,self.r.label)
				xbmc.sleep(1000)
			self.dialog.close()
			visible=False

			
			while plr.active:
				#!!!!!!!!!1тут буду использовать _com_received
				if plr.duration: 
					comm='DUR '+self.r.got_url.replace('\r','').replace('\n','')+' '+str(plr.duration)
					comm='PLAYBACK '+self.r.got_url.replace('\r','').replace('\n','')+' 0'
					self._TSpush(comm)
					plr.duration=None
				
				if plr.paused: 
					#print 'paused'
					if not visible: 
						#print 'make window'
						self.dialog = progress.DownloadProgress()
						self.dialog.create('Инициализация TS Engine', "")
						self.dialog.update(self.r.progress,self.r.state,self.r.label)
						visible=True
					if visible: self.dialog.update(self.r.progress,self.r.state,self.r.label)
				elif visible:
					#print 'delete window'
					self.dialog.close()
					visible=None
				#print self.r.state
				xbmc.sleep(1000)
			#self.end()
		else: 
			self.dialog.update(0,'Не дождался ссылки')
			time.sleep(3)
		try: self.dialog.close()
		except: pass
	def end(self):
		#print self.r.received
		
		comm="SHUTDOWN"
		self._TSpush(comm)
		self.r.active = False
		#self.r.end()
		_sock.close()
		#print 'Done'
		try: self.dialog.close()
		except: pass
class _TSpull(threading.Thread):

	def _com_received(self,text):
		
		#прогресс (буфферизация, скачано)
		#сиды,пиры и скорости, если будут
		#будет self.state=[progress,state,'seeds/peers']
		try:
			#self.state=None
			#self.progress=0
			#self.label=None
			#print text
			comm=text.split(' ')[1]
			try:
				ss=re.compile('main:[a-z]+',re.S)
				s1=re.findall(ss, text)[0]
				st=s1.split(':')[1]
				#print st
				if st=='prebuf': 
					self.state='Предварительная буфферизация'
					self.progress=int(text.split(';')[1])+0.1
					self.label='Пиры:%s Скорость:%s'%(text.split(';')[6],text.split(';')[3])
				if st=='buf': 
					self.state='Буфферизация'
					self.progress=int(text.split(';')[1])+0.1
					self.label='Пиры:%s Скорость:%s'%(text.split(';')[6],text.split(';')[3])
				if st=='dl': 
					self.state='Скачивание'
					self.progress=int(text.split(';')[1])+0.1
					self.label='Пиры:%s Скорость:%s'%(text.split(';')[6],text.split(';')[3])
				if st=='check': 
					self.state='Проверка'
					self.progress=int(text.split(';')[1])
					self.label=None
				if st=='idle': 
					self.state='TS Engine бездействует'
					self.progress=0
				if st=='wait': 
					self.state='TS Engine ожидает'
					self.label='Секунд %ы'%(text.split(';')[1])
					self.progress=0
				#print self.state
				#print self.label
			except: pass
			#print re.search('main:prebuf;',comm)
			#print re.search('main:dl;',comm)
			return text.split(' ')[0]
		except: return text

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
		self.buffer=50000000			#размер буффера для приема нужен большой, если файлов много
		self.count=None
		self.state=''
		self.label=''
		self.progress=0
	def run(self):
		while self.active:
			try:
				self.last_received=_sock.recv(self.buffer)
				#print self.last_received
				#self.received.append(self.last_received)
				self.last_com = self._com_received(self.last_received)
				
				if self.last_com=='PLAY': self.got_url=self.last_received.split(' ')[1] # если пришло PLAY URL, то забираем себе ссылку
				if self.last_com=='LOADRESP': 
					fil = self.last_received
					ll= fil[fil.find('{'):len(fil)]
					self.files=ll
					#!!!!!!!!запихать файлы в {file:ind}
					#print self.files
					try:
						json_files=json.loads(ll)
						if json_files['status']==2:
							self.count=len(json_files['files'])
						if json_files['status']==1:
							self.count=1
						if json_files['status']==0:
							self.count=None
					except:
						self.count=None
						
			except:
				pass
				
	def end(self):
		self.daemon = False


		