#!/usr/bin/python
# -*- coding: utf-8 -*-

#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially
#  distributed other than under the conditions noted above.
#  Lululla coder and MMark skinner 2022.07.20
#  NOT REMOVE DISCLAIMER!!!
from __future__ import absolute_import
from . import _
from .addons import Uri
from .addons.Utils import RequestAgent
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import configfile
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Components.config import config, ConfigOnOff
from Components.config import ConfigSubsection, getConfigListEntry
from Components.config import ConfigSelection, ConfigText
from Components.config import NoSave, ConfigNothing, ConfigYesNo
from Plugins.Plugin import PluginDescriptor
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Tools.Directories import fileExists
from Tools.Directories import SCOPE_PLUGINS
from Tools.Directories import resolveFilename
from enigma import ePicLoad, loadPic, eTimer
import os
import sys
import time

global nss_my_cur_skin, zaddon
PY3 = sys.version_info.major >= 3
thisdir = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('oZetaNSS'))
my_cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
cur_skin = 'oZetaNSS-FHD'
if str(my_cur_skin) == 'oZetaNSS-FHD':
    my_cur_skin = 'oZetaNSS-FHD'
OAWeather = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('OAWeather'))
weatherz = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('WeatherPlugin'))
theweather = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('TheWeather'))
SkinSelectorD = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('SystemPlugins/SkinSelector'))
SkinSelectorE = '/usr/lib/enigma2/python/Screens/SkinSelector.pyo'
SkinSelectorF = '/usr/lib/enigma2/python/Screens/SkinSelector.pyc'
zaddon = False
zaddons = os.path.join(thisdir, 'addons')
if os.path.exists(zaddons):
    zaddon = True
nss_my_cur_skin = False
_firstStartZ = True
mvi = '/usr/share/'
tmdb_skin = "%senigma2/%s/apikey" % (mvi, my_cur_skin)
tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_skin = "%senigma2/%s/omdbkey" % (mvi, my_cur_skin)
omdb_api = "cb1d9f55"
visual_skin = "/etc/enigma2/VisualWeather/apikey.txt"
visual_api = "5KAUFAYCDLUYVQPNXPN3K24V5"
thetvdb_skin = "%senigma2/%s/thetvdbkey" % (mvi, my_cur_skin)
thetvdbkey = 'D19315B88B2DE21F'
welcome = 'WELCOME Z USER\nfrom\nLululla and Mmark'
tarfile = '/tmp/download.tar'
plitrue = False
if os.path.exists('/usr/lib/enigma2/python/Plugins/PLi'):
    plitrue = True
#  -----------------

XStreamity = False
if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/XStreamity'):
    XStreamity = True

try:
    if nss_my_cur_skin is False:
        if fileExists(tmdb_skin):
            with open(tmdb_skin, "r") as f:
                tmdb_api = f.read()
        if fileExists(omdb_skin):
            with open(omdb_skin, "r") as f:
                omdb_api = f.read()
        if fileExists(visual_skin):
            with open(visual_skin, "r") as f:
                visual_api = f.read()
        if fileExists(thetvdb_skin):
            with open(thetvdb_skin, "r") as f:
                thetvdbkey = f.read()
        nss_my_cur_skin = True
except:
    nss_my_cur_skin = False
    pass

Uri.imagevers()
#  config section - ===========
version = '1.0_r1'
descplug = 'Customization tool for oZeta NSS Skin v.%s' % version
plugindesc = 'Manage your oZeta NSS Skin v.%s' % version
iconpic = 'plugin.png'
sample = mvi + 'enigma2/' + my_cur_skin + '/zSetup/zSample'


config.misc.pluginstyle = ConfigSelection(default="1", choices=[
    (1, _("Style 1")),
    (2, _("Style 2")),
    (3, _("Style 3")),
    (4, _("Style 4")),
    (5, _("Style 5")),
    (6, _("Style 6"))])


config.ozetanss = ConfigSubsection()
# ozetamenupredefinedlist = []
ozetainfobarpredefinedlist = []
ozetainfobarsecpredefinedlist = []
ozetachannelselectionpredefinedlist = []
ozetavolumepredefinedlist = []
ozetaradiopredefinedlist = []
ozetamediaplayerpredefinedlist = []
ozetaeventviewpredefinedlist = []
ozetapluginspredefinedlist = []
# ozetaalogopredefinedlist = []
# ozetablogopredefinedlist = []
# ozetamvipredefinedlist = []

config.ozetanss.actapi = NoSave(ConfigOnOff(default=False))
config.ozetanss.data = NoSave(ConfigOnOff(default=False))
config.ozetanss.api = NoSave(ConfigSelection(['-> Ok']))
config.ozetanss.txtapi = ConfigText(default=tmdb_api, visible_width=50, fixed_size=False)
config.ozetanss.data2 = NoSave(ConfigOnOff(default=False))
config.ozetanss.api2 = NoSave(ConfigSelection(['-> Ok']))
config.ozetanss.txtapi2 = ConfigText(default=omdb_api, visible_width=50, fixed_size=False)
config.ozetanss.data3 = NoSave(ConfigOnOff(default=False))
config.ozetanss.api3 = NoSave(ConfigSelection(['-> Ok']))
config.ozetanss.txtapi3 = ConfigText(default=visual_api, visible_width=50, fixed_size=False)
config.ozetanss.data4 = NoSave(ConfigOnOff(default=False))
config.ozetanss.api4 = NoSave(ConfigSelection(['-> Ok']))
config.ozetanss.txtapi4 = ConfigText(default=thetvdbkey, visible_width=50, fixed_size=False)
# config.ozetanss.mmpicons = NoSave(ConfigSelection(['-> Ok']))
# config.ozetanss.update = NoSave(ConfigOnOff(default=False))
# config.ozetanss.upfind = NoSave(ConfigSelection(['-> Ok']))
# config.ozetanss.options = NoSave(ConfigSelection(['-> Ok']))
config.ozetanss.zweather = NoSave(ConfigOnOff(default=False))
config.ozetanss.weather = NoSave(ConfigSelection(['-> Ok']))
config.ozetanss.oaweather = NoSave(ConfigSelection(['-> Ok']))
config.ozetanss.city = ConfigText(default='', visible_width=50, fixed_size=False)
# config.ozetanss.FirstMenuFHD = ConfigSelection(default='Menu Default', choices=ozetamenupredefinedlist)
config.ozetanss.FirstInfobarFHD = ConfigSelection(default='InfoBar Default', choices=ozetainfobarpredefinedlist)
config.ozetanss.SecondInfobarFHD = ConfigSelection(default='SecondInfoBar Default', choices=ozetainfobarsecpredefinedlist)
config.ozetanss.ChannSelectorFHD = ConfigSelection(default='Channel Default', choices=ozetachannelselectionpredefinedlist)
config.ozetanss.VolumeFHD = ConfigSelection(default='Volume Default', choices=ozetavolumepredefinedlist)
config.ozetanss.RadioFHD = ConfigSelection(default='RadioInfoBar Default', choices=ozetaradiopredefinedlist)
config.ozetanss.MediaPlayerFHD = ConfigSelection(default='MediaPlayer Default', choices=ozetamediaplayerpredefinedlist)
config.ozetanss.EventviewFHD = ConfigSelection(default='Eventview Default', choices=ozetaeventviewpredefinedlist)
config.ozetanss.PluginsFHD = ConfigSelection(default='PluginBrowser Default', choices=ozetapluginspredefinedlist)
# config.ozetanss.LogoaFHD = ConfigSelection(default='TopLogo Default', choices=ozetaalogopredefinedlist)
# config.ozetanss.LogobFHD = ConfigSelection(default='BottomLogo Default', choices=ozetablogopredefinedlist)
# config.ozetanss.Logoboth = ConfigSelection(default='Bootlogo Default', choices=ozetamvipredefinedlist)
config.ozetanss.XStreamity = NoSave(ConfigSelection(['-> Ok']))
config.ozetanss.fake = NoSave(ConfigNothing())

#  parameters - =============
try:
    f = os.listdir('%s/' % sample)
except:
    f = []
