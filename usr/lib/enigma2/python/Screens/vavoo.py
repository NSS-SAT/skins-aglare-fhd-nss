#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
****************************************
*        coded by Lululla              *
*             26/04/2024               *
****************************************
# --------------------#
# Info Linuxsat-support.com & corvoboys.org

put to menu.xml this:

<!--  <id val="mainmenu"/>  -->

<item weight="11" level="0" text="NSS Vavoo Stream Live" entryID="vavoo">
<code>
from Screens.vavoo import MainVavoo
self.session.open(MainVavoo)
</code>
</item>


'''
from __future__ import print_function
# Standard library imports
import os
import re
import six
import ssl
import sys
import time
import traceback

# Enigma2 components
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import (MultiContentEntryPixmapAlphaTest, MultiContentEntryText)
from Components.ServiceEventTracker import (ServiceEventTracker, InfoBarBase)
from Components.config import (
    ConfigSelection,
    getConfigListEntry,
    ConfigSelectionNumber,
    ConfigClock,
    ConfigText,
    configfile,
    config,
    ConfigEnableDisable,
    ConfigSubsection,
)
from Plugins.Plugin import PluginDescriptor
from Screens.InfoBarGenerics import (
    InfoBarSubtitleSupport,
    InfoBarMenu,
    InfoBarSeek,
    InfoBarAudioSelection,
    InfoBarNotifications,
)
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.VirtualKeyBoard import VirtualKeyBoard
from six.moves.urllib.parse import unquote
from Tools.Directories import (SCOPE_PLUGINS, resolveFilename)
from enigma import (
    RT_VALIGN_CENTER,
    RT_HALIGN_LEFT,
    RT_HALIGN_RIGHT,
    eListboxPythonMultiContent,
    eServiceReference,
    eTimer,
    iPlayableService,
    iServiceInformation,
    gFont,
    loadPNG,
)
from os import path as os_path
from os.path import exists as file_exists
from random import choice
import base64
import json
import requests


try:
    from Tools.Directories import SCOPE_GUISKIN as SCOPE_SKIN
except ImportError:
    from Tools.Directories import SCOPE_SKIN
from six import unichr, iteritems
from six.moves import html_entities
import types

global HALIGN

tmlast = None
now = None
_session = None
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


if sys.version_info >= (2, 7, 9):
    try:
        sslContext = ssl._create_unverified_context()
    except:
        sslContext = None


if PY3:
    bytes = bytes
    unicode = str
    from urllib.request import Request, urlopen
    class_types = type,
    text_type = str
    binary_type = bytes
    MAXSIZE = sys.maxsize
else:
    str = str
    from urllib2 import Request, urlopen
    import unicode
    class_types = (type, types.ClassType)
    text_type = unicode
    binary_type = str
    if sys.platform.startswith("java"):
        # Jython always uses 32 bits.
        MAXSIZE = int((1 << 31) - 1)
    else:
        # It's possible to have sizeof(long) != sizeof(Py_ssize_t).
        class X(object):

            def __len__(self):
                return 1 << 31
        try:
            len(X())
        except OverflowError:
            # 32-bit
            MAXSIZE = int((1 << 31) - 1)
        else:
            # 64-bit
            MAXSIZE = int((1 << 63) - 1)
        del X

currversion = '1.30'
title_plug = 'Vavoo'
desc_plugin = ('..:: Vavoo by Lululla v.%s ::..' % currversion)
stripurl = 'aHR0cHM6Ly92YXZvby50by9jaGFubmVscw=='
keyurl = 'aHR0cDovL3BhdGJ1d2ViLmNvbS92YXZvby92YXZvb2tleQ=='

enigma_list = '/usr/vavoo/'
enigma_path = '/etc/enigma2/'
json_file = '/tmp/vavookey'
HALIGN = RT_HALIGN_LEFT

_UNICODE_MAP = {k: unichr(v) for k, v in iteritems(html_entities.name2codepoint)}
_ESCAPE_RE = re.compile("[&<>\"']")
_UNESCAPE_RE = re.compile(r"&\s*(#?)(\w+?)\s*;")  # Whitespace handling added due to "hand-assed" parsers of html pages
_ESCAPE_DICT = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&apos;"}
global ipv6
ipv6 = 'off'
if os_path.islink('/etc/rc3.d/S99ipv6dis.sh'):
    ipv6 = 'on'


# log
def trace_error():
    try:
        # Stampa la traccia dell'errore su stdout
        traceback.print_exc(file=sys.stdout)
        # Scrive la traccia dell'errore su un file di log
        with open("/tmp/vavoo.log", "a") as log_file:
            traceback.print_exc(file=log_file)
    except Exception as e:
        # Gestisce qualsiasi eccezione che potrebbe verificarsi durante la registrazione dell'errore
        print("Failed to log the error:", e, file=sys.stderr)


myser = [("https://vavoo.to", "vavoo"), ("https://oha.to", "oha"), ("https://kool.to", "kool"), ("https://huhu.to", "huhu")]
modemovie = [("4097", "4097")]
if file_exists("/usr/bin/gstplayer"):
    modemovie.append(("5001", "5001"))
if file_exists("/usr/bin/exteplayer3"):
    modemovie.append(("5002", "5002"))
if file_exists('/var/lib/dpkg/info'):
    modemovie.append(("8193", "8193"))


# config section
config.plugins.vavoo = ConfigSubsection()
cfg = config.plugins.vavoo
cfg.autobouquetupdate = ConfigEnableDisable(default=False)
cfg.server = ConfigSelection(default="https://vavoo.to", choices=myser)
cfg.services = ConfigSelection(default='4097', choices=modemovie)
cfg.timetype = ConfigSelection(default="interval", choices=[("interval", _("interval")), ("fixed time", _("fixed time"))])
cfg.updateinterval = ConfigSelectionNumber(default=10, min=5, max=3600, stepwidth=5)
# cfg.updateinterval = ConfigSelectionNumber(default=24, min=1, max=48, stepwidth=1)
cfg.fixedtime = ConfigClock(default=46800)
cfg.last_update = ConfigText(default="Never")

cfg.ipv6 = ConfigEnableDisable(default=False)
# cfg.fonts = ConfigSelection(default='vav', choices=fonts)
# FONTSTYPE = FNTPath + '/' + str(cfg.fonts.value) + '.ttf'

eserv = int(cfg.services.value)


if os_path.islink('/etc/rc3.d/S99ipv6dis.sh'):
    cfg.ipv6.setValue(True)
    cfg.ipv6.save()


# language
locl = "ar", "ae", "bh", "dz", "eg", "in", "iq", "jo", "kw", "lb", "ly", "ma", "om", "qa", "sa", "sd", "ss", "sy", "tn", "ye"
global lngx
lngx = 'en'
try:
    from Components.config import config
    lng = config.osd.language.value
    lng = lng[:-3]
    if any(s in lngx for s in locl):
        HALIGN = RT_HALIGN_RIGHT
except:
    lng = 'en'
    pass


def ensure_str(s, encoding='utf-8', errors='strict'):
    """Coerce *s* to `str`.
    For Python 2:
      - `unicode` -> encoded to `str`
      - `str` -> `str`

    For Python 3:
      - `str` -> `str`
      - `bytes` -> decoded to `str`
    """
    # Optimization: Fast return for the common case.
    if type(s) is str:
        return s
    if PY2 and isinstance(s, text_type):
        return s.encode(encoding, errors)
    elif PY3 and isinstance(s, binary_type):
        return s.decode(encoding, errors)
    elif not isinstance(s, (text_type, binary_type)):
        raise TypeError("not expecting type '%s'" % type(s))
    return s


def html_escape(value):
    return _ESCAPE_RE.sub(lambda match: _ESCAPE_DICT[match.group(0)], ensure_str(value).strip())


def html_unescape(value):
    return _UNESCAPE_RE.sub(_convert_entity, ensure_str(value).strip())


def _convert_entity(m):
    if m.group(1) == "#":
        try:
            return unichr(int(m.group(2)[1:], 16)) if m.group(2)[:1].lower() == "x" else unichr(int(m.group(2)))
        except ValueError:
            return "&#%s;" % m.group(2)
    return _UNICODE_MAP.get(m.group(2), "&%s;" % m.group(2))


def getserviceinfo(sref):
    try:
        from ServiceReference import ServiceReference
        p = ServiceReference(sref)
        servicename = str(p.getServiceName())
        serviceurl = str(p.getPath())
        return servicename, serviceurl
    except:
        return None, None


def getUrl(url):
    req = Request(url)
    req.add_header('User-Agent', RequestAgent())
    try:
        response = urlopen(req, timeout=20)
        if PY3:
            link = response.read().decode(errors='ignore')
        else:
            link = response.read()
        response.close()
    except Exception as e:
        print(e)
        gcontext = ssl._create_unverified_context()
        response = urlopen(req, timeout=20, context=gcontext)
        if PY3:
            link = response.read().decode(errors='ignore')
        else:
            link = response.read()
        response.close()
    return link


def b64decoder(s):

    s = str(s).strip()
    try:
        output = base64.b64decode(s)
        if PY3:
            output = output.decode('utf-8')
        return output
    except Exception:
        padding = len(s) % 4
        if padding == 1:
            print('Invalid base64 string: {}'.format(s))
            return ""
        elif padding == 2:
            s += b'=='
        elif padding == 3:
            s += b'='
        else:
            return ""


def Sig():
    sig = ''
    if not file_exists(json_file):
        myUrl = b64decoder(keyurl)
        vecKeylist = requests.get(myUrl).json()
        vecs = {'time': int(time.time()), 'vecs': vecKeylist}
        with open(json_file, "w") as f:
            json.dump(vecKeylist, f, indent=2)
    else:
        vec = None
        with open(json_file) as f:
            vecs = json.load(f)
            vec = choice(vecs)
        headers = {
            'Content-Type': 'application/json',
        }
        json_data = '{"vec": "' + str(vec) + '"}'
        # try:
        if PY3:
            req = requests.post('https://www.vavoo.tv/api/box/ping2', headers=headers, data=json_data).json()
        else:
            req = requests.post('https://www.vavoo.tv/api/box/ping2', headers=headers, verify=False, data=json_data).json()
        if req.get('signed'):
            sig = req['signed']
        elif req.get('data', {}).get('signed'):
            sig = req['data']['signed']
        elif req.get('response', {}).get('signed'):
            sig = req['response']['signed']
        # except requests.RequestException as e:
            # print("Request failed:", e)
    return sig


def loop_sig():
    while True:
        sig = ''
        now = int(time.time())
        print('now=', str(now))
        last = tmlast
        print('last=', str(last))
        if now > last + 1200:
            print('go to sig....')
            sig = Sig()
        else:
            print('sleep time loop sig....')
            time.sleep(int(last + 1200 - now))
        return sig
    pass


def returnIMDB(text_clear):
    TMDB = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('TMDB'))
    IMDb = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('IMDb'))
    text = html_unescape(text_clear)
    if file_exists(TMDB):
        try:
            from Plugins.Extensions.TMBD.plugin import TMBD
            _session.open(TMBD.tmdbScreen, text, 0)
        except Exception as e:
            print("[XCF] TMDB error:", e)
            _session.open(MessageBox, "Error opening TMDB plugin: {}".format(e), MessageBox.TYPE_ERROR)
    elif file_exists(IMDb):
        try:
            from Plugins.Extensions.IMDb.plugin import main as imdb
            imdb(_session, text)
        except Exception as e:
            print("[XCF] IMDb error:", e)
            _session.open(MessageBox, "Error opening IMDb plugin: {}".format(e), MessageBox.TYPE_ERROR)
    else:
        _session.open(MessageBox, text, MessageBox.TYPE_INFO)
    return True


# check server
def raises(url):
    try:
        from requests.adapters import HTTPAdapter, Retry
        retries = Retry(total=1, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retries)
        http = requests.Session()
        http.mount("http://", adapter)
        http.mount("https://", adapter)
        r = http.get(url, headers={'User-Agent': RequestAgent()}, timeout=10, verify=False, stream=True, allow_redirects=False)
        r.raise_for_status()
        if r.status_code == requests.codes.ok:
            return True
    except Exception as error:
        print(error)
        trace_error()
    return False


def zServer(opt=0, server=None, port=None):
    try:
        from urllib.error import HTTPError
    except ImportError:
        from urllib2 import HTTPError
    try:
        if raises(server):
            print('server is raise:', str(server))
            return str(server)
    except HTTPError as err:
        print(err.code)
        return 'https://vavoo.to'


def rimuovi_parentesi(testo):
    return re.sub(r'\([^)]*\)', '', testo)


# menulist
class m2list(MenuList):
    def __init__(self, items):
        super(m2list, self).__init__(items, False, eListboxPythonMultiContent)
        # MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setItemHeight(50)
        textfont = int(34)
        self.l.setFont(0, gFont('Regular', textfont))


Panel_list = ("Albania", "Arabia", "Balkans", "Bulgaria",
              "France", "Germany", "Italy", "Netherlands",
              "Poland", "Portugal", "Romania", "Russia",
              "Spain", "Turkey", "United Kingdom")


'''
# def show_(name, link):
    # res = [(name, link)]
    # cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
    # pngx = os_path.dirname(resolveFilename(SCOPE_SKIN, str(cur_skin))) + "/vavoo/Internat.png"
    # if any(s in name for s in Panel_list):
        # pngx = os_path.dirname(resolveFilename(SCOPE_SKIN, str(cur_skin))) + '/vavoo/%s.png' % str(name)
    # if os_path.isfile(pngx):
        # print('pngx =:', pngx)
        # res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 5), size=(60, 40), png=loadPNG(pngx)))
    # res.append(MultiContentEntryText(pos=(85, 0), size=(540, 50), font=0, text=name, flags=HALIGN | RT_VALIGN_CENTER))
    # return res


