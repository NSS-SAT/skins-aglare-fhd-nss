#!/usr/bin/python
# -*- coding: utf-8 -*-

# by digiteng
# v1 07.2020, 11.2021
# recode from lululla 2022
# for channellist
# <widget source="ServiceEvent" render="AglareStarX" position="750,390" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
# or
# <widget source="ServiceEvent" render="AglareStarX" pixmap="xtra/star.png" position="750,390" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
# edit lululla 05-2022
# <ePixmap pixmap="oZeta-FHD/star.png" position="136,104" size="200,20" alphatest="blend" zPosition="10" transparent="1" />
# <widget source="session.Event_Now" render="AglareStarX" pixmap="oZeta-FHD/menu/staryellow.png" position="560,367" size="200,20" alphatest="blend" transparent="1" zPosition="3" />
# <ePixmap pixmap="menu/stargrey.png" position="136,104" size="200,20" alphatest="blend" zPosition="10" transparent="1" />
# <widget source="session.Event_Next" render="AglareStarX" pixmap="oZeta-FHD/menu/staryellow.png" position="560,367" size="200,20" alphatest="blend" transparent="1" zPosition="3" />

from __future__ import print_function
from Components.Renderer.Renderer import Renderer
from Components.Sources.Event import Event
from Components.Sources.EventInfo import EventInfo
from Components.Sources.ServiceEvent import ServiceEvent
from Components.VariableValue import VariableValue
from Components.config import config
from six import text_type
from enigma import (eSlider, eTimer)
import json
import os
import re
import socket
import sys

from re import search, sub, I, S, escape

global cur_skin, my_cur_skin, tmdb_api
PY3 = False
if sys.version_info[0] >= 3:
    PY3 = True
    from urllib.request import urlopen
    from urllib.error import HTTPError, URLError
    from urllib.parse import quote_plus
else:
    from urllib2 import urlopen
    from urllib2 import HTTPError, URLError
    from urllib import quote_plus


try:
    from urllib import unquote, quote
except ImportError:
    from urllib.parse import unquote, quote


try:
    lng = config.osd.language.value
    lng = lng[:-3]
except:
    lng = 'en'
    pass
print('language: ', lng)


formatImg = 'w185'
tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
omdb_api = "cb1d9f55"
thetvdbkey = 'D19315B88B2DE21F'
# thetvdbkey = "a99d487bb3426e5f3a60dea6d3d3c7ef"


def isMountReadonly(mnt):
    mount_point = ''
    with open('/proc/mounts') as f:
        for line in f:
            line = line.split(',')[0]
            line = line.split()
            print('line ', line)
            try:
                device, mount_point, filesystem, flags = line
            except Exception as err:
                print("Error: %s" % err)
            if mount_point == mnt:
                return 'ro' in flags
    return "mount: '%s' doesn't exist" % mnt


def isMountedInRW(path):
    testfile = path + '/tmp-rw-test'
    os.system('touch ' + testfile)
    if os.path.exists(testfile):
        os.system('rm -f ' + testfile)
        return True
    return False


my_cur_skin = False
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
path_folder = "/tmp/poster"
if os.path.exists("/media/hdd"):
    if isMountedInRW("/media/hdd"):
        path_folder = "/media/hdd/poster"
elif os.path.exists("/media/usb"):
    if isMountedInRW("/media/usb"):
        path_folder = "/media/usb/poster"
elif os.path.exists("/media/mmc"):
    if isMountedInRW("/media/mmc"):
        path_folder = "/media/mmc/poster"

if not os.path.exists(path_folder):
    os.makedirs(path_folder)


try:
    if my_cur_skin is False:
        skin_paths = {
            "tmdb_api": "/usr/share/enigma2/{}/apikey".format(cur_skin),
            "omdb_api": "/usr/share/enigma2/{}/omdbkey".format(cur_skin),
            "thetvdbkey": "/usr/share/enigma2/{}/thetvdbkey".format(cur_skin)
        }
        for key, path in skin_paths.items():
            if os.path.exists(path):
                with open(path, "r") as f:
                    value = f.read().strip()
                    if key == "tmdb_api":
                        tmdb_api = value
                    elif key == "omdb_api":
                        omdb_api = value
                    elif key == "thetvdbkey":
                        thetvdbkey = value
                my_cur_skin = True