if f:
    for line in f:
        # print('file line ', line)
        parts = line.split()
        nssline = parts[0][:-4]
        # print("********** Find %s" % nssline)
        # if 'menu_' in nssline:
            # ozetamenu = nssline[5:].replace("-", " ")
            # ozetamenupredefinedlist.append(ozetamenu)
        # if 'bootlogo_' in nssline:
            # ozetabootlogo = nssline[9:].replace("-", " ")
            # ozetamvipredefinedlist.append(ozetabootlogo)
        if 'infobar_' in nssline:
            ozetainfobar = nssline[8:].replace("-", " ")
            ozetainfobarpredefinedlist.append(ozetainfobar)
        if 'second_' in nssline:
            ozetasecinfobar = nssline[7:].replace("-", " ")
            ozetainfobarsecpredefinedlist.append(ozetasecinfobar)
        if 'channel_' in nssline:
            ozetachannelselection = nssline[8:].replace("-", " ")
            ozetachannelselectionpredefinedlist.append(ozetachannelselection)
        if 'volume_' in nssline:
            ozetavolume = nssline[7:].replace("-", " ")
            ozetavolumepredefinedlist.append(ozetavolume)
        if 'radio_' in nssline:
            ozetaradio = nssline[6:].replace("-", " ")
            ozetaradiopredefinedlist.append(ozetaradio)
        if 'mediaplayer_' in nssline:
            ozetamediaplayer = nssline[12:].replace("-", " ")
            ozetamediaplayerpredefinedlist.append(ozetamediaplayer)
        if 'eventview_' in nssline:
            ozetaeventview = nssline[10:].replace("-", " ")
            ozetaeventviewpredefinedlist.append(ozetaeventview)
        if not os.path.exists('/usr/lib/enigma2/python/Plugins/PLi'):
            if 'plugins_' in nssline:
                ozetaplugins = nssline[8:].replace("-", " ")
                ozetapluginspredefinedlist.append(ozetaplugins)
        # if 'alogo_' in nssline:
            # ozetalogo = nssline[6:].replace("-", " ")
            # ozetaalogopredefinedlist.append(ozetalogo)
        # else:
            # if'blogo_' in nssline:
                # ozetalogob = nssline[6:].replace("-", " ")
                # ozetablogopredefinedlist.append(ozetalogob)
    # ozetamenupredefinedlist.sort()
    ozetainfobarpredefinedlist.sort()
    ozetainfobarsecpredefinedlist.sort()
    ozetachannelselectionpredefinedlist.sort()
    ozetavolumepredefinedlist.sort()
    ozetaradiopredefinedlist.sort()
    ozetamediaplayerpredefinedlist.sort()
    ozetaeventviewpredefinedlist.sort()
    if not os.path.exists('/usr/lib/enigma2/python/Plugins/PLi'):
        ozetapluginspredefinedlist.sort()
    # ozetamvipredefinedlist.sort()
    # ozetaalogopredefinedlist.sort()
    # ozetablogopredefinedlist.sort()
    # if ozetamenupredefinedlist and 'Menu Default' in ozetamenupredefinedlist:
        # config.ozetanss.FirstMenuFHD = ConfigSelection(default='Menu Default', choices=ozetamenupredefinedlist)
    # else:
        # config.ozetanss.FirstMenuFHD = ConfigSelection(choices=ozetamenupredefinedlist)
    if ozetainfobarpredefinedlist and 'InfoBar Default' in ozetainfobarpredefinedlist:
        config.ozetanss.FirstInfobarFHD = ConfigSelection(default='InfoBar Default', choices=ozetainfobarpredefinedlist)
    else:
        config.ozetanss.FirstInfobarFHD = ConfigSelection(choices=ozetainfobarpredefinedlist)
    if ozetainfobarsecpredefinedlist and 'SecondInfoBar Default' in ozetainfobarsecpredefinedlist:
        config.ozetanss.SecondInfobarFHD = ConfigSelection(default='SecondInfoBar Default', choices=ozetainfobarsecpredefinedlist)
    else:
        config.ozetanss.SecondInfobarFHD = ConfigSelection(choices=ozetainfobarsecpredefinedlist)
    if ozetachannelselectionpredefinedlist and 'Channel Default' in ozetachannelselectionpredefinedlist:
        config.ozetanss.ChannSelectorFHD = ConfigSelection(default='Channel Default', choices=ozetachannelselectionpredefinedlist)
    else:
        config.ozetanss.ChannSelectorFHD = ConfigSelection(choices=ozetachannelselectionpredefinedlist)
    if ozetavolumepredefinedlist and 'Volume Default' in ozetavolumepredefinedlist:
        config.ozetanss.VolumeFHD = ConfigSelection(default='Volume Default', choices=ozetavolumepredefinedlist)
    else:
        config.ozetanss.VolumeFHD = ConfigSelection(choices=ozetavolumepredefinedlist)
    if ozetaradiopredefinedlist and 'RadioInfoBar Default' in ozetaradiopredefinedlist:
        config.ozetanss.RadioFHD = ConfigSelection(default='RadioInfoBar Default', choices=ozetaradiopredefinedlist)
    else:
        config.ozetanss.RadioFHD = ConfigSelection(choices=ozetaradiopredefinedlist)
    if ozetamediaplayerpredefinedlist and 'MediaPlayer Default' in ozetamediaplayerpredefinedlist:
        config.ozetanss.MediaPlayerFHD = ConfigSelection(default='MediaPlayer Default', choices=ozetamediaplayerpredefinedlist)
    else:
        config.ozetanss.MediaPlayerFHD = ConfigSelection(choices=ozetamediaplayerpredefinedlist)
    if ozetaeventviewpredefinedlist and 'Eventview Default' in ozetaeventviewpredefinedlist:
        config.ozetanss.EventviewFHD = ConfigSelection(default='Eventview Default', choices=ozetaeventviewpredefinedlist)
    else:
        config.ozetanss.EventviewFHD = ConfigSelection(choices=ozetaeventviewpredefinedlist)
    if not os.path.exists('/usr/lib/enigma2/python/Plugins/PLi'):
        if ozetapluginspredefinedlist and 'PluginBrowser Default' in ozetapluginspredefinedlist:
            config.ozetanss.PluginsFHD = ConfigSelection(default='PluginBrowser Default', choices=ozetapluginspredefinedlist)
        else:
            config.ozetanss.PluginsFHD = ConfigSelection(choices=ozetapluginspredefinedlist)

    # if ozetaalogopredefinedlist and 'TopLogo Default' in ozetaalogopredefinedlist:
        # config.ozetanss.LogoaFHD = ConfigSelection(default='TopLogo Default', choices=ozetaalogopredefinedlist)
    # else:
        # config.ozetanss.LogoaFHD = ConfigSelection(choices=ozetaalogopredefinedlist)
    # if ozetablogopredefinedlist and 'BottomLogo Default' in ozetablogopredefinedlist:
        # config.ozetanss.LogobFHD = ConfigSelection(default='BottomLogo Default', choices=ozetablogopredefinedlist)
    # else:
        # config.ozetanss.LogobFHD = ConfigSelection(choices=ozetablogopredefinedlist)
    # if ozetamvipredefinedlist and 'Bootlogo Default' in ozetamvipredefinedlist:
        # config.ozetanss.Logoboth = ConfigSelection(default='Bootlogo Default', choices=ozetamvipredefinedlist)
    # else:
        # config.ozetanss.Logoboth = ConfigSelection(choices=ozetamvipredefinedlist)


def fakeconfig(name):
    retr = [
           ['NONSOLOSAT SKIN OPTIONS'],
           ['NONSOLOSAT SKIN: INSTALLED BUT NOT ACTIVE'],
           ['SKIN PARTS SETUP'],
           ['SERVER API KEY SETUP'],
           ['WEATHER BOX SETUP'],
           ['MISC SETUP'],
           ['API KEY SETUP:'],
           ['TMDB API:'],
           ['OMDB API:'],
           ['THETVDB API:'],
           ['WEATHER:'],
           ['Update Conponent Skin'],
           ['--Load TMDB Apikey'],
           ['--Load OMDB Apikey'],
           ['-Load THETVDB Apikey'],
           ['Install'],
           ['VisualWeather Plugin API:'],
           ['--Load VISUALWEATHER Apikey'],
           ['Install or Open mmPicons Plugin']]
    for nname in retr:
        if nname[0] in str(name):
            return True
    return False


def localreturn(name):
    retr = [
        ["pluginbrowser", "pluginbrowser"],
        ["omdb", "omdb"],
        ["tmdb", "tmdb"],
        ["thetvdb", "thetvdb"],
        ["oaweather ", "oaweather"],
        ["weather", "weather"],
        ["autoupdate", "autoupdate"],
        ["update", "update"],
        ["ok", "ok"],
        ["mmpicons", "mmpicons"],
        ["xstreamity", "xstreamity"],
        ["bootlogo", "bootlogo"],
        ["setup", "setup"],
        ["options", "options"],
        ["tmdb api:", "tmdb api:"],
        ["omdb api:", "omdb api:"],
        ["visualweather api:", "visualweather api:"],
    ]
    for nname in retr:
        if nname[0] in str(name).lower():
            return True
    return False


