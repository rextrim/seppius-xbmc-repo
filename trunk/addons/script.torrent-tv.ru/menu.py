import xbmcgui
import time
import xbmcaddon
import json

import defines

def LogToXBMC(text, type = 1):
    ttext = ''
    if type == 2:
        ttext = 'ERROR:'
 
    log = open(defines.ADDON_PATH + '/menuform.log', 'a')
    print '[MenuForm %s] %s %s\r' % (time.strftime('%X'),ttext, text)
    log.write('[MenuForm %s] %s %s\r' % (time.strftime('%X'),ttext, text))
    log.close()
    del log

class MenuForm(xbmcgui.WindowXMLDialog):
    CMD_ADD_FAVOURITE = 'add_favourite'
    CMD_DEL_FAVOURITE = 'del_favourite'
    CMD_UP_FAVOURITE = 'up_favourite'
    CMD_DOWN_FAVOURITE = 'down_favourite'
    CONTROL_CMD_LIST = 301
    def __ini__(self, *args, **kwargs):
        self.li = None
        self.get_method = None
        self.session = None
        self.result = 'None'
        pass

    def onInit(self):
        if not self.li:
            return
        try:
            cmds = self.li.getProperty('commands').split(',')
            list = self.getControl(MenuForm.CONTROL_CMD_LIST)
            list.reset()
            for c in cmds:
                if c == MenuForm.CMD_ADD_FAVOURITE:
                    title = 'Добавить в избранное'
                elif c == MenuForm.CMD_DEL_FAVOURITE:
                    title = 'Удалить из избранного'
                elif c == MenuForm.CMD_DOWN_FAVOURITE:
                    title = 'Поднять вверх'
                list.addItem(xbmcgui.ListItem(title, c))
            list.setHeight(cmds.__len__()*38)
            list.selectItem(0)
            self.setFocusId(MenuForm.CONTROL_CMD_LIST)
            LogToXBMC('Focus Controld %s' % self.getFocusId())
        except Exception, e: 
            LogToXBMC("В списке нет комманд %s" % e)
            pass

    def onClick(self, controlId):
        LogToXBMC('ControlID = %s' % controlId)
        if controlId == MenuForm.CONTROL_CMD_LIST:
            lt = self.getControl(MenuForm.CONTROL_CMD_LIST)
            li = lt.getSelectedItem()
            cmd = li.getLabel2()
            if cmd == MenuForm.CMD_DEL_FAVOURITE:
                self.DelFromFavourite()
            elif cmd == MenuForm.CMD_ADD_FAVOURITE:
                self.AddToFavourite()
            self.close()

    def _sendCmd(self, cmd):
        channel_id = self.li.getLabel2()
        res = self.get_method('http://xbmc.torrent-tv.ru/%s?session=%s&channel_id=%s' % (cmd, self.session, channel_id), cookie = self.session)
        LogToXBMC(res)
        LogToXBMC('http://xbmc.torrent-tv.ru/%s?session=%s&channel_id=%s' % (cmd, self.session, channel_id))
        jdata = json.loads(res)
        if jdata['success'] == '0':
            self.result = jdata['error']
        else:
            self.result = 'OK'
    def DelFromFavourite(self):
        self._sendCmd('favourite_delete.php')

    def AddToFavourite(self):
        self._sendCmd('favourite_add.php')

    def GetResult(self):
        res = self.result
        self.result = 'None'
        return res