except Exception as e:
    print("Errore nel caricamento delle API:", str(e))
    my_cur_skin = False


def checkRedirect(url):
    # print("*** check redirect ***")
    import requests
    from requests.adapters import HTTPAdapter, Retry
    hdr = {"User-Agent": "Enigma2 - Enigma2 Plugin"}
    content = None
    retries = Retry(total=1, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retries)
    http = requests.Session()
    http.mount("http://", adapter)
    http.mount("https://", adapter)
    try:
        r = http.get(url, headers=hdr, timeout=(10, 30), verify=False)
        r.raise_for_status()
        if r.status_code == requests.codes.ok:
            try:
                content = r.json()
            except Exception as e:
                print('zstar checkRedirect error:', e)
        # return content
    except Exception as e:
        print('next ret: ', e)
    return content


def OnclearMem():
    try:
        os.system('sync')
        os.system('echo 1 > /proc/sys/vm/drop_caches')
        os.system('echo 2 > /proc/sys/vm/drop_caches')
        os.system('echo 3 > /proc/sys/vm/drop_caches')
    except:
        pass


def quoteEventName(eventName):
    try:
        text = eventName.decode('utf8').replace(u'\x86', u'').replace(u'\x87', u'').encode('utf8')
    except:
        text = eventName
    return quote_plus(text, safe="+")


REGEX = re.compile(
    r'[\(\[].*?[\)\]]|'                    # Parentesi tonde o quadre
    r':?\s?odc\.\d+|'                      # odc. con o senza numero prima
    r'\d+\s?:?\s?odc\.\d+|'                # numero con odc.
    r'[:!]|'                               # due punti o punto esclamativo
    r'\s-\s.*|'                            # trattino con testo successivo
    r',|'                                  # virgola
    r'/.*|'                                # tutto dopo uno slash
    r'\|\s?\d+\+|'                         # | seguito da numero e +
    r'\d+\+|'                              # numero seguito da +
    r'\s\*\d{4}\Z|'                        # * seguito da un anno a 4 cifre
    r'[\(\[\|].*?[\)\]\|]|'                # Parentesi tonde, quadre o pipe
    r'(?:\"[\.|\,]?\s.*|\"|'               # Testo tra virgolette
    r'\.\s.+)|'                            # Punto seguito da testo
    r'Премьера\.\s|'                       # Specifico per il russo
    r'[хмтдХМТД]/[фс]\s|'                  # Pattern per il russo con /ф o /с
    r'\s[сС](?:езон|ерия|-н|-я)\s.*|'      # Stagione o episodio in russo
    r'\s\d{1,3}\s[чсЧС]\.?\s.*|'           # numero di parte/episodio in russo
    r'\.\s\d{1,3}\s[чсЧС]\.?\s.*|'         # numero di parte/episodio in russo con punto
    r'\s[чсЧС]\.?\s\d{1,3}.*|'             # Parte/Episodio in russo
    r'\d{1,3}-(?:я|й)\s?с-н.*',            # Finale con numero e suffisso russo
    re.DOTALL)


def intCheck():
    try:
        response = urlopen("http://google.com", None, 5)
        response.close()
    except HTTPError:
        return False
    except URLError:
        return False
    except socket.timeout:
        return False
    return True


def remove_accents(string):
    if not isinstance(string, text_type):
        string = text_type(string, 'utf-8')
    string = re.sub(u"[àáâãäå]", 'a', string)
    string = re.sub(u"[èéêë]", 'e', string)
    string = re.sub(u"[ìíîï]", 'i', string)
    string = re.sub(u"[òóôõö]", 'o', string)
    string = re.sub(u"[ùúûü]", 'u', string)
    string = re.sub(u"[ýÿ]", 'y', string)
    return string


