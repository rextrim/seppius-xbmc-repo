# Copyright (c) 2010-2011 Torrent-TV.RU
# Writer (c) 2011, Welicobratov K.A., E-mail: 07pov23@gmail.com

#imports
import xbmcgui
import xbmc
import xbmcaddon
import threading
import json
import urllib2
import time

from ts import TSengine as tsengine
from player import MyPlayer
from adswnd import AdsForm
from menu import MenuForm

import defines

def LogToXBMC(text, type = 1):
    ttext = ''
    if type == 2:
        ttext = 'ERROR:'

    log = open(defines.ADDON_PATH + '/mainform.log', 'a')
    print '[MainForm %s] %s %s\r' % (time.strftime('%X'),ttext, text)
    log.write('[MainForm %s] %s %s\r' % (time.strftime('%X'),ttext, text))
    log.close()
    del log

#classes

class MyThread(threading.Thread):

    def __init__(self, func, params, back = True):
        threading.Thread.__init__(self)
        self.func = func
        self.params = params
        #self.parent = parent

    def run(self):
        self.func(self.params)
    def stop(self):
        pass

def GET(target, post=None, cookie = None):
    try:
        print target
        req = urllib2.Request(url = target, data = post)
        req.add_header('User-Agent', 'XBMC (script.torrent-tv.ru)')
        if cookie:
            req.add_header('Cookie', 'PHPSESSID=%s' % cookie)
        resp = urllib2.urlopen(req)
        http = resp.read()
        resp.close()
        return http
    except Exception, e:
        xbmc.log( 'GET EXCEPT [%s]' % (e), 4 )

