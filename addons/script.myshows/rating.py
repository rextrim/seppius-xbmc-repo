# -*- coding: utf-8 -*-
"""Module used to launch rating dialogues and send ratings to trakt"""

import xbmc
import xbmcaddon
import xbmcgui
import utilities as utils

__addon__ = xbmcaddon.Addon("script.myshows")

def rate(rating, media):
    import kp, kinopoisk
    cookie=utils.get_string_setting('cookie')
    if cookie=='': cookie=None
    if not cookie:
        login=utils.get_string_setting('login')
        password=utils.get_string_setting('password')
        kpLogin=kp.Login(login,password,cookie)
        cookie=kpLogin.get_cookie()
        utils.set_string_setting('cookie', cookie)
    k=kinopoisk.KinoPoiskRuAgent()
    if 'kinopoiskId' not in media:
        movies=k.search([],{'name':media['title'],'year':media['year']},'English')
        if len(movies)>0:
            if movies[0][4]>90:
                ret=0
            else:
                items=[]
                for i in movies: items.append('%s (%s)'%(i[1],str(i[2])))
                ret=xbmcgui.Dialog().select('Movies:',items)
            if ret>-1:
                kpId=movies[ret][0]
                title=movies[ret][1].encode('utf-8')
                year=str(movies[ret][2])
    else:
        kpId=str(media['kinopoiskId'])
        title=media['title'].encode('utf-8')
        year=str(media['year'])
    r=kp.Rate(str(rating),str(kpId), cookie).rateit()
    if r:
        utils.notification('Rated %s OK!' % (str(kpId)),'%s to %s (%s)!' %(str(rating), title, year))



def rateMedia(media_type, summary_info, unrate=False, rating=None):
    xbmc.executebuiltin('Dialog.Close(all, true)')

    gui = RatingDialog(
        "RateKP.xml",
        __addon__.getAddonInfo('path'),
        media_type=media_type,
        media=summary_info,
        rating_type='advanced',
    )

    gui.doModal()
    if gui.rating:
        rating = gui.rating

        if rating == 0 or rating == "unrate":
            return
        else:
            rate(rating, gui.media)
    else:
        utils.Debug("[Rating] Rating dialog was closed with no rating.")

    del gui

class RatingDialog(xbmcgui.WindowXMLDialog):
    buttons = {
        10030:    'love',
        10031:    'hate',
        11030:    1,
        11031:    2,
        11032:    3,
        11033:    4,
        11034:    5,
        11035:    6,
        11036:    7,
        11037:    8,
        11038:    9,
        11039:    10
    }

    focus_labels = {
        10030: 1314,
        10031: 1315,
        11030: 1315,
        11031: 1316,
        11032: 1317,
        11033: 1318,
        11034: 1319,
        11035: 1320,
        11036: 1321,
        11037: 1322,
        11038: 1323,
        11039: 1314
    }

    def __init__(self, xmlFile, resourcePath, forceFallback=False, media_type=None, media=None, rating_type=None, rerate=False):
        self.media_type = media_type
        self.media = media
        self.rating_type = rating_type
        self.rating = None
        self.rerate = rerate

    def onInit(self):
        self.getControl(10014).setVisible(False)
        self.getControl(10015).setVisible(True)

        s = "%s (%s)" % (self.media['title'], self.media['year'])
        self.getControl(10012).setLabel(s)
        self.getControl(10011).setLabel('KinoPoisk.ru Rate')

        rateID = 11037
        self.setFocus(self.getControl(rateID))

    def onClick(self, controlID):
        if controlID in self.buttons:
            self.rating = self.buttons[controlID]
            self.close()

    def onFocus(self, controlID):
        if controlID in self.focus_labels:
            s = utils.getString(self.focus_labels[controlID])
            if self.rerate:
                if self.media['rating'] == self.buttons[controlID] or self.media['rating_advanced'] == self.buttons[controlID]:
                    s = utils.getString(1325)
            
            self.getControl(10013).setLabel(s)
        else:
            self.getControl(10013).setLabel('')