def unicodify(s, encoding='utf-8', norm=None):
    if not isinstance(s, text_type):
        s = text_type(s, encoding)
    if norm:
        from unicodedata import normalize
        s = normalize(norm, s)
    return s


def str_encode(text, encoding="utf8"):
    if not PY3:
        if isinstance(text, text_type):
            return text.encode(encoding)
    return text


def cutName(eventName=""):
    if eventName:
        eventName = eventName.replace('"', '').replace('.', '').replace(' | ', '')  # .replace('Х/Ф', '').replace('М/Ф', '').replace('Х/ф', '')
        eventName = eventName.replace('(18+)', '').replace('18+', '').replace('(16+)', '').replace('16+', '').replace('(12+)', '')
        eventName = eventName.replace('12+', '').replace('(7+)', '').replace('7+', '').replace('(6+)', '').replace('6+', '')
        eventName = eventName.replace('(0+)', '').replace('0+', '').replace('+', '')
        eventName = eventName.replace('مسلسل', '')
        eventName = eventName.replace('فيلم وثائقى', '')
        eventName = eventName.replace('حفل', '')
        return eventName
    return ""


def getCleanTitle(eventitle=""):
    # save_name = re.sub('\\(\d+\)$', '', eventitle)
    # save_name = re.sub('\\(\d+\/\d+\)$', '', save_name)  # remove episode-number " (xx/xx)" at the end
    # # save_name = re.sub('\ |\?|\.|\,|\!|\/|\;|\:|\@|\&|\'|\-|\"|\%|\(|\)|\[|\]\#|\+', '', save_name)
    save_name = eventitle.replace(' ^`^s', '').replace(' ^`^y', '')
    return save_name


def dataenc(data):
    if PY3:
        data = data.decode("utf-8")
    else:
        data = data.encode("utf-8")
    return data


def sanitize_filename(filename):
    # Replace spaces with underscores and remove invalid characters (like ':')
    sanitized = re.sub(r'[^\w\s-]', '', filename)  # Remove invalid characters
    # sanitized = sanitized.replace(' ', '_')      # Replace spaces with underscores
    # sanitized = sanitized.replace('-', '_')      # Replace dashes with underscores
    return sanitized.strip()