class oZetaNSS(ConfigListScreen, Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        global _session
        _session = session
        self.session = session
        skin = os.path.join(thisdir, 'skin/oZetaNSS.xml')
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('oZetaNSS Skin Setup')
        self.onChangedEntry = []
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
        self.skinFileTmp = '%senigma2/%s/zSkin/skin_infochannel.tmp' % (mvi, my_cur_skin)
        self.skinFile = '%senigma2/%s/zSkin/skin_infochannel.xml' % (mvi, my_cur_skin)
        self.chooseFile = '%s/' % sample
        self.getImg = Uri.imagevers()
        self['Preview'] = Pixmap()
        self['key_red'] = Label(_('Cancel'))
        self['key_green'] = Label(_('Save'))
        self['key_yellow'] = Label('')
        if str(my_cur_skin) == 'oZetaNSS-FHD':
            self['key_yellow'] = Label(_('Preview'))
        # self['key_blue'] = Label(_('Restart'))
        # self["key_blue"] = StaticText(self.getSkinSelector() is not None and "Skin" or "")
        self["key_blue"] = Label('Skin')
        # self["key_blue"].hide()
        self["HelpWindow"] = Pixmap()
        self["HelpWindow"].hide()
        self["VKeyIcon"] = Pixmap()
        self["VKeyIcon"].hide()
        self['status'] = StaticText()
        self['description'] = Label("SELECT YOUR CHOICE")
        self['author'] = Label(_('by Lululla'))
        self['image'] = Label('')
        self['city'] = Label('')

        self.PicLoad = ePicLoad()
        self.Scale = AVSwitch().getFramebufferScale()
        try:
            self.PicLoad.PictureData.get().append(self.DecodePicture)
        except:
            self.PicLoad_conn = self.PicLoad.PictureData.connect(self.DecodePicture)
        self['actions'] = ActionMap([
            'DirectionActions',
            'EPGSelectActions',
            'MenuActions',
            'NumberActions',
            'OkCancelActions',
            'HelpActions',
            'InfoActions',
            'ColorActions',
            'VirtualKeyboardActions',
            'HotkeyActions',
        ], {
            'left': self.keyLeft,
            'down': self.keyDown,
            'up': self.keyUp,
            'right': self.keyRight,
            'red': self.zExit,
            'green': self.nssSave,
            # 'InfoPressed': self.zHelp,
            'info': self.zHelp,
            'displayHelp': self.zHelp,
            # 'EPGPressed': self.zHelp,
            'yellow': self.ShowPictureFull,
            # 'blue': self.zSwitchMode,
            'blue': self.keyOpenSkinselector,
            'menu': self.KeyMenu,
            'showVirtualKeyboard': self.KeyText,
            'ok': self.keyRun,
            '0': self.nssDefault,
            '5': self.answercheck,
            'yellowlong': self.answercheck,
            'yellow_long': self.answercheck,
            'cancel': self.zExit}, -2)
        self.createSetup()
        if self.setInfo not in self['config'].onSelectionChanged:
            self['config'].onSelectionChanged.append(self.setInfo)
        self.current_skin = config.skin.primary_skin.value
        self.onFirstExecBegin.append(self.check_dependencies)
        self.onLayoutFinish.append(self.__layoutFinished)
        self.onLayoutFinish.append(self.UpdatePicture)

    def passs(self, foo):
        pass

    def __layoutFinished(self):
        self.setTitle(self.setup_title)

    def check_dependencies(self):
        dependencies = True
        try:
            import requests
        except Exception as e:
            print("**** missing dependencies ***")
            print(e)
            dependencies = False
        if dependencies is False:
            os.chmod("/usr/lib/enigma2/python/Plugins/Extensions/oZetaNSS/dependencies.sh", 0o0755)
            cmd1 = ". /usr/lib/enigma2/python/Plugins/Extensions/oZetaNSS/dependencies.sh"
            self.session.openWithCallback(self.layoutFinished, Console, title="Checking Python Dependencies", cmdlist=[cmd1], closeOnSuccess=False)
        else:
            if str(my_cur_skin) != 'oZetaNSS-FHD' and os.path.exists('/usr/share/enigma2/oZetaNSS-FHD'):
                text = _("ATTENTION!!\nThe Skin is already installed:\nto activate you must choose from:\nmenu-setup-system-skin\nand select it!\nNow you can only update the installation.")
                self.msg = self.session.openWithCallback(self.passs, MessageBox, text, MessageBox.TYPE_INFO, timeout=5)
            self.layoutFinished()

    def layoutFinished(self):
        if os.path.isdir(weatherz):
            self.UpdateComponents()
        self.createSetup()
        self.nssXml()
        # self.UpdatePicture()
        self['image'].setText("%s" % Uri.imagevers())
        self['city'].setText("%s" % str(config.ozetanss.city.value))
        self.setTitle(self.setup_title)

    def getSkinSelector(self):
        try:
            if os.path.exists(SkinSelectorD):
                from Plugins.SystemPlugins.SkinSelector.plugin import SkinSelector
                return SkinSelector
            elif os.path.exists(SkinSelectorE) or os.path.exists(SkinSelectorF):
                from Screens.SkinSelector import SkinSelector
                return SkinSelector
        except Exception as e:
            print(e)

    def keyOpenSkinselector(self):
        try:
            if self.getSkinSelector() is not None:
                self.session.openWithCallback(self.restoreCurrentSkin, self.getSkinSelector())
        except Exception as e:
            print(e)

    def restoreCurrentSkin(self, SkinSelector):
        try:
            print("[oZetaNSS] restore current skin")
            config.skin.primary_skin.value = self.current_skin
            config.skin.primary_skin.save()
        except Exception as e:
            print(e)

    def answercheck(self, answer=None):
        if str(my_cur_skin) == 'oZetaNSS-FHD':
            if answer is None:
                self.session.openWithCallback(self.answercheck, MessageBox, _("This operation checks if the skin has its components (is not sure)..\nDo you really want to continue?"))
            else:
                if zaddon is True:
                    from .addons import checkskin
                    self.check_module = eTimer()
                    check = checkskin.check_module_skin()
                    try:
                        self.check_module_conn = self.check_module.timeout.connect(check)
                    except:
                        self.check_module.callback.append(check)
                    self.check_module.start(100, True)
                    self.openVi()

    def openVi(self):
        from .addons.type_utils import zEditor
        user_log = '/tmp/debug_my_skin.log'
        if fileExists(user_log):
            self.session.open(zEditor, user_log)

    def _space(self):
        self.list.append(getConfigListEntry(" ", config.ozetanss.fake, False))

    def createSetup(self):
        self.editListEntry = None
        self.list = []
        # char = 120
        # tab = " " * 9
        # sep = "-"
        try:
            if str(my_cur_skin) != 'oZetaNSS-FHD' and os.path.exists('/usr/share/enigma2/oZetaNSS-FHD'):
                self.list.append(getConfigListEntry(_("NONSOLOSAT SKIN: INSTALLED BUT NOT ACTIVE")))

            if str(my_cur_skin) == 'oZetaNSS-FHD':
                self.list.append(getConfigListEntry(_("NONSOLOSAT SKIN OPTIONS")))
                # if ozetamenupredefinedlist:
                    # self.list.append(getConfigListEntry('Menu:', config.ozetanss.FirstMenuFHD, _("Settings Menu Image Panel")))
                if ozetainfobarpredefinedlist:
                    self.list.append(getConfigListEntry('Infobar:', config.ozetanss.FirstInfobarFHD, _("Settings Infobar Panels")))
                if ozetainfobarsecpredefinedlist:
                    self.list.append(getConfigListEntry('Second Infobar:', config.ozetanss.SecondInfobarFHD, _("Settings SecInfobar Panels")))
                if ozetachannelselectionpredefinedlist:
                    self.list.append(getConfigListEntry('Channel Selection:', config.ozetanss.ChannSelectorFHD, _("Settings Channel Panels")))
                if ozetavolumepredefinedlist:
                    self.list.append(getConfigListEntry('Volume Panel:', config.ozetanss.VolumeFHD, _("Settings Volume Panels")))
                if ozetaradiopredefinedlist:
                    self.list.append(getConfigListEntry('Radio Panel:', config.ozetanss.RadioFHD, _("Settings Radio Panels")))
                if ozetamediaplayerpredefinedlist:
                    self.list.append(getConfigListEntry('MediaPlayer Panel:', config.ozetanss.MediaPlayerFHD, _("Settings MediaPlayer Panels")))
                if ozetaeventviewpredefinedlist:
                    self.list.append(getConfigListEntry('Eventview Panel:', config.ozetanss.EventviewFHD, _("Settings Eventview Panels")))
                self.list.append(getConfigListEntry('PluginBrowser Style:', config.misc.pluginstyle, _("Settings Style PluginBrowser [need restart GUI]")))
                if not os.path.exists('/usr/lib/enigma2/python/Plugins/PLi'):
                    if ozetapluginspredefinedlist:
                        self.list.append(getConfigListEntry('PluginBrowser Panel:', config.ozetanss.PluginsFHD, _("Settings PluginBrowser Panels")))
                # if ozetaalogopredefinedlist:
                    # self.list.append(getConfigListEntry('Logo Image Top:', config.ozetanss.LogoaFHD, _("Settings Logo Image Top")))
                # if ozetablogopredefinedlist:
                    # self.list.append(getConfigListEntry('Logo Image Bottom:', config.ozetanss.LogobFHD, _("Settings Logo Image Bottom")))
                # if ozetamvipredefinedlist:
                    # self.list.append(getConfigListEntry('Bootlogo Image:', config.ozetanss.Logoboth, _("Settings Bootlogo Image\nPress Ok for change")))
                self.list.append(getConfigListEntry(("SERVER API KEY SETUP")))
                self.list.append(getConfigListEntry("API KEY SETUP:", config.ozetanss.actapi, _("Settings oZeta Apikey Server")))
                if config.ozetanss.actapi.value is True:
                    self.list.append(getConfigListEntry("TMDB API:", config.ozetanss.data, _("Settings TMDB ApiKey")))
                    if config.ozetanss.data.value is True:
                        self.list.append(getConfigListEntry("--Load TMDB Apikey", config.ozetanss.api, _("Load TMDB Apikey from /tmp/apikey.txt")))
                        self.list.append(getConfigListEntry("--Set TMDB Apikey", config.ozetanss.txtapi, _("Signup on TMDB and input free personal ApiKey")))
                    self.list.append(getConfigListEntry("OMDB API:", config.ozetanss.data2, _("Settings OMDB APIKEY")))
                    if config.ozetanss.data2.value is True:
                        self.list.append(getConfigListEntry("--Load OMDB Apikey", config.ozetanss.api2, _("Load OMDB Apikey from /tmp/omdbkey.txt")))
                        self.list.append(getConfigListEntry("--Set OMDB Apikey", config.ozetanss.txtapi2, _("Signup on OMDB and input free personal ApiKey")))
                    self.list.append(getConfigListEntry("THETVDB API:", config.ozetanss.data4, _("Settings THETVDB APIKEY")))
                    if config.ozetanss.data4.value is True:
                        self.list.append(getConfigListEntry("--Load THETVDB Apikey", config.ozetanss.api4, _("Load THETVDB Apikey from /tmp/thetvdbkey.txt")))
                        self.list.append(getConfigListEntry("--Set THETVDB Apikey", config.ozetanss.txtapi4, _("Signup on THETVDB and input free personal ApiKey")))
            self.list.append(getConfigListEntry(("WEATHER BOX SETUP")))
            self.list.append(getConfigListEntry("WEATHER:", config.ozetanss.zweather, _("Settings oZeta Weather")))
            if config.ozetanss.zweather.value is True:
                # if os.path.isdir(OAWeather):
                self.list.append(getConfigListEntry("Install or Open OAWeather Plugin", config.ozetanss.oaweather, _("Install or Open OAWeather Plugin\nPress OK")))
                self.list.append(getConfigListEntry("Install or Open Weather Plugin", config.ozetanss.weather, _("Install or Open Weather Plugin\nPress OK")))
                if os.path.isdir(weatherz):
                    self.list.append(getConfigListEntry("--Setting Weather City", config.ozetanss.city, _("Settings City Weather Plugin")))
                VisualWeather = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('VisualWeather'))
                if os.path.isdir(VisualWeather):
                    self.list.append(getConfigListEntry("VisualWeather Plugin API:", config.ozetanss.data3, _("Settings VISUALWEATHER APIKEY")))
                    if config.ozetanss.data3.value is True:
                        self.list.append(getConfigListEntry("--Load VISUALWEATHER Apikey", config.ozetanss.api3, _("Load VISUALWEATHER Apikey from /etc/enigma2/VisualWeather/apikey.txt")))
                        self.list.append(getConfigListEntry("--Set VISUALWEATHER Apikey", config.ozetanss.txtapi3, _("Signup on www.visualcrossing.com and input free personal ApiKey")))
            if XStreamity is True:
                self.list.append(getConfigListEntry(("MISC SETUP")))
                # self.list.append(getConfigListEntry("Install or Open mmPicons Plugin", config.ozetanss.mmpicons, _("Install or Open mmPicons Plugin\nPress OK")))
                self.list.append(getConfigListEntry('Install Skin Zeta for XStreamity Plugin (only FHD)', config.ozetanss.XStreamity, _("Install Skin Zeta for XStreamity Plugin (only FHD)\nPress Ok")))
            self["config"].list = self.list
            self["config"].l.setList(self.list)
            # self.handleInputHelpers()
        except KeyError:
            print("keyError")

    def setInfo(self):
        try:
            sel = self['config'].getCurrent()[2]
            if sel:
                self['description'].setText(str(sel))
            else:
                self['description'].setText(_('SELECT YOUR CHOICE'))
            return
        except Exception as e:
            print("Error setInfo ", e)

    def handleInputHelpers(self):
        from enigma import ePoint
        currConfig = self["config"].getCurrent()
        if currConfig is not None:
            if isinstance(currConfig[1], ConfigText):
                if "VKeyIcon" in self:
                    try:
                        self["VirtualKB"].setEnabled(True)
                    except:
                        pass
                    try:
                        self["virtualKeyBoardActions"].setEnabled(True)
                    except:
                        pass
                    self["VKeyIcon"].show()

                if "HelpWindow" in self and currConfig[1].help_window and currConfig[1].help_window.instance is not None:
                    helpwindowpos = self["HelpWindow"].getPosition()
                    currConfig[1].help_window.instance.move(ePoint(helpwindowpos[0], helpwindowpos[1]))
            else:
                if "VKeyIcon" in self:
                    try:
                        self["VirtualKB"].setEnabled(False)
                    except:
                        pass
                    try:
                        self["virtualKeyBoardActions"].setEnabled(False)
                    except:
                        pass
                    self["VKeyIcon"].hide()

    # def selectionChanged(self):
        # self['status'].setText(self['config'].getCurrent()[0])

    def changedEntry(self):
        self.item = self["config"].getCurrent()
        for x in self.onChangedEntry:
            x()

        try:
            if isinstance(self["config"].getCurrent()[1], ConfigYesNo) or isinstance(self["config"].getCurrent()[1], ConfigSelection):
                self.createSetup()
        except:
            pass

    def getCurrentEntry(self):
        return self["config"].getCurrent() and self["config"].getCurrent()[0] or ""

    def getCurrentValue(self):
        return self["config"].getCurrent() and str(self["config"].getCurrent()[1].getText()) or ""

    def createSummary(self):
        from Screens.Setup import SetupSummary
        return SetupSummary

    def keyRun(self):
        sel = self["config"].getCurrent()[1]
        if sel and sel == config.ozetanss.api:
            self.keyApi()
        if sel and sel == config.ozetanss.txtapi:
            self.KeyText()
        if sel and sel == config.ozetanss.api2:
            self.keyApi2()
        if sel and sel == config.ozetanss.txtapi2:
            self.KeyText()
        if sel and sel == config.ozetanss.api3:
            self.keyApi3()
        if sel and sel == config.ozetanss.txtapi3:
            self.KeyText()
        if sel and sel == config.ozetanss.api4:
            self.keyApi4()
        if sel and sel == config.ozetanss.txtapi4:
            self.KeyText()
        # if sel and sel == config.ozetanss.mmpicons:
            # self.mmWaitReload()
        if sel and sel == config.ozetanss.XStreamity:
            self.zXStreamity()
        if sel and sel == config.ozetanss.weather:
            self.KeyMenu()
        if sel and sel == config.ozetanss.oaweather:
            self.KeyMenu2()
        if sel and sel == config.ozetanss.city:
            self.KeyText()
        else:
            return
        return

    def zXStreamity(self, answer=None):
        if XStreamity is True:
            if answer is None:
                self.session.openWithCallback(self.zXStreamity, MessageBox, _('Install Skin Zeta for XStreamity Plugin (only FHD)\nDo you really want to install now?'))
            elif answer:
                try:
                    Options = self.session.openWithCallback(Uri.zXStreamop, MessageBox, _('Install Skin Zeta for XStreamity Plugin (only FHD)...\nPlease Wait'), MessageBox.TYPE_INFO, timeout=4)
                    Options.setTitle(_('Install Skin Zeta for XStreamity Plugin'))
                    print('Install Skin Zeta for XStreamity Plugin - Done!!!')
                    self.createSetup()
                except Exception as e:
                    print('error zXStreamity ', e)
        else:
            self.session.open(MessageBox, _("Missing XStreamity Plugins!"), MessageBox.TYPE_INFO, timeout=4)

    def zLogoboth(self, answer=None):
        sel2 = self['config'].getCurrent()[1].value
        print('sel2-- ', sel2)
        sel2 = sel2.replace(" ", "-")
        filemvi = self.chooseFile + 'bootlogo_' + sel2 + '.mvi'
        origmvi = self.chooseFile + 'bootlogo_Original-Bootlogo.mvi'
        print('filemvi ', filemvi)
        if answer is None:
            self.session.openWithCallback(self.zLogoboth, MessageBox, _("Do you really want to change Bootlogo image?"))
        elif answer:
            print('answer True')
            if filemvi == origmvi:
                os.remove('%s%s' % (mvi, 'default_bootlogo.mvi'))
            if fileExists('%s%s' % (mvi, 'default_bootlogo.mvi')):
                # overwrite
                cmdz = 'cp -rf %s %sbootlogo.mvi > /dev/null 2>&1' % (filemvi, mvi)
                os.system(cmdz)
                self.session.open(MessageBox, _('Bootlogo changed and backup to default_bootlogo.mvi!'), MessageBox.TYPE_INFO, timeout=5)
            else:
                if fileExists('%sbootlogo.mvi' % mvi):
                    cmdk = 'cp -rf %sbootlogo.mvi %sdefault_bootlogo.mvi > /dev/null 2>&1' % (mvi, mvi)
                    # print('file moved to default_bootlogo.mvi ', cmdk)
                    os.system(cmdk)
                    # copy original mvi to zsetup only the first time
                    if not fileExists(origmvi):
                        cmdk = 'cp -rf %sbootlogo.mvi %s > /dev/null 2>&1' % (mvi, origmvi)
                        # print('file moved to bootlogo_Original-Bootlogo.mvi ', cmdk)
                        os.system(cmdk)
                    # overwrite
                    cmdz = 'cp -rf %s %sbootlogo.mvi > /dev/null 2>&1' % (filemvi, mvi)
                    # print('apply bootlogo ', cmdz)
                    os.system(cmdz)
                    self.session.open(MessageBox, _('Bootlogo changed!\nRestart Gui please'), MessageBox.TYPE_INFO, timeout=5)

    def zHelp(self):
        self.session.open(ozHelp)

    def ShowPictureFull(self):
        try:
            self.path = self.GetPicturePath()
            if fileExists(self.path):
                self.session.open(ShowPictureFullX, self.path)
        except:
            return

    def nssXml(self):
        self['author'].setText(welcome)
        sel1 = self['config'].getCurrent()[1].value  # InfoBar-Meteo
        selx = self['config'].getCurrent()[0]

        if localreturn(selx):
            return
        sel2 = sel1.replace(" ", "-")
        filexml = ''
        # if 'menu' in sel2.lower():
            # filexml = self.chooseFile + 'menu_' + sel2 + '.xml'
        if 'infobar' in sel2.lower():
            filexml = self.chooseFile + 'infobar_' + sel2 + '.xml'
        if 'second' in sel2.lower():
            filexml = self.chooseFile + 'second_' + sel2 + '.xml'
        if 'channel' in sel2.lower():
            filexml = self.chooseFile + 'channel_' + sel2 + '.xml'
        if 'radio' in sel2.lower():
            filexml = self.chooseFile + 'radio_' + sel2 + '.xml'
        if 'mediaplayer' in sel2.lower():
            filexml = self.chooseFile + 'mediaplayer_' + sel2 + '.xml'
        if 'eventview' in sel2.lower():
            filexml = self.chooseFile + 'eventview_' + sel2 + '.xml'
        if 'plugins' in sel2.lower():
            filexml = self.chooseFile + 'plugins_' + sel2 + '.xml'
        if 'bottom' in sel2.lower():
            filexml = self.chooseFile + 'blogo_' + sel2 + '.xml'
        if 'top' in sel2.lower():
            filexml = self.chooseFile + 'alogo_' + sel2 + '.xml'
        if 'volume' in sel2.lower():
            filexml = self.chooseFile + 'volume_' + sel2 + '.xml'
        # print('===========filexml========== ', filexml)
        #  <!-- Author mmark Infobar + Crypt + Cover + DataChannel + IP -->
        if fileExists(filexml):
            with open(filexml, 'r') as openFile:
                for x in openFile:
                    y = x.find('Author')
                    if y > 1:
                        x = x.replace('<!-- ', '').replace(' -->', '')
                        x.replace('+', '\n')
                        x = x.strip()
                        break
                self['author'].setText(x)
        else:
            try:
                self['author'].setText(welcome)
                cpr = Uri.get_cpyright()
                self['description'].setText(cpr)
            except Exception as e:
                print(e)
                self['author'].setText(welcome)
                self['description'].setText('-')

