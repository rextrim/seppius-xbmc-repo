# Copyright (c) 2010-2011 Torrent-TV.RU
# Writer (c) 2011, Welicobratov K.A., E-mail: 07pov23@gmail.com

import xbmcgui
import threading
import xbmcaddon    
import xbmc

from ts import TSengine as tsengine
#defines
CANCEL_DIALOG  = ( 9, 10, 11, 92, 216, 247, 257, 275, 61467, 61448, )
class MyPlayer(xbmcgui.WindowXML):
    def __init__(self, *args, **kwargs):
        self.played = False
        self.thr = None
        self.TSPlayer = None
        self.parent = None

    def onInit(self):
        pass

    def Stop(self):
        print 'CLOSE STOP'
        xbmc.executebuiltin('PlayerControl(Stop)')

    def Start(self, li):
        pass
        if not self.TSPlayer :
            self.TSPlayer = tsengine(parent = self.parent)
        if self.TSPlayer.playing:
            self.TSPlayer.end()
            xbmc.sleep(16)
        self.TSPlayer.connectToTS()
        if li.getProperty('url_type') == 'torrent':
            self.TSPlayer.load_torrent(li.getProperty('url'),'TORRENT')
        else:
            self.TSPlayer.load_torrent(li.getProperty('url'), 'PID')

        #if self.TSPlayer.last_error:
        #    self.hide()

        self.TSPlayer.play_url_ind(0,li.getLabel(), li.getProperty('icon'), li.getProperty('icon'))
        
    def hide(self):
        xbmc.executebuiltin('Action(PreviousMenu)')
        if self.TSPlayer.playing:
            print 'Главное меню'
            xbmc.executebuiltin('Action(PreviousMenu)')

    def getPlayed(self):
        return self.played

    def onAction(self, action):
        if action in CANCEL_DIALOG:
            print 'Closes player'
            self.close()
        elif action.getId() == 101:
            self.close()

    def onClick(self, controlID):
        control = self.getControl(controlID)
        if controlID == 200:
            print 'CLOSE'
            self.Stop()
            self.hide()