def convtext(text=''):
    try:
        if text is None:
            print('return None original text: ' + str(type(text)))
            return
        if text == '': 
            print('text is an empty string')
        else:
            print('original text:' + text)
            text = text.lower()
            print('lowercased text:' + text)
            text = text.lstrip()
            
            # text = cutName(text)
            # text = getCleanTitle(text)

            if text.endswith("the"):
                text = "the " + text[:-4]
            
            # Modifiche personalizzate
            if 'giochi olimpici parigi' in text:
                text = 'olimpiadi di parigi'
            if 'bruno barbieri' in text:
                text = text.replace('bruno barbieri', 'brunobarbierix')
            if "anni '60" in text:
                text = "anni 60"
            if 'tg regione' in text:
                text = 'tg3'
            if 'studio aperto' in text:
                text = 'studio aperto'
            if 'josephine ange gardien' in text:
                text = 'josephine ange gardien'
            if 'elementary' in text:
                text = 'elementary'
            if 'squadra speciale cobra 11' in text:
                text = 'squadra speciale cobra 11'
            if 'criminal minds' in text:
                text = 'criminal minds'
            if 'i delitti del barlume' in text:
                text = 'i delitti del barlume'
            if 'senza traccia' in text:
                text = 'senza traccia'
            if 'hudson e rex' in text:
                text = 'hudson e rex'
            if 'ben-hur' in text:
                text = 'ben-hur'
            if 'alessandro borghese - 4 ristoranti' in text:
                text = 'alessandroborgheseristoranti'
            if 'alessandro borghese: 4 ristoranti' in text:
                text = 'alessandroborgheseristoranti' 

            cutlist = ['x264', '720p', '1080p', '1080i', 'pal', 'german', 'english', 'ws', 'dvdrip', 'unrated',
                       'retail', 'web-dl', 'dl', 'ld', 'mic', 'md', 'dvdr', 'bdrip', 'bluray', 'dts', 'uncut', 'anime',
                       'ac3md', 'ac3', 'ac3d', 'ts', 'dvdscr', 'complete', 'internal', 'dtsd', 'xvid', 'divx', 'dubbed',
                       'line.dubbed', 'dd51', 'dvdr9', 'dvdr5', 'h264', 'avc', 'webhdtvrip', 'webhdrip', 'webrip',
                       'webhdtv', 'webhd', 'hdtvrip', 'hdrip', 'hdtv', 'ituneshd', 'repack', 'sync', '1^tv', '1^ tv',
                       '1^ visione rai', '1^ visione', ' - prima tv', ' - primatv', 'prima visione',
                       'film -', 'de filippi', 'first screening',
                       'live:', 'new:', 'film:', 'première diffusion', 'nouveau:', 'en direct:', 
                       'premiere:', 'estreno:', 'nueva emisión:', 'en vivo:'
                       ]
            for word in cutlist:
                text = text.replace(word, '')
            text = ' '.join(text.split())
            print(text)

            text = cutName(text)
            text = getCleanTitle(text)

            text = text.partition("-")[0]  # Mantieni solo il testo prima del primo "-"

            # Pulizia finale
            text = text.replace('.', ' ').replace('-', ' ').replace('_', ' ').replace('+', '')

            # Rimozione pattern specifici
            if search(r'[Ss][0-9]+[Ee][0-9]+', text):
                text = sub(r'[Ss][0-9]+[Ee][0-9]+.*[a-zA-Z0-9_]+', '', text, flags=S | I)
            text = sub(r'\(.*\)', '', text).rstrip()
            text = text.partition("(")[0]
            text = sub(r"\\s\d+", "", text)
            text = text.partition(":")[0]
            text = re.sub(r'(odc.\s\d+)+.*?FIN', '', text)
            text = re.sub(r'(odc.\d+)+.*?FIN', '', text)
            text = re.sub(r'(\d+)+.*?FIN', '', text)
            text = re.sub('FIN', '', text)

            # Rimuovi accenti e normalizza
            text = remove_accents(text)
            print('remove_accents text: ' + text)

            # Forzature finali
            text = text.replace('XXXXXX', '60')
            text = text.replace('brunobarbierix', 'bruno barbieri - 4 hotel')
            text = text.replace('alessandroborgheseristoranti', 'alessandro borghese - 4 ristoranti')
            text = text.replace('il ritorno di colombo', 'colombo')

            # text = sanitize_filename(text)
            # print('sanitize_filename text: ' + text)
            return text.capitalize()
    except Exception as e:
        print('convtext error: ' + str(e))
        pass