# (1, _("Style 1")),
# (2, _("Style 2")),
# (3, _("Style 3")),
# (4, _("Style 4")),
# (5, _("Style 5")),
# (6, _("Style 6"))])

    def GetPicturePath(self):
        PicturePath = '%sbasefile/default.jpg' % thisdir
        sel = self["config"].getCurrent()[1]
        sel2 = self['config'].getCurrent()[1].value
        xxxx = self["config"].getCurrent()[0]
        # print('sel2: ', str(sel2))
        # print(type(sel2))
        returnValue = '%sbasefile/default.jpg' % thisdir
        try:
            if 'tmdb api:' in xxxx.lower():
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'tmdb'))
                return PicturePath
            if 'omdb api:' in xxxx.lower():
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'omdb'))
                return PicturePath
            if 'thetvdb api:' in xxxx.lower():
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'thetvdb'))
                return PicturePath
            if 'visualweather plugin api:' in xxxx.lower():
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'visualweather'))
                return PicturePath

            if '1' in str(sel2) and 'style' in xxxx.lower():
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'style1'))
                return PicturePath
            if '2' in str(sel2) and 'style' in xxxx.lower():
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'style2'))
                return PicturePath
            if '3' in str(sel2) and 'style' in xxxx.lower():
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'style3'))
                return PicturePath
            if '4' in str(sel2) and 'style' in xxxx.lower():
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'style4'))
                return PicturePath
            if '5' in str(sel2) and 'style' in xxxx.lower():
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'style5'))
                return PicturePath
            if '6' in str(sel2) and 'style' in xxxx.lower():
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'style6'))
                return PicturePath

            c = ['setup', 'autoupdate', ' weather', 'oaweather', 'nonsolosat']
            if xxxx.lower() in c:
                PicturePath = '%sbasefile/default.jpg' % thisdir
                return PicturePath

            if sel and sel == config.ozetanss.data:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'tmdb'))
            if sel and sel == config.ozetanss.data2:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'omdb'))
            if sel and sel == config.ozetanss.data3:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'visualweather'))
            if sel and sel == config.ozetanss.data4:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'thetvdb'))
            # if sel and sel == config.ozetanss.mmpicons:
                # PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'mmPicons'))
            if sel and sel == config.ozetanss.api:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'API-Apikey'))
            if sel and sel == config.ozetanss.txtapi:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'API-Manualkey'))
            if sel and sel == config.ozetanss.api2:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'API-Apikey2'))
            if sel and sel == config.ozetanss.txtapi2:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'API-Manualkey'))
            if sel and sel == config.ozetanss.api3:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'API-Apikey3'))
            if sel and sel == config.ozetanss.txtapi3:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'API-Manualkey'))
            if sel and sel == config.ozetanss.api4:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'API-Apikey4'))
            if sel and sel == config.ozetanss.txtapi4:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'API-Manualkey'))
            if sel and sel == config.ozetanss.XStreamity:
                PicturePath = ('%sbasefile/%s.jpg' % (thisdir, 'xstreamity'))
            
            if sel2 is not None or sel2 != '' or sel2 != 'None':
                returnValue = str(sel2).replace(" ", "-")
            if fileExists('%senigma2/%s/zSetup/zPreview/%s.jpg' % (mvi, my_cur_skin, returnValue)):
                PicturePath = '%senigma2/%s/zSetup/zPreview/%s.jpg' % (mvi, my_cur_skin, returnValue)
            else:
                return '%sbasefile/default.jpg' % thisdir
        except Exception as e:
            print(e)
        return PicturePath

    def UpdatePicture(self):
        self.onLayoutFinish.append(self.ShowPicture)

    def ShowPicture(self, data=None):
        if self["Preview"].instance:
            width = 700
            height = 394
            self.PicLoad.setPara([width, height, self.Scale[0], self.Scale[1], 0, 1, "FF000000"])
            if self.PicLoad.startDecode(self.GetPicturePath()):
                self.PicLoad = ePicLoad()
                try:
                    self.PicLoad.PictureData.get().append(self.DecodePicture)
                except:
                    self.PicLoad_conn = self.PicLoad.PictureData.connect(self.DecodePicture)
            return

    def DecodePicture(self, PicInfo=None):
        ptr = self.PicLoad.getData()
        if ptr is not None:
            self["Preview"].instance.setPixmap(ptr)
            self["Preview"].instance.show()
        return

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.createSetup()
        self.nssXml()
        self.ShowPicture()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.createSetup()
        self.nssXml()
        self.ShowPicture()

    def keyDown(self):
        self['config'].instance.moveSelection(self['config'].instance.moveDown)
        self.createSetup()
        self.nssXml()
        self.ShowPicture()

    def keyUp(self):
        self['config'].instance.moveSelection(self['config'].instance.moveUp)
        self.createSetup()
        self.nssXml()
        self.ShowPicture()

    def nssSave(self):
        if str(my_cur_skin) == 'oZetaNSS-FHD':
            # menu_file = (self.chooseFile + 'menu_' + config.ozetanss.FirstMenuFHD.value + '.xml').replace(" ", "-")
            infobar_file = (self.chooseFile + 'infobar_' + config.ozetanss.FirstInfobarFHD.value + '.xml').replace(" ", "-")
            secinfobar_file = (self.chooseFile + 'second_' + config.ozetanss.SecondInfobarFHD.value + '.xml').replace(" ", "-")
            chansel_file = (self.chooseFile + 'channel_' + config.ozetanss.ChannSelectorFHD.value + '.xml').replace(" ", "-")
            volume_file = (self.chooseFile + 'volume_' + config.ozetanss.VolumeFHD.value + '.xml').replace(" ", "-")
            radio_file = (self.chooseFile + 'radio_' + config.ozetanss.RadioFHD.value + '.xml').replace(" ", "-")
            mediaplayer_file = (self.chooseFile + 'mediaplayer_' + config.ozetanss.MediaPlayerFHD.value + '.xml').replace(" ", "-")
            eventview_file = (self.chooseFile + 'eventview_' + config.ozetanss.EventviewFHD.value + '.xml').replace(" ", "-")
            if not os.path.exists('/usr/lib/enigma2/python/Plugins/PLi'):
                plugins_file = (self.chooseFile + 'plugins_' + config.ozetanss.PluginsFHD.value + '.xml').replace(" ", "-")
            # alogo_file = (self.chooseFile + 'alogo_' + config.ozetanss.LogoaFHD.value + '.xml').replace(" ", "-")
            # blogo_file = (self.chooseFile + 'blogo_' + config.ozetanss.LogobFHD.value + '.xml').replace(" ", "-")
            file_lines = ''
            try:
                init_file = '%s/basefile/init' % thisdir
                #  print (init_file + "\n#########################")
                skFile = open(init_file, 'r')
                file_lines = skFile.read()
                skFile.close()
                skFilew = open(self.skinFileTmp, 'w')
                skFilew.write(file_lines + '\n')
                # if fileExists(menu_file):
                    # print("Menu file %s found, reading....." % menu_file)
                    # menu_file = open(menu_file, 'r')
                    # file_menu = menu_file.read()
                    # skinMenu = mvi + 'enigma2/oZetaNSS-FHD/zSkin/skin_menu.xml'
                    # skFilewM = open(skinMenu, 'w')
                    # skFilewM.write('<?xml version="1.0" encoding="UTF-8"?>\n<skin>\n' + file_menu + '\n</skin>\n')
                    # skFilewM.close()

                if fileExists(infobar_file):
                    print("Infobar file %s found, writing....." % infobar_file)
                    skFile = open(infobar_file, 'r')
                    file_lines = skFile.read()
                    skFile.close()
                    skFilew.write('\n' + file_lines + '\n')
                if fileExists(secinfobar_file):
                    print("Second Infobar file %s found, writing....." % secinfobar_file)
                    skFile = open(secinfobar_file, 'r')
                    file_lines = skFile.read()
                    skFile.close()
                    skFilew.write('\n' + file_lines + '\n')

                if fileExists(chansel_file):
                    print("Channel Selection file %s found, writing....." % chansel_file)
                    skFile = open(chansel_file, 'r')
                    file_lines = skFile.read()
                    skFile.close()
                    skFilew.write('\n' + file_lines + '\n')

                if fileExists(volume_file):
                    print("Volume file %s found, writing....." % volume_file)
                    skFile = open(volume_file, 'r')
                    file_lines = skFile.read()
                    skFile.close()
                    skFilew.write('\n' + file_lines + '\n')

                if fileExists(radio_file):
                    print("Radio file %s found, writing....." % radio_file)
                    skFile = open(radio_file, 'r')
                    file_lines = skFile.read()
                    skFile.close()
                    skFilew.write('\n' + file_lines + '\n')

                if fileExists(mediaplayer_file):
                    print("mediaplayer file %s found, writing....." % mediaplayer_file)
                    skFile = open(mediaplayer_file, 'r')
                    file_lines = skFile.read()
                    skFile.close()
                    skFilew.write('\n' + file_lines + '\n')

                if fileExists(eventview_file):
                    print("eventview file %s found, writing....." % eventview_file)
                    skFile = open(eventview_file, 'r')
                    file_lines = skFile.read()
                    skFile.close()
                    skFilew.write('\n' + file_lines + '\n')

                if not os.path.exists('/usr/lib/enigma2/python/Plugins/PLi'):
                    if fileExists(plugins_file):
                        print("plugins_file file %s found, writing....." % plugins_file)
                        skFile = open(plugins_file, 'r')
                        file_lines = skFile.read()
                        skFile.close()
                        skFilew.write('\n' + file_lines + '\n')

                # if fileExists(alogo_file):
                    # print("Logo Top file %s found, writing....." % alogo_file)
                    # skFile = open(alogo_file, 'r')
                    # file_lines = skFile.read()
                    # skFile.close()
                    # skFilew.write('\n' + file_lines + '\n')

                # if fileExists(blogo_file):
                    # print("Logo Bottom file %s found, writing....." % blogo_file)
                    # skFile = open(blogo_file, 'r')
                    # file_lines = skFile.read()
                    # skFile.close()
                    # skFilew.write('\n' + file_lines + '\n')
                skFilew.write('\n</skin>\n')
                skFilew.close()

                #  final write
                if fileExists(self.skinFile):
                    os.remove(self.skinFile)
                    print("********** Removed %s" % self.skinFile)
                os.rename(self.skinFileTmp, self.skinFile)
                print("********** Renamed %s" % self.skinFileTmp)
                self.savecfgall()
                self.session.open(MessageBox, _('Successfully creating Skin!'), MessageBox.TYPE_INFO, timeout=5)
                # self.keyOpenSkinselector()
            except Exception as e:
                print(e)
                self.session.open(MessageBox, _('Error creating Skin!\nError %s' % e), MessageBox.TYPE_ERROR, timeout=5)

    def savecfgall(self):
        try:
            # if self["config"].isChanged():
                # for x in self["config"].list:
                    # # if fakeconfig(x):
                        # # print('fake:', fakeconfig(x))
                        # print('xxxx:', x)
                        # # continue
                    # # x[1].save()
                # config.ozetanss.save()
                # configfile.save()
                # ######### recover try
                # # config.ozetanss.txtapi.save()
                # # config.ozetanss.txtapi2.save()
                # # config.ozetanss.txtapi3.save()
                # # config.ozetanss.txtapi4.save()
                # # config.ozetanss.zweather.save()
                config.ozetanss.city.save()
                config.ozetanss.FirstInfobarFHD.save()
                config.ozetanss.SecondInfobarFHD.save()
                config.ozetanss.ChannSelectorFHD.save()
                config.ozetanss.VolumeFHD.save()
                config.ozetanss.RadioFHD.save()
                config.ozetanss.MediaPlayerFHD.save()
                config.ozetanss.EventviewFHD.save()
                config.misc.pluginstyle.save()
                if not os.path.exists('/usr/lib/enigma2/python/Plugins/PLi'):
                    config.ozetanss.PluginsFHD.save()
                # # config.ozetanss.FirstMenuFHD.save()
                # # config.ozetanss.LogoaFHD.save()
                # # config.ozetanss.LogobFHD.save()
                # # config.ozetanss.Logoboth.save()
        except Exception as e:
            print('error save:', e)

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

    def keyApi(self, answer=None):
        api = "/tmp/apikey.txt"
        if answer is None:
            if fileExists(api) and os.stat(api).st_size > 0:
                self.session.openWithCallback(self.keyApi, MessageBox, _("Import Api Key TMDB from /tmp/apikey.txt?"))
            else:
                self.session.open(MessageBox, (_("Missing %s !") % api), MessageBox.TYPE_INFO, timeout=4)
        elif answer:
            if fileExists(api) and os.stat(api).st_size > 0:
                with open(api, 'r') as f:
                    fpage = f.readline()
                    with open(tmdb_skin, "w") as t:
                        t.write(str(fpage))
                        t.close()
                    config.ozetanss.txtapi.setValue(str(fpage))
                    config.ozetanss.txtapi.save()
                    self.createSetup()
                    self.session.open(MessageBox, (_("TMDB ApiKey Imported & Stored!")), MessageBox.TYPE_INFO, timeout=4)
            else:
                self.session.open(MessageBox, (_("Missing %s !") % api), MessageBox.TYPE_INFO, timeout=4)
        return

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
                    fpage = f.readline()
                    with open(omdb_skin, "w") as t:
                        t.write(str(fpage))
                        t.close()
                    config.ozetanss.txtapi2.setValue(str(fpage))
                    config.ozetanss.txtapi2.save()
                    self.createSetup()
                    self.session.open(MessageBox, (_("OMDB ApiKey Imported & Stored!")), MessageBox.TYPE_INFO, timeout=4)
            else:
                self.session.open(MessageBox, (_("Missing %s !") % api2), MessageBox.TYPE_INFO, timeout=4)
        return

    def keyApi3(self, answer=None):
        api3 = "/etc/enigma2/VisualWeather/apikey.txt"
        if answer is None:
            if fileExists(api3) and os.stat(api3).st_size > 0:
                self.session.openWithCallback(self.keyApi3, MessageBox, _("Import Api Key VISUALWEATHER from /etc/enigma2/VisualWeather/apikey.txt?"))
            else:
                self.session.open(MessageBox, (_("Missing %s !") % api3), MessageBox.TYPE_INFO, timeout=4)
        elif answer:
            if fileExists(api3) and os.stat(api3).st_size > 0:
                with open(api3, 'r') as f:
                    fpage = f.readline()
                    with open(visual_skin, "w") as t:
                        t.write(str(fpage))
                        t.close()
                    config.ozetanss.txtapi3.setValue(str(fpage))
                    config.ozetanss.txtapi3.save()
                    self.createSetup()
                    self.session.open(MessageBox, (_("VISUALWEATHER ApiKey Imported & Stored!")), MessageBox.TYPE_INFO, timeout=4)
            else:
                self.session.open(MessageBox, (_("Missing %s !") % api3), MessageBox.TYPE_INFO, timeout=4)
        return

    def keyApi4(self, answer=None):
        api4 = "/tmp/thetvdbkey.txt"
        if answer is None:
            if fileExists(api4) and os.stat(api4).st_size > 0:
                self.session.openWithCallback(self.keyapi4, MessageBox, _("Import Api Key THETVDB from /tmp/thetvdbkey.txt?"))
            else:
                self.session.open(MessageBox, (_("Missing %s !") % api4), MessageBox.TYPE_INFO, timeout=4)
        elif answer:
            if fileExists(api4) and os.stat(api4).st_size > 0:
                with open(api4, 'r') as f:
                    fpage = f.readline()
                    with open(thetvdb_skin, "w") as t:
                        t.write(str(fpage))
                        t.close()
                    config.ozetanss.txtapi4.setValue(str(fpage))
                    config.ozetanss.txtapi4.save()
                    self.createSetup()
                    self.session.open(MessageBox, (_("THETVDB ApiKey Imported & Stored!")), MessageBox.TYPE_INFO, timeout=4)
            else:
                self.session.open(MessageBox, (_("Missing %s !") % api4), MessageBox.TYPE_INFO, timeout=4)
        return