class WMainForm(xbmcgui.WindowXML):
    CANCEL_DIALOG  = ( 9, 10, 11, 92, 216, 247, 257, 275, 61467, 61448, )
    CONTEXT_MENU_IDS = (117, 101)
    ARROW_ACTIONS = (1,2,3,4)
    BTN_CHANNELS_ID = 102
    BTN_TRANSLATIONS_ID = 103
    BTN_VOD_ID = 113
    BTN_CLOSE = 101
    BTN_FULLSCREEN = 208
    CONTROL_LIST = 50
    PANEL_ADS = 105
    PROGRESS_BAR = 110
    
    CHN_TYPE_FAVOURITE = 'Избранное'
    CHN_TYPE_TRANSLATION = 'Трансляции'
    CHN_TYPE_MODERATION = 'На модерации'
    API_ERROR_INCORRECT = 'incorrect'
    API_ERROR_NOCONNECT = 'noconnect'
    API_ERROR_ALREADY = 'already'
    API_ERROR_NOPARAM = 'noparam'
    API_ERROR_NOFAVOURITE = 'nofavourite'


    def __init__(self, *args, **kwargs):
        self.isCanceled = False
        self.translation = []
        self.category = {}
        self.seltab = 0
        self.epg = {}        
        self.selitem = '0'
        self.img_progress = None
        self.txt_progress = None
        self.list = None
        self.player = MyPlayer("player.xml", defines.ADDON_PATH, 'default')
        self.player.parent = self
        self.amalkerWnd = AdsForm("adsdialog.xml", defines.ADDON_PATH, 'default')
        self.cur_category = WMainForm.CHN_TYPE_FAVOURITE
    
    def initLists(self):
        self.category = {}
        self.category[WMainForm.CHN_TYPE_MODERATION] = []
        self.category[WMainForm.CHN_TYPE_FAVOURITE] = []
        self.translation = []
        self.epg = {}

    def getChannels(self, param):
        data = GET('http://xbmc.torrent-tv.ru/alltranslation.php?session=%s&type=%s' % (self.session, param), cookie = self.session)
        jdata = json.loads(data)
        if jdata['success'] == 0:
            print jdata['error']
            self.showStatus(jdata['error'])
            return
        for ch in jdata['channel']:
            if not ch['logo']:
                ch['logo'] = ''
            else:
                ch['logo'] = 'http://torrent-tv.ru/uploads/' + ch['logo']
            li = xbmcgui.ListItem(ch['name'], ch['id'], ch['logo'], ch['logo'])
            li.setProperty('url_type', ch['stream_type'])
            li.setProperty('url', ch['stream_url'])
            li.setProperty('epg_cdn_id', '%s' % ch['epg_cdn_id'])
            li.setProperty('icon', ch['logo'])
            if param == 'channel':
                if not self.category.has_key(ch['category'].encode('utf-8')):
                    self.category[ch['category'].encode('utf-8')] = []
                li.setProperty('commands', MenuForm.CMD_ADD_FAVOURITE)
                self.category[ch['category'].encode('utf-8')].append(li)
            elif param == 'moderation':
                li.setProperty('commands', MenuForm.CMD_ADD_FAVOURITE)
                self.category[WMainForm.CHN_TYPE_MODERATION].append(li)
            elif param == 'translation':
                li.setProperty('commands', MenuForm.CMD_ADD_FAVOURITE)
                self.translation.append(li)
            elif param == 'favourite':
                li.setProperty('commands', MenuForm.CMD_DEL_FAVOURITE)
                self.category[WMainForm.CHN_TYPE_FAVOURITE].append(li)

    def getEpg(self, param):
       data = GET('http://xbmc.torrent-tv.ru/get_epg.php?session=%s&channel_id=%s' % (self.session, param), cookie = self.session)
       jdata = json.loads(data)
       if jdata['success'] == 0:
          print jdata['error']
          self.epg[param] = []
          self.showSimpleEpg(param)
          self.hideStatus()
          return
       else:
           self.epg[param] = jdata['data']
           if self.selitem != jdata['data'][0]['channel_id']:
               self.showSimpleEpg(param)
               self.hideStatus()

    def onInit(self):
        try:
            LogToXBMC('OnInit')
            self.img_progress = self.getControl(108)
            self.txt_progress = self.getControl(107)
            self.progress = self.getControl(WMainForm.PROGRESS_BAR)
            self.showStatus("Авторизация")
            data = GET('http://xbmc.torrent-tv.ru/auth.php?username=%s&password=%s' % (defines.ADDON.getSetting('login'), defines.ADDON.getSetting('password')))
            jdata = json.loads(data)
            if jdata['success'] == 0:
                print jdata['error']
                self.showStatus(jdata['error'])
                return
            print jdata
            self.session = jdata['session']
            print 'Login OK'
            self.updateList()
            
        except Exception, e:
            LogToXBMC('OnInit: %s' % e, 2)

    def onFocus(self, ControlID):
        if ControlID == 50:
            if not self.list:
                return
            selItem = self.list.getSelectedItem()
            if selItem:
                if selItem.getLabel2() == self.selitem or selItem.getLabel() == '..':
                    return
                self.selitem = selItem.getLabel2()
                epg_id = selItem.getProperty('epg_cdn_id')
                #LogToXBMC('Icon list item = %s' % selItem.getIconImage())
                if epg_id == '0':
                    self.showSimpleEpg()
                elif self.epg.has_key(epg_id):
                    self.showSimpleEpg(epg_id)
                else:
                    self.showStatus('Загрузка программы')
                    thr = MyThread(self.getEpg, epg_id)
                    thr.start()
                img = self.getControl(1111)
                LogToXBMC(selItem.getProperty('icon'))
                img.setImage(selItem.getProperty('icon'))
    
    def onClickChannels(self):
        LogToXBMC('onClickChannels')
        self.fillChannels()
        if self.seltab != WMainForm.BTN_CHANNELS_ID:
            control = self.getControl(WMainForm.BTN_CHANNELS_ID)
            control.setLabel('>%s<' % control.getLabel())
            if self.seltab:
                btn = self.getControl(self.seltab)
                btn.setLabel(btn.getLabel().replace('<', '').replace('>',''))
        self.seltab = WMainForm.BTN_CHANNELS_ID

    def onClickTranslations(self):
        self.fillTranslation()
        if self.seltab != WMainForm.BTN_TRANSLATIONS_ID:
            control = self.getControl(WMainForm.BTN_TRANSLATIONS_ID)
            control.setLabel('>%s<' % control.getLabel())
            if self.seltab:
                btn = self.getControl(self.seltab)
                btn.setLabel(btn.getLabel().replace('<', '').replace('>',''))
        self.seltab = WMainForm.BTN_TRANSLATIONS_ID

    def onClick(self, controlID):
        control = self.getControl(controlID)
        LogToXBMC('onClick %s' % controlID)
        if controlID == WMainForm.BTN_CHANNELS_ID: self.onClickChannels()
        elif controlID == WMainForm.BTN_TRANSLATIONS_ID: self.onClickTranslations()
        elif controlID == 200: self.setFocusId(50)
        elif controlID == 50:
            selItem = control.getSelectedItem()
            if not selItem:
                return
            if selItem.getLabel() == '..':
                self.fillCategory()
                return
            if selItem.getProperty('type') == 'category':
                self.cur_category = selItem.getLabel()
                self.fillChannels()
                return
            buf = xbmcgui.ListItem(selItem.getLabel())
            buf.setProperty('epg_cdn_id', selItem.getProperty('epg_cdn_id'))
            buf.setProperty('icon', selItem.getProperty('icon'))
            buf.setProperty('url_type', selItem.getProperty('url_type'))
            buf.setProperty('url', selItem.getProperty('url'))
            self.player.Start(buf)
           
            LogToXBMC('CUR SELTAB %s' % self.seltab)
            
            print 'END PLAYED| Click Channels'
            xbmc.executebuiltin('SendClick(12345,102)')
        elif controlID == WMainForm.BTN_FULLSCREEN:
            self.player.show()

    def showSimpleEpg(self, epg_id = None):
        controlEpg = self.getControl(109)
        controlEpg1 = self.getControl(112)
        if epg_id and self.epg[epg_id].__len__() > 0:
            ctime = time.time()
            curepg = filter(lambda x: (float(x['etime']) > ctime), self.epg[epg_id])
            bt = float(curepg[0]['btime'])
            et = float(curepg[0]['etime'])
            sbt = time.localtime(bt)
            set = time.localtime(et)
            self.progress.setPercent((ctime - bt)*100/(et - bt))
            controlEpg.setLabel('%.2d:%.2d - %.2d:%.2d %s' % (sbt.tm_hour, sbt.tm_min, set.tm_hour, set.tm_min, curepg[0]['name']))
            nextepg = ''
            for i in (1,2,3):
                if i >= curepg.__len__():
                    break
                sbt = time.localtime(curepg[i]['btime'])
                set = time.localtime(curepg[i]['etime'])
                nextepg = nextepg + '%.2d:%.2d - %.2d:%.2d %s\n' % (sbt.tm_hour, sbt.tm_min, set.tm_hour, set.tm_min, curepg[i]['name'])
            controlEpg1.setLabel(nextepg)

        else:
            controlEpg.setLabel('Нет программы')
            controlEpg1.setLabel('')
            self.progress.setPercent(1)

    def onAction(self, action):
        if not action:
            super(WMainForm, self).onAction(action)
            return
        if action in WMainForm.CANCEL_DIALOG:
            LogToXBMC('CLOSE FORM')
            self.isCanceled = True
            #xbmc.executebuiltin('Action(PreviousMenu)')
            self.player.Stop()
            self.close()
        elif action.getId() in WMainForm.ARROW_ACTIONS:
            self.onFocus(self.getFocusId())
        elif action.getId() in WMainForm.CONTEXT_MENU_IDS and self.getFocusId() == WMainForm.CONTROL_LIST:
            if action.getId() == 101:
                return
            mnu = MenuForm("menu.xml", defines.ADDON_PATH, 'default')
            mnu.li = self.getFocus().getSelectedItem()
            mnu.get_method = GET
            mnu.session = self.session
            LogToXBMC('Выполнить комманду')
            mnu.doModal()
            LogToXBMC('Комманда выполнена')
            res = mnu.GetResult()
            LogToXBMC('Результат комманды %s' % res)
            if res == 'OK':
                self.updateList()
            elif res == WMainForm.API_ERROR_INCORRECT:
                self.showStatus('Пользователь не опознан по сессии')
            elif res == WMainForm.API_ERROR_NOCONNECT:
                self.showStatus('Ошибка соединения с БД')
            elif res == WMainForm.API_ERROR_ALREADY:
                self.showStatus('Канал уже был добавлен в избранное ранее')
            elif res == WMainForm.API_ERROR_NOPARAM:
                self.showStatus('Ошибка входных параметров')
            elif res == WMainForm.API_ERROR_NOFAVOURITE:
                self.showStatus('Канал не найден в избранном')
        else:
            super(WMainForm, self).onAction(action)

    def updateList(self):
        self.list = self.getControl(50)
        self.initLists()
        thr = MyThread(self.getChannels, 'channel', not (self.cur_category in (WMainForm.CHN_TYPE_TRANSLATION, WMainForm.CHN_TYPE_MODERATION, WMainForm.CHN_TYPE_FAVOURITE)))
        thr.daemon = False
        thr.start()
        thr1 = MyThread(self.getChannels, 'translation', self.cur_category == WMainForm.CHN_TYPE_TRANSLATION)
        thr1.daemon = False
        thr1.start()
        thr2 = MyThread(self.getChannels, 'moderation', self.cur_category == WMainForm.CHN_TYPE_MODERATION)
        thr2.daemon = False
        thr2.start()
        thr3 = MyThread(self.getChannels, 'favourite', self.cur_category == WMainForm.CHN_TYPE_FAVOURITE)
        thr3.start()
        LogToXBMC('Ожидание результата')
        if self.cur_category == WMainForm.CHN_TYPE_FAVOURITE:
            thr3.join()
        elif self.cur_category == WMainForm.CHN_TYPE_MODERATION:
            thr2.join()
        elif self.cur_category == WMainForm.CHN_TYPE_TRANSLATION:
            thr1.join()
        else:
            thr.join()
        self.list.reset()
        self.setFocus(self.getControl(WMainForm.BTN_CHANNELS_ID))
        self.img_progress.setVisible(False)
        self.hideStatus()

    def showStatus(self, str):
        if self.img_progress: self.img_progress.setVisible(True)
        if self.txt_progress: self.txt_progress.setLabel(str)

    def hideStatus(self):
        if self.img_progress: self.img_progress.setVisible(False)
        if self.txt_progress: self.txt_progress.setLabel("")

    def fillChannels(self):
        self.showStatus("Заполнение списка")
        if not self.list:
            self.showStatus("Список не инициализирован")
            return
        self.list.reset()
        li = xbmcgui.ListItem('..')
        self.list.addItem(li)
        for ch in self.category[self.cur_category]:
            self.list.addItem(ch)
        self.img_progress.setVisible(True)
        self.hideStatus()

    def fillTranslation(self):
        if not self.list:
            self.showStatus("Список не инициализирован")
            return
        self.showStatus("Заполнение списка")
        self.list.reset()
        for ch in self.translation:
            self.list.addItem(ch)
        self.hideStatus()

    def fillCategory(self):
        if not self.list:
            self.showStatus("Список не инициализирован")
            return
        self.list.reset()
        for gr in self.category:
            li = xbmcgui.ListItem(gr)
            li.setProperty('type', 'category')
            self.list.addItem(li)
    def IsCanceled(self):
        return self.isCanceled