def convtextPAUSED(text=''):
    text = text.lower()
    print('text lower init=', text)
    text = text.lstrip()
    text = text.replace("\xe2\x80\x93", "").replace('\xc2\x86', '').replace('\xc2\x87', '')  # replace special
    if 'bruno barbieri' in text:
        text = text.replace('bruno barbieri', 'brunobarbierix')
    if "anni '60" in text:
        text = "anni 60"
    if 'tg regione' in text:
        text = 'tg3'
    if 'studio aperto' in text:
        text = 'studio aperto'
    if 'josephine ange gardien' in text:
        text = 'josephine ange gardien'
    if 'elementary' in text:
        text = 'elementary'
    if 'squadra speciale cobra 11' in text:
        text = 'squadra speciale cobra 11'
    if 'criminal minds' in text:
        text = 'criminal minds'
    if 'i delitti del barlume' in text:
        text = 'i delitti del barlume'
    if 'senza traccia' in text:
        text = 'senza traccia'
    if 'hudson e rex' in text:
        text = 'hudson e rex'
    if 'ben-hur' in text:
        text = 'ben-hur'
    if 'la7 ' in text:
        text = 'la7'
    if 'skytg24' in text:
        text = 'skytg24'
    cutlist = ['x264', '720p', '1080p', '1080i', 'pal', 'german', 'english', 'ws', 'dvdrip', 'unrated',
               'retail', 'web-dl', 'dl', 'ld', 'mic', 'md', 'dvdr', 'bdrip', 'bluray', 'dts', 'uncut', 'anime',
               'ac3md', 'ac3', 'ac3d', 'ts', 'dvdscr', 'complete', 'internal', 'dtsd', 'xvid', 'divx', 'dubbed',
               'line.dubbed', 'dd51', 'dvdr9', 'dvdr5', 'h264', 'avc', 'webhdtvrip', 'webhdrip', 'webrip',
               'webhdtv', 'webhd', 'hdtvrip', 'hdrip', 'hdtv', 'ituneshd', 'repack', 'sync', '1^tv', '1^ tv',
               '1^ visione rai', '1^ visione', ' - prima tv', ' - primatv', 'prima visione',
               'film -', 'de filippi', 'first screening', 'premiere:', 'live:', 'new:', 
               'première diffusion', 'nouveau:', 'en direct:',
               'estreno:', 'nueva emisión:', 'en vivo:']
    text = text.replace('.wmv', '').replace('.flv', '').replace('.ts', '').replace('.m2ts', '').replace('.mkv', '').replace('.avi', '').replace('.mpeg', '').replace('.mpg', '').replace('.iso', '').replace('.mp4', '')

    for word in cutlist:
        text = sub(r'(\_|\-|\.|\+)' + escape(word.lower()) + r'(\_|\-|\.|\+)', '+', text, flags=I)
    text = text.replace('.', ' ').replace('-', ' ').replace('_', ' ').replace('+', '').replace(" Director's Cut", "").replace(" director's cut", "").replace("[Uncut]", "").replace("Uncut", "")

    text_split = text.split()
    if text_split and text_split[0].lower() in ("new:", "live:"):
        text_split.pop(0)  # remove annoying prefixes
    text = " ".join(text_split)

    if search(r'[Ss][0-9]+[Ee][0-9]+', text):
        text = sub(r'[Ss][0-9]+[Ee][0-9]+.*[a-zA-Z0-9_]+', '', text, flags=S | I)
    text = sub(r'\(.*\)', '', text).rstrip()  # remove episode number from series, like "series name (234)"

    # # List of bad strings to remove
    # bad_strings = [
        # "ae|", "al|", "ar|", "at|", "ba|", "be|", "bg|", "br|", "cg|", "ch|", "cz|", "da|", "de|", "dk|",
        # "ee|", "en|", "es|", "eu|", "ex-yu|", "fi|", "fr|", "gr|", "hr|", "hu|", "in|", "ir|", "it|", "lt|",
        # "mk|", "mx|", "nl|", "no|", "pl|", "pt|", "ro|", "rs|", "ru|", "se|", "si|", "sk|", "sp|", "tr|",
        # "uk|", "us|", "yu|",
        # "1080p-dual-lat-cine-calidad.com", "1080p-dual-lat-cine-calidad.com-1",
        # "1080p-dual-lat-cinecalidad.mx", "1080p-lat-cine-calidad.com", "1080p-lat-cine-calidad.com-1",
        # "1080p-lat-cinecalidad.mx", "1080p.dual.lat.cine-calidad.com", "3d", "'", "#", "[]",  # "/", "(", ")", "-",
        # "4k", "aac", "blueray", "ex-yu:", "fhd", "hd", "hdrip", "hindi", "imdb", "multi:", "multi-audio",
        # "multi-sub", "multi-subs", "multisub", "ozlem", "sd", "top250", "u-", "uhd", "vod", "x264"
    # ]

    # # Remove numbers from 1900 to 2030
    # bad_strings.extend(map(str, range(1900, 2030)))
    # # Construct a regex pattern to match any of the bad strings
    # bad_strings_pattern = re.compile('|'.join(map(re.escape, bad_strings)))
    # # Remove bad strings using regex pattern
    # text = bad_strings_pattern.sub('', text)
    # # List of bad suffixes to remove
    # bad_suffix = [
        # " al", " ar", " ba", " da", " de", " en", " es", " eu", " ex-yu", " fi", " fr", " gr", " hr", " mk",
        # " nl", " no", " pl", " pt", " ro", " rs", " ru", " si", " swe", " sw", " tr", " uk", " yu"
    # ]
    # # Construct a regex pattern to match any of the bad suffixes at the end of the string
    # bad_suffix_pattern = re.compile(r'(' + '|'.join(map(re.escape, bad_suffix)) + r')$')
    # # Remove bad suffixes using regex pattern
    # text = bad_suffix_pattern.sub('', text)
    # # Replace ".", "_", "'" with " "
    # text = re.sub(r'[._\']', ' ', text)

    text = text.partition("-")[0]

    text = remove_accents(text)
    print('remove_accents text:', text)

    text = text + 'FIN'
    text = re.sub(r'(odc.\s\d+)+.*?FIN', '', text)
    text = re.sub(r'(odc.\d+)+.*?FIN', '', text)
    text = re.sub(r'(\d+)+.*?FIN', '', text)
    text = text.partition("(")[0]
    text = re.sub(r"\\s\d+", "", text)
    text = re.sub('FIN', '', text)

    text = sanitize_filename(text)
    print('sanitize_filename text:', text)

    # forced
    text = text.replace('XXXXXX', '60')
    text = text.replace('brunobarbierix', 'bruno barbieri - 4 hotel')

    text = quote(text, safe="")
    print('text final:', text)
    return unquote(text).capitalize()


