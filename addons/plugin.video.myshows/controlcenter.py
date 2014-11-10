# -*- coding: utf-8 -*-

import xbmcaddon

from functions import TimeOut, WatchedDB

from resources.pyxbmct.addonwindow import *

__version__ = "1.9.11"
__plugin__ = "MyShows.ru " + __version__
__author__ = "DiMartino"
__settings__ = xbmcaddon.Addon(id='plugin.video.myshows')
__language__ = __settings__.getLocalizedString


class MyAddon(AddonDialogWindow):
    def __init__(self, title=''):
        super(MyAddon, self).__init__(title)
        self.setGeometry(700, 450, 9, 4)
        self.set_info_controls()
        self.set_active_controls()
        self.set_navigation()
        # Connect a key action (Backspace) to close the window.
        self.connect(ACTION_NAV_BACK, self.close)

    def set_info_controls(self):
        # Demo for PyXBMCt UI controls.
        no_int_label = Label('Information output', alignment=ALIGN_CENTER)
        self.placeControl(no_int_label, 0, 0, 1, 2)
        #
        label_label = Label('Label')
        self.placeControl(label_label, 1, 0)
        # Label
        self.label = Label('Simple label')
        self.placeControl(self.label, 1, 1)
        #
        fadelabel_label = Label('FadeLabel')
        self.placeControl(fadelabel_label, 2, 0)
        # FadeLabel
        self.fade_label = FadeLabel()
        self.placeControl(self.fade_label, 2, 1)
        self.fade_label.addLabel('Very long string can be here.')
        #
        textbox_label = Label('TextBox')
        self.placeControl(textbox_label, 3, 0)
        # TextBox
        self.textbox = TextBox()
        self.placeControl(self.textbox, 3, 1, 2, 1)
        self.textbox.setText('Text box.\nIt can contain several lines.')
        #
        image_label = Label('Image')
        self.placeControl(image_label, 5, 0)

    def set_active_controls(self):
        int_label = Label('Interactive Controls', alignment=ALIGN_CENTER)
        self.placeControl(int_label, 0, 2, 1, 2)
        #
        radiobutton_label = Label('RadioButton')
        self.placeControl(radiobutton_label, 1, 2)
        # RadioButton
        self.radiobutton = RadioButton('Off')
        self.placeControl(self.radiobutton, 1, 3)
        self.connect(self.radiobutton, self.radio_update)
        #
        edit_label = Label('Edit')
        self.placeControl(edit_label, 2, 2)
        # Edit
        self.edit = Edit('Edit')
        self.placeControl(self.edit, 2, 3)
        # Additional properties must be changed after (!) displaying a control.
        self.edit.setText('Enter text here')
        #
        list_label = Label('List')
        self.placeControl(list_label, 3, 2)
        #
        self.list_item_label = Label('', textColor='0xFF808080')
        self.placeControl(self.list_item_label, 4, 2)
        # List
        self.list = List()
        self.placeControl(self.list, 3, 3, 3, 1)
        # Add items to the list
        items = ['Item %s' % i for i in range(1, 8)]
        self.list.addItems(items)
        # Connect the list to a function to display which list item is selected.
        self.connect(self.list, lambda: xbmc.executebuiltin('Notification(Note!,%s selected.)' %
                                                            self.list.getListItem(
                                                                self.list.getSelectedPosition()).getLabel()))
        # Connect key and mouse events for list navigation feedback.
        self.connectEventList(
            [ACTION_MOVE_DOWN, ACTION_MOVE_UP, ACTION_MOUSE_WHEEL_DOWN, ACTION_MOUSE_WHEEL_UP, ACTION_MOUSE_MOVE],
            self.list_update)
        # Slider value label
        SLIDER_INIT_VALUE = 25.0
        self.slider_value = Label(str(SLIDER_INIT_VALUE), alignment=ALIGN_CENTER)
        self.placeControl(self.slider_value, 6, 3)
        #
        slider_caption = Label('Slider')
        self.placeControl(slider_caption, 7, 2)
        # Slider
        self.slider = Slider()
        self.placeControl(self.slider, 7, 3, pad_y=10)
        self.slider.setPercent(SLIDER_INIT_VALUE)
        # Connect key and mouse events for slider update feedback.
        self.connectEventList([ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT, ACTION_MOUSE_DRAG], self.slider_update)
        #
        button_label = Label('Button')
        self.placeControl(button_label, 8, 2)
        # Button
        self.button = Button('Close')
        self.placeControl(self.button, 8, 3)
        # Connect control to close the window.
        self.connect(self.button, self.close)

    def set_navigation(self):
        # Set navigation between controls
        self.button.controlUp(self.slider)
        self.button.controlDown(self.radiobutton)
        self.radiobutton.controlUp(self.button)
        self.radiobutton.controlDown(self.edit)
        self.edit.controlUp(self.radiobutton)
        self.edit.controlDown(self.list)
        self.list.controlUp(self.edit)
        self.list.controlDown(self.slider)
        self.slider.controlUp(self.list)
        self.slider.controlDown(self.button)
        # Set initial focus
        self.setFocus(self.radiobutton)

    def slider_update(self):
        # Update slider value label when the slider nib moves
        try:
            if self.getFocus() == self.slider:
                self.slider_value.setLabel('%.1f' % self.slider.getPercent())
        except (RuntimeError, SystemError):
            pass

    def radio_update(self):
        # Update radiobutton caption on toggle
        if self.radiobutton.isSelected():
            self.radiobutton.setLabel('On')
        else:
            self.radiobutton.setLabel('Off')

    def list_update(self):
        # Update list_item label when navigating through the list.
        try:
            if self.getFocus() == self.list:
                self.list_item_label.setLabel(self.list.getListItem(self.list.getSelectedPosition()).getLabel())
            else:
                self.list_item_label.setLabel('')
        except (RuntimeError, SystemError):
            pass

    def setAnimation(self, control):
        # Set fade animation for all add-on window controls
        control.setAnimations([('WindowOpen', 'effect=fade start=0 end=100 time=500',),
                               ('WindowClose', 'effect=fade start=100 end=0 time=500',)])