#  reset config
    def nssDefault(self, answer=None):
        if str(my_cur_skin) == 'oZetaNSS-FHD':
            if answer is None:
                self.session.openWithCallback(self.nssDefault, MessageBox, _("Reset Settings to Defaults Parameters?"))
            else:
                # config.ozetanss.FirstMenuFHD.value = 'Menu Default'
                config.ozetanss.FirstInfobarFHD.value = 'InfoBar Default'
                config.ozetanss.SecondInfobarFHD.value = 'SecondInfoBar Default'
                config.ozetanss.ChannSelectorFHD.value = 'Channel Default'
                config.ozetanss.VolumeFHD.value = 'Volume Default'
                config.ozetanss.RadioFHD.value = 'RadioInfoBar Default'
                config.ozetanss.MediaPlayerFHD.value = 'MediaPlayer Default'
                config.ozetanss.EventviewFHD.value = 'Eventview Default'
                if not os.path.exists('/usr/lib/enigma2/python/Plugins/PLi'):
                    config.ozetanss.PluginsFHD.value = 'PluginBrowser Default'
                # config.ozetanss.LogoaFHD.value = 'TopLogo Default'
                # config.ozetanss.LogobFHD.value = 'BottomLogo Default'
                # config.ozetanss.Logoboth.value = 'Bootlogo Default'
                self.createSetup()
                self.UpdatePicture()

    def dowfil(self):
        if PY3:
            import urllib.request as urllib2
            import http.cookiejar as cookielib
        else:
            import urllib2
            import cookielib
        Req = RequestAgent()
        headers = {'User-Agent': Req}
        cookie_jar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
        urllib2.install_opener(opener)
        try:
            req = urllib2.Request(self.com, data=None, headers=headers)
            handler = urllib2.urlopen(req, timeout=15)
            data = handler.read()
            with open(tarfile, 'wb') as f:
                f.write(data)
            print('MYDEBUG - download ok - URL: %s , filename: %s' % (self.com, tarfile))
        except:
            print('MYDEBUG - download failed - URL: %s , filename: %s' % (self.com, tarfile))
        return tarfile

    def start(self):
        pass

    def starts(self):
        pass

    def check_line(self):
        # if str(my_cur_skin) == 'oZetaNSS-FHD':
        lulu = 'skin_templatepanelslulu.xml'
        fldlulu = '/usr/share/enigma2/oZetaNSS-FHD/zSkin/skin_templatepanelslulu.xml'
        filename = '/usr/share/enigma2/oZetaNSS-FHD/skin.xml'
        filename2 = '/usr/share/enigma2/oZetaNSS-FHD/skin2.xml'
        if fileExists(fldlulu):
            with open(filename, 'r') as f:
                fpage = f.readline()
                if lulu in fpage:
                    print('line lulu exist')
                    f.close()
                else:
                    print('line lulu not exist')
                    fin = open(filename, "rt")
                    fout = open(filename2, "wt")
                    for line in fin:
                        fout.write(line.replace('</skin>', '\t<include filename="zSkin/skin_templatepanelslulu.xml"/>\n</skin>'))
                    fin.close()
                    fout.close()
                    cmd1 = 'mv -f %s %s > /dev/null 2>&1' % (filename2, filename)
                    os.system(cmd1)
            self.session.open(MessageBox, _('OZSKIN UPDATE\nPLEASE RESTART GUI'), MessageBox.TYPE_INFO, timeout=5)

