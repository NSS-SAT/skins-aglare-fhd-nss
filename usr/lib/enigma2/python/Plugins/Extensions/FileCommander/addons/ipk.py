#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from Components.PluginComponent import plugins
from Plugins.Extensions.FileCommander.addons.unarchiver import ArchiverMenuScreen, ArchiverInfoScreen
# commented aout
#from Screens.Console import Console
# added
from Plugins.Extensions.FileCommander.Console import Console
# commented out
# from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS
# added
from Plugins.Extensions.FileCommander.Directories import fileExists, resolveFilename, SCOPE_PLUGINS


# commented out
#shellquote
from Tools.Directories import shellquote
import subprocess

# for locale (gettext)
from . import _

pname = _("File Commander - ipk Addon")
pdesc = _("install/unpack ipk Files")
pversion = "0.2-r1"


class ipkMenuScreen(ArchiverMenuScreen):

	def __init__(self, session, sourcelist, targetlist):
		super(ipkMenuScreen, self).__init__(session, sourcelist, targetlist)

		self.skinName = "ArchiverMenuScreen"

		self.list.append((_("Show contents of ipk file"), 1))
		self.list.append((_("Install"), 4))

		self.pname = pname
		self.pdesc = pdesc
		self.pversion = pversion

	def unpackModus(self, id):
		if id == 1:
			# This is done in a subshell because using two
			# communicating Popen commands can deadlock on the
			# pipe output. Using communicate() avoids deadlock
			# on reading stdout and stderr from the pipe.
			fname = shellquote(self.sourceDir + self.filename)
			p = subprocess.Popen("ar -t %s > /dev/null 2>&1" % fname, shell=True)
			if p.wait():
				cmd = "tar -xOf %s ./data.tar.gz | tar -tzf -" % fname
			else:
				cmd = "ar -p %s data.tar.gz | tar -tzf -" % fname
			self.unpackPopen(cmd, UnpackInfoScreen)
		elif id == 4:
			self.ulist = []
			if fileExists("/usr/bin/opkg"):
				self.session.openWithCallback(self.doCallBack, Console, title=_("Installing Plugin ..."), cmdlist=(("opkg", "install", self.sourceDir + self.filename),))

	def doCallBack(self):
		if self.filename.startswith("enigma2-plugin-"):
			plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
		return


class UnpackInfoScreen(ArchiverInfoScreen):

	def __init__(self, session, list, sourceDir, filename):
		super(UnpackInfoScreen, self).__init__(session, list, sourceDir, filename)
		self.skinName = "ArchiverInfoScreen"
		self.pname = pname
		self.pdesc = pdesc
		self.pversion = pversion
