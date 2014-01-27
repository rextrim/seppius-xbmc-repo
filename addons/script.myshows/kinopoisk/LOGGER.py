# -*- coding: utf-8 -*-
#
try:
    import xbmcaddon
    __settings__ = xbmcaddon.Addon("script.myshows")
    __myshows__ = xbmcaddon.Addon("plugin.video.myshows")

    try:
        debug = __myshows__.getSetting("debug")
    except:
        debug = __settings__.getSetting("debug")
except:
    debug='true'

def Log(msg, force = False):
    try:
        print "[myshows log] " + msg
    except UnicodeEncodeError:
        print "[myshows log] " + msg.encode( "utf-8", "ignore" )

def Debug(msg, force = False):
    if debug=='true' or force:
        try:
            print "[myshows] " + msg
        except UnicodeEncodeError:
            print "[myshows] " + msg.encode( "utf-8", "ignore" )

def Info(msg, force = False):
    if debug=='true' or force:
        try:
            print "[myshows] " + msg
        except UnicodeEncodeError:
            print "[myshows] " + msg.encode( "utf-8", "ignore" )

def Warn(msg, force = False):
    if debug=='true' or force:
        try:
            print "[myshows] " + msg
        except UnicodeEncodeError:
            print "[myshows] " + msg.encode( "utf-8", "ignore" )