import xbmcaddon
import xbmc
import sys

ADDON = xbmcaddon.Addon( id = 'script.torrent-tv.ru' )
ADDON_ICON	 = ADDON.getAddonInfo('icon')
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_ICON	 = ADDON.getAddonInfo('icon')

if (sys.platform == 'win32') or (sys.platform == 'win64'):
    ADDON_PATH = ADDON_PATH.decode('utf-8')

def showMessage(message = '', heading='Torrent-TV.RU', times = 3000):
    try: 
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % (heading.encode('utf-8'), message.encode('utf-8'), times))
    except Exception, e:
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % (heading, message, times))
        except Exception, e:
            xbmc.log( 'showMessage: exec failed [%s]' % 3 )