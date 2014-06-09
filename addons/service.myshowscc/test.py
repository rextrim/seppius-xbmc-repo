# -*- coding: utf-8 -*-
import xbmc, xbmcaddon, os

def main():
    xbmc.executebuiltin(
                    'xbmc.RunScript('+xbmcaddon.Addon("plugin.video.myshows").getAddonInfo("path")+os.sep+
                    'controlcenter.py,)')

if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        import xbmc
        import traceback
        map(xbmc.log, traceback.format_exc().split("\n"))
        raise
