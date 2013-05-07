# Copyright (c) 2013 Torrent-TV.RU
# Writer (c) 2011, Welicobratov K.A., E-mail: 07pov23@gmail.com

import xbmc
import xbmcaddon

import defines

defines.showMessage('Start plugin')

import mainform 

if __name__ == '__main__':
    w = mainform.WMainForm("DialogDownloadProgress.xml", defines.ADDON_PATH, 'default')
    
    w.doModal()
    #del w
    defines.showMessage('Close plugin')
    del w
    