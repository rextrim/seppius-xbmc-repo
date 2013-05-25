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




_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Addon = xbmcaddon.Addon(id='script.module.torrent.ts')
language = Addon.getLocalizedString
server_ip=Addon.getSetting('ip_addr')
prt_file=Addon.getSetting('port_path')
if Addon.getSetting('pausable')=='true': pausable=True
else: pausable=False
if Addon.getSetting('autoexit')=='true': autoexit=True
else: autoexit=False
if Addon.getSetting('autobuf')=='true': autobuf=True
else: autobuf=False
if Addon.getSetting('save')=='true': save=True
else: save=False
if save and not Addon.getSetting('folder'): Addon.openSettings()

lock_file = xbmc.translatePath('special://temp/'+ 'ts.lock')
aceport=62062

class TSengine():
    
    def __init__(self):
        self.files=None
        xbmc.Player().stop()
        if xbmc.Player().isPlaying():
            xbmc.sleep(300)
        while os.path.exists(lock_file):
            print Addon.getSetting('stopped')
            print 'wait to stop old ts'
            try: print 'go=%s'%go
            except: print 'no go'
            time.sleep(1.3)
        self.dvijitel=ASengine()
        f = file(lock_file, "w")
        f.close()
        self.error=None
    def load_torrent(self, torrent, mode, host=server_ip, port=aceport ):
        result=self.dvijitel.load_torrent(torrent, mode, host, port)
        if not result: self.error=True
        self.files=self.dvijitel.files
        return result
    def play_url_ind(self, index=0, title='', icon='', thumb=''):
        if not self.error:
            result=self.dvijitel.play_url_ind(index, title, icon, thumb)
            return result
        return result
    def end(self):
        result=self.dvijitel.end()
        return result
