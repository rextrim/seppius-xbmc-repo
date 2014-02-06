# Copyright (c) 2013 Torrent-TV.RU
# Writer (c) 2011, Welicobratov K.A., E-mail: 07pov23@gmail.com

import xbmc
import xbmcaddon
import cPickle
import defines
import os

#from ACEStream.Core.Utilities.TSCrypto import AES_encrypt, AES_decrypt, m2_AES_encrypt, m2_AES_decrypt

#defines.showMessage('Start plugin')

import mainform 

def AES_decrypt(data, key):
        aes = AES.new(key, AES.MODE_CFB)
        return aes.decrypt(data)

if __name__ == '__main__':
    if not defines.ADDON.getSetting('skin'):
       defines.ADDON.setSetting('skin', 'st.anger')
    if defines.ADDON.getSetting("skin") == "default":
       defines.ADDON.setSetting("skin", "st.anger")
    if not defines.ADDON.getSetting("login"):
       defines.ADDON.setSetting("login", "anonymous")
       defines.ADDON.setSetting("password", "anonymous")
       
    w = mainform.WMainForm("mainform.xml", defines.ADDON_PATH, defines.ADDON.getSetting('skin'))
    
    w.doModal()
    #del w
    defines.showMessage('Close plugin')
    del w
    