def convtextxx(text=''):
    try:
        if text is None:
            print('return None original text: ', type(text))
            return  # Esci dalla funzione se text è None
        if text == '':
            print('text is an empty string')
        else:
            print('original text: ', text)
            text = text.lower()
            print('lowercased text: ', text)
            text = text.lstrip()
            # #
            text = cutName(text)
            text = getCleanTitle(text)
            # #
            if text.endswith("the"):
                text = "the " + text[:-4]

            # text = re.sub(r'^\w{4}:', '', text)

            text_split = text.split()
            if text_split and text_split[0].lower() in ("new:", "live:"):
                text_split.pop(0)  # remove annoying prefixes
            text = " ".join(text_split)

            text = text.replace("\xe2\x80\x93", "").replace('\xc2\x86', '').replace('\xc2\x87', '')  # replace special
            text = text.replace('1^ visione rai', '').replace('1^ visione', ''.replace(' - prima tv', '')).replace('primatv', '')
            text = text.replace('prima visione', '').replace('1^tv', '').replace('1^ tv', '')
            text = text.replace('live:', '').replace('new:', '').replace('((', '(').replace('))', ')')
            if 'giochi olimpici parigi' in text:
                text = 'olimpiadi di parigi'
            if 'bruno barbieri' in text:
                text = text.replace('bruno barbieri', 'brunobarbierix')
            if "anni '60" in text:
                text = "anni 60"
            if 'tg regione' in text:
                text = 'tg3'
            if 'studio aperto' in text:
                text = 'studio aperto'
            if 'josephine ange gardien' in text:
                text = 'josephine ange gardien'
            if 'elementary' in text:
                text = 'elementary'
            if 'squadra speciale cobra 11' in text:
                text = 'squadra speciale cobra 11'
            if 'criminal minds' in text:
                text = 'criminal minds'
            if 'i delitti del barlume' in text:
                text = 'i delitti del barlume'
            if 'senza traccia' in text:
                text = 'senza traccia'
            if 'hudson e rex' in text:
                text = 'hudson e rex'
            if 'ben-hur' in text:
                text = 'ben-hur'
            if 'la7 ' in text:
                text = 'la7'
            if 'skytg24' in text:
                text = 'skytg24'
            # remove xx: at start
            text = re.sub(r'^\w{2}:', '', text)
            # remove xx|xx at start
            text = re.sub(r'^\w{2}\|\w{2}\s', '', text)
            # remove xx - at start
            text = re.sub(r'^.{2}\+? ?- ?', '', text)
            # remove all leading content between and including ||
            text = re.sub(r'^\|\|.*?\|\|', '', text)
            text = re.sub(r'^\|.*?\|', '', text)
            # remove everything left between pipes.
            text = re.sub(r'\|.*?\|', '', text)
            # remove all content between and including () multiple times
            text = re.sub(r'\(\(.*?\)\)|\(.*?\)', '', text)
            # remove all content between and including [] multiple times
            text = re.sub(r'\[\[.*?\]\]|\[.*?\]', '', text)
            # remove episode number in arabic series
            text = re.sub(r' +ح', '', text)
            # remove season number in arabic series
            text = re.sub(r' +ج', '', text)
            # remove season number in arabic series
            text = re.sub(r' +م', '', text)
            # List of bad strings to remove
            bad_strings = [
                "ae|", "al|", "ar|", "at|", "ba|", "be|", "bg|", "br|", "cg|", "ch|", "cz|", "da|", "de|", "dk|",
                "ee|", "en|", "es|", "eu|", "ex-yu|", "fi|", "fr|", "gr|", "hr|", "hu|", "in|", "ir|", "it|", "lt|",
                "mk|", "mx|", "nl|", "no|", "pl|", "pt|", "ro|", "rs|", "ru|", "se|", "si|", "sk|", "sp|", "tr|",
                "uk|", "us|", "yu|",
                "1080p", "1080p-dual-lat-cine-calidad.com", "1080p-dual-lat-cine-calidad.com-1",
                "1080p-dual-lat-cinecalidad.mx", "1080p-lat-cine-calidad.com", "1080p-lat-cine-calidad.com-1",
                "1080p-lat-cinecalidad.mx", "1080p.dual.lat.cine-calidad.com", "3d", "'", "#", "[]",  # "/", "(", ")", "-",
                "4k", "720p", "aac", "blueray", "ex-yu:", "fhd", "hd", "hdrip", "hindi", "imdb", "multi:", "multi-audio",
                "multi-sub", "multi-subs", "multisub", "ozlem", "sd", "top250", "u-", "uhd", "vod", "x264"
            ]

            # Remove numbers from 1900 to 2030
            bad_strings.extend(map(str, range(1900, 2030)))
            # Construct a regex pattern to match any of the bad strings
            bad_strings_pattern = re.compile('|'.join(map(re.escape, bad_strings)))
            # Remove bad strings using regex pattern
            text = bad_strings_pattern.sub('', text)
            # List of bad suffixes to remove
            bad_suffix = [
                " al", " ar", " ba", " da", " de", " en", " es", " eu", " ex-yu", " fi", " fr", " gr", " hr", " mk",
                " nl", " no", " pl", " pt", " ro", " rs", " ru", " si", " swe", " sw", " tr", " uk", " yu"
            ]
            # Construct a regex pattern to match any of the bad suffixes at the end of the string
            bad_suffix_pattern = re.compile(r'(' + '|'.join(map(re.escape, bad_suffix)) + r')$')
            # Remove bad suffixes using regex pattern
            text = bad_suffix_pattern.sub('', text)
            # Replace ".", "_", "'" with " "
            text = re.sub(r'[._\']', ' ', text)
            # recoded lulu
            text = text + 'FIN'
            '''
            if re.search(r'[Ss][0-9][Ee][0-9]+.*?FIN', text):
                text = re.sub(r'[Ss][0-9][Ee][0-9]+.*?FIN', '', text)
            if re.search(r'[Ss][0-9] [Ee][0-9]+.*?FIN', text):
                text = re.sub(r'[Ss][0-9] [Ee][0-9]+.*?FIN', '', text)
            '''
            text = re.sub(r'(odc.\s\d+)+.*?FIN', '', text)
            text = re.sub(r'(odc.\d+)+.*?FIN', '', text)
            text = re.sub(r'(\d+)+.*?FIN', '', text)
            text = text.partition("(")[0] + 'FIN'
            text = re.sub(r"\\s\d+", "", text)
            text = text.partition("(")[0]
            # text = text.partition(":")[0]  # not work on csi: new york (only-->  csi)
            text = text.partition(" -")[0]
            text = re.sub(' - +.+?FIN', '', text)  # all episodes and series ????
            text = re.sub('FIN', '', text)
            text = re.sub(r"[\<\>\:\"\/\\\|\?\*!]", "_", str(text))
            # text = re.sub(r'^\|[\w\-\|]*\|', '', text)
            text = re.sub(r"[-,?!+/\.\":]", '', text)  # replace (- or , or ! or / or . or " or :) by space
            # recoded  end
            text = text.strip(' -')

            text = remove_accents(text)
            print('remove_accents text: ', text)

            # forced
            text = text.replace('XXXXXX', '60')
            text = text.replace('brunobarbierix', 'bruno barbieri - 4 hotel')
            text = quote(text, safe="")
            print('text safe: ', text)
        return unquote(text).capitalize()
    except Exception as e:
        print('convtext error: ', e)
        pass


