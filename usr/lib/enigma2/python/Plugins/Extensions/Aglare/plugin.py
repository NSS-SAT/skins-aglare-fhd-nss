# -*- coding: utf-8 -*-
# mod by Lululla

from . import _
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import (
    # ConfigInteger,
    # ConfigNothing,
    configfile,
    ConfigOnOff,
    NoSave,
    ConfigText,
    ConfigSelection,
    ConfigSubsection,
    ConfigYesNo,
    config,
    getConfigListEntry,
)
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.Progress import Progress
from Components.Sources.StaticText import StaticText
from enigma import ePicLoad, eTimer, loadPic
from PIL import Image
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Tools.Directories import fileExists
from Tools.Directories import SCOPE_PLUGINS
from Tools.Directories import resolveFilename
from Tools.Downloader import downloadWithProgress
import os
import sys
import glob

PY3 = sys.version_info.major >= 3
if PY3:
    from urllib.request import urlopen
    from urllib.request import Request
else:
    from urllib2 import urlopen
    from urllib2 import Request


version = '1.10'
my_cur_skin = False
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
OAWeather = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('OAWeather'))
weatherz = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('WeatherPlugin'))
mvi = '/usr/share/'
tmdb_skin = "%senigma2/%s/tmdbkey" % (mvi, cur_skin)
tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_skin = "%senigma2/%s/omdbkey" % (mvi, cur_skin)
omdb_api = "cb1d9f55"

try:
    if my_cur_skin is False:
        skin_paths = {
            "tmdb_api": "/usr/share/enigma2/{}/tmdbkey".format(cur_skin),
            "omdb_api": "/usr/share/enigma2/{}/omdbkey".format(cur_skin),
            # "thetvdbkey": "/usr/share/enigma2/{}/thetvdbkey".format(cur_skin)
            # "visual_api": "/etc/enigma2/VisualWeather/visualkey.txt"
        }
        for key, path in skin_paths.items():
            if fileExists(path):
                with open(path, "r") as f:
                    value = f.read().strip()
                    if key == "tmdb_api":
                        tmdb_api = value
                    elif key == "omdb_api":
                        omdb_api = value
                    # elif key == "thetvdbkey":
                        # thetvdbkey = value
                    # elif key == "visual_api":
                        # visual_api = value
                my_cur_skin = True
except Exception as e:
    print("Errore nel caricamento delle API:", str(e))
    my_cur_skin = False