# def show2_(name, link):
    # res = [(name, link)]
    # cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
    # pngx = os_path.dirname(resolveFilename(SCOPE_SKIN, str(cur_skin))) + '/vavoo/vavoo_ico.png'
    # if os_path.isfile(pngx):
        # res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 5), size=(40, 40), png=loadPNG(pngx)))
        # res.append(MultiContentEntryText(pos=(65, 0), size=(540, 50), font=0, text=name, flags=HALIGN | RT_VALIGN_CENTER))
    # return res
'''


def show_(name, link):
    res = [(name, link)]
    cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
    base_skin_path = os.path.dirname(resolveFilename(SCOPE_SKIN, str(cur_skin)))
    pngx = os.path.join(base_skin_path, "vavoo", "Internat.png")
    if any(s in name for s in Panel_list):
        pngx = os.path.join(base_skin_path, 'vavoo', f'{str(name)}.png')
    if os.path.isfile(pngx):
        print('pngx =:', pngx)
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 5), size=(60, 40), png=loadPNG(pngx)))
    res.append(MultiContentEntryText(pos=(85, 0), size=(540, 50), font=0, text=name, flags=HALIGN | RT_VALIGN_CENTER))
    return res


def show2_(name, link):
    res = [(name, link)]
    cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
    base_skin_path = os.path.dirname(resolveFilename(SCOPE_SKIN, str(cur_skin)))
    pngx = os.path.join(base_skin_path, 'vavoo', 'vavoo_ico.png')
    if os.path.isfile(pngx):
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 5), size=(40, 40), png=loadPNG(pngx)))
    res.append(MultiContentEntryText(pos=(65, 0), size=(540, 50), font=0, text=name, flags=HALIGN | RT_VALIGN_CENTER))
    return res


class vavoo_configx(Screen, ConfigListScreen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.setup_title = ('Vavoo Config')
        self.list = []
        self.onChangedEntry = []
        self["version"] = Label()
        self['statusbar'] = Label()
        self["description"] = Label("")
        self["red"] = Label(_("Back"))
        self["green"] = Label(_("Save"))
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions', 'DirectionActions'], {
            "cancel": self.extnok,
            "left": self.keyLeft,
            "right": self.keyRight,
            "up": self.keyUp,
            "down": self.keyDown,
            "red": self.extnok,
            "green": self.save,
            "ok": self.save,
        }, -1)
        self.update_status()
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
        self.createSetup()
        self.v6 = cfg.ipv6.getValue()
        self.showhide()
        self.onLayoutFinish.append(self.layoutFinished)

    def update_status(self):
        if cfg.autobouquetupdate:
            self['statusbar'].setText(_("Last channel update: %s") % cfg.last_update.value)

    def layoutFinished(self):
        self.setTitle(self.setup_title)
        self['version'].setText('V.' + currversion)

    def createSetup(self):
        self.editListEntry = None
        self.list = []
        indent = "- "
        self.list.append(getConfigListEntry(_("Server for Player Used"), cfg.server, _("Server for player.\nNow %s") % cfg.server.value))
        self.list.append(getConfigListEntry(_("Ipv6 State Of Lan (On/Off)"), cfg.ipv6, _("Active or Disactive lan Ipv6.\nNow %s") % cfg.ipv6.value))
        self.list.append(getConfigListEntry(_("Movie Services Reference"), cfg.services, _("Configure service Reference Iptv-Gstreamer-Exteplayer3")))
        # self.list.append(getConfigListEntry(_("Select Fonts"), cfg.fonts, _("Configure Fonts.\nEg:Arabic or other language.")))
        self.list.append(getConfigListEntry(_("Scheduled Bouquet Update:"), cfg.autobouquetupdate, _("Active Automatic Bouquet Update")))
        if cfg.autobouquetupdate.value is True:
            self.list.append(getConfigListEntry(indent + _("Schedule type:"), cfg.timetype, _("At an interval of hours or at a fixed time")))
            if cfg.timetype.value == "interval":
                self.list.append(getConfigListEntry(2 * indent + _("Update interval (minutes):"), cfg.updateinterval, _("Configure every interval of minutes from now")))
            if cfg.timetype.value == "fixed time":
                self.list.append(getConfigListEntry(2 * indent + _("Time to start update:"), cfg.fixedtime, _("Configure at a fixed time")))
        self["config"].list = self.list
        self["config"].l.setList(self.list)
        self.setInfo()

    def setInfo(self):
        try:
            sel = self['config'].getCurrent()[2]
            if sel:
                self['description'].setText(str(sel))
            else:
                self['description'].setText(_('SELECT YOUR CHOICE'))
            return
        except Exception as error:
            print(error)
            trace_error()

    def ipv6(self):
        if os_path.islink('/etc/rc3.d/S99ipv6dis.sh'):
            self.session.openWithCallback(self.ipv6check, MessageBox, _("Ipv6 [Off]?"), MessageBox.TYPE_YESNO, timeout=5, default=True)
        else:
            self.session.openWithCallback(self.ipv6check, MessageBox, _("Ipv6 [On]?"), MessageBox.TYPE_YESNO, timeout=5, default=True)

    def ipv6check(self, result):
        if result:
            if os_path.islink('/etc/rc3.d/S99ipv6dis.sh'):
                os.unlink('/etc/rc3.d/S99ipv6dis.sh')
                cfg.ipv6.setValue(False)
            else:
                os.system("echo '#!/bin/bash")
                os.system("echo 1 > /proc/sys/net/ipv6/conf/all/disable_ipv6' > /etc/init.d/ipv6dis.sh")
                os.system("chmod 755 /etc/init.d/ipv6dis.sh")
                os.system("ln -s /etc/init.d/ipv6dis.sh /etc/rc3.d/S99ipv6dis.sh")
                cfg.ipv6.setValue(True)
            cfg.ipv6.save()

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()

    def getCurrentEntry(self):
        return self["config"].getCurrent()[0]

    def showhide(self):
        pass

    def getCurrentValue(self):
        return str(self["config"].getCurrent()[1].getText())

    def createSummary(self):
        from Screens.Setup import SetupSummary
        return SetupSummary

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.createSetup()
        self.showhide()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.createSetup()
        self.showhide()

    def keyDown(self):
        self['config'].instance.moveSelection(self['config'].instance.moveDown)
        self.createSetup()
        self.showhide()

    def keyUp(self):
        self['config'].instance.moveSelection(self['config'].instance.moveUp)
        self.createSetup()
        self.showhide()

    def save(self):
        if self["config"].isChanged():
            for x in self["config"].list:
                x[1].save()
            if self.v6 != cfg.ipv6.value:
                self.ipv6()
            configfile.save()
            restartbox = self.session.openWithCallback(self.restartGUI, MessageBox, _('Settings saved successfully !\nyou need to restart the GUI\nto apply the new configuration!\nDo you want to Restart the GUI now?'), MessageBox.TYPE_YESNO)
            restartbox.setTitle(_('Restart GUI now?'))
        else:
            self.close()

    def restartGUI(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

    def extnok(self, answer=None):
        if answer is None:
            self.session.openWithCallback(self.extnok, MessageBox, _("Really close without saving settings?"))
        elif answer:
            for x in self["config"].list:
                x[1].cancel()
            self.close()
        else:
            return


class MainVavoox(Screen):
    def __init__(self, session):
        self.session = session
        global _session
        _session = session
        Screen.__init__(self, session)
        self.menulist = []
        self['menulist'] = m2list([])
        self['red'] = Label(_('Exit'))
        self['green'] = Label(_('Remove') + ' Fav')
        self['yellow'] = Label()
        self["blue"] = Label()
        if HALIGN == RT_HALIGN_RIGHT:
            self['blue'].setText(_('Halign Left'))
        else:
            self['blue'].setText(_('Halign Right'))
        self['name'] = Label('Loading...')
        self['version'] = Label()
        self.currentList = 'menulist'
        self.loading_ok = False
        self.count = 0
        self.loading = 0
        self.url = b64decoder(stripurl)
        self['actions'] = ActionMap(['ButtonSetupActions', 'MenuActions', 'OkCancelActions', 'DirectionActions', 'HotkeyActions', 'InfobarEPGActions', 'ChannelSelectBaseActions'], {
            'prevBouquet': self.chDown,
            'nextBouquet': self.chUp,
            'ok': self.ok,
            'menu': self.goConfig,
            'green': self.msgdeleteBouquets,
            'blue': self.arabic,
            'cancel': self.close,
            'info': self.info,
            'showEventInfo': self.info,
            'red': self.close,
        }, -1)

        self.onLayoutFinish.append(self.cat)

    def arabic(self):
        global HALIGN
        if HALIGN == RT_HALIGN_LEFT:
            HALIGN = RT_HALIGN_RIGHT
            self['blue'].setText(_('Halign Left'))
        elif HALIGN == RT_HALIGN_RIGHT:
            HALIGN = RT_HALIGN_LEFT
            self['blue'].setText(_('Halign Right'))
        self.cat()
        # self.timer.start(200, True)

    def goConfig(self):
        self.session.open(vavoo_configx)

    def info(self):
        aboutbox = self.session.open(MessageBox, _('%s\n\n\nThanks:\n@KiddaC\n@oktus\nQu4k3\nAll staff Linuxsat-support.com\nCorvoboys - Forum\n\nThis plugin is free,\nno stream direct on server\nbut only free channel found on the net') % desc_plugin, MessageBox.TYPE_INFO)
        aboutbox.setTitle(_('Info Vavoo'))

    def chUp(self):
        for x in range(5):
            self[self.currentList].pageUp()
        txtsream = self['menulist'].getCurrent()[0][0]
        self['name'].setText(str(txtsream))

    def chDown(self):
        for x in range(5):
            self[self.currentList].pageDown()
        txtsream = self['menulist'].getCurrent()[0][0]
        self['name'].setText(str(txtsream))

    def cat(self):
        self.cat_list = []
        items = []
        self.items_tmp = []
        name = ''
        country = ''
        try:
            content = getUrl(self.url)
            if PY3:
                content = six.ensure_str(content)
            regexcat = '"country".*?"(.*?)".*?"id".*?"name".*?".*?"'
            match = re.compile(regexcat, re.DOTALL).findall(content)
            for country in match:
                if country not in self.items_tmp:
                    country = unquote(country).strip("\r\n")
                    self.items_tmp.append(country)
                    item = country + "###" + self.url + '\n'
                    items.append(item)
            items.sort()
            for item in items:
                name = item.split('###')[0]
                url = item.split('###')[1]
                if name not in self.cat_list:
                    self.cat_list.append(show_(name, url))
            if len(self.cat_list) < 1:
                return
            else:
                self['menulist'].l.setList(self.cat_list)
                self['menulist'].moveToIndex(0)
                txtsream = self['menulist'].getCurrent()[0][0]
                self['name'].setText(str(txtsream))
        except Exception as error:
            print(error)
            trace_error()
            self['name'].setText('Error')
        self['version'].setText('V.' + currversion)

    def ok(self):
        name = self['menulist'].getCurrent()[0][0]
        url = self['menulist'].getCurrent()[0][1]
        try:
            self.session.open(vavoox, name, url)
        except Exception as error:
            print(error)
            trace_error()

    def exit(self):
        self.close()

    def msgdeleteBouquets(self):
        self.session.openWithCallback(self.deleteBouquets, MessageBox, _("Remove all Vavoo Favorite Bouquet?"), MessageBox.TYPE_YESNO, timeout=5, default=True)

    def deleteBouquets(self, result):
        if result:
            try:
                for fname in os.listdir(enigma_path):
                    if 'userbouquet.vavoo_' in fname:
                        purge(enigma_path, fname)
                    elif 'bouquets.tv.bak' in fname:
                        purge(enigma_path, fname)
                os.rename(os_path.join(enigma_path, 'bouquets.tv'), os_path.join(enigma_path, 'bouquets.tv.bak'))
                tvfile = open(os_path.join(enigma_path, 'bouquets.tv'), 'w+')
                bakfile = open(os_path.join(enigma_path, 'bouquets.tv.bak'))
                for line in bakfile:
                    if '.vavoo_' not in line:
                        tvfile.write(line)
                bakfile.close()
                tvfile.close()
                if file_exists(enigma_path + '/Favorite.txt'):
                    os.remove(enigma_path + '/Favorite.txt')
                self.session.open(MessageBox, _('Vavoo Favorites List have been removed'), MessageBox.TYPE_INFO, timeout=5)
                ReloadBouquets()
            except Exception as error:
                print(error)
                trace_error()


class vavoox(Screen):
    def __init__(self, session, name, url):
        self.session = session
        global _session
        _session = session
        Screen.__init__(self, session)
        self.menulist = []
        global search_ok
        search_ok = False
        self['menulist'] = m2list([])
        self['red'] = Label(_('Back'))
        self['green'] = Label(_('Export') + ' Fav')
        self['yellow'] = Label(_('Search'))
        self["blue"] = Label()
        if HALIGN == RT_HALIGN_RIGHT:
            self['blue'].setText(_('Halign Left'))
        else:
            self['blue'].setText(_('Halign Right'))
        self['name'] = Label('Loading ...')
        self['version'] = Label()
        self.currentList = 'menulist'
        self.loading_ok = False
        self.count = 0
        self.loading = 0
        self.name = name
        self.url = url
        self['actions'] = ActionMap(['ButtonSetupActions', 'MenuActions', 'OkCancelActions', 'ShortcutActions', 'HotkeyActions', 'DirectionActions', 'InfobarEPGActions', 'ChannelSelectBaseActions'], {
            'prevBouquet': self.chDown,
            'nextBouquet': self.chUp,
            'ok': self.ok,
            'green': self.message1,
            'yellow': self.search_vavoo,
            'blue': self.arabic,
            'cancel': self.backhome,
            'menu': self.goConfig,
            'info': self.info,
            'red': self.backhome
        }, -1)

        self.onLayoutFinish.append(self.cat)

    def arabic(self):
        global HALIGN
        if HALIGN == RT_HALIGN_LEFT:
            HALIGN = RT_HALIGN_RIGHT
            self['blue'].setText(_('Halign Left'))
        elif HALIGN == RT_HALIGN_RIGHT:
            HALIGN = RT_HALIGN_LEFT
            self['blue'].setText(_('Halign Right'))
        self.cat()
        # self.timer.start(200, True)

    def backhome(self):
        if search_ok is True:
            self.cat()
        else:
            self.close()

    def goConfig(self):
        self.session.open(vavoo_configx)

    def info(self):
        aboutbox = self.session.open(MessageBox, _('%s\n\n\nThanks:\n@KiddaC\n@oktus\nQu4k3\nAll staff Linuxsat-support.com\nCorvoboys - Forum\n\nThis plugin is free,\nno stream direct on server\nbut only free channel found on the net') % desc_plugin, MessageBox.TYPE_INFO)
        aboutbox.setTitle(_('Info Vavoo'))

    def chUp(self):
        for x in range(5):
            self[self.currentList].pageUp()
        txtsream = self['menulist'].getCurrent()[0][0]
        self['name'].setText(str(txtsream))

    def chDown(self):
        for x in range(5):
            self[self.currentList].pageDown()
        txtsream = self['menulist'].getCurrent()[0][0]
        self['name'].setText(str(txtsream))

    def cat(self):
        self.cat_list = []
        items = []
        xxxname = '/tmp/' + self.name + '.m3u'
        svr = cfg.server.value
        server = zServer(0, svr, None)
        global search_ok
        search_ok = False
        try:
            with open(xxxname, 'w') as outfile:
                outfile.write('#NAME %s\r\n' % self.name.capitalize())
                content = getUrl(self.url)
                if PY3:
                    content = six.ensure_str(content)
                names = self.name
                regexcat = '"country".*?"(.*?)".*?"id"(.*?)"name".*?"(.*?)"'
                match = re.compile(regexcat, re.DOTALL).findall(content)
                for country, ids, name in match:
                    if country != names:
                        continue
                    ids = ids.replace(':', '').replace(' ', '').replace(',', '')
                    url = str(server) + '/live2/play/' + str(ids) + '.ts'  # + app
                    name = decodeHtml(name)
                    name = rimuovi_parentesi(name)
                    item = name + "###" + url + '\n'
                    items.append(item)
                items.sort()
                # use for search
                global itemlist
                itemlist = items
                # use for search end
                for item in items:
                    name1 = item.split('###')[0]
                    url = item.split('###')[1]
                    name = unquote(name1).strip("\r\n")
                    self.cat_list.append(show_(name, url))
                    # make m3u
                    nname = '#EXTINF:-1,' + str(name) + '\n'
                    outfile.write(nname)
                    outfile.write('#EXTVLCOPT:http-user-agent=VAVOO/2.6' + '\n')
                    outfile.write(str(url) + '\n')
                # make m3u end
                if len(self.cat_list) < 1:
                    return
                else:
                    self['menulist'].l.setList(self.cat_list)
                    self['menulist'].moveToIndex(0)
                    txtsream = self['menulist'].getCurrent()[0][0]
                    self['name'].setText(str(txtsream))
        except Exception as error:
            print(error)
            trace_error()
            self['name'].setText('Error')
        self['version'].setText('V.' + currversion)

    def ok(self):
        try:
            i = self['menulist'].getSelectedIndex()
            self.currentindex = i
            selection = self['menulist'].l.getCurrentSelection()
            if selection is not None:
                item = self.cat_list[i][0]
                name = item[0]
                url = item[1]
            self.play_that_shit(url, name, self.currentindex, item, self.cat_list)
        except Exception as error:
            print(error)
            trace_error()

    def play_that_shit(self, url, name, index, item, cat_list):
        self.session.open(Playstream2, name, url, index, item, cat_list)

    def message0(self, name, url, response):
        name = self.name
        url = self.url
        filenameout = enigma_path + '/userbouquet.vavoo_%s.tv' % name.lower()
        if file_exists(filenameout):
            self.message3(name, url, False)
        else:
            self.message2(name, url, False)

    def message1(self, answer=None):
        if answer is None:
            self.session.openWithCallback(self.message1, MessageBox, _('Do you want to Convert to favorite .tv ?\n\nAttention!! It may take some time\ndepending on the number of streams contained !!!'))
        elif answer:
            name = self.name
            url = self.url
            filenameout = enigma_path + '/userbouquet.vavoo_%s.tv' % name.lower()
            if file_exists(filenameout):
                self.message4()
            else:
                self.message2(name, url, True)

    def message2(self, name, url, response):
        service = cfg.services.value
        ch = 0
        ch = convert_bouquet(service, name, url)
        if int(ch) > 0:
            localtime = time.asctime(time.localtime(time.time()))
            cfg.last_update.value = localtime
            cfg.last_update.save()
            if response is True:
                _session.open(MessageBox, _('bouquets reloaded..\nWith %s channel') % str(ch), MessageBox.TYPE_INFO, timeout=5)
        else:
            _session.open(MessageBox, _('Download Error'), MessageBox.TYPE_INFO, timeout=5)

    def message3(self, name, url, response):
        sig = Sig()
        app = str(sig)
        filename = enigma_list + '/userbouquet.vavoo_%s.tv' % name.lower()
        filenameout = enigma_path + '/userbouquet.vavoo_%s.tv' % name.lower()
        key = None
        with open(filename, "rt") as fin:
            data = fin.read()
            regexcat = '#SERVICE.*?vavoo_auth=(.+?)#User'
            match = re.compile(regexcat, re.DOTALL).findall(data)
            for key in match:
                key = str(key)

        with open(filename, 'r') as f:
            newlines = []
            for line in f.readlines():
                newlines.append(line.replace(key, app))

        with open(filenameout, 'w') as f:
            for line in newlines:
                f.write(line)
        ReloadBouquets()
        localtime = time.asctime(time.localtime(time.time()))
        cfg.last_update.value = localtime
        cfg.last_update.save()
        if response is True:
            _session.open(MessageBox, _('Wait...\nUpdate List Bouquet...\nbouquets reloaded..'), MessageBox.TYPE_INFO, timeout=5)

    def message4(self, answer=None):
        if answer is None:
            self.session.openWithCallback(self.message4, MessageBox, _('The favorite channel list exists.\nWant to update it with epg and picons?\n\nYES for Update'))
        elif answer:
            name = self.name
            url = self.url
            # filenameout = enigma_path + '/userbouquet.vavoo_%s.tv' % name.lower()
            self.message3(name, url, True)

    def search_vavoo(self):
        self.session.openWithCallback(
            self.filterM3u,
            VirtualKeyBoard,
            title=_("Filter this category..."),
            text='')

    def filterM3u(self, result):
        global search_ok
        if result:
            try:
                self.cat_list = []
                search = result
                for item in itemlist:
                    name = item.split('###')[0]
                    url = item.split('###')[1]
                    if search.lower() in str(name).lower():
                        search_ok = True
                        namex = name
                        urlx = url.replace('%0a', '').replace('%0A', '')
                        self.cat_list.append(show_(namex, urlx))
                if len(self.cat_list) < 1:
                    _session.open(MessageBox, _('No channels found in search!!!'), MessageBox.TYPE_INFO, timeout=5)
                    return
                else:
                    self['menulist'].l.setList(self.cat_list)
                    self['menulist'].moveToIndex(0)
                    txtsream = self['menulist'].getCurrent()[0][0]
                    self['name'].setText(str(txtsream))
            except Exception as error:
                print(error)
                trace_error()
                self['name'].setText('Error')
                search_ok = False


class TvInfoBarShowHide():
    STATE_HIDDEN = 0
    STATE_HIDING = 1
    STATE_SHOWING = 2
    STATE_SHOWN = 3
    FLAG_CENTER_DVB_SUBS = 2048
    skipToggleShow = False

    def __init__(self):
        self["ShowHideActions"] = ActionMap(["InfobarShowHideActions"],
                                            {"toggleShow": self.OkPressed,
                                             "hide": self.hide}, 0)
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evStart: self.serviceStarted})
        self.__state = self.STATE_SHOWN
        self.__locked = 0
        self.hideTimer = eTimer()
        try:
            self.hideTimer_conn = self.hideTimer.timeout.connect(self.doTimerHide)
        except:
            self.hideTimer.callback.append(self.doTimerHide)
        self.hideTimer.start(3000, True)
        self.onShow.append(self.__onShow)
        self.onHide.append(self.__onHide)

    def OkPressed(self):
        self.toggleShow()

    def __onShow(self):
        self.__state = self.STATE_SHOWN
        self.startHideTimer()

    def __onHide(self):
        self.__state = self.STATE_HIDDEN

    def serviceStarted(self):
        if self.execing:
            # if config.usage.show_infobar_on_zap.value:
            self.doShow()

    def startHideTimer(self):
        if self.__state == self.STATE_SHOWN and not self.__locked:
            self.hideTimer.stop()
            self.hideTimer.start(3000, True)
        elif hasattr(self, "pvrStateDialog"):
            self.hideTimer.stop()
        self.skipToggleShow = False

    def doShow(self):
        self.hideTimer.stop()
        self.show()
        self.startHideTimer()

    def doTimerHide(self):
        self.hideTimer.stop()
        if self.__state == self.STATE_SHOWN:
            self.hide()

    def toggleShow(self):
        if self.skipToggleShow:
            self.skipToggleShow = False
            return
        if self.__state == self.STATE_HIDDEN:
            self.show()
            self.hideTimer.stop()
        else:
            self.hide()
            self.startHideTimer()

    def lockShow(self):
        try:
            self.__locked += 1
        except:
            self.__locked = 0
        if self.execing:
            self.show()
            self.hideTimer.stop()
            self.skipToggleShow = False

    def unlockShow(self):
        try:
            self.__locked -= 1
        except:
            self.__locked = 0
        if self.__locked < 0:
            self.__locked = 0
        if self.execing:
            self.startHideTimer()


class Playstream2(
    InfoBarBase,
    InfoBarMenu,
    InfoBarSeek,
    InfoBarAudioSelection,
    InfoBarSubtitleSupport,
    InfoBarNotifications,
    TvInfoBarShowHide,
    Screen
):
    STATE_IDLE = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    ENABLE_RESUME_SUPPORT = True
    ALLOW_SUSPEND = True
    screen_timeout = 5000

    def __init__(self, session, name, url, index, item, cat_list):
        global streaml, _session
        Screen.__init__(self, session)
        self.session = session
        _session = session
        self.skinName = 'MoviePlayer'
        self.currentindex = index
        self.item = item
        self.itemscount = len(cat_list)
        self.list = cat_list
        streaml = False
        for x in InfoBarBase, \
                InfoBarMenu, \
                InfoBarSeek, \
                InfoBarAudioSelection, \
                InfoBarSubtitleSupport, \
                InfoBarNotifications, \
                TvInfoBarShowHide:
            x.__init__(self)
        try:
            self.init_aspect = int(self.getAspect())
        except:
            self.init_aspect = 0
        self.new_aspect = self.init_aspect
        self.service = None
        self.url = url.replace('%0a', '').replace('%0A', '')
        self.name = name
        self.state = self.STATE_PLAYING
        self.srefInit = self.session.nav.getCurrentlyPlayingServiceReference()
        self['actions'] = ActionMap(['MoviePlayerActions', 'MovieSelectionActions', 'MediaPlayerActions', 'EPGSelectActions', 'OkCancelActions',
                                    'InfobarShowHideActions', 'InfobarActions', 'DirectionActions', 'InfobarSeekActions'], {
            'epg': self.showIMDB,
            'info': self.showIMDB,
            'tv': self.cicleStreamType,
            'stop': self.leavePlayer,
            'cancel': self.cancel,
            'channelDown': self.previousitem,
            'channelUp': self.nextitem,
            'down': self.previousitem,
            'up': self.nextitem,
            'back': self.cancel
        }, -1)

        self.onFirstExecBegin.append(self.cicleStreamType)
        self.onClose.append(self.cancel)

    def nextitem(self):
        currentindex = int(self.currentindex) + 1
        if currentindex == self.itemscount:
            currentindex = 0
        self.currentindex = currentindex
        i = self.currentindex
        item = self.list[i][0]
        self.name = item[0]
        self.url = item[1]
        self.cicleStreamType()

    def previousitem(self):
        currentindex = int(self.currentindex) - 1
        if currentindex < 0:
            currentindex = self.itemscount - 1
        self.currentindex = currentindex
        i = self.currentindex
        item = self.list[i][0]
        self.name = item[0]
        self.url = item[1]
        self.cicleStreamType()

    # def doEofInternal(self, playing):
        # self.close()

    # def __evEOF(self):
        # self.end = True

    def doEofInternal(self, playing):
        print('doEofInternal', playing)
        MemClean()
        if self.execing and playing:
            self.cicleStreamType()

    def __evEOF(self):
        print('__evEOF')
        self.end = True
        MemClean()
        self.cicleStreamType()

    def getAspect(self):
        return AVSwitch().getAspectRatioSetting()

    def getAspectString(self, aspectnum):
        return {0: '4:3 Letterbox',
                1: '4:3 PanScan',
                2: '16:9',
                3: '16:9 always',
                4: '16:10 Letterbox',
                5: '16:10 PanScan',
                6: '16:9 Letterbox'}[aspectnum]

    def setAspect(self, aspect):
        map = {0: '4_3_letterbox',
               1: '4_3_panscan',
               2: '16_9',
               3: '16_9_always',
               4: '16_10_letterbox',
               5: '16_10_panscan',
               6: '16_9_letterbox'}
        config.av.aspectratio.setValue(map[aspect])
        try:
            AVSwitch().setAspectRatio(aspect)
        except:
            pass

    def av(self):
        self.new_aspect += 1
        if self.new_aspect > 6:
            self.new_aspect = 0
        try:
            AVSwitch.getInstance().setAspectRatio(self.new_aspect)
            return VIDEO_ASPECT_RATIO_MAP[self.new_aspect]
        except Exception as error:
            print(error)
            trace_error()
            return _("Resolution Change Failed")

    def nextAV(self):
        message = self.av()
        self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=1)

    def showinfo(self):
        sTitle = ''
        sServiceref = ''
        try:
            servicename, serviceurl = getserviceinfo(self.sref)
            if servicename is not None:
                sTitle = servicename
            else:
                sTitle = ''
            if serviceurl is not None:
                sServiceref = serviceurl
            else:
                sServiceref = ''
            currPlay = self.session.nav.getCurrentService()
            sTagCodec = currPlay.info().getInfoString(iServiceInformation.sTagCodec)
            sTagVideoCodec = currPlay.info().getInfoString(iServiceInformation.sTagVideoCodec)
            sTagAudioCodec = currPlay.info().getInfoString(iServiceInformation.sTagAudioCodec)
            message = 'stitle:' + str(sTitle) + '\n' + 'sServiceref:' + str(sServiceref) + '\n' + 'sTagCodec:' + str(sTagCodec) + '\n' + 'sTagVideoCodec:' + str(sTagVideoCodec) + '\n' + 'sTagAudioCodec : ' + str(sTagAudioCodec)
            self.mbox = self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        except:
            pass
        return

    def showIMDB(self):
        try:
            text_clear = self.name
            if returnIMDB(text_clear):
                print('show imdb/tmdb')
        except Exception as error:
            trace_error()
            print("Error: can't find Playstream2 in live_to_stream", str(error))

    def slinkPlay(self):
        url = self.url
        name = self.name
        ref = "{0}:{1}".format(url.replace(":", "%3a"), name.replace(":", "%3a"))
        # print('final reference:   ', ref)
        sref = eServiceReference(ref)
        self.sref = sref
        sref.setName(name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def openTest(self, servicetype, url):
        # tmlast = int(time.time())
        sig = Sig()
        app = '?n=1&b=5&vavoo_auth=' + str(sig) + '#User-Agent=VAVOO/2.6'
        # print('sig:', str(sig))
        name = self.name
        url = url + app
        ref = "{0}:0:0:0:0:0:0:0:0:0:{1}:{2}".format(servicetype, url.replace(":", "%3a"), name.replace(":", "%3a"))
        print('final reference:   ', ref)
        sref = eServiceReference(ref)
        self.sref = sref
        self.sref.setName(name)
        self.session.nav.stopService()
        self.session.nav.playService(self.sref)

    def cicleStreamType(self):
        self.servicetype = cfg.services.value
        if not self.url.startswith('http'):
            self.url = 'http://' + self.url
        url = str(self.url)
        if str(os_path.splitext(self.url)[-1]) == ".m3u8":
            if self.servicetype == "1":
                self.servicetype = "4097"
        self.openTest(self.servicetype, url)

    def showVideoInfo(self):
        if self.shown:
            self.hideInfobar()
        if self.infoCallback is not None:
            self.infoCallback()
        return

    def showAfterSeek(self):
        if isinstance(self, TvInfoBarShowHide):
            self.doShow()

    def cancel(self):
        if os_path.isfile('/tmp/hls.avi'):
            os.remove('/tmp/hls.avi')
        self.session.nav.stopService()
        self.session.nav.playService(self.srefInit)
        if not self.new_aspect == self.init_aspect:
            try:
                self.setAspect(self.init_aspect)
            except:
                pass
        self.close()

    def leavePlayer(self):
        self.close()


VIDEO_ASPECT_RATIO_MAP = {0: "4:3 Letterbox", 1: "4:3 PanScan", 2: "16:9", 3: "16:9 Always", 4: "16:10 Letterbox", 5: "16:10 PanScan", 6: "16:9 Letterbox"}
VIDEO_FMT_PRIORITY_MAP = {"38": 1, "37": 2, "22": 3, "18": 4, "35": 5, "34": 6}


def convert_bouquet(service, name, url):
    sig = Sig()
    app = '?n=1&b=5&vavoo_auth=%s#User-Agent=VAVOO/2.6' % (str(sig))
    files = '/tmp/%s.m3u' % name
    bouquet_type = 'tv'
    if "radio" in name.lower():
        bouquet_type = "radio"
    name_file = re.sub(r'[<>:"/\\|?*, ]', '_', str(name))  # Replace spaces and commas with "_"
    name_file = re.sub(r'\d+:\d+:[\d.]+', '_', name_file)  # Replace numeric patterns with "_"
    name_file = re.sub(r'_+', '_', name_file)  # Replace sequences of "_" with a single "_"

    with open(enigma_path + '/Favorite.txt', 'w', encoding='utf-8') as r:
        r.write(str(name_file) + '###' + str(url))

    bouquet_name = 'userbouquet.vavoo_%s.%s' % (name_file.lower(), bouquet_type.lower())
    print("Converting Bouquet %s" % name_file)
    path1 = '/etc/enigma2/' + str(bouquet_name)
    path2 = '/etc/enigma2/bouquets.' + str(bouquet_type.lower())
    ch = 0
    if os.path.exists(files) and os.stat(files).st_size > 0:
        try:
            tplst = []
            tplst.append('#NAME %s (%s)' % (name_file.capitalize(), bouquet_type.upper()))
            tplst.append('#SERVICE 1:64:0:0:0:0:0:0:0:0::%s CHANNELS' % name_file)
            tplst.append('#DESCRIPTION --- %s ---' % name_file)
            namel = ''
            svz = ''
            dct = ''
            with open(files, 'r') as f:  # 'r' is for universal newlines mode
                for line in f:
                    if line.startswith("#EXTINF"):
                        namel = '%s' % line.split(',')[-1]
                        dsna = ('#DESCRIPTION %s' % namel).splitlines()
                        dct = ''.join(dsna)

                    elif line.startswith('http'):
                        line = str(line).strip('\n\r') + str(app)
                        tag = '1'
                        if bouquet_type.upper() == 'RADIO':
                            tag = '2'

                        svca = ('#SERVICE %s:0:%s:0:0:0:0:0:0:0:%s' % (service, tag, line.replace(':', '%3a')))
                        svz = (svca + ':' + namel).splitlines()
                        svz = ''.join(svz)

                    if svz not in tplst:
                        tplst.append(svz)
                        tplst.append(dct)
                        ch += 1

            with open(path1, 'w+', encoding='utf-8') as f:
                f_content = f.read()
                for item in tplst:
                    if item not in f_content:
                        f.write("%s\n" % item)
                        # print('item  -------- ', item)

            in_bouquets = False
            with open('/etc/enigma2/bouquets.%s' % bouquet_type.lower(), 'r') as f:
                for line in f:
                    if bouquet_name in line:
                        in_bouquets = True
            if not in_bouquets:
                with open(path2, 'a+', encoding='utf-8') as f:
                    bouquetTvString = '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "' + str(bouquet_name) + '" ORDER BY bouquet\n'
                    f.write(bouquetTvString)
            ReloadBouquets()
        except Exception as error:
            print(error)

    return ch


autoStartTimer = None


class AutoStartTimer:
    def __init__(self, session):
        print("*** running AutoStartTimer Vavoo ***")
        self.session = session
        self.timer = eTimer()
        try:
            self.timer.callback.append(self.on_timer)
        except:
            self.timer_conn = self.timer.timeout.connect(self.on_timer)
        self.timer.start(100, True)
        self.update()  # issue loop

    def get_wake_time(self):
        if cfg.autobouquetupdate.value is True:
            if cfg.timetype.value == "interval":
                interval = int(cfg.updateinterval.value)
                nowt = time.time()
                return int(nowt) + interval * 60  # * 60
            if cfg.timetype.value == "fixed time":
                ftc = cfg.fixedtime.value
                now = time.localtime(time.time())
                fwt = int(time.mktime((now.tm_year,
                                       now.tm_mon,
                                       now.tm_mday,
                                       ftc[0],
                                       ftc[1],
                                       now.tm_sec,
                                       now.tm_wday,
                                       now.tm_yday,
                                       now.tm_isdst)))
                return fwt
        else:
            return -1

    def update(self, constant=0):
        self.timer.stop()
        wake = self.get_wake_time()
        nowt = time.time()
        if wake > 0:
            if wake < nowt + constant:
                if cfg.timetype.value == "interval":
                    interval = int(cfg.updateinterval.value)
                    wake += interval * 60  # * 60
                elif cfg.timetype.value == "fixed time":
                    wake += 86400
            next = wake - int(nowt)
            if next > 3600:
                next = 3600
            if next <= 0:
                next = 60
            self.timer.startLongTimer(next)
        else:
            wake = -1
        return wake

    def on_timer(self):
        self.timer.stop()
        now = int(time.time())
        wake = now
        constant = 0
        if cfg.timetype.value == "fixed time":
            wake = self.get_wake_time()
        # if wake - now < 60:
        if abs(wake - now) < 60:
            try:
                self.startMain()
                constant = 60
                # self.update()
                localtime = time.asctime(time.localtime(time.time()))
                cfg.last_update.value = localtime
                cfg.last_update.save()
            except Exception as error:
                print(error)
                trace_error()
        self.update(constant)

    def startMain(self):
        name = url = ''
        favorite_channel = os.path.join(enigma_path, 'Favorite.txt')
        if file_exists(favorite_channel):
            with open(favorite_channel, 'r') as f:
                line = f.readline()
                name = line.split('###')[0]
                url = line.split('###')[1]
                '''# print('name %s and url %s:' % (name, url))
            # try:'''
            print('session start convert time')
            vid2 = vavoox(_session, name, url)
            vid2.message0(name, url, False)
            '''# except Exception as e:
                # print('timeredit error vavoo', e)'''


