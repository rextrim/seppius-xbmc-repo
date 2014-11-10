# -*- coding: utf-8 -*-
"""Module used to launch rating dialogues and send ratings to myshows"""

import xbmc
import xbmcaddon
import xbmcgui
from functions import id2title, RateShow

__settings__ = xbmcaddon.Addon(id='plugin.video.myshows')
__language__ = __settings__.getLocalizedString

buttons = {
11030: '5',
11031: '4',
11032: '3',
11033: '2',
11034: '1',
}

focus_labels = {
11030: __language__(1315).encode('utf-8', 'ignore'),
11031: __language__(1316).encode('utf-8', 'ignore'),
11032: __language__(1317).encode('utf-8', 'ignore'),
11033: __language__(1318).encode('utf-8', 'ignore'),
11034: __language__(1319).encode('utf-8', 'ignore'),
}


def rateMedia(showId=None, id=None, rate_item=None):
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
    def __init__(self, xmlFile, resourcePath, forceFallback=False, media_type=None, media=None, rating_type=None,
                 showId=None, id=None, rate_item=None):
        self.rating = None
        self.showId, self.id, self.rate_item = showId, id, rate_item

    def onInit(self):
        self.getControl(10015).setVisible(True)
        if self.showId:
            self.title = id2title(self.showId, self.id)
        else:
            self.title = ['None', 'None']
        if self.id and self.id != '0':
            self.getControl(10011).setLabel(self.rate_item)
            self.getControl(10012).setLabel('%s\n%s' % (self.title[0], self.title[1]))
        else:
            self.getControl(10011).setLabel('%s %s' % (__language__(30303).encode('utf-8', 'ignore'), self.title[0]))
            if self.showId:
                rating, seasonNumber, seasonrating, old_rating = RateShow(int(self.showId)).count()
                if old_rating: self.setFocusId([11030, 11031, 11032, 11033, 11034][old_rating - 1])
                self.getControl(10012).setLabel(
                    __language__(1314).encode('utf-8', 'ignore') % (str(rating), seasonNumber, str(seasonrating)))
            if not self.showId and self.rate_item:
                self.getControl(10011).setLabel(__language__(30520))
                self.getControl(10012).setLabel(self.rate_item.encode('utf-8', 'ignore'))


    def onClick(self, controlID):
        if controlID in buttons:
            self.rating = buttons[controlID]
            self.close()


    def onFocus(self, controlID):
        if controlID in focus_labels:
            self.getControl(10013).setLabel(focus_labels[controlID])
        else:
            self.getControl(10013).setLabel('')
