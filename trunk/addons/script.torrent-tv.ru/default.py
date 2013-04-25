# Copyright (c) 2010-2011 Torrent-TV.RU
# Writer (c) 2011, Welicobratov K.A., E-mail: 07pov23@gmail.com

import xbmc
import xbmcaddon

def showMessage(message = '', heading='Torrent-TV.RU', times = 3000):
    try: 
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % (heading.encode('utf-8'), message.encode('utf-8'), times))
    except Exception, e:
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % (heading, message, times))
        except Exception, e:
            xbmc.log( 'showMessage: exec failed [%s]' % 3 )


import mainform 
ADDON = xbmcaddon.Addon(id = 'script.torrent-tv.ru')
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_ICON	 = ADDON.getAddonInfo('icon')

if __name__ == '__main__':
    w = mainform.WMainForm("DialogDownloadProgress.xml", ADDON_PATH, 'default')
    showMessage('Open Form')
    w.doModal()
    #del w
    showMessage('Close plugin')
    del w
    