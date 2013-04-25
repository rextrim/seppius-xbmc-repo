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

def LogToXBMC(text, type = 1):
    ttext = ''
    if type == 2:
        ttext = 'ERROR:'

    PLUGIN_DATA_PATH = WMainForm.ADDON.getAddonInfo('path')
    log = open(PLUGIN_DATA_PATH + '/mainform.log', 'a')
    log.write('[MainForm %s] %s %s\r' % (time.strftime('%X'),ttext, text))
    log.close()
    del log

#classes

class MyThread(threading.Thread):

    def __init__(self, func, params):
        threading.Thread.__init__(self)
        self.daemon = True
        self.TSPlayer = None
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
    CANCEL_DIALOG  = ( 9, 10, 11, 92, 101, 216, 247, 257, 275, 61467, 61448, )
    ARROW_ACTIONS = (1,2,3,4)
    BTN_CHANNELS_ID = 102
    BTN_TRANSLATIONS_ID = 103
    BTN_VOD_ID = 113
    BTN_CLOSE = 101
    PANEL_ADS = 105
    PROGRESS_BAR = 110
    ADDON = xbmcaddon.Addon( id = 'script.torrent-tv.ru' )
    ADDON_ICON	 = ADDON.getAddonInfo('icon')
    ADDON_PATH = ADDON.getAddonInfo('path')

    def __init__(self, *args, **kwargs):
        self.isCanceled = False
        self.translation = []
        self.category = {}
        self.seltab = 0
        self.epg = {}        
        self.selitem = '0'
        self.TSPlayer = None
        self.img_progress = None
        self.txt_progress = None
        self.list = None
        self.player = MyPlayer("player.xml", WMainForm.ADDON_PATH, 'default')
        self.player.parent = self
        self.amalkerWnd = AdsForm("adsdialog.xml", WMainForm.ADDON_PATH, 'default')
    
    def initLists(self):
        self.category = {}
        self.category['На модерации'] = []
        self.category['Избранное'] = []
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
            li.setProperty('icon', 'http://torrent-tv.ru/uploads/' + ch['logo'])
            if param == 'channel':
                if not self.category.has_key(ch['category'].encode('utf-8')):
                    self.category[ch['category'].encode('utf-8')] = []
                self.category[ch['category'].encode('utf-8')].append(li)
            elif param == 'moderation':
                self.category['На модерации'].append(li)
            elif param == 'translation':
                self.translation.append(li)

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
            self.img_progress = self.getControl(108)
            self.txt_progress = self.getControl(107)
            self.progress = self.getControl(WMainForm.PROGRESS_BAR)
            self.showStatus("Авторизация")
            data = GET('http://xbmc.torrent-tv.ru/auth.php?username=%s&password=%s' % (WMainForm.ADDON.getSetting('login'), WMainForm.ADDON.getSetting('password')))
            jdata = json.loads(data)
            if jdata['success'] == 0:
                print jdata['error']
                self.showStatus(jdata['error'])
                return
            print jdata
            self.session = jdata['session']
            print 'Login OK'
            self.initLists()
            thr = MyThread(self.getChannels, 'channel')
            thr.start()
            thr1 = MyThread(self.getChannels, 'translation')
            thr1.start()
            thr2 = MyThread(self.getChannels, 'moderation')
            thr2.start()
            self.showStatus("Получение списка каналов")
            data = GET('http://xbmc.torrent-tv.ru/alltranslation.php?session=%s&type=favourite' % self.session, cookie = self.session)
            jdata = json.loads(data)
            if jdata['success'] == 0:
                print jdata['error']
                self.showStatus(jdata['error'])
                return
            self.category['Избранное'] = []
            for ch in jdata['channel']:
                if not ch['logo']:
                    ch['logo'] = ''
                else:
                    ch['logo'] = 'http://torrent-tv.ru/uploads/' + ch['logo']
                li = xbmcgui.ListItem(ch['name'], ch['id'], ch['logo'], ch['logo'])
                if not ch['stream_type']:
                    ch['stream_type'] = ''
                if not ch['stream_url']:
                    ch['stream_url'] = ''
                li.setProperty('url_type', ch['stream_type'])
                li.setProperty('url', ch['stream_url'])
                li.setProperty('type', 'translation')
                li.setProperty('icon', ch['logo'])
                li.setProperty('epg_cdn_id', ch['epg_cdn_id'])
                self.category['Избранное'].append(li)
            self.cur_category = 'Избранное'
            self.list = self.getControl(50)
            self.setFocus(self.getControl(WMainForm.BTN_CHANNELS_ID))
            self.img_progress.setVisible(False)
            self.hideStatus()
        except Exception, e:
            LogToXBMC('OnInit: ' % e, 2)

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
                img = self.getControl(111)
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
        if controlID == WMainForm.BTN_CHANNELS_ID: 
            self.onClickChannels()
        if controlID == WMainForm.BTN_TRANSLATIONS_ID: self.onClickTranslations()

        if controlID == 50:
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
            self.player.Start(selItem)
           
            LogToXBMC('CUR SELTAB %s' % self.seltab)
            
            print 'END PLAYED| Click Channels'
            xbmc.executebuiltin('SendClick(12345,102)')

    def showSimpleEpg(self, epg_id = None):
        controlEpg = self.getControl(109)
        controlEpg1 = self.getControl(112)
        if epg_id and self.epg[epg_id].__len__() > 0:
            ctime = time.time()
            LogToXBMC('%s %s' % (self.epg[epg_id][0]['name'].encode('utf-8'), time.localtime(float(self.epg[epg_id][0]['btime']))))
            curepg = filter(lambda x: (float(x['etime']) > ctime), self.epg[epg_id])
            LogToXBMC('%s %s' % (curepg[0]['name'].encode('utf-8'), time.localtime(float(curepg[0]['btime']))))
            bt = float(curepg[0]['btime'])
            et = float(curepg[0]['etime'])
            sbt = time.localtime(bt)
            set = time.localtime(et)
            self.progress.setPercent((ctime - bt)*100/(et - bt))
            controlEpg.setLabel('%.2d:%.2d - %.2d:%.2d %s' % (sbt.tm_hour, sbt.tm_min, set.tm_hour, set.tm_min, curepg[0]['name']))
            nextepg = ''
            for i in (1,2,3):
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
            self.close()
        elif action.getId() in WMainForm.ARROW_ACTIONS:
            self.onFocus(self.getFocusId())
        #elif action.getId() == 101:
        #    self.player.Stop()
        #    xbmc.executebuiltin('Action(back)')


    def showStatus(self, str):
        if self.img_progress: self.img_progress.setVisible(True)
        if self.txt_progress: self.txt_progress.setLabel(str)

    def hideStatus(self):
        if self.img_progress: self.img_progress.setVisible(False)
        if self.txt_progress: self.txt_progress.setLabel("")

    def fillChannels(self):
        self.showStatus("Заполнение списка")
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