#  error load
    def errorLoad(self):
        print('error: errorLoad')

# weather search
# config.plugins.ozeta.zweather = ConfigOnOff(default=False)
# config.plugins.ozeta.weather = NoSave(ConfigSelection(['-> Ok']))
# config.plugins.ozeta.city = ConfigText(default='', visible_width=50, fixed_size=False)

    def KeyMenu(self):
        if os.path.isdir(weatherz):
            weatherPluginEntryCount = config.plugins.WeatherPlugin.entrycount.value
            if weatherPluginEntryCount >= 1:
                self.session.openWithCallback(self.goWeather, MessageBox, _('Data entered for the Weather, do you want to continue the same?'), MessageBox.TYPE_YESNO)
            else:
                self.goWeather(True)
        elif os.path.isdir(theweather):
            locdirsave = "/etc/enigma2/TheWeather_last.cfg"
            location = 'n\\A'
            if os.path.exists(locdirsave):
                for line in open(locdirsave):
                    location = line.rstrip()
                # zLine = str(location)
                if location != 'n\\A':
                    zLine = str(location)
                # zLine = str(city) + ' - ' + str(location)
                config.ozetanss.city.setValue(zLine)
                config.ozetanss.city.save()
                self['city'].setText(zLine)
                self.createSetup()
            else:
                return
        else:
            restartbox = self.session.openWithCallback(self.goWeatherInstall, MessageBox, _('Weather Plugin Plugin Not Installed!!\nDo you really want to install now?'), MessageBox.TYPE_YESNO)
            restartbox.setTitle(_('Install Weather Plugin and Reboot'))
        self.UpdatePicture()

    def goWeather(self, result=False):
        if result:
            try:
                from .addons import WeatherSearch
                entry = config.plugins.WeatherPlugin.Entry[0]
                self.session.openWithCallback(self.UpdateComponents, WeatherSearch.MSNWeatherPluginEntryConfigScreen, entry)
            except:
                pass

    def goWeatherInstall(self, result=False):
        if result:
            try:
                cmd = 'enigma2-plugin-extensions-weatherplugin'
                self.session.open(Console, _('Install WeatherPlugin'), ['opkg install %s' % cmd], closeOnSuccess=False)
                time.sleep(5)
                # self.zSwitchMode()
            except Exception as e:
                print(e)
        else:
            message = _('Plugin WeatherPlugin not installed!!!')
            self.session.open(MessageBox, message, MessageBox.TYPE_INFO)

    def KeyMenu2(self, answer=None):
        if os.path.isdir(OAWeather):
            if answer is None:
                self.session.openWithCallback(self.KeyMenu2, MessageBox, _('Open OAWeather, do you want to continue?'), MessageBox.TYPE_YESNO)
            elif answer:
                self.goOAWeather(True)
        else:
            restartbox = self.session.openWithCallback(self.goOAWeatherInstall, MessageBox, _('OAWeather Plugin Plugin Not Installed!!\nDo you really want to install now?'), MessageBox.TYPE_YESNO)
            restartbox.setTitle(_('Install OAWeather Plugin and Reboot'))
        self.UpdatePicture()

    def goOAWeather(self, result=False):
        if result:
            try:
                from Plugins.Extensions.OAWeather.plugin import WeatherSettingsView
                print('i am here!!')
                self.session.openWithCallback(self.UpdateComponents2, WeatherSettingsView)
            except:
                print('passed!!')
                pass

    def goOAWeatherInstall(self, result=False):
        if result:
            try:
                cmd = 'enigma2-plugin-extensions-oaweather'
                self.session.open(Console, _('Install OAWeatherPlugin'), ['opkg install %s' % cmd], closeOnSuccess=False)
                time.sleep(5)
                # self.zSwitchMode()
            except Exception as e:
                print(e)
        else:
            message = _('Plugin OAWeatherPlugin not installed!!!')
            self.session.open(MessageBox, message, MessageBox.TYPE_INFO)

    def UpdateComponents(self):
        try:
            weatherPluginEntryCount = config.plugins.WeatherPlugin.entrycount.value
            if weatherPluginEntryCount >= 1:
                zLine = ''
                weatherPluginEntry = config.plugins.WeatherPlugin.Entry[0]
                location = weatherPluginEntry.weatherlocationcode.value
                city = weatherPluginEntry.city.value
                zLine = str(city) + ' - ' + str(location)
                config.ozetanss.city.setValue(zLine)
                config.ozetanss.city.save()
                self['city'].setText(zLine)
                self.createSetup()
            else:
                return
        except:
            pass

    def UpdateComponents2(self):
        try:
            if config.plugins.OAWeather.enabled.value:
                zLine = ''
                city = config.plugins.OAWeather.weathercity.value
                location = config.plugins.OAWeather.owm_geocode.value.split(",")
                zLine = str(city)
                if location:
                    zLine += ' - ' + str(location)
                # zLine = str(city) + ' - ' + str(location)
                config.ozetanss.city.setValue(zLine)
                config.ozetanss.city.save()
                self['city'].setText(zLine)
                self.createSetup()
            else:
                return
        except:
            pass

    def zExit(self):
        self.close()