class AglareStarX(VariableValue, Renderer):

    def __init__(self):
        adsl = intCheck()
        if not adsl:
            return
        Renderer.__init__(self)
        VariableValue.__init__(self)
        self.__start = 0
        self.__end = 100
        self.text = ""
        self.timer30 = eTimer()

    GUI_WIDGET = eSlider

    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            (self.range, self.value) = ((0, 1), 0)
            return
        if what[0] != self.CHANGED_CLEAR:
            print('zstar event B what[0] != self.CHANGED_CLEAR')
            if self.instance:
                self.instance.hide()
            self.infos()

    def infos(self):
        try:
            rating = 0
            max_range = 100
            value = 0
            ImdbRating = "0"
            ids = None
            data = ""
            
            self.event = self.source.event
            if self.event and self.event != "None":
                self.evnt = self.event.getEventName().replace("\xc2\x86", "").replace("\xc2\x87", "")
                self.evntNm = convtext(self.evnt)
                dwn_infos = "{}/{}".format(path_folder, self.evntNm)
                
                if not os.path.exists(dwn_infos):
                    OnclearMem()
                    try:
                        url = "http://api.themoviedb.org/3/search/multi?api_key={}&query={}".format(
                            str(tmdb_api), quoteEventName(self.evntNm)
                        )
                        url = checkRedirect(url)
                        print("url2:", url)
                        
                        if url and "results" in url and url["results"]:
                            ids = url["results"][0]["id"]
                            print("url2 ids:", ids)
                            
                            if ids:
                                try:
                                    data_url = "https://api.themoviedb.org/3/movie/{}?api_key={}&append_to_response=credits&language={}".format(
                                        str(ids), str(tmdb_api), str(lng)
                                    )
                                    print("Fetching movie data...")
                                    data = json.load(urlopen(data_url))
                                    open(dwn_infos, "w").write(json.dumps(data))
                                except Exception as e:
                                    print("Movie fetch exception, trying TV show:", e)
                                    data_url = "https://api.themoviedb.org/3/tv/{}?api_key={}&append_to_response=credits&language={}".format(
                                        str(ids), str(tmdb_api), str(lng)
                                    )
                                    data = json.load(urlopen(data_url))
                                    open(dwn_infos, "w").write(json.dumps(data))
                    except Exception as e:
                        print("Exception while searching for IDs:", e)
                else:
                    try:
                        with open(dwn_infos, "r") as f:
                            data = json.load(f)
                        
                        if "vote_average" in data:
                            ImdbRating = data["vote_average"]
                        elif "imdbRating" in data:
                            ImdbRating = data["imdbRating"]
                        else:
                            ImdbRating = "0"
                        
                        print("IMDB Rating:", ImdbRating)
                        
                        if ImdbRating and ImdbRating != "0":
                            rating = int(10 * float(ImdbRating))
                        
                        value = rating
                        self.range, self.value = (0, max_range), value
                        self.instance.show()
                    except Exception as e:
                        print("Error processing saved data:", e)
            else:
                print("No event available.")
        except Exception as e:
            print("General error in infos method:", e)


    def postWidgetCreate(self, instance):
        instance.setRange(self.__start, self.__end)

    def setRange(self, range):
        (self.__start, self.__end) = range
        if self.instance is not None:
            self.instance.setRange(self.__start, self.__end)

    def getRange(self):
        return self.__start, self.__end

    range = property(getRange, setRange)
