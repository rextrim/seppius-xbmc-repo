# -*- coding: utf-8 -*-
"""Module used to launch rating dialogues and send ratings to myshows"""

import xbmc
import xbmcaddon
import xbmcgui
from functions import id2title

__settings__ = xbmcaddon.Addon(id='plugin.video.myshows')
__language__ = __settings__.getLocalizedString

buttons = {
	11030:	'5',
	11031:	'4',
	11032:	'3',
	11033:	'2',
	11034:	'1',
}

focus_labels = {
	11030: __language__(1315).encode('utf-8', 'ignore'),
	11031: __language__(1316).encode('utf-8', 'ignore'),
	11032: __language__(1317).encode('utf-8', 'ignore'),
	11033: __language__(1318).encode('utf-8', 'ignore'),
	11034: __language__(1319).encode('utf-8', 'ignore'),
}

def rateMedia(showId, id, rate_item):
    xbmc.executebuiltin('Dialog.Close(all, true)')

    gui = RatingDialog(
        "RatingDialog.xml",
        __settings__.getAddonInfo('path'),
        showId=showId, id=id, rate_item=rate_item
    )

    gui.doModal()
    if gui.rating:
        gui.close()
        return gui.rating
    del gui


class RatingDialog(xbmcgui.WindowXMLDialog):
    def __init__(self, xmlFile, resourcePath, forceFallback=False, media_type=None, media=None, rating_type=None, showId='None', id='None', rate_item='None'):
        self.rating = None
        self.showId, self.id, self.rate_item = showId, id, rate_item

    def onInit(self):
        self.getControl(10015).setVisible(True)
        self.getControl(10011).setLabel(self.rate_item)
        self.title=id2title(self.showId, self.id)
        self.getControl(10012).setLabel('%s - %s' % (self.title[0],self.title[1]))


    def onClick(self, controlID):
        if controlID in buttons:
            self.rating = buttons[controlID]
            self.close()


    def onFocus(self, controlID):
        if controlID in focus_labels:
            self.getControl(10013).setLabel(focus_labels[controlID])
        else:
            self.getControl(10013).setLabel('')