class ozHelp(Screen):

    skin = """
              <screen name="ozHelp" position="center,center" size="1700,1000" title="oZeta Skin Help" backgroundColor="#10000000" flags="wfNoBorder">
                    <widget name="helpdesc" position="20,20" font="Regular;28" size="1640,960" halign="left" foregroundColor="#ffffff" backgroundColor="#101010" transparent="1" zPosition="1" />
                    <eLabel position="10,900" size="1680,3" backgroundColor="#303030" zPosition="1" />
                    <ePixmap position="30,930"      pixmap="/usr/lib/enigma2/python/Plugins/Extensions/oZetaNSS/basefile/red.png"    size="30,30" alphatest="blend" zPosition="2" />
                    <ePixmap position="330,930" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/oZetaNSS/basefile/green.png"      size="30,30" alphatest="blend" zPosition="2" />
                    <ePixmap position="630,930" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/oZetaNSS/basefile/yellow.png" size="30,30" alphatest="blend" zPosition="2" />
                    <ePixmap position="930,930" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/oZetaNSS/basefile/blue.png"       size="30,30" alphatest="blend" zPosition="2" />
                    <widget name="key_red"    font="Regular;28" position="70,930"  size="300,30" halign="left" valign="center" backgroundColor="black" zPosition="1" transparent="1" />
                    <widget name="key_green"  font="Regular;28" position="370,930" size="300,30" halign="left" valign="center" backgroundColor="black" zPosition="1" transparent="1" />
                    <widget name="key_yellow" font="Regular;28" position="670,930" size="300,30" halign="left" valign="center" backgroundColor="black" zPosition="2" transparent="1" />
                    <widget name="key_blue"   font="Regular;28" position="970,930" size="300,30" halign="left" valign="center" backgroundColor="black" zPosition="2" transparent="1" />
              </screen>
            """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.setup_title = ('About oZetaNSS')
        self["version"] = Label(version)
        self['key_red'] = Label(_('Back'))
        self['key_green'] = Label(_('ApiKey Info'))
        self['key_yellow'] = Label(_('Preview Info'))
        self['key_blue'] = Label(_('Restart Info'))
        self["helpdesc"] = Label()
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions'], {"red": self.zExit,
                                                       "green": self.green,
                                                       "yellow": self.yellow,
                                                       "blue": self.blue,
                                                       "ok": self.zExit,
                                                       "cancel": self.zExit}, -1)
        self.onLayoutFinish.append(self.finishLayout)

    def finishLayout(self):
        helpdesc = self.homecontext()
        self["helpdesc"].setText(helpdesc)

    def homecontext(self):
        conthelp = "Original oZeta Skin"
        conthelp += "Version : " + "%s\n" % version
        conthelp += "License: Open\n\n"
        conthelp += "Skin Author: Mmark - Info: e2skin.blogspot.it\n"
        conthelp += "Tested on:\n"
        conthelp += "openATV 7.x - OpenPLi 8.x - OpenSPA\n"
        conthelp += "zSetup Base Release: 2.0.0 - 30/06/2022\n"
        conthelp += "***Coded by @Lululla - @Corvoboys ***\n"
        conthelp += "*************************************\n\n"
        conthelp += "*SETUP FOR OZETA NSS TEAM*\n\n"
        conthelp += "edited for NONSOLOSAT Image\n"
        conthelp += "Please reports bug or info to blog:\n"
        conthelp += "http://nonsolosat.net\n\n"
        conthelp += "*************************************\n\n"
        conthelp += "This plugin is NOT free software. It is open source, you are allowed to"
        conthelp += "modify it (if you keep the license), but it may not be commercially"
        conthelp += "distributed other than under the conditions noted above.\n\n"
        conthelp += "***NONSOLOSAT TEAM***\n"

        return conthelp

    def yellow(self):
        helpdesc = self.yellowcontext()
        self["helpdesc"].setText(helpdesc)

    def yellowcontext(self):
        conthelp = "HELP ZSETUP PLUGIN:\n\n"
        conthelp += (" (RED BUTTON):\n")
        conthelp += _("         Exit zSetup\n\n")
        conthelp += (" (GREEN BUTTON):\n")
        conthelp += _("         Save and Copy changes in the Settings xml file\n\n")
        conthelp += (" (YELLOW BUTTON):\n")
        conthelp += _("         View Pic of Panels preview, in the FullHD mode\n\n")
        conthelp += (" (BLUE BUTTON):\n")
        conthelp += _("         Restart E2 but not apply changes\n\n")
        conthelp += (" (0 BUTTON):\n")
        conthelp += _("         Reset Settings\n\n")
        conthelp += (" (MENU BUTTON):\n")
        conthelp += _("         Install or Set Weather Plugin if installed\n\n")
        conthelp += (" (ALTERNATIVE RADIO)\n")
        conthelp += _("         Menu/Setup/Graphic Interface/OSD Setup\n")
        conthelp += _("         Alternative Radio Mode= Yes\n")
        return conthelp

    def green(self):
        helpdesc = self.greencontext()
        self["helpdesc"].setText(helpdesc)

    def greencontext(self):
        conthelp = "SETTINGS APIKEY: COVER AND WEATHER:\n\n"
        conthelp += ("(OMDB ApiKey):\n")
        conthelp += _("    For use The OMDB Covers, copy the omdbkey file in the skin folder:\n")
        conthelp += _("    /usr/share/enigma2/oZetaNSS-FHD/omdbkey\n")
        conthelp += _("    Or manually enter the key, created on the OMDB portal'\n")
        conthelp += _("    use the virtual keyboard.\n")
        conthelp += _("    Or import from /tmp the file omdbkey.txt\n\n")
        conthelp += ("(TMDB ApiKey):\n")
        conthelp += _("    For use The TMDB Covers, copy the apikey file in the skin folder:\n")
        conthelp += _("    /usr/share/enigma2/oZetaNSS-FHD/apikey\n")
        conthelp += _("    Or manually enter the key, created on the TMDB portal\n")
        conthelp += _("    use the virtual keyboard.\n\n")
        conthelp += _("    Or import from /tmp the file apikey.txt\n\n")
        conthelp += ("(THETMDB ApiKey):\n")
        conthelp += _("    For use The THETMDB Covers, copy the apikey file in the skin folder:\n")
        conthelp += _("    /usr/share/enigma2/oZetaNSS-FHD/thetvdbkey\n")
        conthelp += _("    Or manually enter the key, created on the THETMDB portal\n")
        conthelp += _("    use the virtual keyboard.\n\n")
        conthelp += _("    Or import from /tmp the file thetvdbkey.txt\n\n")
        conthelp += ("(WEATHER Config):\n")
        conthelp += _("    For use The WeatherPlugin:\n")
        conthelp += _("    --Automatic Import from Plugin\n")
        conthelp += _("    For use VisualWeather\n")
        conthelp += _("    --use the virtual keyboard or import from default config plugin")
        return conthelp

    def blue(self):
        helpdesc = self.bluecontext()
        self["helpdesc"].setText(helpdesc)

    def bluecontext(self):
        conthelp = _("SAVE & RESTART\n\n")
        conthelp += (" (GREEN BUTTON):\n")
        conthelp += _("         Save and Copy changes in the xml file config\n")
        conthelp += (" (BLUE BUTTON):\n")
        conthelp += _("         Restart E2 but not apply changes\n")
        return conthelp

    def zExit(self):
        self.close()


