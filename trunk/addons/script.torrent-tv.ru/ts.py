# Copyright (c) 2010-2011 Torrent-TV.RU
# Writer (c) 2011, Welicobratov K.A., E-mail: 07pov23@gmail.com

#imports
import xbmc
import xbmcaddon
import xbmcgui

import sys
import socket
import os
import threading
import subprocess
import random
import json
import urllib
import copy
import time

#from player import MyPlayer
from adswnd import AdsForm


#defines
ADDON = xbmcaddon.Addon( id = 'script.torrent-tv.ru' )
ADDON_PATH = ADDON.getAddonInfo('path')
DEFAULT_TIMEOUT = 125

#functions
def LogToXBMC(text, type = 1):
    ttext = ''
    if type == 2:
        ttext = 'ERROR:'

    PLUGIN_DATA_PATH = ADDON.getAddonInfo('path')
    log = open(PLUGIN_DATA_PATH + '/ts.log', 'a')
    log.write('[TSEngine %s] %s %s\r' % (time.strftime('%X'),ttext, text))
    log.close()
    del log

#classes
class TSengine(xbmc.Player):
    MODE_TORRENT = 'TORRENT'
    MODE_INFOHASH = 'INFOHASH'
    MODE_RAW = 'RAW'
    MODE_PID = 'PID'
    MODE_NONE = None

    def onPlayBackStopped(self):
        if not self.amalker:
            LogToXBMC('STOP')
            #self.parent.player.close()
            self.end()
        else:
            self.parent.amalkerWnd.close()

    def onPlayBackStarted(self):
        pass
        LogToXBMC('%s %s %s' % (xbmcgui.getCurrentWindowId(), self.amalker, self.getPlayingFile()))
        if not self.amalker:
            #self.parent.player.show()
            pass
        else:
            pass
            LogToXBMC('SHOW ADS Window')
            self.parent.amalkerWnd.show()
            LogToXBMC('END SHOW ADS Window')

    def startTS(self, path):
        if (sys.platform == 'win32') or (sys.platform == 'win64'):
            try:
                os.startfile(path)
            except Exception, e: 
                self.last_error = '%s' % e
                LogToXBMC('RunProcess %s' % e, 2)

    def connectToTS(self):
        try:
            print 'Подключение к TS %s %s ' % (self.server_ip, self.aceport)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(60)
            self.sock.connect((self.server_ip, self.aceport))
        except Exception, e:
            print 'Ошибка подключения %s' % e
            if ((sys.platform == 'win32') or (sys.platform == 'win64')) and self.server_ip == '127.0.0.1':
                try:
                    print 'Считываем порт'
                    import _winreg
                    t = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'Software\\TorrentStream')
                    print 'Получили нужную ветку реестра'
                    self.ts_path =  _winreg.QueryValueEx(t , 'EnginePath')[0]
                    print 'Получили нужный ключ'
                    _winreg.CloseKey(t)
                    
                    path= self.ts_path.replace('tsengine.exe','').decode('utf-8')
                    print 'Местонахождение tsengine %s' % path.encode('utf-8')
                    self.pfile= os.path.join( path,'acestream.port')
                    if not os.path.exists(self.pfile):
                        if self.parent: self.parent.showStatus("Запуск TS")
                        a = 0
                        self.startTS(self.ts_path)
                        while not os.path.exists(self.pfile):
                            a = a + 1
                            if a >= 30:
                                if self.parent: self.parent.showStatus("Запуск TS")
                                raise Exception("Не возможно запустить TS")
                            xbmc.sleep(1000)
                    print 'Aceport найден'
                    if self.parent: self.parent.hideStatus()
                    print 'Открытие файла'
                    gf = open(self.pfile, 'r')
                    self.aceport=int(gf.read())
                    gf.close()
                    del gf
                    ADDON.setSetting('port', '%s' % self.aceport)
                    print 'Порт считан. Переподключаемся'
                    self.connectToTS()
                    return
                except Exception, e:
                    LogToXBMC('connectToTS: %s' % e)
                    return
            else:
                LogToXBMC('ConnectToTS: %s' % e)
                return
        print 'Все ок'
        self.thr = SockThread(self.sock)
        self.thr.state_method = self.showState
        self.thr.owner = self
        self.thr.start()

        self.sendCommand('HELLOBG version=3')
        self.Wait(TSMessage.HELLOTS)
        msg = self.thr.getTSMessage()
        if msg.getType() == TSMessage.HELLOTS:
            if msg.getParams()['version'].find('2.0') == -1:
                strerr = 'Unsupport TS version %s' % msg.getParams()['version']
                if self.parent: self.parent.showStatus("Не поддерживаемая версия TS")
                self.last_error = strerr
                LogToXBMC('init: %s' % strerr, 2)
                self.thr.msg = TSMessage()
                self.end()
                return
        else:
            self.last_error = 'Incorrect msg from TS'
            if self.parent: self.parent.showStatus("Неверный ответ от TS. Операция прервана")
            LogToXBMC('Incorrect msg from TS %s' % msg.getType(), 2)
            self.end()
            return
        self.thr.msg = TSMessage()
        LogToXBMC('Send READY')
        self.sendCommand('READY')
        self.Wait(TSMessage.AUTH)
        msg = self.thr.getTSMessage()
        if msg.getType() == TSMessage.AUTH:
            if msg.getParams() == '0':
                LogToXMC('Пользователь не зарегестрирован', 2)
                self.last_error = 'Пользователь не зарегестрирован'
                self.end()
                return
        else:
            self.last_error = 'Incorrect msg from TS'
            LogToXBMC('Incorrect msg from TS %s' % msg.getType(), 2)
            if self.parent: self.parent.showStatus("Неверный ответ от TS. Операция прервана")
            self.end()
            return

        self.thr.msg = TSMessage()
        LogToXBMC('End Init TSEngine')
        if self.parent: self.parent.hideStatus()
        
    def __init__(self, parent = None, ipaddr = '127.0.0.1'):
        LogToXBMC("Init TSEngine")
        self.last_error = None
        self.quid = 0
        self.torrent = ''
        self.amalker = False
        self.parent = parent
        self.stream = False
        self.playing = False
        self.ts_path = ''
       
        LogToXBMC(ADDON.getSetting('ip_addr'))
        if ADDON.getSetting('ip_addr'):
            self.server_ip=ADDON.getSetting('ip_addr')
        else:
            self.server_ip = ipaddr
            ADDON.setSetting('ip_addr', ipaddr)
        if ADDON.getSetting('web_port'):
            self.webport = ADDON.getSetting('webport')
        else:
            self.webport = '6878'
        if ADDON.getSetting('port'):
            self.aceport = int(ADDON.getSetting('port'))
        else:
            self.aceport = 62062
        
        try:
            self.connectToTS()
            LogToXBMC('Connected to TS')
        except Exception, e:
            LogToXBMC('ERROR Connect to TS: %s' % e, 2)
            return
        
    def sendCommand(self, cmd):
        try:
            LogToXBMC('Send command %s' % cmd)
            self.sock.send(cmd + '\r\n')
        except Exception, e:
            try:
                self.connectToTS()
            except Exception, e:
                self.thr.active = False
                self.parent.close()
                LogToXBMC('ERROR Send command: %s' % e)
    
    def Wait(self, msg):
        a = 0
        while self.thr.getTSMessage().getType() != msg and not self.thr.error:
            xbmc.sleep(DEFAULT_TIMEOUT)
            if not self.stream: xbmc.sleep(DEFAULT_TIMEOUT)
            a = a + 1
            if a >= 250:
                LogToXBMC('TS is freeze', 2)
                if self.parent: self.parent.showStatus("Ошибка ожидания. Операция прервана")
                self.end()
                return

    def load_torrent(self, torrent, mode):
        cmdparam = ''
        self.mode = mode
        if mode != TSengine.MODE_PID:
            cmdparam = ' 0 0 0'
        self.quid = str(random.randint(0, 0x7fffffff))
        self.torrent = torrent
        comm = 'LOADASYNC ' + self.quid + ' ' + mode + ' ' + torrent + cmdparam
        if self.parent: self.parent.showStatus("Загрузка торрента")
        self.sendCommand(comm)
        self.Wait(TSMessage.LOADRESP)
        msg = self.thr.getTSMessage()
        LogToXBMC('load_torrent - %s' % msg.getType())
        if msg.getType() == TSMessage.LOADRESP:
            try:
                jsonfile = msg.getParams()['json']
                if not jsonfile.has_key('files'):
                    self.parent.showStatus(jsonfile['message'])
                    self.last_error = Exception(jsonfile['message'])
                    return
                self.count= len(jsonfile['files'])
                self.files = {}
                for file in jsonfile['files']:
                    self.files[file[1]] = urllib.unquote_plus(urllib.quote(file[0]))
            except Exception, e:
                LogToXBMC(e, 2)
                self.last_error = e
                self.end()
        else:
            self.last_error = 'Incorrect msg from TS'
            if self.parent: self.parent.showStatus("Неверный ответ от TS. Операция прервана")
            LogToXBMC('Incorrect msg from TS %s' % msg.getType(), 2)
            self.end()
            return

        LogToXBMC("Load Torrent: %s, mode: %s" % (torrent, mode))
        if self.parent: self.parent.hideStatus()

    def showState(self, state):
        if state.getType() == TSMessage.STATUS and self.parent:
            _params = state.getParams()
            if _params.has_key('main'):
                _descr = _params['main'].split(';')
                if _descr[0] == 'prebuf':
                    LogToXBMC('showState: Пытаюсь показать состояние')
                    self.parent.showStatus('Пребуферизация %s' % _descr[1])
                elif _descr[0] == 'check':
                    LogToXBMC('showState: Проверка %s' % _descr[1])
                    self.parent.showStatus('Проверка %s' % _descr[1])
        elif state.getType() == TSMessage.ERROR:
            self.parent.showStatus(state.getParams())
        LogToXBMC('showState: %s' % state.getParams())
    
    def play_url_ind(self, index=0, title='', icon=None, thumb=None):
        if self.last_error:
            return
        spons = ''
        if self.mode != TSengine.MODE_PID:
            spons = ' 0 0 0'
        comm='START '+self.mode+ ' ' + self.torrent + ' '+ str(index) + spons
        self.sendCommand(comm)
        if self.parent: self.parent.showStatus("Запуск торрента")
        self.Wait(TSMessage.START)
        msg = self.thr.getTSMessage()
        if msg.getType() == TSMessage.START:
            try:
                _params = msg.getParams()
                if not _params.has_key('url'):
                    if self.parent: self.parent.showStatus("Неверный ответ от TS. Операция прервана")
                    raise Exception('Incorrect msg from TS %s' % msg.getType())
                self.play_url = _params['url']
                self.amalker = _params.has_key('ad') and not _params.has_key('interruptable')
                LogToXBMC('Преобразование ссылки')
                self.link = _params['url'].replace('127.0.0.1', self.server_ip).replace('6878', self.webport)
                LogToXBMC('Преобразование ссылки: %s' % self.link)
                self.title = title
                self.icon = icon
                self.playing = True
                self.thr.msg = TSMessage()
                if self.amalker:
                    self.parent.showStatus('Рекламный ролик')
                #    self.parent.player.doModal()
                #else:
                #    self.parent.amalker.show()
                LogToXBMC('Первый запуск. Окно = %s. Реклама = %s' % (xbmcgui.getCurrentWindowId(), self.amalker))
                self.icon = icon
                self.thumb = thumb
                lit= xbmcgui.ListItem(title, iconImage = icon, thumbnailImage = thumb)
                self.play(self.link, lit, windowed = self.amalker)
                self.playing = True
                self.loop()
                LogToXBMC('Цикл')
            except Exception, e:
                LogToXBMC(e, 2)
                self.last_error = e
                if self.parent: self.parent.showStatus("Ошибка. Операция прервана")
                self.end()
        else:
            self.last_error = 'Incorrect msg from TS %s' % msg.getType()
            LogToXBMC(self.last_error, 2)
            if self.parent: self.parent.showStatus("Неверный ответ от TS. Операция прервана")
            self.end()
        LogToXBMC("PlayUrlInd (index: %s, title: %s)" % (index, title))

    def loop(self):
        #xbmc.sleep(500)
        a = 0
        while self.playing:
            #if not self.isPlayingVideo():
            #    break
            if self.isPlayingVideo() and self.amalker and (self.getTotalTime() - self.getTime()) < 0.5:
                self.parent.amalkerWnd.close()
                break
            try:
                xbmc.sleep(250)
            except:
                LogToXBMC('ERROR SLEEPING')
                self.parent.close()
                return
        LogToXBMC('START7 %s' % self.isPlayingVideo())
        if self.amalker:
            self.sendCommand('PLAYBACK ' + self.play_url + ' 100')
            self.Wait(TSMessage.START)
            msg = self.thr.getTSMessage()
            if msg.getType() == TSMessage.START:
                try:
                    LogToXBMC('START1')
                    _params = msg.getParams()
                    if not _params.has_key('url'):
                        raise Exception('Incorrect msg from TS %s' % msg.getType())
                    if _params.has_key('stream') and _params['stream'] == '1':
                        self.stream = True
                    else:
                        self.stream = False
                    LogToXBMC('START2')
                    self.play_url = _params['url'].replace('127.0.0.1', self.server_ip).replace('6878', self.webport)
                    self.amalker = _params.has_key('ad') and not _params.has_key('interruptable')
                    LogToXBMC('START3 %s' % self.play_url)
                    if self.amalker:
                        self.parent.showStatus('Рекламный ролик')
                    LogToXBMC('Повторный запуск. Реклама = %s' % (self.amalker))
                    lit= xbmcgui.ListItem(title, iconImage = self.icon, thumbnailImage = self.thumb)
                    self.play(self.play_url, lit, windowed = self.amalker)
                    self.loop()
                except Exception, e:
                    LogToXBMC(e, 2)
                    self.last_error = e
                    if self.parent: self.parent.showStatus(" Ошибка. Операция прервана")
                    self.end()
            else:
                self.last_error = 'Incorrect msg from TS %s' % msg.getType()
                if self.parent: self.parent.showStatus("Неверный ответ от TS. Операция прервана")
                LogToXBMC(self.last_error, 2)
                self.end()

    def end(self):
        self.sendCommand('STOP')
        self.sendCommand('SHUTDOWN')
        self.last_error = None
        LogToXBMC("Request to close connection")
        self.thr.msg = TSMessage()
        self.thr.active = False
        self.playing = False
        self.sock.close()

    def tsstop(self):
        self.sendCommand('STOP')
        self.playing = False
        self.stop()