def isMountedInRW(mount_point):
    with open("/proc/mounts", "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) > 1 and parts[1] == mount_point:
                return True
    return False


path_poster = "/tmp/poster"
patch_backdrop = "/tmp/backdrop"
if os.path.exists("/media/hdd") and isMountedInRW("/media/hdd"):
    path_poster = "/media/hdd/poster"
    patch_backdrop = "/media/hdd/backdrop"

elif os.path.exists("/media/usb") and isMountedInRW("/media/usb"):
    path_poster = "/media/usb/poster"
    patch_backdrop = "/media/usb/backdrop"

elif os.path.exists("/media/mmc") and isMountedInRW("/media/mmc"):
    path_poster = "/media/mmc/poster"
    patch_backdrop = "/media/mmc/backdrop"


def removePng():
    print('Rimuovo file PNG e JPG...')
    if os.path.exists(path_poster):
        png_files = glob.glob(os.path.join(path_poster, "*.png"))
        jpg_files = glob.glob(os.path.join(path_poster, "*.jpg"))
        files_to_remove = png_files + jpg_files
        if not files_to_remove:
            print("Nessun file PNG o JPG trovato nella cartella " + path_poster)
        for file in files_to_remove:
            try:
                os.remove(file)
                print("Rimosso: " + file)
            except Exception as e:
                print("Errore durante la rimozione di " + file + ": " + str(e))
    else:
        print("La cartella " + path_poster + " non esiste.")

    if os.path.exists(patch_backdrop):
        png_files_backdrop = glob.glob(os.path.join(patch_backdrop, "*.png"))
        jpg_files_backdrop = glob.glob(os.path.join(patch_backdrop, "*.jpg"))
        files_to_remove_backdrop = png_files_backdrop + jpg_files_backdrop
        if not files_to_remove_backdrop:
            print("Nessun file PNG o JPG trovato nella cartella " + patch_backdrop)
        else:
            for file in files_to_remove_backdrop:
                try:
                    os.remove(file)
                    print("Rimosso: " + file)
                except Exception as e:
                    print("Errore durante la rimozione di " + file + ": " + str(e))
    else:
        print("La cartella " + patch_backdrop + " non esiste.")


config.plugins.AglareNss = ConfigSubsection()
config.plugins.AglareNss.actapi = NoSave(ConfigOnOff(default=False))
config.plugins.AglareNss.data = NoSave(ConfigOnOff(default=False))
config.plugins.AglareNss.api = NoSave(ConfigYesNo(default=False))  # NoSave(ConfigSelection(['-> Ok']))
config.plugins.AglareNss.txtapi = ConfigText(default=tmdb_api, visible_width=50, fixed_size=False)
config.plugins.AglareNss.data2 = NoSave(ConfigOnOff(default=False))
config.plugins.AglareNss.api2 = NoSave(ConfigYesNo(default=False))  # NoSave(ConfigSelection(['-> Ok']))
config.plugins.AglareNss.txtapi2 = ConfigText(default=omdb_api, visible_width=50, fixed_size=False)
config.plugins.AglareNss.png = NoSave(ConfigYesNo(default=False))  # NoSave(ConfigSelection(['-> Ok']))
config.plugins.AglareNss.colorSelector = ConfigSelection(default='head', choices=[
    ('head', _('Default')),
    ('color1', _('Black')),
    ('color2', _('Brown')),
    ('color3', _('Green')),
    ('color4', _('Magenta')),
    ('color5', _('Blue')),
    ('color6', _('Red')),
    ('color7', _('Purple')),
    ('color8', _('Dark Green'))])
config.plugins.AglareNss.FontStyle = ConfigSelection(default='basic', choices=[
    ('basic', _('Default')),
    ('font1', _('HandelGotD')),
    ('font2', _('KhalidArtboldRegular')),
    ('font3', _('BebasNeue')),
    ('font4', _('Greta')),
    ('font5', _('Segoe UI light')),
    ('font6', _('MV Boli'))])
config.plugins.AglareNss.skinSelector = ConfigSelection(default='base', choices=[
    ('base', _('Default'))])
config.plugins.AglareNss.InfobarStyle = ConfigSelection(default='infobar_base1', choices=[
    ('infobar_base1', _('Default')),
    ('infobar_base2', _('Style2')),
    ('infobar_base3', _('Style3')),
    ('infobar_base4', _('Style4'))])
config.plugins.AglareNss.InfobarPosterx = ConfigSelection(default='infobar_posters_posterx_off', choices=[
    ('infobar_posters_posterx_off', _('OFF')),
    ('infobar_posters_posterx_on', _('ON'))])
config.plugins.AglareNss.InfobarXtraevent = ConfigSelection(default='infobar_posters_xtraevent_off', choices=[
    ('infobar_posters_xtraevent_off', _('OFF')),
    ('infobar_posters_xtraevent_on', _('ON')),
    ('infobar_posters_xtraevent_info', _('Backdrop'))])
config.plugins.AglareNss.InfobarDate = ConfigSelection(default='infobar_no_date', choices=[
    ('infobar_no_date', _('Infobar_NO_Date')),
    ('infobar_date', _('Infobar_Date'))])
config.plugins.AglareNss.InfobarWeather = ConfigSelection(default='infobar_no_weather', choices=[
    ('infobar_no_weather', _('Infobar_NO_Weather')),
    ('infobar_weather', _('Infobar_Weather'))])
config.plugins.AglareNss.SecondInfobarStyle = ConfigSelection(default='secondinfobar_base1', choices=[
    ('secondinfobar_base1', _('Default')),
    ('secondinfobar_base2', _('Style2')),
    ('secondinfobar_base3', _('Style3')),
    ('secondinfobar_base4', _('Style4'))])
config.plugins.AglareNss.SecondInfobarPosterx = ConfigSelection(default='secondinfobar_posters_posterx_off', choices=[
    ('secondinfobar_posters_posterx_off', _('OFF')),
    ('secondinfobar_posters_posterx_on', _('ON'))])
config.plugins.AglareNss.SecondInfobarXtraevent = ConfigSelection(default='secondinfobar_posters_xtraevent_off', choices=[
    ('secondinfobar_posters_xtraevent_off', _('OFF')),
    ('secondinfobar_posters_xtraevent_on', _('ON'))])
config.plugins.AglareNss.ChannSelector = ConfigSelection(default='channellist_no_posters', choices=[
    ('channellist_no_posters', _('ChannelSelection_NO_Posters')),
    ('channellist_no_posters_no_picon', _('ChannelSelection_NO_Posters_NO_Picon')),
    ('channellist_backdrop_v', _('ChannelSelection_BackDrop_V')),
    ('channellist_backdrop_h', _('ChannelSelection_BackDrop_H')),
    ('channellist_1_poster', _('ChannelSelection_1_Poster')),
    ('channellist_4_posters', _('ChannelSelection_4_Posters')),
    ('channellist_6_posters', _('ChannelSelection_6_Posters')),
    ('channellist_big_mini_tv', _('ChannelSelection_big_mini_tv'))])
config.plugins.AglareNss.EventView = ConfigSelection(default='eventview_no_posters', choices=[
    ('eventview_no_posters', _('EventView_NO_Posters')),
    ('eventview_7_posters', _('EventView_7_Posters'))])

config.plugins.AglareNss.VolumeBar = ConfigSelection(default='volume1', choices=[
    ('volume1', _('Default')),
    ('volume2', _('volume2'))])

config.plugins.AglareNss.E2iplayerskins = ConfigSelection(default='OFF', choices=[
    ('e2iplayer_skin_off', _('OFF')),
    ('e2iplayer_skin_on', _('ON'))])


def Plugins(**kwargs):
    return PluginDescriptor(name='NSS Skin', description=_('Customization tool for Aglare-FHD-NSS Skin'), where=PluginDescriptor.WHERE_PLUGINMENU, icon='plugin.png', fnc=main)


def main(session, **kwargs):
    session.open(AglareSetup)


def remove_exif(image_path):
    with Image.open(image_path) as img:
        img.save(image_path, "PNG")


def convert_image(image):
    path = image
    img = Image.open(path)
    img.save(path, "PNG")
    return image


class AglareSetup(ConfigListScreen, Screen):
    skin = '''
        <screen name="AglareSetup" title="Aglare-FHD-NSS" position="center,center" size="1000,640" zPosition="0">
            <eLabel text="Cancel" font="Regular;24" position="10,596" size="120,26" foregroundColor="#00ff4A3C" halign="center" zPosition="1" />
            <eLabel text="Save" font="Regular;24" position="135,596" size="120,26" foregroundColor="#0056C856" halign="center" zPosition="1" />
            <eLabel text="Update" font="Regular;24" position="244,596" size="120,26" foregroundColor="#fefe00" halign="center" zPosition="1" />
            <eLabel text="CheckSkin" font="Regular;24" position="367,596" size="150,26" foregroundColor="#2a70a4" halign="center" zPosition="1" />
            <widget name="config" font="Regular;24" position="5,5" size="990,347" itemHeight="40" scrollbarMode="showOnDemand" />
            <widget name="Preview" position="505,360" size="498,280" zPosition="11" />
        </screen>
    '''

    def __init__(self, session):
        self.version = '.Aglare-FHD-NSS'
        Screen.__init__(self, session)
        self.session = session
        self.skinFile = '/usr/share/enigma2/Aglare-FHD-NSS/skin.xml'
        self.previewFiles = '/usr/lib/enigma2/python/Plugins/Extensions/Aglare/sample/'
        self['Preview'] = Pixmap()
        self.onChangedEntry = []
        self.setup_title = ('Aglare-FHD-NSS')
        list = []
        section = '--------------------------( SKIN GENERAL SETUP )-----------------------'
        list.append(getConfigListEntry(section))
        section = '--------------------------( SKIN APIKEY SETUP )-----------------------'
        list.append(getConfigListEntry(section))
        ConfigListScreen.__init__(self, list, session=self.session, on_change=self.changedEntry)
        self['actions'] = ActionMap(
            [
                'OkCancelActions',
                'InputBoxActions',
                'HotkeyActions',
                'VirtualKeyboardActions',
                'MenuActions',
                'NumberActions',
                'InfoActions',
                'ColorActions'
            ],
            {
                'left': self.keyLeft,
                'right': self.keyRight,
                'down': self.keyDown,
                'up': self.keyUp,
                'red': self.keyExit,
                'green': self.keySave,
                'menu': self.Checkskin,
                'yellow': self.checkforUpdate,
                'showVirtualKeyboard': self.KeyText,
                'ok': self.keyRun,
                'info': self.info,
                'blue': self.info,
                '5': self.Checkskin,
                'cancel': self.keyExit
            },
            -1
        )
        self.createSetup()
        self.PicLoad = ePicLoad()
        self.Scale = AVSwitch().getFramebufferScale()
        self.onLayoutFinish.append(self.ShowPicture)
        self.onLayoutFinish.append(self.__layoutFinished)

    def __layoutFinished(self):
        self.setTitle(self.setup_title)

    def passs(self, foo):
        pass

    def keyRun(self):
        sel = self["config"].getCurrent()[1]
        if sel and sel == config.plugins.AglareNss.png:
            self.removPng()
            config.plugins.AglareNss.png.setValue(0)
            config.plugins.AglareNss.png.save()
        if sel and sel == config.plugins.AglareNss.api:
            self.keyApi()
        if sel and sel == config.plugins.AglareNss.txtapi:
            self.KeyText()
        if sel and sel == config.plugins.AglareNss.api2:
            self.keyApi2()
        if sel and sel == config.plugins.AglareNss.txtapi2:
            self.KeyText()

    def keyApi(self, answer=None):
        api = "/tmp/tmdbkey.txt"
        if answer is None:
            if fileExists(api) and os.stat(api).st_size > 0:
                self.session.openWithCallback(self.keyApi, MessageBox, _("Import Api Key TMDB from /tmp/tmdbkey.txt?"))
            else:
                self.session.open(MessageBox, (_("Missing %s !") % api), MessageBox.TYPE_INFO, timeout=4)
        elif answer:
            if fileExists(api) and os.stat(api).st_size > 0:
                with open(api, 'r') as f:
                    fpage = f.readline().strip()
                if fpage:
                    with open(tmdb_skin, "w") as t:
                        t.write(fpage)
                    config.plugins.AglareNss.txtapi.setValue(fpage)
                    config.plugins.AglareNss.txtapi.save()
                    self.session.open(MessageBox, _("TMDB ApiKey Imported & Stored!"), MessageBox.TYPE_INFO, timeout=4)
                else:
                    self.session.open(MessageBox, _("TMDB ApiKey is empty!"), MessageBox.TYPE_INFO, timeout=4)
            else:
                self.session.open(MessageBox, (_("Missing %s !") % api), MessageBox.TYPE_INFO, timeout=4)
        self.createSetup()

    def keyApi2(self, answer=None):
        api2 = "/tmp/omdbkey.txt"
        if answer is None:
            if fileExists(api2) and os.stat(api2).st_size > 0:
                self.session.openWithCallback(self.keyApi2, MessageBox, _("Import Api Key OMDB from /tmp/omdbkey.txt?"))
            else:
                self.session.open(MessageBox, (_("Missing %s !") % api2), MessageBox.TYPE_INFO, timeout=4)
        elif answer:
            if fileExists(api2) and os.stat(api2).st_size > 0:
                with open(api2, 'r') as f:
                    fpage = f.readline().strip()
                if fpage:
                    with open(omdb_skin, "w") as t:
                        t.write(fpage)
                    config.plugins.AglareNss.txtapi2.setValue(fpage)
                    config.plugins.AglareNss.txtapi2.save()
                    self.session.open(MessageBox, _("OMDB ApiKey Imported & Stored!"), MessageBox.TYPE_INFO, timeout=4)
                else:
                    self.session.open(MessageBox, _("OMDB ApiKey is empty!"), MessageBox.TYPE_INFO, timeout=4)
            else:
                self.session.open(MessageBox, (_("Missing %s !") % api2), MessageBox.TYPE_INFO, timeout=4)
        self.createSetup()

    def KeyText(self):
        from Screens.VirtualKeyBoard import VirtualKeyBoard
        sel = self["config"].getCurrent()
        if sel:
            self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self["config"].getCurrent()[0], text=self["config"].getCurrent()[1].value)

    def VirtualKeyBoardCallback(self, callback=None):
        if callback is not None and len(callback):
            self["config"].getCurrent()[1].value = callback
            self["config"].invalidate(self["config"].getCurrent())
        return

    def createSetup(self):
        try:
            self.editListEntry = None
            list = []
            section = '--------------------------( SKIN GENERAL SETUP )-----------------------'
            list.append(getConfigListEntry(section))
            list.append(getConfigListEntry(_('Color Style:'), config.plugins.AglareNss.colorSelector))
            list.append(getConfigListEntry(_('Select Your Font:'), config.plugins.AglareNss.FontStyle))
            list.append(getConfigListEntry(_('Skin Style:'), config.plugins.AglareNss.skinSelector))
            list.append(getConfigListEntry(_('InfoBar Style:'), config.plugins.AglareNss.InfobarStyle))
            list.append(getConfigListEntry(_('InfoBar PosterX:'), config.plugins.AglareNss.InfobarPosterx))
            list.append(getConfigListEntry(_('InfoBar Xtraevent:'), config.plugins.AglareNss.InfobarXtraevent))
            list.append(getConfigListEntry(_('InfoBar Date:'), config.plugins.AglareNss.InfobarDate))
            list.append(getConfigListEntry(_('InfoBar Weather:'), config.plugins.AglareNss.InfobarWeather))
            list.append(getConfigListEntry(_('SecondInfobar Style:'), config.plugins.AglareNss.SecondInfobarStyle))
            list.append(getConfigListEntry(_('SecondInfobar Posterx:'), config.plugins.AglareNss.SecondInfobarPosterx))
            list.append(getConfigListEntry(_('SecondInfobar Xtraevent:'), config.plugins.AglareNss.SecondInfobarXtraevent))
            list.append(getConfigListEntry(_('ChannelSelection Style:'), config.plugins.AglareNss.ChannSelector))
            list.append(getConfigListEntry(_('EventView Style:'), config.plugins.AglareNss.EventView))
            list.append(getConfigListEntry(_('VolumeBar Style:'), config.plugins.AglareNss.VolumeBar))
            list.append(getConfigListEntry(_('Support E2iplayer Skins:'), config.plugins.AglareNss.E2iplayerskins))

            section = '--------------------------( SKIN APIKEY SETUP )-----------------------'
            list.append(getConfigListEntry(section))
            list.append(getConfigListEntry("API KEY SETUP:", config.plugins.AglareNss.actapi, _("Settings Apikey Server")))
            if config.plugins.AglareNss.actapi.value is True:
                list.append(getConfigListEntry("TMDB API:", config.plugins.AglareNss.data, _("Settings TMDB ApiKey")))
                if config.plugins.AglareNss.data.value is True:
                    list.append(getConfigListEntry("--Load TMDB Apikey", config.plugins.AglareNss.api, _("Load TMDB Apikey from /tmp/tmdbkey.txt")))
                    list.append(getConfigListEntry("--Set TMDB Apikey", config.plugins.AglareNss.txtapi, _("Signup on TMDB and input free personal ApiKey")))
                list.append(getConfigListEntry("OMDB API:", config.plugins.AglareNss.data2, _("Settings OMDB APIKEY")))
                if config.plugins.AglareNss.data2.value is True:
                    list.append(getConfigListEntry("--Load OMDB Apikey", config.plugins.AglareNss.api2, _("Load OMDB Apikey from /tmp/omdbkey.txt")))
                    list.append(getConfigListEntry("--Set OMDB Apikey", config.plugins.AglareNss.txtapi2, _("Signup on OMDB and input free personal ApiKey")))

            section = '--------------------------( SKIN UTILITY SETUP )-----------------------'
            list.append(getConfigListEntry(_('Remove all png (OK)'), config.plugins.AglareNss.png, _("This operation remove all png from folder device (Poster-Backdrop)")))

            self["config"].list = list
            self["config"].l.setList(list)
        except KeyError:
            print("keyError")

    def Checkskin(self):
        self.session.openWithCallback(
            self.Checkskin2,
            MessageBox,
            _("[Checkskin] This operation checks if the skin has its components (this is not guaranteed).\nDo you really want to continue?"),
            MessageBox.TYPE_YESNO
        )

    def Checkskin2(self, answer):
        if answer:
            from .addons import checkskin
            self.check_module = eTimer()
            check = checkskin.check_module_skin()
            try:
                self.check_module_conn = self.check_module.timeout.connect(check)
            except AttributeError:
                self.check_module.callback.append(check)
            self.check_module.start(100, True)
            self.openVi()

    def openVi(self, callback=''):
        from .addons.File_Commander import File_Commander
        user_log = '/tmp/my_debug.log'
        if fileExists(user_log):
            self.session.open(File_Commander, user_log)

    def GetPicturePath(self):
        returnValue = self['config'].getCurrent()[1].value
        PicturePath = '/usr/lib/enigma2/python/Plugins/Extensions/Aglare/screens/default.png'
        if not isinstance(returnValue, str):
            returnValue = PicturePath  # if fileExists(PicturePath) else ''

        base_path = '/usr/lib/enigma2/python/Plugins/Extensions/Aglare/screens/' + returnValue
        png_path = base_path + '.png'
        jpg_path = base_path + '.jpg'

        if fileExists(png_path):
            return convert_image(png_path)
        elif fileExists(jpg_path):
            return convert_image(jpg_path)
        else:
            return convert_image(PicturePath)

    def UpdatePicture(self):
        self.onLayoutFinish.append(self.ShowPicture)

    def ShowPicture(self, data=None):
        if self["Preview"].instance:
            size = self['Preview'].instance.size()
            if size.isNull():
                size.setWidth(498)
                size.setHeight(280)
            pixmapx = self.GetPicturePath()
            if not fileExists(pixmapx):
                print("Immagine non trovata:", pixmapx)
                return
            png = loadPic(pixmapx, size.width(), size.height(), 0, 0, 0, 1)
            self["Preview"].instance.setPixmap(png)
            return

    def DecodePicture(self, PicInfo=None):
        ptr = self.PicLoad.getData()
        if ptr is not None:
            self["Preview"].instance.setPixmap(ptr)
            self["Preview"].instance.show()
        return

    def UpdateComponents(self):
        self.UpdatePicture()

    def info(self):
        message = (
            "Aglare skin is created by Odem2014.\n"
            "Users can fully customize their interface, and change layout,\n"
            "colors, fonts, and screens to suit their preferences.\n"
            "including the efficient PosterX component recoded by Lululla.\n\n"
            "Supported Images: NonSoloSat\n"
            "Aglare-FHD-NSS v.%s\n"
            "-----------------\n"
            "Forum support: nonsolosat.org\n"
            "NSS"
        ) % version
        aboutbox = self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        aboutbox.setTitle(_('Info Setup NSS Aglare'))

    def removPng(self):
        self.session.openWithCallback(
            self.removPng2,
            MessageBox,
            _("[RemovePng] This operation will remove all PNG files from the device folder (Poster-Backdrop).\nDo you really want to continue?"),
            MessageBox.TYPE_YESNO
        )

    def removPng2(self, result):
        if result:
            print('from remove png......')
            removePng()
            print('png are removed')
            aboutbox = self.session.open(MessageBox, _('All png are removed from folder!'), MessageBox.TYPE_INFO)
            aboutbox.setTitle(_('Info...'))

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.createSetup()
        self.ShowPicture()

        sel = self["config"].getCurrent()[1]
        if sel and sel == config.plugins.AglareNss.png:
            config.plugins.AglareNss.png.setValue(0)
            config.plugins.AglareNss.png.save()
            self.removPng()

        if sel and sel == config.plugins.AglareNss.api:
            config.plugins.AglareNss.api.setValue(0)
            config.plugins.AglareNss.api.save()
            self.keyApi()

        if sel and sel == config.plugins.AglareNss.api2:
            config.plugins.AglareNss.api2.setValue(0)
            config.plugins.AglareNss.api2.save()
            self.keyApi2()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.createSetup()
        self.ShowPicture()
        sel = self["config"].getCurrent()[1]

        if sel and sel == config.plugins.AglareNss.png:
            config.plugins.AglareNss.png.setValue(0)
            config.plugins.AglareNss.png.save()
            self.removPng()

        if sel and sel == config.plugins.AglareNss.api:
            config.plugins.AglareNss.api.setValue(0)
            config.plugins.AglareNss.api.save()
            self.keyApi()

        if sel and sel == config.plugins.AglareNss.api2:
            config.plugins.AglareNss.api2.setValue(0)
            config.plugins.AglareNss.api2.save()
            self.keyApi2()

    def keyDown(self):
        self['config'].instance.moveSelection(self['config'].instance.moveDown)
        self.createSetup()
        self.ShowPicture()

    def keyUp(self):
        self['config'].instance.moveSelection(self['config'].instance.moveUp)
        self.createSetup()
        self.ShowPicture()

    def changedEntry(self):
        self.item = self["config"].getCurrent()
        for x in self.onChangedEntry:
            x()

    def getCurrentValue(self):
        if self["config"].getCurrent() and len(self["config"].getCurrent()) > 0:
            return str(self["config"].getCurrent()[1].getText())
        return ""

    def getCurrentEntry(self):
        return self["config"].getCurrent() and self["config"].getCurrent()[0] or ""

    def createSummary(self):
        from Screens.Setup import SetupSummary
        return SetupSummary

    def keySave(self):
        # if not fileExists(self.skinFile + self.version):
            # for x in self['config'].list:
                # x[1].cancel()
            # self.close()
            # return

        for x in self['config'].list:
            if len(x) > 1:  # Check if x has at least two elements
                x[1].save()

        config.plugins.AglareNss.save()
        configfile.save()

        def append_skin_file(file_path, skin_lines):
            try:
                with open(file_path, 'r') as skFile:
                    skin_lines.extend(skFile.readlines())
            except FileNotFoundError:
                print("File not found:", file_path)

        skin_lines = []

        file_paths = [
            self.previewFiles + 'head-' + config.plugins.AglareNss.colorSelector.value + '.xml',
            self.previewFiles + 'font-' + config.plugins.AglareNss.FontStyle.value + '.xml',
            self.previewFiles + 'infobar-' + config.plugins.AglareNss.InfobarStyle.value + '.xml',
            self.previewFiles + 'infobar-' + config.plugins.AglareNss.InfobarPosterx.value + '.xml',
            self.previewFiles + 'infobar-' + config.plugins.AglareNss.InfobarXtraevent.value + '.xml',
            self.previewFiles + 'infobar-' + config.plugins.AglareNss.InfobarDate.value + '.xml',
            self.previewFiles + 'infobar-' + config.plugins.AglareNss.InfobarWeather.value + '.xml',
            self.previewFiles + 'secondinfobar-' + config.plugins.AglareNss.SecondInfobarStyle.value + '.xml',
            self.previewFiles + 'secondinfobar-' + config.plugins.AglareNss.SecondInfobarPosterx.value + '.xml',
            self.previewFiles + 'secondinfobar-' + config.plugins.AglareNss.SecondInfobarXtraevent.value + '.xml',
            self.previewFiles + 'channellist-' + config.plugins.AglareNss.ChannSelector.value + '.xml',
            self.previewFiles + 'eventview-' + config.plugins.AglareNss.EventView.value + '.xml',
            self.previewFiles + 'vol-' + config.plugins.AglareNss.VolumeBar.value + '.xml',
            self.previewFiles + 'e2iplayer-' + config.plugins.AglareNss.E2iplayerskins.value + '.xml'
        ]

        base_file = 'base.xml'
        if config.plugins.AglareNss.skinSelector.value == 'base1':
            base_file = 'base1.xml'
        file_paths.append(self.previewFiles + base_file)
        for path in file_paths:
            append_skin_file(path, skin_lines)
        with open(self.skinFile, 'w') as xFile:
            xFile.writelines(skin_lines)
        restartbox = self.session.openWithCallback(self.restartGUI, MessageBox, _('GUI needs a restart to apply a new skin.\nDo you want to Restart the GUI now?'), MessageBox.TYPE_YESNO)
        restartbox.setTitle(_('Restart GUI now?'))

    def restartGUI(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

    def checkforUpdate(self):
        try:
            fp = ''
            destr = '/tmp/AglareUpdate.txt'
            req = Request('http://nonsolosat.net/AglareImage/AglareUpdate.txt')
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
            fp = urlopen(req)
            fp = fp.read().decode('utf-8')
            print('fp read:', fp)
            with open(destr, 'w') as f:
                f.write(str(fp))  # .decode("utf-8"))
                f.seek(0)
            if fileExists(destr):
                with open(destr, 'r') as cc:
                    s1 = cc.readline()  # .decode("utf-8")
                    vers = s1.split('#')[0]
                    url = s1.split('#')[1]
                    version_server = vers.strip()
                    self.updateurl = url.strip()
                    cc.close()

                    if str(version_server) == str(version):
                        message = "%s %s\n%s %s\n\n%s" % (
                            _('Server version:'), version_server,
                            _('Version installed:'), version,
                            _('You have the current version Aglare!')
                        )
                        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)

                    elif version_server > version:
                        message = "%s %s\n%s %s\n\n%s" % (
                            _('Server version:'), version_server,
                            _('Version installed:'), version,
                            _('The update is available!\n\nDo you want to run the update now?')
                        )
                        self.session.openWithCallback(self.update, MessageBox, message, MessageBox.TYPE_YESNO)

                    else:
                        self.session.open(
                            MessageBox,
                            _('You have version %s!!!') % version,
                            MessageBox.TYPE_ERROR
                        )
        except Exception as e:
            print('error: ', str(e))

    def update(self, answer):
        if answer is True:
            self.session.open(AglareUpdater, self.updateurl)
        else:
            return

    def keyExit(self):
        self.close()


