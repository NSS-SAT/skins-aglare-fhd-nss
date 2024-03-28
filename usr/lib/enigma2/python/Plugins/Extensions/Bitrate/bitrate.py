from enigma import eConsoleAppContainer, iServiceInformation
import platform
# edit from #lululla 20240315
based = platform.machine()
open('/tmp/based.txt', 'w').write(str(based))
if based == 'sh4':
    btrt = 'bitrate1_sh4 '
elif based == 'mips':
    btrt = 'bitrate1_mips '
elif based == 'aarch64':
    btrt = 'bitrate1_arm '
elif based == 'armv7l':
    btrt = 'bitrate_arm '
else:
    btrt = 'bitrate_mips '


class Bitrate:
    def __init__(self, session, refresh_func=None, finished_func=None):
        self.session = session
        self.refresh_func = refresh_func
        self.finished_func = finished_func
        self.remainingdata = ""
        self.running = False
        self.clearValues()
        self.datalines = []
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.appClosed)
        self.container.dataAvail.append(self.dataAvail)

    def start(self):
        if self.running:
            return
        service = self.session.nav.getCurrentService()
        if service:
            adapter = 0
            demux = 0
            try:
                stream = service.stream()
                if stream:
                    streamdata = stream.getStreamingData()
                    if streamdata:
                        if 'demux' in streamdata:
                            demux = streamdata["demux"]
                        if 'adapter' in streamdata:
                            adapter = streamdata["adapter"]
            except:
                pass
            info = service.info()
            vpid = info.getInfo(iServiceInformation.sVideoPID)
            apid = info.getInfo(iServiceInformation.sAudioPID)
            # cmd = "bitrate "
            cmd = btrt
            cmd += str(adapter)
            cmd += " "
            cmd += str(demux)
            cmd += " "
            cmd += str(vpid)
            cmd += " "
            cmd += str(apid)
            self.running = True
            self.container.execute(cmd)

    def clearValues(self):
        self.vmin = 0
        self.vmax = 0
        self.vavg = 0
        self.vcur = 0
        self.amin = 0
        self.amax = 0
        self.aavg = 0
        self.acur = 0

    def stop(self):
        self.container.kill()
        self.remainingdata = ""
        self.clearValues()
        self.running = False

    def appClosed(self, retval):
        self.remainingdata = ""
        self.clearValues()
        self.running = False
        if self.finished_func:
            self.finished_func(retval)

    def dataAvail(self, stri):
        # prepend any remaining data from the previous call
        if stri:
            strii = str(self.remainingdata) + str(stri)
            # split in lines
            newlines = strii.split('\n')
            # 'str' should end with '\n', so when splitting, the last line should be empty. If this is not the case, we received an incomplete line
            if len(newlines[-1]):
                # remember this data for next time
                self.remainingdata = newlines[-1]
                newlines = newlines[0:-1]
            else:
                self.remainingdata = ""

            for line in newlines:
                if len(line):
                    self.datalines.append(line)
            if len(self.datalines) >= 2:
                try:
                    self.vmin, self.vmax, self.vavg, self.vcur = self.datalines[0].split(' ')
                    self.amin, self.amax, self.aavg, self.acur = self.datalines[1].split(' ')
                except:
                    self.clearValues()
                self.datalines = []
                if self.refresh_func:
                    self.refresh_func()