def check_configuring():
    if cfg.autobouquetupdate.value is True:
        """Check for new config values for auto start
        """
        global autoStartTimer
        if autoStartTimer is not None:
            autoStartTimer.update()
        return


def autostart(reason, session=None, **kwargs):
    global autoStartTimer
    global _session
    if reason == 0 and _session is None:
        if session is not None:
            _session = session
            if autoStartTimer is None:
                autoStartTimer = AutoStartTimer(session)
    return


def get_next_wakeup():
    return -1


def main(session, **kwargs):
    try:
        if file_exists('/tmp/vavoo.log'):
            os.remove('/tmp/vavoo.log')

        session.open(MainVavoox)
    except Exception as error:
        print(error)
        trace_error()


def Plugins(**kwargs):
    result = [PluginDescriptor(name=title_plug, description="Vavoo Stream Live", where=[PluginDescriptor.WHERE_AUTOSTART, PluginDescriptor.WHERE_SESSIONSTART], fnc=autostart, wakeupfnc=get_next_wakeup)]
    return result


def decodeHtml(text):
    if PY3:
        import html
        text = html.unescape(text.encode('utf-8').decode('unicode_escape'))
    else:
        from six.moves import (html_parser)
        h = html_parser.HTMLParser()
        text = h.unescape(text.decode('utf8')).encode('utf8')
    text = text.replace('&amp;', '&')
    text = text.replace('&apos;', "'")
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&ndash;', '-')
    text = text.replace('&quot;', '"')
    text = text.replace('&ntilde;', '~')
    text = text.replace('&rsquo;', '\'')
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&equals;', '=')
    text = text.replace('&quest;', '?')
    text = text.replace('&comma;', ',')
    text = text.replace('&period;', '.')
    text = text.replace('&colon;', ':')
    text = text.replace('&lpar;', '(')
    text = text.replace('&rpar;', ')')
    text = text.replace('&excl;', '!')
    text = text.replace('&dollar;', '$')
    text = text.replace('&num;', '#')
    text = text.replace('&ast;', '*')
    text = text.replace('&lowbar;', '_')
    text = text.replace('&lsqb;', '[')
    text = text.replace('&rsqb;', ']')
    text = text.replace('&half;', '1/2')
    text = text.replace('&DiacriticalTilde;', '~')
    text = text.replace('&OpenCurlyDoubleQuote;', '"')
    text = text.replace('&CloseCurlyDoubleQuote;', '"')
    return text.strip()


