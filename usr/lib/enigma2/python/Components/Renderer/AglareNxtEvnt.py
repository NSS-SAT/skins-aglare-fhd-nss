from __future__ import absolute_import
from Components.Renderer.Renderer import Renderer
from enigma import eLabel, eEPGCache
from Components.VariableText import VariableText
from time import localtime

try:
    import sys
    if sys.version_info[0] == 3:
        from builtins import range
except:
    pass


class AglareNxtEvnt(Renderer, VariableText):

    def __init__(self):
        Renderer.__init__(self)
        VariableText.__init__(self)
        self.snglEvnt = 0
        self.epgcache = eEPGCache.getInstance()

    def applySkin(self, desktop, parent):
        attribs = self.skinAttributes[:]
        for attrib, value in self.skinAttributes:
            if attrib == 'nxtEvents':
                self.nxEvnt = value
            if attrib == 'snglEvent':
                self.snglEvnt = value

        self.skinAttributes = attribs
        return Renderer.applySkin(self, desktop, parent)

    GUI_WIDGET = eLabel

    def changed(self, what):
        self.text = ''
        try:
            ref = self.source.service
            if ref:
                events = self.epgcache.lookupEvent(['IBDCT', (ref.toString(),
                                                              0,
                                                              -1,
                                                              1200)])
                if events and self.snglEvnt == '':
                    for i in range(int(self.nxEvnt)):
                        evnts = events[i + 1][4]
                        bt = localtime(events[i + 1][1])
                        self.text = '%s %02d:%02d - %s\n' % (self.text,
                                                             bt[3],
                                                             bt[4],
                                                             evnts)

                if events and self.snglEvnt != '':
                    evnts = events[int(self.snglEvnt)][4]
                    bt = localtime(events[int(self.snglEvnt)][1])
                    self.text = '%s %02d:%02d - %s\n' % (self.text,
                                                         bt[3],
                                                         bt[4],
                                                         evnts)
                else:
                    return ''
            else:
                return ''
        except:
            return ''
