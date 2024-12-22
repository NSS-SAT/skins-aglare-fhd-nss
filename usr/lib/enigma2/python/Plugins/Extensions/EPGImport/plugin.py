from __future__ import absolute_import, print_function
from . import _
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.ConfigList import ConfigListScreen
from Components.Console import Console
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.config import config, ConfigEnableDisable, ConfigSubsection, \
    ConfigYesNo, ConfigClock, getConfigListEntry, ConfigText, ConfigInteger, ConfigDirectory, \
    ConfigSelection, ConfigNumber, ConfigSubDict, NoSave, configfile
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.LocationBox import LocationBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools import Notifications
from Tools.Directories import SCOPE_PLUGINS, fileExists, resolveFilename
from Tools.FuzzyDate import FuzzyTime
from Tools.StbHardware import getFPWasTimerWakeup
from enigma import eServiceCenter, eServiceReference, eEPGCache, getDesktop, eTimer, eConsoleAppContainer
import Components.PluginComponent
import NavigationInstance
import Screens.Standby
import os
import time

from . import log
from . import ExpandableSelectionList
from . import EPGImport
from . import EPGConfig
from . import filtersServices


def lastMACbyte():
    try:
        return int(open('/sys/class/net/eth0/address').readline().strip()[-2:], 16)
    except:
        return 256


def calcDefaultStarttime():
    try:
        # Use the last MAC byte as time offset (half-minute intervals)
        offset = lastMACbyte() * 30
    except:
        offset = 7680
    return (5 * 60 * 60) + offset


def getMountPoints():
    mount_points = []
    try:
        with open('/proc/mounts', 'r') as mounts:
            for line in mounts:
                parts = line.split()
                mount_point = parts[1]
                if os.path.ismount(mount_point) and os.access(mount_point, os.W_OK):
                    mount_points.append(mount_point)
    except Exception as e:
        print("[EPGImport] Error reading /proc/mounts:", e)
    return mount_points


mount_points = getMountPoints()
mount_point = None
for mp in mount_points:
    epg_path = os.path.join(mp, 'epg.dat')
    if os.path.exists(epg_path):
        mount_point = epg_path
        break


# HDD_EPG_DAT = mount_point or '/etc/enigma2/epg.dat'
HDD_EPG_DAT = '/etc/enigma2/epg.dat'
if config.misc.epgcache_filename.value:
    HDD_EPG_DAT = config.misc.epgcache_filename.value
else:
    config.misc.epgcache_filename.setValue(HDD_EPG_DAT)
# config.misc.epgcache_filename.save()
# Set default configuration
config.plugins.epgimport = ConfigSubsection()
config.plugins.epgimport.enabled = ConfigEnableDisable(default=True)
config.plugins.epgimport.repeat_import = ConfigInteger(default=0, limits=(0, 23))
config.plugins.epgimport.runboot = ConfigSelection(default="4", choices=[
    ("1", _("always")),
    ("2", _("only manual boot")),
    ("3", _("only automatic boot")),
    ("4", _("never"))
])
config.plugins.epgimport.runboot_restart = ConfigYesNo(default=False)
config.plugins.epgimport.runboot_day = ConfigYesNo(default=False)
config.plugins.epgimport.wakeup = ConfigClock(default=calcDefaultStarttime())
config.plugins.epgimport.showinextensions = ConfigYesNo(default=True)
config.plugins.epgimport.deepstandby = ConfigSelection(default="skip", choices=[
    ("wakeup", _("wake up and import")),
    ("skip", _("skip the import"))
])
config.plugins.epgimport.loadepg_only = ConfigSelection(default="default", choices=[
    ("default", _("checking service reference(default)")),
    ("iptv", _("only IPTV channels")),
    ("all", _("all channels"))
])
config.plugins.epgimport.pathdb = ConfigDirectory(default='/etc/enigma2/epg.dat')
config.plugins.epgimport.execute_shell = ConfigYesNo(default=False)
config.plugins.epgimport.shell_name = ConfigText(default="")
config.plugins.epgimport.standby_afterwakeup = ConfigYesNo(default=False)
config.plugins.epgimport.run_after_standby = ConfigYesNo(default=False)
config.plugins.epgimport.shutdown = ConfigYesNo(default=False)
config.plugins.epgimport.longDescDays = ConfigNumber(default=5)
config.plugins.epgimport.showinmainmenu = ConfigYesNo(default=False)
config.plugins.epgimport.deepstandby_afterimport = NoSave(ConfigYesNo(default=False))
config.plugins.epgimport.parse_autotimer = ConfigYesNo(default=False)
config.plugins.epgimport.import_onlybouquet = ConfigYesNo(default=False)
config.plugins.epgimport.clear_oldepg = ConfigYesNo(default=False)
config.plugins.epgimport.filter_custom_channel = ConfigYesNo(default=True)
config.plugins.epgimport.day_profile = ConfigSelection(choices=[("1", _("Press OK"))], default="1")
config.plugins.extra_epgimport = ConfigSubsection()
config.plugins.extra_epgimport.last_import = ConfigText(default="0")
config.plugins.extra_epgimport.day_import = ConfigSubDict()
for i in range(7):
    config.plugins.extra_epgimport.day_import[i] = ConfigEnableDisable(default=True)

weekdays = [
    _("Monday"),
    _("Tuesday"),
    _("Wednesday"),
    _("Thursday"),
    _("Friday"),
    _("Saturday"),
    _("Sunday"),
]

# historically located (not a problem, we want to update it)
CONFIG_PATH = '/etc/epgimport'

# Global variable
autoStartTimer = None
_session = None
BouquetChannelListList = None
serviceIgnoreList = None
filterCounter = 0
isFilterRunning = 0


def getAlternatives(service):
    if not service:
        return None
    alternativeServices = eServiceCenter.getInstance().list(service)
    return alternativeServices and alternativeServices.getContent("S", True)


def getRefNum(ref):
    ref = ref.split(':')[3:7]
    try:
        return int(ref[0], 16) << 48 | int(ref[1], 16) << 32 | int(ref[2], 16) << 16 | int(ref[3], 16) >> 16
    except:
        return