ListAgent = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2919.83 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.14 (KHTML, like Gecko) Chrome/24.0.1292.0 Safari/537.14',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
    'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1284.0 Safari/537.13',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.8 (KHTML, like Gecko) Chrome/17.0.940.0 Safari/535.8',
    'Mozilla/6.0 (Windows NT 6.2; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/4.0; InfoPath.2; SV1; .NET CLR 2.0.50727; WOW64)',
    'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10',
    'Mozilla/5.0 (iPad; CPU OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko ) Version/5.1 Mobile/9B176 Safari/7534.48.3']


def RequestAgent():
    from random import choice
    RandomAgent = choice(ListAgent)
    return RandomAgent


def remove_line(filename, what):
    if os_path.isfile(filename):
        file_read = open(filename).readlines()
        file_write = open(filename, 'w')
        for line in file_read:
            if what not in line:
                file_write.write(line)
        file_write.close()


def ReloadBouquets():
    print('\n----Reloading bouquets----\n')
    try:
        from enigma import eDVBDB
    except ImportError:
        eDVBDB = None
    if eDVBDB:
        db = eDVBDB.getInstance()
        if db:
            db.reloadServicelist()
            db.reloadBouquets()
            print("eDVBDB: bouquets reloaded...")
    else:
        os.system("wget -qO - http://127.0.0.1/web/servicelistreload?mode=2 > /dev/null 2>&1 &")
        os.system("wget -qO - http://127.0.0.1/web/servicelistreload?mode=4 > /dev/null 2>&1 &")
        print("wGET: bouquets reloaded...")


def purge(dir, pattern):
    for f in os.listdir(dir):
        file_path = os_path.join(dir, f)
        if os_path.isfile(file_path):
            if re.search(pattern, f):
                os.remove(file_path)


def MemClean():
    try:
        os.system('sync')
        os.system('echo 1 > /proc/sys/vm/drop_caches')
        os.system('echo 2 > /proc/sys/vm/drop_caches')
        os.system('echo 3 > /proc/sys/vm/drop_caches')
    except:
        pass
