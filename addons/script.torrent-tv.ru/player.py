# Copyright (c) 2010-2011 Torrent-TV.RU
# Writer (c) 2011, Welicobratov K.A., E-mail: 07pov23@gmail.com

import xbmcgui
import threading
import xbmcaddon    
import xbmc
import time

import defines

from ts import TSengine as tsengine
#defines
CANCEL_DIALOG  = ( 9, 10, 11, 92, 216, 247, 257, 275, 61467, 61448, )

def LogToXBMC(text, type = 1):
    ttext = ''
    if type == 2:
        ttext = 'ERROR:'

    log = open(defines.ADDON_PATH + '/player.log', 'a')
    print '[MyPlayer %s] %s %s\r' % (time.strftime('%X'),ttext, text)
    log.write('[MyPlayer %s] %s %s\r' % (time.strftime('%X'),ttext, text))
    log.close()
    del log

class MyPlayer(xbmcgui.WindowXML):
    CONTROL_EPG_ID = 109
    CONTROL_PROGRESS_ID = 110
    CONTROL_ICON_ID = 202
    CONTROL_WINDOW_ID = 203
    CONTROL_BUTTON_PAUSE = 204
    CONTROL_BUTTON_STOP = 200
    ACTION_RBC = 101

    def __init__(self, *args, **kwargs):
        self.played = False
        self.thr = None
        self.TSPlayer = None
        self.parent = None
        self.li = None
        self.visible = False
        self.t = None
        self.focusId = 203

    def onInit(self):
        if not self.li:
            return
        
        cicon = self.getControl(MyPlayer.CONTROL_ICON_ID)
        cicon.setImage(self.li.getProperty('icon'))
        if not self.parent:
            return
        self.UpdateEpg()
        self.getControl(MyPlayer.CONTROL_WINDOW_ID).setVisible(False)
        self.setFocusId(MyPlayer.CONTROL_EPG_ID)

    def UpdateEpg(self):
        if not self.li:
            return
        epg_id = self.li.getProperty('epg_cdn_id')
        controlEpg = self.getControl(MyPlayer.CONTROL_EPG_ID)
        controlEpg1 = self.getControl(112)
        progress = self.getControl(MyPlayer.CONTROL_PROGRESS_ID)
        if epg_id and self.parent.epg.has_key(epg_id) and self.parent.epg[epg_id].__len__() > 0:
            ctime = time.time()
            curepg = filter(lambda x: (float(x['etime']) > ctime), self.parent.epg[epg_id])
            bt = float(curepg[0]['btime'])
            et = float(curepg[0]['etime'])
            sbt = time.localtime(bt)
            set = time.localtime(et)
            progress.setPercent((ctime - bt)*100/(et - bt))
            controlEpg.setLabel('%.2d:%.2d - %.2d:%.2d %s' % (sbt.tm_hour, sbt.tm_min, set.tm_hour, set.tm_min, curepg[0]['name']))
            #nextepg = ''
            #for i in (1,2,3):
            #    if i >= curepg.__len__():
            #        break
            #    sbt = time.localtime(curepg[i]['btime'])
            #    set = time.localtime(curepg[i]['etime'])
            #    nextepg = nextepg + '%.2d:%.2d - %.2d:%.2d %s\n' % (sbt.tm_hour, sbt.tm_min, set.tm_hour, set.tm_min, curepg[i]['name'])
            #controlEpg1.setLabel(nextepg)
        else:
            controlEpg.setLabel('Нет программы')
            #controlEpg1.setLabel('')
            progress.setPercent(1)

    def Stop(self):
        print 'CLOSE STOP'
        #self.TSPlayer.thr.error = Exception('Stop player')
        xbmc.executebuiltin('PlayerControl(Stop)')

    def Start(self, li):
        pass
        if not self.TSPlayer :
            LogToXBMC('InitTS')
            self.TSPlayer = tsengine(parent = self.parent)
            #self.TSPlayer.connectToTS()
        #self.TSPlayer.connectToTS()
        self.li = li
        LogToXBMC('Load Torrent')
        if li.getProperty('url_type') == 'torrent':
            self.TSPlayer.load_torrent(li.getProperty('url'),'TORRENT')
        else:
            self.TSPlayer.load_torrent(li.getProperty('url'), 'PID')

        #if self.TSPlayer.last_error:
        #    self.hide()
        LogToXBMC('Play torrent')
        self.TSPlayer.play_url_ind(0,li.getLabel(), li.getProperty('icon'), li.getProperty('icon'))
        
    def hide(self):
        pass
        #xbmc.executebuiltin('Action(ParentDir)')
        #if self.TSPlayer.playing:
        #    xbmc.executebuiltin('Action(ParentDir)')
        #    print 'Главное меню'

    def getPlayed(self):
        return self.played

    def hideControl(self):
        self.getControl(MyPlayer.CONTROL_WINDOW_ID).setVisible(False)
        self.setFocusId(MyPlayer.CONTROL_WINDOW_ID)
        self.focusId = MyPlayer.CONTROL_WINDOW_ID
        

    def onAction(self, action):
        if action in CANCEL_DIALOG:
            print 'Closes player'
            self.close()
        elif action.getId() == MyPlayer.ACTION_RBC:
            print 'CLOSE PLAYER 101'
            self.close()
        wnd = self.getControl(MyPlayer.CONTROL_WINDOW_ID)
        if not self.visible:
            self.UpdateEpg()
            wnd.setVisible(True)
            if self.focusId == MyPlayer.CONTROL_WINDOW_ID:
                self.setFocusId(MyPlayer.CONTROL_BUTTON_PAUSE)
            else:
                self.setFocusId(self.focusId)
            self.setFocusId(self.getFocusId())
            if self.t:
                self.t.cancel()
                self.t = None
            self.t = threading.Timer(2, self.hideControl)
            self.t.start()

    def onClick(self, controlID):
        if controlID == MyPlayer.CONTROL_BUTTON_STOP:
            self.close()