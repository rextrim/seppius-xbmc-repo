import xbmcaddon
import xbmc
import sys
import urllib2
import urllib

ADDON = xbmcaddon.Addon( id = 'script.torrent-tv.ru' )
ADDON_ICON	 = ADDON.getAddonInfo('icon')
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_ICON	 = ADDON.getAddonInfo('icon')

if (sys.platform == 'win32') or (sys.platform == 'win64'):
    ADDON_PATH = ADDON_PATH.decode('utf-8')

def showMessage(message = '', heading='Torrent-TV.RU', times = 6789):
    try: 
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, %s)' % (heading.encode('utf-8'), message.encode('utf-8'), times, ADDON_ICON))
    except Exception, e:
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, %s)' % (heading, message, times, ADDON_ICON))
        except Exception, e:
            xbmc.log( 'showMessage: exec failed [%s]' % 3 )

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