class TSMessage:
    ERROR = 'ERROR'
    HELLOTS = 'HELLOTS'
    AUTH = 'AUTH'
    LOADRESP = 'LOADRESP'
    STATUS = 'STATUS'
    STATE = 'STATE'
    START = 'START'
    NONE = ''
    def __init__(self):
        self.type = TSMessage.NONE
        self.params = {}
    
    def getType(self):
        return self.type
    def getParams(self):
        return self.params
    def setParams(self, value):
        self.params = value
    def setType(self, value):
        self.type = value
    


class SockThread(threading.Thread):
    def __init__(self, _sock):
        LogToXBMC('Init SockThread')
        threading.Thread.__init__(self)
        self.daemon = True
        self.sock = _sock
        self.buffer = 65025
        self.isRecv = False
        self.lastRecv = ''
        self.lstCmd = ''
        self.active = True
        self.error = None
        self.msg = TSMessage()
        self.state_method = None
        self.owner = None

    def run(self):
        LogToXBMC('Start SockThread')
        while self.active and not self.error:
            try:
                self.lastRecv = self.lastRecv + self.sock.recv(self.buffer)
                if self.lastRecv.find('\r\n') > -1:
                    cmds = self.lastRecv.split('\r\n')
                    for cmd in cmds:
                        if cmd.replace(' ', '').__len__() > 0:
                            self._constructMsg(cmd)
                            LogToXBMC('RUN Получена комманда = ' + cmd)
                            LogToXBMC('%s' % self.isRecv)
                    self.lastRecv = ''

            except Exception, e:
                self.isRecv = True
                self.active = False
                self.error = e
                LogToXBMC('RECV THREADING %s' % e, 2)
                _msg = TSMessage();
                _msg.type = TSMessage.ERROR
                _msg.params = 'Ошибка соединения с TS'
                self.state_method(_msg)
                #self.owner.parent.close()
        LogToXBMC('Close from threed')

    def _constructMsg(self,  strmsg):
        posparam = strmsg.find(' ')
        _msg = strmsg[:posparam]

        if _msg == TSMessage.HELLOTS:
            self.msg = TSMessage()
            self.msg.setType(TSMessage.HELLOTS)
            _prm = strmsg[posparam+1:].split('=')
            self.msg.setParams({_prm[0]: _prm[1]})
        elif _msg == TSMessage.AUTH:
            self.msg = TSMessage()
            self.msg.setType(TSMessage.AUTH)
            self.msg.setParams(strmsg[posparam+1:])
        elif _msg == TSMessage.LOADRESP:
            self.msg = TSMessage()
            strparams = strmsg[posparam+1:]
            posparam = strparams.find(' ')
            _params = {}
            _params['qid'] = strparams[:posparam]
            _params['json'] = json.loads(strparams[posparam+1:])
            self.msg.setType(TSMessage.LOADRESP)
            self.msg.setParams(_params)
        elif _msg == TSMessage.STATUS:
            buf = strmsg[posparam+1:].split('|')
            _params = {}
            for item in buf:
                buf1 = item.split(':')
                _params[buf1[0]] = buf1[1]
            
            if strmsg.find('err') >= 0:
                raise Exception(strmsg[posparam+1:])
            elif self.state_method:
                self.status = TSMessage()
                self.status.setType(TSMessage.STATUS)
                self.status.setParams(_params)
                self.state_method(self.status)
            else:
                LogToXBMC('I DONT KNOW HOW IT PROCESS %s' % strmsg)
            return
        elif _msg == TSMessage.STATE:
            if self.state_method: 
                self.state = TSMessage()
                self.state.setType(TSMessage.STATE)
                self.state.setParams(strmsg[posparam+1:])
                self.state_method(self.state)
            return
        elif _msg == TSMessage.START:
            self.msg = TSMessage()
            _strparams = strmsg[posparam+1:].split(' ')
            _params = {}
            if _strparams.__len__() >= 2:
                _params['url'] = _strparams[0]
                prms = _strparams[1:]
                for prm in prms:
                    sprm = prm.split('=')
                    _params[sprm[0]] = sprm[1]
                    
            else:
                _params['url'] = _strparams[0]
            self.msg.setType(TSMessage.START)
            self.msg.setParams(_params)

    def getTSMessage(self):
        res = copy.deepcopy(self.msg)
        return res

    def end(self):
        self.active = False
        self.daemon = False