class ShowPictureFullX(Screen):
    skin = """
            <screen position="center,center" size="1024,576" title="Preview" backgroundColor="transparent" flags="wfNoBorder">
                <widget name="PreviewFull" position="0,0" size="1920,1080" zPosition="0" />
                <widget name="lab2" position="0,0" size="1920,0" zPosition="2" font="Regular;30" halign="center" valign="center" backgroundColor="green" foregroundColor="white" />
            </screen>
           """

    def __init__(self, session, myprev):
        Screen.__init__(self, session)
        self['PreviewFull'] = Pixmap()
        self['actions'] = ActionMap(['OkCancelActions'], {"cancel": self.close})
        self["lab2"] = Label(_("Click Exit for close this window"))
        self.path = myprev
        self.onLayoutFinish.append(self.PreviewPictureFull)

    def PreviewPictureFull(self):
        myicon = self.path
        if myicon:
            png = loadPic(myicon, 1280, 720, 0, 0, 0, 1)
        self["PreviewFull"].instance.setPixmap(png)


def mainmenu(menuid, **kwargs):
    if menuid == "setup":
        return [('oZetaNSS', main, _('oZetaNSS'), None)]
    else:
        return []


def main(session, **kwargs):
    try:
        session.open(oZetaNSS)
    except:
        import traceback
        traceback.print_exc()
        pass


# def __init__(self, name="Plugin", where=None, description="", icon=None, fnc=None, wakeupfnc=None, needsRestart=None, internal=False, weight=0):
def Plugins(**kwargs):
    result = [
              # PluginDescriptor(name='oZetaNSS', description=descplug, where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=autostart),
              PluginDescriptor(name='oZetaNSS', description=descplug, where=PluginDescriptor.WHERE_MENU, icon=iconpic, fnc=mainmenu),
              PluginDescriptor(name='oZetaNSS', description=descplug, where=PluginDescriptor.WHERE_PLUGINMENU, icon=iconpic, fnc=main),
             ]
    return result

#  ~ end code lululla 2022.10