def getBouquetChannelList():
    channels = []
    global isFilterRunning, filterCounter
    isFilterRunning = 1
    serviceHandler = eServiceCenter.getInstance()
    mask = (eServiceReference.isMarker | eServiceReference.isDirectory)
    altrernative = eServiceReference.isGroup
    if config.usage.multibouquet.value:
        bouquet_rootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'
        bouquet_root = eServiceReference(bouquet_rootstr)
        list = serviceHandler.list(bouquet_root)
        if list:
            while True:
                s = list.getNext()
                if not s.valid():
                    break
                if s.flags & eServiceReference.isDirectory:
                    info = serviceHandler.info(s)
                    if info:
                        clist = serviceHandler.list(s)
                        if clist:
                            while True:
                                service = clist.getNext()
                                filterCounter += 1
                                if not service.valid():
                                    break
                                if not (service.flags & mask):
                                    if service.flags & altrernative:
                                        altrernative_list = getAlternatives(service)
                                        if altrernative_list:
                                            for channel in altrernative_list:
                                                refnum = getRefNum(channel)
                                                if refnum and refnum not in channels:
                                                    channels.append(refnum)
                                    else:
                                        refnum = getRefNum(service.toString())
                                        if refnum and refnum not in channels:
                                            channels.append(refnum)
    else:
        bouquet_rootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet'
        bouquet_root = eServiceReference(bouquet_rootstr)
        services = serviceHandler.list(bouquet_root)
        if services is not None:
            while True:
                service = services.getNext()
                filterCounter += 1
                if not service.valid():
                    break
                if not (service.flags & mask):
                    if service.flags & altrernative:
                        altrernative_list = getAlternatives(service)
                        if altrernative_list:
                            for channel in altrernative_list:
                                refnum = getRefNum(channel)
                                if refnum and refnum not in channels:
                                    channels.append(refnum)
                    else:
                        refnum = getRefNum(service.toString())
                        if refnum and refnum not in channels:
                            channels.append(refnum)
    isFilterRunning = 0
    return channels

# Filter servicerefs that this box can display by starting a fake recording.


def channelFilter(ref):
    if not ref:
        return False
    loadepg_only = config.plugins.epgimport.loadepg_only.value
    if loadepg_only != "default":
        if loadepg_only == "all":
            return True
        elif loadepg_only == "iptv":
            return ("%3a//" not in ref.lower() or ref.startswith("1")) and False or True
    sref = eServiceReference(ref)
    refnum = getRefNum(sref.toString())
    if config.plugins.epgimport.import_onlybouquet.value:
        global BouquetChannelListList
        if BouquetChannelListList is None:
            BouquetChannelListList = getBouquetChannelList()
        if refnum not in BouquetChannelListList:
            print("Serviceref not in bouquets:", sref.toString(), file=log)
            return False
    global serviceIgnoreList
    if serviceIgnoreList is None:
        serviceIgnoreList = [getRefNum(x) for x in filtersServices.filtersServicesList.servicesList()]
    if refnum in serviceIgnoreList:
        print("Serviceref is in ignore list:", sref.toString(), file=log)
        return False
    if "%3a//" in ref.lower():
        # print("URL detected in serviceref, not checking fake recording on serviceref:", ref, file=log)
        return True
    fakeRecService = NavigationInstance.instance.recordService(sref, True)
    if fakeRecService:
        fakeRecResult = fakeRecService.start(True)
        NavigationInstance.instance.stopRecordService(fakeRecService)
        # -7 (errNoSourceFound) occurs when tuner is disconnected.
        r = fakeRecResult in (0, -7)
        return r
    print("Invalid serviceref string:", ref, file=log)
    return False


epgimport = EPGImport.EPGImport(eEPGCache.getInstance(), channelFilter)

lastImportResult = None


def startImport():
    if not epgimport.isImportRunning():
        EPGImport.HDD_EPG_DAT = config.misc.epgcache_filename.value
        if config.plugins.epgimport.filter_custom_channel.value:
            EPGConfig.filterCustomChannel = True
        else:
            EPGConfig.filterCustomChannel = False
        if config.plugins.epgimport.clear_oldepg.value and hasattr(epgimport.epgcache, 'flushEPG'):
            EPGImport.unlink_if_exists(EPGImport.HDD_EPG_DAT)
            EPGImport.unlink_if_exists(EPGImport.HDD_EPG_DAT + '.backup')
            epgimport.epgcache.flushEPG()
        epgimport.onDone = doneImport
        epgimport.beginImport(longDescUntil=config.plugins.epgimport.longDescDays.value * 24 * 3600 + time.time())
    else:
        print("[startImport] Already running, won't start again", file=log)


##################################
# Configuration GUI
HD = False
try:
    if getDesktop(0).size().width() >= 1280:
        HD = True
except:
    pass