class ASengine(xbmc.Player):
    
    def __init__(self):
        
        if hasattr(sys.modules["__main__"], "dbglevel"):
            self.dbglevel = sys.modules["__main__"].dbglevel
            print 'new hasattr'
        else:
            self.dbglevel = 3
            print 'old hasattr'
        
        self.progress = xbmcgui.DialogProgress()
        self.progress.create('AceStream', 'Initialization')

        self.filename=None
        self.ind=None
        self.files=None
        self.mode=self.url=''
        self.active=True
        self.r=None
        self.link=None
        self.paused=False

        self.isStream=False
        
        self.host=None
        self.port=None
        self.mode=None
        self.url=None
        
        self.err=None
        self.active=True
        self.activeplay=False
        #self.stop()
        
        ''' if self.isPlaying():
            xbmc.sleep(300)
        while int(Addon.getSetting('stopped'))!=1 and not self.progress.iscanceled():
            time.sleep(1.3)
        if self.progress.iscanceled():
            self.err=1
            self.progress.close()'''
        
        
        
    def start_win_engine(self):
        try:
            import _winreg
            t = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'Software\\TorrentStream')
            needed_value =  _winreg.QueryValueEx(t , 'EnginePath')[0]
            path= needed_value.replace('tsengine.exe','')
            print needed_value
            try: 
                os.startfile(needed_value)
            except: 
                self.progress.close()
                self.err=1
                return None
            self.progress.update(0,'AceStream','Starting TSEngine','')
            return 1
        except: 
            try:
                import _winreg
                t = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'Software\AceStream')
                needed_value =  _winreg.QueryValueEx(t , 'EnginePath')[0]
                path= needed_value.replace('ace_engine.exe','')
                print needed_value
                try: 
                    os.startfile(needed_value)
                except: 
                    self.progress.close()
                    self.err=1
                    return None
                self.progress.update(0,'AceStream','Starting AceEngine','')
                return 1
            except:
                self.progress.close()
                self.err=1
                return None
            self.progress.close()
            self.err=1
            return None
    
    def start_lin_engine(self):
    
        needed_value='acestreamengine-client-console'
                    
        import subprocess
        st = None
        try: subprocess.Popen(needed_value)
        except: 
            try: 
                subprocess.Popen(Addon.getSetting('prog'))
            except: 
                _tsMessage('AceStream','TSEngine not Installed')
                return None
        
        return 1            
            
    def _TSpush(self,command):
        #print ">>%s"%command
        try:
            _sock.send(command+'\r\n')
        except: 
            print 'send error'

    def conn(self,aceport):
        self.r = _ASpull(1)
        self.r.start()
        comm="HELLOBG"# version=3"
        self._TSpush(comm)

        while not self.r.version and not self.progress.iscanceled():
            time.sleep(0.3)
        if self.progress.iscanceled():
            self.err=1
            self.progress.close()
            return False	
        comm='READY'
        self._TSpush(comm)
        Addon.setSetting('aceport',str(aceport))
        return True
    
    def get_new_port(self):
        if (sys.platform == 'win32') or (sys.platform == 'win64'):
            try:
                import _winreg
                t = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'Software\\TorrentStream')
                needed_value =  _winreg.QueryValueEx(t , 'EnginePath')[0]
                path= needed_value.replace('tsengine.exe','')
                pfile= os.path.join( path,'acestream.port')
                gf = open(pfile, 'r')
                aceport=int(gf.read())
            except: 
                try:
                    import _winreg
                    t = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'Software\\AceStream')
                    needed_value =  _winreg.QueryValueEx(t , 'EnginePath')[0]
                    path= needed_value.replace('ace_engine.exe','')
                    pfile= os.path.join( path,'acestream.port')
                    gf = open(pfile, 'r')
                    aceport=int(gf.read())
                except: return None
            return aceport
        return 62062
    
    def ts_init(self):

        self.progress.update(0,'Progress',"Инициализация","")

        if Addon.getSetting('ip_addr'):
            server_ip=str(Addon.getSetting('ip_addr'))
        else: server_ip='127.0.0.1'
        
        #Get port
        try:
            aceport=int(Addon.getSetting('aceport'))
        except: aceport=62062
        
        #try to connect
        try:
            _sock.connect((server_ip, aceport))
            self.conn(aceport)

        except:
            self.progress.update(0,'Progress',"Попытка запуска движка","")
            if (sys.platform == 'win32') or (sys.platform == 'win64'):
                result=self.start_win_engine()
            else:
                result=self.start_lin_engine()
            if result:
                n=1
                started=None
                while not self.progress.iscanceled() and n!=0:
                    self.progress.update(0,'Progress',"Попытка запуска движка %s"%(n),"")
                    aceport=self.get_new_port()
                    if aceport:
                        try:
                            _sock.connect((server_ip, aceport))
                            started=1
                            print 'Started'
                            n=-1
                        except:
                            started=None
                    time.sleep(1)
                    n=n+1
                    
                if self.progress.iscanceled():
                    self.err=1
                    self.progress.close()
                if started:
                    self.conn(aceport)
            else:
                self.err=1
                print 'not installed'
    
    def load_torrent(self, torrent, mode, host=server_ip, port=aceport ):
        self.host=host
        self.port=port
        self.mode=mode
        self.url=torrent
        self.ts_init()
        if not self.err:
            self.progress.update( 0, "Load",'Start', "" )
            
            if mode!='PID': spons=' 0 0 0'
            else: spons=''
            comm='LOADASYNC '+ str(random.randint(0, 0x7fffffff)) +' '+mode+' ' + torrent + spons
            self._TSpush(comm)
            
            while not self.r.files and not self.progress.iscanceled():
                time.sleep(0.2)
            if self.progress.iscanceled(): 
                self.err=1
                self.progress.close()
                return False
            self.filelist=self.r.files
            self.file_count = self.r.count
            self.files={}
            self.progress.update(89,'Загрузка','')
            if self.file_count>1:
                flist=json.loads(self.filelist)
                for list in flist['files']:
                    self.files[urllib.unquote_plus(urllib.quote(list[0]))]=list[1]
            elif self.file_count==1:
                flist=json.loads(self.filelist)
                list=flist['files'][0]
                self.files[urllib.unquote_plus(urllib.quote(list[0]))]=list[1]
            print self.files
            self.progress.update(100,'Загрузка данных завершена')
            return 'Ok'
            
    def play_url_ind(self, index=0, title='', icon='', thumb=''):
        self.ind=index
        self.r.ind=index
        for k,v in self.files.iteritems():
            if v==self.ind: self.filename=k
        
        if save and os.path.exists((Addon.getSetting('folder')+self.filename)):
            time=0
            i = xbmcgui.ListItem(title)
            i.setProperty('StartOffset', str(time))
            self.play((Addon.getSetting('folder')+self.filename),i)
        else:
            if not self.err:
                self.progress.update( 0, "Play",'Start', "" )
                spons=''
                if self.mode!='PID': spons=' 0 0 0'
                comm='START '+self.mode+ ' ' + self.url + ' '+ str(index) + spons
                self._TSpush(comm)

                while not self.r.got_url and not self.progress.iscanceled() and not self.r.err:
                    
                    if self.r.last_com=='STATUS':
                        try:
                            if self.r.state: self.progress.update(self.r.progress,self.r.state,self.r.label,'')
                        except: pass
                        xbmc.sleep(1000)

                if self.progress.iscanceled() or self.r.err: 
                    self.err=1
                    self.progress.close()
                    return False
                else:
                    self.link=self.r.got_url
                    self.progress.close()
                    self.title=title
                    lit= xbmcgui.ListItem(title, iconImage = thumb, thumbnailImage =thumb)
                    print self.r.got_url
                    self.play(self.r.got_url,lit)
                    self.r.got_url=None
                    self.loop()
                    return 'Ok'      

    def loop(self):
        print 'start loop'
        visible=False
        pos=[0,25,50,75,100]
        while self.active or self.r.ad:
            
            if self.r.event and save:
                print self.r.event
                comm='SAVE %s path=%s'%(self.r.event[0]+' '+self.r.event[1],urllib.quote(Addon.getSetting('folder')+self.filename))
                print comm
                self._TSpush(comm)
                self.r.event=None
                while not os.path.exists((Addon.getSetting('folder')+self.filename)):
                    print 'fcnk loop'
                    xbmc.sleep(300)
                try: time=self.getTime()
                except: time=0
                i = xbmcgui.ListItem(self.title)
                i.setProperty('StartOffset', str(time))
                self.play((Addon.getSetting('folder')+self.filename),i)
                self.active=False
                self.r.ad=False
            if self.r.ad and not self.active:
                self.progress.create(0,'Progress','Init','')
                
                while not self.r.got_url and not self.progress.iscanceled() and not self.r.err:
                    
                    if self.r.last_com=='STATUS':
                        try:
                            if self.r.state: self.progress.updater(self.r.progress,self.r.state,self.r.label)
                        except: pass
                        xbmc.sleep(1000)
                if self.progress.iscanceled() or self.r.err: 
                    self.progress.close()
                    break
                self.progress.close()
                lit= xbmcgui.ListItem(self.title)
                self.play(self.r.got_url,lit)
                self.r.got_url=None
                self.active=True
                pos=[0,25,50,75,100]
            if self.isPlaying() and not self.isStream:
                if self.getTotalTime()>0: cpos= int((1-(self.getTotalTime()-self.getTime())/self.getTotalTime())*100)
                else: cpos=0
                if cpos in pos: 
                    #print cpos
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
        
            xbmc.sleep(1000)
        print 'end loop'
    def end(self):
        print 'ts finally ending'
        try: self.progress.close()
        except: pass
        if not self.err:
            comm="SHUTDOWN"
            self._TSpush(comm)
        if self.r:
            self.r.active=False
            self.r.join(500)
            #self.r=None
        print 'ts shuted up'
        if os.path.exists(lock_file): os.remove(lock_file)
        if self.activeplay and autoexit:
            if sys.platform == 'win32' or sys.platform == 'win64':
                subprocess.Popen('taskkill /F /IM tsengine.exe /T')
    def shut(self):
        pass

    def onPlayBackStarted( self ):
        try: self.duration= int(xbmc.Player().getTotalTime()*1000)
        except: self.duration=0
        comm='DUR '+self.link.replace('\r','').replace('\n','')+' '+str(self.duration)
        self._TSpush(comm)
        comm='PLAYBACK '+self.link.replace('\r','').replace('\n','')+' 0'
        self._TSpush(comm)
        self.activeplay=True
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
        #if not self.r.ad:
        self.end()
    def onPlayBackStopped( self ):
        comm='EVENT stop'
        self._TSpush(comm)
        self.active = False
        self.r.ad = False
        self.end()
    def onPlayBackPaused( self ):
        comm='EVENT pause'
        self._TSpush(comm)
        self.paused=True
    def onPlayBackSeek(self, time, seekOffset):
        comm='EVENT seek position=%s'%(int(time/1000))
        self._TSpush(comm)        
    def __del__(self):
        pass
        