class ControlCenter(AddonDialogWindow):
    def __init__(self, title=''):
        super(ControlCenter, self).__init__(title)
        self.setGeometry(700, 450, 9, 3)
        self.set_info_controls()
        self.set_active_controls()
        self.set_navigation()
        # Connect a key action (Backspace) to close the window.
        self.connect(ACTION_NAV_BACK, self.close)

    def set_info_controls(self):
        # Demo for PyXBMCt UI controls.
        no_int_label = Label(__language__(30146), alignment=ALIGN_CENTER)
        self.placeControl(no_int_label, 0, 0, 1, 3)
        #
        label_timeout = Label(__language__(30410))
        self.placeControl(label_timeout, 1, 0)
        # Label
        self.label = Label(__language__(30545) % TimeOut().timeout())
        self.placeControl(self.label, 1, 1)
        #
        label_watched = Label(__language__(30414) % (WatchedDB().count()))
        self.placeControl(label_watched, 2, 0)

    def set_active_controls(self):
        # RadioButton
        self.radiobutton = RadioButton(__language__(30411))

        self.placeControl(self.radiobutton, 1, 2)
        self.radiobutton.setSelected(TimeOut().timeout() != TimeOut().online)
        self.connect(self.radiobutton, self.radio_update)

        # Button
        self.button_sendoff = Button(__language__(30041), font='font12')
        self.placeControl(self.button_sendoff, 2, 1, 1, 2)
        self.connect(self.button_sendoff, self.sendOffline)

        # Button
        self.button_openset = Button(__language__(30413))
        self.placeControl(self.button_openset, 8, 0)
        # Connect control to close the window.
        self.connect(self.button_openset, self.openSettings)

        # Button
        self.button_utorrent = Button(__language__(30287))
        self.placeControl(self.button_utorrent, 8, 1)
        # Connect control to close the window.
        self.connect(self.button_utorrent, self.openUtorrent)

        # Button
        self.button_close = Button(__language__(30412))
        self.placeControl(self.button_close, 8, 2)
        # Connect control to close the window.
        self.connect(self.button_close, self.close)

    def set_navigation(self):
        # Set navigation between controls
        self.radiobutton.controlUp(self.button_close)
        self.radiobutton.controlDown(self.button_sendoff)
        self.radiobutton.controlLeft(self.button_sendoff)
        self.radiobutton.controlRight(self.button_openset)

        self.button_sendoff.controlUp(self.radiobutton)
        self.button_sendoff.controlDown(self.button_close)
        # self.button_sendoff.controlLeft(self.button_openset)
        #self.button_sendoff.controlRight(self.button_openset)

        self.button_openset.controlUp(self.button_sendoff)
        self.button_openset.controlDown(self.radiobutton)
        self.button_openset.controlLeft(self.button_close)
        self.button_openset.controlRight(self.button_utorrent)

        self.button_utorrent.controlUp(self.button_sendoff)
        self.button_utorrent.controlDown(self.radiobutton)
        self.button_utorrent.controlLeft(self.button_openset)
        self.button_utorrent.controlRight(self.button_close)

        self.button_close.controlUp(self.button_sendoff)
        self.button_close.controlDown(self.radiobutton)
        self.button_close.controlLeft(self.button_utorrent)
        self.button_close.controlRight(self.button_openset)
        # Set initial focus
        self.setFocus(self.button_close)

    def openSettings(self):
        __settings__.openSettings()

    def openUtorrent(self):
        xbmc.executebuiltin('ActivateWindow(Videos,plugin://plugin.video.myshows/?mode=52)')
        self.close()

    def sendOffline(self):
        xbmc.executebuiltin("RunPlugin(plugin://plugin.video.myshows/?mode=71)")

    def slider_update(self):
        # Update slider value label when the slider nib moves
        try:
            if self.getFocus() == self.slider:
                self.slider_value.setLabel('%.1f' % self.slider.getPercent())
        except (RuntimeError, SystemError):
            pass

    def radio_update(self):
        # Update radiobutton caption on toggle
        if self.radiobutton.isSelected() or (TimeOut().timeout() == TimeOut().online):
            TimeOut().go_offline(manual=True)
        else:
            TimeOut().go_online()
        self.label.setLabel(__language__(30545) % TimeOut().timeout())

    def list_update(self):
        # Update list_item label when navigating through the list.
        try:
            if self.getFocus() == self.list:
                self.list_item_label.setLabel(self.list.getListItem(self.list.getSelectedPosition()).getLabel())
            else:
                self.list_item_label.setLabel('')
        except (RuntimeError, SystemError):
            pass

    def setAnimation(self, control):
        # Set fade animation for all add-on window controls
        control.setAnimations([('WindowOpen', 'effect=fade start=0 end=100 time=500',),
                               ('WindowClose', 'effect=fade start=100 end=0 time=500',)])


def main():
    window = ControlCenter('MyShows.ru Control Center')
    window.doModal()


if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        import xbmc
        import traceback

        map(xbmc.log, traceback.format_exc().split("\n"))
        raise