class EPGImportConfig(ConfigListScreen, Screen):
    if HD:
        skin = """
            <screen position="center,center" size="600,605" title="EPG Import Configuration" >
                <ePixmap name="red" position="0,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
                <ePixmap name="green" position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
                <ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
                <ePixmap name="blue" position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
                <ePixmap position="562,0" size="35,25" pixmap="skin_default/buttons/key_info.png" alphatest="on" />
                <ePixmap position="562,30" size="35,25" pixmap="skin_default/buttons/key_menu.png" alphatest="on" />
                <widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;19" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
                <widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;19" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
                <widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;19" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
                <widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;19" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
                <widget name="config" position="10,70" size="590,355" scrollbarMode="showOnDemand" />
                <ePixmap alphatest="on" pixmap="icons/clock.png" position="520,583" size="14,14" zPosition="3"/>
                <widget font="Regular;18" halign="left" position="545,580" render="Label" size="55,20" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
                    <convert type="ClockToText">Default</convert>
                </widget>
                <widget name="description" position="10,430" size="590,100" font="Regular;17" valign="top"/>
                <widget name="statusbar" position="10,535" size="590,20" font="Regular;18" />
                <widget name="status" position="10,560" size="590,40" font="Regular;19" />
            </screen>"""
    else:
        skin = """
            <screen position="center,center" size="600,430" title="EPG Import Configuration" >
                <ePixmap name="red" position="0,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
                <ePixmap name="green" position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
                <ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
                <ePixmap name="blue" position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
                <ePixmap position="562,0" size="35,25" pixmap="skin_default/buttons/key_info.png" alphatest="on" />
                <ePixmap position="562,30" size="35,25" pixmap="skin_default/buttons/key_menu.png" alphatest="on" />
                <widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
                <widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
                <widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
                <widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
                <widget name="config" position="10,60" size="590,250" scrollbarMode="showOnDemand" />
                <ePixmap alphatest="on" pixmap="icons/clock.png" position="520,403" size="14,14" zPosition="3"/>
                <widget font="Regular;18" halign="left" position="545,400" render="Label" size="55,20" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
                    <convert type="ClockToText">Default</convert>
                </widget>
                <widget name="description" position="10,315" size="590,75" itemHeight="18" font="Regular;18" valign="top"/>
                <widget name="statusbar" position="10,410" size="500,20" font="Regular;18" />
                <widget name="status" position="10,330" size="580,60" font="Regular;20" />
            </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.setTitle(_("EPG Import Configuration"))
        self["status"] = Label()
        self["statusbar"] = Label()
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Save"))
        self["key_yellow"] = Button(_("Manual"))
        self["key_blue"] = Button(_("Sources"))
        self["description"] = Label("")
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions", "MovieSelectionActions"],
                                         {"red": self.keyRed,
                                          "green": self.keyGreen,
                                          "yellow": self.doimport,
                                          "blue": self.dosources,
                                          "cancel": self.extnok,
                                          "ok": self.keyOk,
                                          "log": self.keyInfo,
                                          "contextMenu": self.openMenu}, -1)
        # ConfigListScreen.__init__(self, [], session)
        self.lastImportResult = None
        self.list = []
        self.onChangedEntry = []
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
        self.prev_onlybouquet = config.plugins.epgimport.import_onlybouquet.value
        self.initConfig()
        self.createSetup()
        self.filterStatusTemplate = _("Filtering: %s\nPlease wait!")
        self.importStatusTemplate = _("Importing: %s\n%s events")
        self.updateTimer = eTimer()
        self.updateTimer.callback.append(self.updateStatus)
        self.updateTimer.start(2000)
        self.updateStatus()
        self.onLayoutFinish.append(self.createSummary)

    # for summary:
    def changedEntry(self):
        for x in self.onChangedEntry:
            x()

    def getCurrentEntry(self):
        return self["config"].getCurrent()[0]

    def getCurrentValue(self):
        return str(self["config"].getCurrent()[1].getText())

    def createSummary(self):
        from Screens.Setup import SetupSummary
        return SetupSummary

    def __layoutFinished(self):
        self.setTitle(self.setup_title)

    def initConfig(self):
        dx = 4 * " "
        self.EPG = config.plugins.epgimport
        self.cfg_enabled = getConfigListEntry(_("Automatic import EPG"), self.EPG.enabled, _("When enabled, it allows you to schedule an automatic EPG update at the given days and time."))
        self.cfg_pathdb = getConfigListEntry(_("Path DB EPG"), self.EPG.pathdb)
        self.cfg_wakeup = getConfigListEntry(dx + _("Automatic start time"), self.EPG.wakeup, _("Specify the time for the automatic EPG update."))
        self.cfg_deepstandby = getConfigListEntry(dx + _("When in deep standby"), self.EPG.deepstandby, _("Choose the action to perform when the box is in deep standby and the automatic EPG update should normally start."))
        self.cfg_shutdown = getConfigListEntry(dx + _("Return to deep standby after import"), self.EPG.shutdown, _("This will turn back waked up box into deep-standby after automatic EPG import."))
        self.cfg_standby_afterwakeup = getConfigListEntry(dx + _("Standby at startup"), self.EPG.standby_afterwakeup, _("The waked up box will be turned into standby after automatic EPG import wake up."))
        self.cfg_day_profile = getConfigListEntry(_("Choice days for start import"), self.EPG.day_profile, _("You can select the day(s) when the EPG update must be performed."))
        self.cfg_runboot = getConfigListEntry(_("Start import after booting up"), self.EPG.runboot, _("Specify in which case the EPG must be automatically updated after the box has booted."))
        self.cfg_import_onlybouquet = getConfigListEntry(dx + _("Load EPG only services in bouquets"), self.EPG.import_onlybouquet, _("To save memory you can decide to only load EPG data for the services that you have in your bouquet files."))
        self.cfg_loadepg_only = getConfigListEntry(_("Load EPG"), self.EPG.loadepg_only, _("Select load EPG mode for services."))
        self.cfg_runboot_day = getConfigListEntry(dx + _("Consider setting \"Days Profile\""), self.EPG.runboot_day, _("When you decide to import the EPG after the box booted mention if the \"days profile\" must be take into consideration or not."))
        self.cfg_runboot_restart = getConfigListEntry(dx + _("Skip import on restart GUI"), self.EPG.runboot_restart, _("When you restart the GUI you can decide to skip or not the EPG data import."))
        self.cfg_showinextensions = getConfigListEntry(_("Show \"EPG import now\" in extensions"), self.EPG.showinextensions, _("Display a shortcut \"EPG import now\" in the extension menu. This menu entry will immediately start the EPG update process when selected."))
        self.cfg_showinmainmenu = getConfigListEntry(_("Show \"EPG import\" in epg menu"), self.EPG.showinmainmenu, _("Display a shortcut \"EPG import\" in your STB epg menu screen. This allows you to access the configuration."))
        self.cfg_longDescDays = getConfigListEntry(_("Load long descriptions up to X days"), self.EPG.longDescDays, _("Define the number of days that you want to get the full EPG data, reducing this number can help you to save memory usage on your box. But you are also limited with the EPG provider available data. You will not have 15 days EPG if it only provide 7 days data."))
        self.cfg_parse_autotimer = getConfigListEntry(_("Run AutoTimer after import"), self.EPG.parse_autotimer, _("You can start automatically the plugin AutoTimer after the EPG data update to have it refreshing its scheduling after EPG data refresh."))
        self.cfg_clear_oldepg = getConfigListEntry(_("Clearing current EPG before import"), config.plugins.epgimport.clear_oldepg, _("This will clear the current EPG data in memory before updating the EPG data. This allows you to always have a clean new EPG with the latest EPG data, for example in case of program changes between refresh, otherwise EPG data are cumulative."))
        self.cfg_filter_custom_channel = getConfigListEntry(_("Also apply \"channel id\" filtering on custom.channels.xml"), self.EPG.filter_custom_channel, _("This is for advanced users that are using the channel id filtering feature. If enabled, the filter rules defined into /etc/epgimport/channel_id_filter.conf will also be applied on your /etc/epgimport/custom.channels.xml file."))
        self.cfg_execute_shell = getConfigListEntry(_("Execute shell command before import EPG"), self.EPG.execute_shell, _("When enabled, then you can run the desired script before starting the import, after which the import of the EPG will begin."))
        self.cfg_shell_name = getConfigListEntry(dx + _("Shell command name"), self.EPG.shell_name, _("Enter shell command name."))
        self.cfg_run_after_standby = getConfigListEntry(_("Start import after standby"), self.EPG.run_after_standby, _("Start import after resuming from standby mode."))
        self.cfg_repeat_import = getConfigListEntry(dx + _("Hours after which the import is repeated"), self.EPG.repeat_import, _("Number of hours (1-23, or 0 for no repeat) after which the import is repeated. This value is not saved and will be reset when the GUI restarts."))

    def createSetup(self):
        self.list = [self.cfg_enabled]
        if self.EPG.enabled.value:
            self.list.append(self.cfg_wakeup)
            self.list.append(self.cfg_deepstandby)
            if self.EPG.deepstandby.value == "wakeup":
                self.list.append(self.cfg_shutdown)
                if not self.EPG.shutdown.value:
                    self.list.append(self.cfg_standby_afterwakeup)
                    self.list.append(self.cfg_repeat_import)
            else:
                self.list.append(self.cfg_repeat_import)
        self.list.append(self.cfg_pathdb)
        self.list.append(self.cfg_day_profile)
        self.list.append(self.cfg_runboot)
        if self.EPG.runboot.value != "4":
            self.list.append(self.cfg_runboot_day)
            self.list.append(self.cfg_runboot_restart)
        self.list.append(self.cfg_run_after_standby)
        self.list.append(self.cfg_loadepg_only)
        if self.EPG.loadepg_only.value == "default":
            self.list.append(self.cfg_import_onlybouquet)
        if hasattr(eEPGCache, 'flushEPG'):
            self.list.append(self.cfg_clear_oldepg)
        self.list.append(self.cfg_filter_custom_channel)
        self.list.append(self.cfg_longDescDays)
        self.list.append(self.cfg_execute_shell)
        if self.EPG.execute_shell.value:
            self.list.append(self.cfg_shell_name)
        if fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/AutoTimer/plugin.pyo")) or fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/AutoTimer/plugin.pyc")):
            try:
                from Plugins.Extensions.AutoTimer.AutoTimer import AutoTimer
                self.list.append(self.cfg_parse_autotimer)
            except ImportError:
                print("[EPGImport] AutoTimer plugin not installed correctly", file=log)
        self.list.append(self.cfg_showinmainmenu)
        self.list.append(self.cfg_showinextensions)
        self["config"].list = self.list
        self["config"].l.setList(self.list)

    def newConfig(self):
        cur = self["config"].getCurrent()
        if cur in (self.cfg_enabled, self.cfg_shutdown, self.cfg_deepstandby, self.cfg_runboot, self.cfg_loadepg_only, self.cfg_execute_shell):
            self.createSetup()

    def keyRed(self):
        def setPrevValues(section, values):
            for (key, val) in section.content.items.items():
                value = values.get(key, None)
                if value is not None:
                    if isinstance(val, ConfigSubsection):
                        setPrevValues(val, value)
                    else:
                        val.value = value
        setPrevValues(self.EPG, self.prev_values)
        self.keyGreen()

    def extnok(self, answer=None):
        if answer is None:
            self.session.openWithCallback(self.extnok, MessageBox, _("Really close without saving settings?"))
        elif answer:
            for x in self["config"].list:
                x[1].cancel()
            self.close(True)
        return

    def keyGreen(self):
        self.updateTimer.stop()
        if self.EPG.parse_autotimer.value and (not fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/AutoTimer/plugin.pyo")) or not fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/AutoTimer/plugin.pyc"))):
            self.EPG.parse_autotimer.value = False
        if self.EPG.deepstandby.value == "skip" and self.EPG.shutdown.value:
            self.EPG.shutdown.value = False
        if self.EPG.shutdown.value:
            self.EPG.standby_afterwakeup.value = False
            self.EPG.repeat_import.value = 0
        # self.EPG.save()
        if self.prev_onlybouquet != config.plugins.epgimport.import_onlybouquet.value or (autoStartTimer is not None and autoStartTimer.prev_multibouquet != config.usage.multibouquet.value):
            EPGConfig.channelCache = {}
        self.save()
        # self.close(True)

    def save(self):
        if self["config"].isChanged():
            for x in self["config"].list:
                x[1].save()
            configfile.save()
            self.EPG.save()
            self.session.open(MessageBox, _("Settings saved successfully !"), MessageBox.TYPE_INFO, timeout=5)
        self.close(True)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.newConfig()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.newConfig()

    def keyOk(self):
        # ConfigListScreen.keyOK(self)
        sel = self["config"].getCurrent() and self["config"].getCurrent()[1]
        if sel == self.EPG.pathdb:
            self.setting = "pathdb"
            if hasattr(config.misc.epgcache_filename, 'value'):
                self.openDirectoryBrowser(self.EPG.pathdb.value, self.setting)
                print('new value=', self.EPG.pathdb.getValue())
            else:
                print("[EPGImport] Invalid configuration for epgcache_filename")

        elif sel == self.EPG.day_profile:
            self.session.open(EPGImportProfile)
        elif sel == self.EPG.shell_name:
            self.session.openWithCallback(self.textEditCallback, VirtualKeyBoard, text=self.EPG.shell_name.value)
        else:
            return

    def openDirectoryBrowser(self, path, itemcfg):
        # from Components.config import ConfigLocations
        try:
            # bookmarks = ConfigLocations(default=[config.misc.epgcache_filename.value]) if hasattr(config.misc.epgcache_filename, "value") else ConfigLocations()
            callback_map = {
                "pathdb": self.openDirectoryBrowserCB(config.misc.epgcache_filename),
            }
            if itemcfg in callback_map:
                self.session.openWithCallback(
                    callback_map[itemcfg],
                    LocationBox,
                    windowTitle=_("Choose Directory:"),
                    text=_("Choose directory"),
                    currDir=str(path),
                    bookmarks=config.movielist.videodirs,  # bookmarks,
                    autoAdd=True,
                    editDir=True,
                    inhibitDirs=["/bin", "/boot", "/dev", "/home", "/lib", "/proc", "/run", "/sbin", "/sys", "/usr", "/var"]
                )
        except Exception as e:
            print("[EPGImport] Error opening directory browser:", e)

    def openDirectoryBrowserCB(self, config_entry):
        def callback(path):
            if path is not None:
                pathz = os.path.join(path, 'epg.dat')
                print("epg path=:", pathz)
                self.EPG.pathdb.setValue(pathz)
        return callback

    def textEditCallback(self, callback=None):
        if callback is not None:
            self.EPG.shell_name.value = callback
            self.EPG.shell_name.save()
            self.createSetup()

    def updateStatus(self):
        text = ""
        global isFilterRunning, filterCounter
        if isFilterRunning == 1:
            text = self.filterStatusTemplate % (str(filterCounter))
        elif epgimport.isImportRunning():
            src = epgimport.source
            text = self.importStatusTemplate % (src.description, epgimport.eventCount)
        self["status"].setText(text)

        if lastImportResult and (lastImportResult != self.lastImportResult):
            start, count = lastImportResult
            try:
                # Assicurati che `start` sia un intero (timestamp)
                if isinstance(start, str):
                    start = time.mktime(time.strptime(start, "%Y-%m-%d %H:%M:%S"))
                elif not isinstance(start, (int, float)):
                    raise ValueError("Start value is not a valid timestamp or string")

                # Chiama FuzzyTime con il timestamp corretto
                d, t = FuzzyTime(int(start), inPast=True)
            except Exception as e:
                print("[EPGImport] Errore con FuzzyTime:", e)
                try:
                    d, t = FuzzyTime(int(start))
                except Exception as e:
                    print("[EPGImport] Fallito anche il fallback con FuzzyTime:", e)
                    d, t = _("unknown"), _("unknown")

            self["statusbar"].setText(_("Last: %s %s, %d events") % (d, t, count))
            self.lastImportResult = lastImportResult

    def keyInfo(self):
        self.session.open(MessageBox, _("Last import: %s events") % config.plugins.extra_epgimport.last_import.value, type=MessageBox.TYPE_INFO)

    def doimport(self, one_source=None):
        if epgimport.isImportRunning():
            print("[EPGImport] Already running, won't start again", file=log)
            self.session.open(MessageBox, _("EPGImport\nImport of epg data is still in progress. Please wait."), MessageBox.TYPE_ERROR, timeout=10, close_on_any_key=True)
            return
        if self.prev_onlybouquet != config.plugins.epgimport.import_onlybouquet.value or (autoStartTimer is not None and autoStartTimer.prev_multibouquet != config.usage.multibouquet.value):
            EPGConfig.channelCache = {}
        if one_source is None:
            cfg = EPGConfig.loadUserSettings()
        else:
            cfg = one_source
        sources = [s for s in EPGConfig.enumSources(CONFIG_PATH, filter=cfg["sources"])]
        EPGImport.ServerStatusList = {}
        if not sources:
            self.session.open(MessageBox, _("No active EPG sources found, nothing to do"), MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
            return
        # make it a stack, first on top.
        sources.reverse()
        epgimport.sources = sources
        self.session.openWithCallback(self.do_import_callback, MessageBox, _("EPGImport\nImport of epg data will start.\nThis may take a few minutes.\nIs this ok?"), MessageBox.TYPE_YESNO, timeout=15, default=True)

    def do_import_callback(self, confirmed):
        if not confirmed:
            return
        try:
            if config.plugins.epgimport.execute_shell.value and config.plugins.epgimport.shell_name.value:
                Console().eBatch([config.plugins.epgimport.shell_name.value], self.executeShellEnd, debug=True)
            else:
                startImport()
        except Exception as e:
            print("[EPGImport] Error at start:", e, file=log)
            self.session.open(MessageBox, _("EPGImport Plugin\nFailed to start:\n") + str(e), MessageBox.TYPE_ERROR, timeout=15, close_on_any_key=True)
        self.updateStatus()

    def executeShellEnd(self, *args, **kwargs):
        startImport()

    def dosources(self):
        self.session.openWithCallback(self.sourcesDone, EPGImportSources)

    def sourcesDone(self, confirmed, sources, cfg):
        # Called with True and list of config items on Okay.
        print("sourcesDone(): ", confirmed, sources, file=log)
        if cfg is not None:
            self.doimport(one_source=cfg)

    def openMenu(self):
        menu = [(_("Show log"), self.showLog)]
        if config.plugins.epgimport.loadepg_only.value == "default":
            menu.append((_("Ignore services list"), self.openIgnoreList))
        text = _("Select action")

        def setAction(choice):
            if choice:
                choice[1]()
        self.session.openWithCallback(setAction, ChoiceBox, title=text, list=menu)

    def openIgnoreList(self):
        self.session.open(filtersServices.filtersServicesSetup)

    def showLog(self):
        self.session.open(EPGImportLog)


class EPGImportSources(Screen):
    "Pick sources from config"
    skin = """
        <screen name="EPGImportSources" position="center,center" size="560,400" title="EPG Import Sources" >
            <ePixmap name="red" position="0,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
            <ePixmap name="green" position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
            <ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
            <ePixmap name="blue" position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
            <widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;17" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
            <widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;17" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
            <widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;17" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
            <widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;17" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
            <ePixmap alphatest="on" pixmap="skin_default/icons/clock.png" position="480,383" size="14,14" zPosition="3"/>
            <widget font="Regular;18" halign="left" position="505,380" render="Label" size="55,20" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
                <convert type="ClockToText">Default</convert>
            </widget>
            <widget name="list" position="10,40" size="540,336" scrollbarMode="showOnDemand" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.setTitle(_("EPG Import Sources"))
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Save"))
        self["key_blue"] = Button()
        cfg = EPGConfig.loadUserSettings()
        filter = cfg["sources"]
        tree = []
        cat = None
        for x in EPGConfig.enumSources(CONFIG_PATH, filter=None, categories=True):
            if hasattr(x, 'description'):
                sel = (filter is None) or (x.description in filter)
                entry = (x.description, x.description, sel)
                if cat is None:
                    # If no category defined, use a default one.
                    cat = ExpandableSelectionList.category("[.]")
                    tree.append(cat)
                cat[0][2].append(entry)
                if sel:
                    ExpandableSelectionList.expand(cat, True)
            else:
                cat = ExpandableSelectionList.category(x)
                tree.append(cat)
        self["list"] = ExpandableSelectionList.ExpandableSelectionList(tree, enableWrapAround=True)
        if tree:
            self["key_yellow"] = Button(_("Import"))
        else:
            self["key_yellow"] = Button()
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
                                         {"red": self.cancel,
                                          "green": self.save,
                                          "yellow": self.do_import,
                                          "save": self.save,
                                          "cancel": self.cancel,
                                          "ok": self["list"].toggleSelection}, -2)

    def save(self):
        # Make the entries unique through a set
        sources = list(set([item[1] for item in self["list"].enumSelected()]))
        print("[EPGImport] Selected sources:", sources, file=log)
        EPGConfig.storeUserSettings(sources=sources)
        self.close(True, sources, None)

    def cancel(self):
        self.close(False, None, None)

    def do_import(self):
        list = self["list"].list
        if list and len(list) > 0:
            try:
                idx = self["list"].getSelectedIndex()
                item = self["list"].list[idx][0]
                source = [item[1] or ""]
                cfg = {"sources": source}
                print("[EPGImport] Selected source: ", source, file=log)
            except Exception as e:
                print("[EPGImport] Error at selected source:", e, file=log)
            else:
                if cfg["sources"] != "":
                    self.close(False, None, cfg)