class _ASpull(threading.Thread):

    def _com_received(self,text):

        comm=text.split(' ')[0]
        try:
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
        except: 
            print 'error with text=%s'%text
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
        self.ad=False
        self.err=None
        self.event=None
        self.events=[]
        self.ind=None
        #self.params=[]
        self.temp=''
        print 'Threads %s'%self.getName()
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
            
    
            #xbmc.sleep(500)
        if self.err: print 'need to shut down'
            
    def exec_com(self):
        #print "<<%s"%(self.last_received)
        self.last_com = self._com_received(self.last_received)
        
        if self.last_com=='START' or self.last_com=='PLAY': 
            self.got_url=self.last_received.split(' ')[1].replace('127.0.0.1',server_ip) # если пришло PLAY URL, то забираем себе ссылку
            self.params=self.last_received.split(' ')[2:]
            if len(self.params)>0:
                if 'ad=1' in self.params: 
                    self.ad=True
                    comm='PLAYBACK '+self.got_url.replace('\r','').replace('\n','')+' 100'
                    
                    _sock.send(comm+'\r\n')
                    self.got_url=None
                else: self.ad=False
                if 'stream=1' in self.params: print 'Is Stream'
                #self.ad=True
            #self.params.append('ad=1')
            #self.ad=self.last_received.split(' ')[2]

        elif self.last_com=='STATUS': pass
            
        elif self.last_com=='STATE': 
            self.status=int(self.last_received.split(' ')[1])
        elif self.last_com=='EVENT': 
            if self.last_received.split(' ')[1]=='cansave':
                self.event=self.last_received.split(' ')[2:4]
                ind= self.event[0].split('=')[1]
                print ind
                print self.ind
                if int(ind)!=int(self.ind): self.event=None
                #self.events.append(self.event)
                #print self.events
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

        