class AglareUpdater(Screen):

    def __init__(self, session, updateurl):
        self.session = session
        skin = '''<screen name="AglareUpdater" position="center,center" size="840,360" flags="wfNoBorder" backgroundColor="background">
                    <widget name="status" position="20,10" size="800,70" transparent="1" font="Regular;16" foregroundColor="foreground" backgroundColor="background" valign="center" halign="left" noWrap="1" />
                    <widget source="progress" render="Progress" position="100,153" size="400,6" transparent="1" borderWidth="0" />
                    <widget source="progresstext" render="Label" position="333,184" zPosition="2" font="Regular;18" halign="center" transparent="1" size="180,20" foregroundColor="foreground" backgroundColor="background" />
            </screen>'''
        self.skin = skin
        Screen.__init__(self, session)
        self.updateurl = updateurl
        print('self.updateurl', self.updateurl)
        self['status'] = Label()
        self['progress'] = Progress()
        self['progresstext'] = StaticText()
        self.downloading = False
        self.last_recvbytes = 0
        self.error_message = None
        self.download = None
        self.aborted = False
        self.startUpdate()

    def startUpdate(self):
        self['status'].setText(_('Downloading AglareNss...'))
        self.dlfile = '/tmp/aglarenss.tar'
        print('self.dlfile', self.dlfile)
        self.download = downloadWithProgress(self.updateurl, self.dlfile)
        self.download.addProgress(self.downloadProgress)
        self.download.start().addCallback(self.downloadFinished).addErrback(self.downloadFailed)

    def downloadFinished(self, string=''):
        self['status'].setText(_('Installing updates!'))
        os.system('tar -xvf /tmp/xxx.tar -C /')
        os.system('sync')
        os.system('rm -r /tmp/xxx.tar')
        os.system('sync')
        restartbox = self.session.openWithCallback(self.restartGUI, MessageBox, _('Aglare update was done!!!\nDo you want to restart the GUI now?'), MessageBox.TYPE_YESNO)
        restartbox.setTitle(_('Restart GUI now?'))

    def downloadFailed(self, failure_instance=None, error_message=''):
        text = _('Error downloading files!')
        if error_message == '' and failure_instance is not None:
            error_message = failure_instance.getErrorMessage()
            text += ': ' + error_message
        self['status'].setText(text)
        return

    def downloadProgress(self, recvbytes, totalbytes):
        self['status'].setText(_('Download in progress...'))
        self['progress'].value = int(100 * self.last_recvbytes // float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (self.last_recvbytes // 1024, totalbytes // 1024, 100 * self.last_recvbytes // float(totalbytes))
        self.last_recvbytes = recvbytes

    def restartGUI(self, answer=False):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()