class EPGImportProfile(ConfigListScreen, Screen):
    skin = """
        <screen position="center,center" size="400,230" title="EPGImportProfile" >
            <widget name="config" position="0,0" size="400,180" scrollbarMode="showOnDemand" />
            <widget name="key_red" position="0,190" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;18" transparent="1"/>
            <widget name="key_green" position="140,190" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;18" transparent="1"/>
            <ePixmap name="red" position="0,190" zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
            <ePixmap name="green" position="140,190" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.setTitle(_("Days Profile"))
        self.list = []
        for i in range(7):
            self.list.append(getConfigListEntry(weekdays[i], config.plugins.extra_epgimport.day_import[i]))
        ConfigListScreen.__init__(self, self.list)
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Save"))
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
                                         {"red": self.keyCancel,
                                          "green": self.save,
                                          "save": self.save,
                                          "cancel": self.keyCancel,
                                          "ok": self.save}, -2)
        self.onLayoutFinish.append(self.setCustomTitle)

    def setCustomTitle(self):
        self.setTitle(_("Days Profile"))

    def save(self):
        if not config.plugins.extra_epgimport.day_import[0].value:
            if not config.plugins.extra_epgimport.day_import[1].value:
                if not config.plugins.extra_epgimport.day_import[2].value:
                    if not config.plugins.extra_epgimport.day_import[3].value:
                        if not config.plugins.extra_epgimport.day_import[4].value:
                            if not config.plugins.extra_epgimport.day_import[5].value:
                                if not config.plugins.extra_epgimport.day_import[6].value:
                                    self.session.open(MessageBox, _("You may not use this settings!\nAt least one day a week should be included!"), MessageBox.TYPE_INFO, timeout=6)
                                    return
        ConfigListScreen.keySave(self)
        """
        # for x in self["config"].list:
            # x[1].save()
        # self.close()
        """

    def cancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close()


class EPGImportLog(Screen):
    skin = """
        <screen position="center,center" size="560,400" title="EPG Import Log" >
            <ePixmap name="red" position="0,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
            <ePixmap name="green" position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
            <ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
            <ePixmap name="blue" position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
            <widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
            <widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
            <widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
            <widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
            <ePixmap alphatest="on" pixmap="skin_default/icons/clock.png" position="480,383" size="14,14" zPosition="3"/>
            <widget font="Regular;18" halign="left" position="505,380" render="Label" size="55,20" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
                <convert type="ClockToText">Default</convert>
            </widget>
            <widget name="list" position="10,40" size="540,340" />
        </screen>"""

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self.setTitle(_("EPG Import Log"))
        self.log = log
        self["key_red"] = Button(_("Clear"))
        self["key_green"] = Button()
        self["key_yellow"] = Button()
        self["key_blue"] = Button(_("Save"))
        self["list"] = ScrollLabel(self.log.getvalue())
        self["actions"] = ActionMap(["DirectionActions", "OkCancelActions", "ColorActions"],
                                    {"red": self.clear,
                                     "green": self.cancel,
                                     "yellow": self.cancel,
                                     "save": self.save,
                                     "blue": self.save,
                                     "cancel": self.cancel,
                                     "ok": self.cancel,
                                     "left": self["list"].pageUp,
                                     "right": self["list"].pageDown,
                                     "up": self["list"].pageUp,
                                     "down": self["list"].pageDown,
                                     "pageUp": self["list"].pageUp,
                                     "pageDown": self["list"].pageDown}, -2)

    def save(self):
        try:
            with open('/tmp/epgimport.log', 'w') as f:
                f.write(self.log.getvalue())(MessageBox, _("Write to /tmp/epgimport.log"), MessageBox.TYPE_INFO, timeout=5, close_on_any_key=True)
        except Exception as e:
            self["list"].setText("Failed to write /tmp/epgimport.log:str" + str(e))
        self.close(True)

    def cancel(self):
        self.close(False)

    def clear(self):
        self.log.logfile.write("")
        self.log.logfile.truncate()
        self.close(False)


class EPGImportDownloader(MessageBox):
    def __init__(self, session):
        MessageBox.__init__(self, session, _("Last import: ") + config.plugins.extra_epgimport.last_import.value + _(" events\n") + _("\nImport of epg data will start.\nThis may take a few minutes.\nIs this ok?"), MessageBox.TYPE_YESNO)
        self.skinName = "MessageBox"


def msgClosed(ret):
    global autoStartTimer
    if ret:
        if autoStartTimer is not None and not epgimport.isImportRunning():
            print("[EPGImport] Run manual starting import", file=log)
            autoStartTimer.runImport()


def start_import(session, **kwargs):
    session.openWithCallback(msgClosed, EPGImportDownloader)


def main(session, **kwargs):
    session.openWithCallback(doneConfiguring, EPGImportConfig)


def doneConfiguring(retval=False):
    if retval is True:
        if autoStartTimer is not None:
            autoStartTimer.update(clock=True)


def doneImport(reboot=False, epgfile=None):
    global _session, lastImportResult, BouquetChannelListList, serviceIgnoreList
    BouquetChannelListList = None
    serviceIgnoreList = None
    #
    timestamp = time.time()
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    lastImportResult = (formatted_time, epgimport.eventCount)
    # lastImportResult = (time.time(), epgimport.eventCount)
    try:
        start, count = lastImportResult
        # time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()
        # localtime = time.strftime('%d.%m.%Y - %H:%M:%S', (time.localtime(time.time())))
        localtime = time.asctime(time.localtime(time.time()))
        lastimport = "%s, %d" % (localtime, count)
        config.plugins.extra_epgimport.last_import.value = lastimport
        config.plugins.extra_epgimport.last_import.save()
        print("[EPGImport] Save last import date and count event", file=log)
    except:
        print("[EPGImport] Error to save last import date and count event", file=log)
    if reboot:
        if Screens.Standby.inStandby:
            print("[EPGImport] Restart enigma2", file=log)
            restartEnigma(True)
        else:
            msg = _("EPG Import finished, %d events") % epgimport.eventCount + "\n" + _("You must restart Enigma2 to load the EPG data,\nis this OK?")
            _session.openWithCallback(restartEnigma, MessageBox, msg, MessageBox.TYPE_YESNO, timeout=15, default=True)
            print("[EPGImport] Need restart enigma2", file=log)
    else:
        if config.plugins.epgimport.parse_autotimer.value and (fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/AutoTimer/plugin.pyo")) or fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/AutoTimer/plugin.pyc"))):
            try:
                from Plugins.Extensions.AutoTimer.plugin import autotimer
                if autotimer is None:
                    from Plugins.Extensions.AutoTimer.AutoTimer import AutoTimer
                    autotimer = AutoTimer()
                autotimer.readXml()
                checkDeepstandby(_session, parse=True)
                autotimer.parseEPGAsync(simulateOnly=False)
                print("[EPGImport] Run start parse autotimers", file=log)
            except:
                print("[EPGImport] Could not start autotimers", file=log)
                checkDeepstandby(_session, parse=False)
        else:
            checkDeepstandby(_session, parse=False)


class checkDeepstandby:
    def __init__(self, session, parse=False):
        self.session = session
        if config.plugins.epgimport.enabled.value:
            if parse:
                self.FirstwaitCheck = eTimer()
                self.FirstwaitCheck.callback.append(self.runCheckDeepstandby)
                self.FirstwaitCheck.startLongTimer(600)
                print("[EPGImport] Wait for parse autotimers 600 sec.", file=log)
            else:
                self.runCheckDeepstandby()

    def runCheckDeepstandby(self):
        print("[EPGImport] Run check deep standby after import")
        if config.plugins.epgimport.shutdown.value and config.plugins.epgimport.deepstandby.value == 'wakeup':
            if config.plugins.epgimport.deepstandby_afterimport.value and getFPWasTimerWakeup():
                config.plugins.epgimport.deepstandby_afterimport.value = False
                if Screens.Standby.inStandby and not self.session.nav.getRecordings() and not Screens.Standby.inTryQuitMainloop:
                    print("[EPGImport] Returning to deep standby after wake up for import", file=log)
                    self.session.open(Screens.Standby.TryQuitMainloop, 1)
                else:
                    print("[EPGImport] No return to deep standby, not standby or running recording", file=log)


def restartEnigma(confirmed):
    if not confirmed:
        return
        # save state of enigma, so we can return to previeus state
    if Screens.Standby.inStandby:
        try:
            open('/tmp/enigmastandby', 'wb').close()
        except:
            print("Failed to create /tmp/enigmastandby", file=log)
    else:
        try:
            os.remove("/tmp/enigmastandby")
        except:
            pass
    # now reboot
    _session.open(Screens.Standby.TryQuitMainloop, 3)


##################################
# Autostart section

class AutoStartTimer:
    def __init__(self, session):
        self.session = session
        self.prev_onlybouquet = config.plugins.epgimport.import_onlybouquet.value
        self.prev_multibouquet = config.usage.multibouquet.value
        self.clock = config.plugins.epgimport.wakeup.value
        self.autoStartImport = eTimer()
        self.autoStartImport.callback.append(self.onTimer)
        self.onceRepeatImport = eTimer()
        self.onceRepeatImport.callback.append(self.runImport)
        self.pauseAfterFinishImportCheck = eTimer()
        self.pauseAfterFinishImportCheck.callback.append(self.afterFinishImportCheck)
        self.pauseAfterFinishImportCheck.startLongTimer(30)
        self.container = None
        config.misc.standbyCounter.addNotifier(self.standbyCounterChangedRunImport)
        self.update()

    def getWakeTime(self):
        if config.plugins.epgimport.enabled.value:
            now = time.time()
            now = time.localtime(now)
            return int(time.mktime((now.tm_year, now.tm_mon, now.tm_mday, self.clock[0], self.clock[1], lastMACbyte() // 5, 0, now.tm_yday, now.tm_isdst)))
        else:
            return -1

    def update(self, atLeast=0, clock=False):
        self.autoStartImport.stop()
        if clock and self.clock != config.plugins.epgimport.wakeup.value:
            self.clock = config.plugins.epgimport.wakeup.value
            self.onceRepeatImport.stop()
        wake = self.getWakeTime()
        now_t = time.time()
        now = int(now_t)
        now_day = time.localtime(now_t)
        if wake > 0:
            cur_day = int(now_day.tm_wday)
            wakeup_day = WakeupDayOfWeek()
            if wakeup_day == -1:
                print("[EPGImport] wakeup day of week disabled", file=log)
                return -1
            if wake < now + atLeast:
                wake += 86400 * wakeup_day
            else:
                if not config.plugins.extra_epgimport.day_import[cur_day].value:
                    wake += 86400 * wakeup_day
            next = wake - now
            self.autoStartImport.startLongTimer(next)
        else:
            self.onceRepeatImport.stop()
            wake = -1
        now_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
        wake_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(wake)) if wake > 0 else "Not set"

        print("[EPGImport] WakeUpTime now set to", wake_str, "(now=%s)" % now_str, file=log)
        return wake

    def runImport(self):
        if self.prev_onlybouquet != config.plugins.epgimport.import_onlybouquet.value or self.prev_multibouquet != config.usage.multibouquet.value:
            self.prev_onlybouquet = config.plugins.epgimport.import_onlybouquet.value
            self.prev_multibouquet = config.usage.multibouquet.value
            EPGConfig.channelCache = {}
        cfg = EPGConfig.loadUserSettings()
        sources = [s for s in EPGConfig.enumSources(CONFIG_PATH, filter=cfg["sources"])]
        if sources:
            sources.reverse()
            epgimport.sources = sources
            if config.plugins.epgimport.execute_shell.value and config.plugins.epgimport.shell_name.value:
                if self.container:
                    del self.container
                self.container = eConsoleAppContainer()
                self.container.appClosed.append(self.executeShellEnd)
                if self.container.execute(config.plugins.epgimport.shell_name.value):
                    self.executeShellEnd(-1)
            else:
                startImport()

    def executeShellEnd(self, retval):
        if self.container:
            self.container.appClosed.remove(self.executeShellEnd)
            self.container = None
        startImport()

    def onTimer(self):
        self.autoStartImport.stop()
        now = int(time.time())
        print("[EPGImport] onTimer occured at", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now)), file=log)
        wake = self.getWakeTime()
        # If we're close enough, we're okay...
        atLeast = 0
        if wake - now < 60:
            self.runImport()
            repeat_time = config.plugins.epgimport.repeat_import.value
            if repeat_time:
                self.onceRepeatImport.startLongTimer(repeat_time * 3600)
                print("[EPGImport] start once repeat timer, wait in nours -", repeat_time, file=log)
            atLeast = 60
        self.update(atLeast)

    def getSources(self):
        cfg = EPGConfig.loadUserSettings()
        sources = [s for s in EPGConfig.enumSources(CONFIG_PATH, filter=cfg["sources"])]
        if sources:
            return True
        return False

    def getStatus(self):
        wake_up = self.getWakeTime()
        now_t = time.time()
        now = int(now_t)
        now_day = time.localtime(now_t)
        if wake_up > 0:
            cur_day = int(now_day.tm_wday)
            wakeup_day = WakeupDayOfWeek()
            if wakeup_day == -1:
                print("[EPGImport] wakeup day of week disabled", file=log)
                return -1
            if wake_up < now:
                wake_up += 86400 * wakeup_day
            else:
                if not config.plugins.extra_epgimport.day_import[cur_day].value:
                    wake_up += 86400 * wakeup_day
        else:
            wake_up = -1
        return wake_up

    def afterFinishImportCheck(self):
        if config.plugins.epgimport.deepstandby.value == 'wakeup' and getFPWasTimerWakeup():
            if os.path.exists("/tmp/enigmastandby") or os.path.exists("/tmp/.EPGImportAnswerBoot"):
                print("[EPGImport] is restart enigma2", file=log)
            else:
                wake = self.getStatus()
                now_t = time.time()
                now = int(now_t)
                if 0 < wake - now <= 60 * 5:
                    if config.plugins.epgimport.standby_afterwakeup.value:
                        if not Screens.Standby.inStandby:
                            Notifications.AddNotification(Screens.Standby.Standby)
                            print("[EPGImport] Run to standby after wake up", file=log)
                    if config.plugins.epgimport.shutdown.value:
                        if not config.plugins.epgimport.standby_afterwakeup.value:
                            if not Screens.Standby.inStandby:
                                Notifications.AddNotification(Screens.Standby.Standby)
                                print("[EPGImport] Run to standby after wake up for checking", file=log)
                        if not config.plugins.epgimport.deepstandby_afterimport.value:
                            config.plugins.epgimport.deepstandby_afterimport.value = True
                            self.wait_timer = eTimer()
                            self.wait_timer.timeout.get().append(self.startStandby)
                            print("[EPGImport] start wait_timer (10sec) for goto standby", file=log)
                            self.wait_timer.start(10000, True)

    def afterStandbyRunImport(self):
        if config.plugins.epgimport.run_after_standby.value:
            print("[EPGImport] start import after standby", file=log)
            self.runImport()

    def standbyCounterChangedRunImport(self, configElement):
        if Screens.Standby.inStandby:
            try:
                if self.afterStandbyRunImport not in Screens.Standby.inStandby.onClose:
                    Screens.Standby.inStandby.onClose.append(self.afterStandbyRunImport)
            except:
                print("[EPGImport] error inStandby.onClose append afterStandbyRunImport", file=log)

    def startStandby(self):
        if Screens.Standby.inStandby:
            print("[EPGImport] add checking standby", file=log)
            try:
                if self.onLeaveStandbyFinishImportCheck not in Screens.Standby.inStandby.onClose:
                    Screens.Standby.inStandby.onClose.append(self.onLeaveStandbyFinishImportCheck)
            except:
                print("[EPGImport] error inStandby.onClose append .onLeaveStandbyFinishImportCheck", file=log)

    def onLeaveStandbyFinishImportCheck(self):
        if config.plugins.epgimport.deepstandby_afterimport.value:
            config.plugins.epgimport.deepstandby_afterimport.value = False
            print("[EPGImport] checking standby remove, not deep standby after import", file=log)


def WakeupDayOfWeek():
    start_day = -1
    try:
        now = time.time()
        now_day = time.localtime(now)
        cur_day = int(now_day.tm_wday)
    except:
        cur_day = -1
    if cur_day >= 0:
        for i in (1, 2, 3, 4, 5, 6, 7):
            if config.plugins.extra_epgimport.day_import[(cur_day + i) % 7].value:
                return i
    return start_day


def onBootStartCheck():
    global autoStartTimer
    print("[EPGImport] onBootStartCheck", file=log)
    now = int(time.time())
    wake = autoStartTimer.getStatus()
    print("[EPGImport] now=%d wake=%d wake-now=%d" % (now, wake, wake - now), file=log)
    if (wake < 0) or (wake - now > 600):
        runboot = config.plugins.epgimport.runboot.value
        on_start = False
        if runboot == "1":
            on_start = True
            print("[EPGImport] is always boot", file=log)
        elif runboot == "2" and not getFPWasTimerWakeup():
            on_start = True
            print("[EPGImport] is manual boot", file=log)
        elif runboot == "3" and getFPWasTimerWakeup():
            on_start = True
            print("[EPGImport] is automatic boot", file=log)
        flag = '/tmp/.EPGImportAnswerBoot'
        if config.plugins.epgimport.runboot_restart.value:
            if os.path.exists(flag):
                on_start = False
                print("[EPGImport] not starting import - is restart enigma2", file=log)
            else:
                try:
                    open(flag, 'wb').close()
                except:
                    print("Failed to create /tmp/.EPGImportAnswerBoot", file=log)
        if config.plugins.epgimport.runboot_day.value:
            now = time.localtime()
            cur_day = int(now.tm_wday)
            if not config.plugins.extra_epgimport.day_import[cur_day].value:
                on_start = False
                print("[EPGImport] wakeup day of week does not match", file=log)
        if on_start:
            print("[EPGImport] starting import because auto-run on boot is enabled", file=log)
            autoStartTimer.runImport()
    else:
        print("[EPGImport] import to start in less than 10 minutes anyway, skipping...", file=log)


def autostart(reason, session=None, **kwargs):
    "called with reason=1 to during shutdown, with reason=0 at startup?"
    global autoStartTimer
    global _session
    if reason == 0 and _session is None:
        nms = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        # log.write("[EPGImport] autostart (%s) occured at (%s)" % (reason, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        # print("[EPGImport] autostart (%s) occured at" % reason, time.time(), file=log)
        print("[EPGImport] autostart (%s) occured at" % reason, nms, file=log)
        if session is not None:
            _session = session
            if autoStartTimer is None:
                autoStartTimer = AutoStartTimer(session)
            if config.plugins.epgimport.runboot.value != "4":
                onBootStartCheck()
        # If WE caused the reboot, put the box back in standby.
        if os.path.exists("/tmp/enigmastandby"):
            print("[EPGImport] Returning to standby", file=log)
            if not Screens.Standby.inStandby:
                Notifications.AddNotification(Screens.Standby.Standby)
            try:
                os.remove("/tmp/enigmastandby")
            except:
                pass


def getNextWakeup():
    "returns timestamp of next time when autostart should be called"
    if autoStartTimer:
        if config.plugins.epgimport.enabled.value and config.plugins.epgimport.deepstandby.value == 'wakeup' and autoStartTimer.getSources():
            print("[EPGImport] Will wake up from deep sleep", file=log)
            return autoStartTimer.getStatus()
    return -1

# we need this helper function to identify the descriptor


def run_from_epg_menu(menuid, **kwargs):
    if menuid == "epg" and config.plugins.epgimport.showinmainmenu.getValue():
        return [(_("NSS EPG Import"), main, "epgimporter", 90)]
    else:
        return []


def setExtensionsmenu(el):
    try:
        if el.value:
            Components.PluginComponent.plugins.addPlugin(extDescriptor)
        else:
            Components.PluginComponent.plugins.removePlugin(extDescriptor)
    except Exception as e:
        print("[EPGImport] Failed to update extensions menu:", e)


description = _("Automated EPG Importer")
config.plugins.epgimport.showinextensions.addNotifier(setExtensionsmenu, initial_call=False, immediate_feedback=False)
extDescriptor = PluginDescriptor(name=_("EPG import now"), description=description, where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=start_import)


def Plugins(**kwargs):
    result = [
        PluginDescriptor(name="NSS EPGImport", description=description, where=[PluginDescriptor.WHERE_AUTOSTART, PluginDescriptor.WHERE_SESSIONSTART], fnc=autostart, wakeupfnc=getNextWakeup),
        PluginDescriptor(name=_("NSS EPG Import"), description=description, where=[PluginDescriptor.WHERE_PLUGINMENU], icon="plugin.png", fnc=main),
        PluginDescriptor(name="NSS EPG importer", description=description, where=[PluginDescriptor.WHERE_MENU], fnc=run_from_epg_menu)
    ]
    if config.plugins.epgimport.showinextensions.value:
        result.append(extDescriptor)
    return result
