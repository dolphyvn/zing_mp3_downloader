#!/usr/bin/env python
"""
Zing MP3 downloader
Usage: ./Mp3ZingDownloader.py -h
"""

__author__ = 'heroandtn3 (www.sangnd.com)'
__email__ = 'heroandtn3 [at] gmail.com'
__version__ = '0.2.1'
__released__ = '11/10/2013'
__license__ = "GNU GPL"

import sys
from urllib.request import urlopen
from urllib.request import urlretrieve
from html.parser import HTMLParser
import gzip
import xml.etree.ElementTree as ET
import http.client
import argparse


def get_content(url, encoding='UTF-8', gzip_decompress=False):
        """
        Return str that contains content of url page
        """
        resp = urlopen(url)
        result = ""
        output = resp.read()
        try:
            if gzip_decompress:
                output = gzip.decompress(output)

            if encoding is not None:
                result = output.decode(encoding)
            else:
                result = output

        except UnicodeDecodeError:
            print("There's error while decoding response. Trying again...")
            # try downloading file
            urlretrieve(url, "file.tmp")
            fxml = open("file.tmp", "rb")
            result = gzip.decompress(fxml.read()).decode()
            #print(result)
            fxml.close()

        return result


class Mp3ZingParser(HTMLParser):
    def __init__(self, strict=False):
        HTMLParser.__init__(self, strict=False)
        self.xml_url = ''

    def handle_data(self, data):
        if data.find('param') != -1:
            #print(data)
            data_list = data.split('&amp;')
            for dt in data_list:
                if dt.startswith('xmlURL'):
                    self.xml_url = dt.replace('xmlURL=', '')
                    break


class Song:
    def __init__(self):
        self.url = ''
        self.name = ''
        self.single = ''
        self.type = '.mp3'
        self.direct_url = ''

    def save(self):
        if not self.url:
            print("There's no link to download")
            return
        if not self.direct_url:
            print("It's not able to detect MP3 file in giving link")
            return

        # remove double-spaces character in name and single
        while self.single.find('  ') != -1:
            self.single = self.single.replace('  ', ' ')

        while self.name.find('  ') != -1:
            self.name = self.name.replace('  ', ' ')

        file_name = self.single.replace(' ', '-') + "_"
        + self.name.replace(' ', '-') + self.type

        print('Downloading...')
        urlretrieve(self.direct_url, file_name)
        print('Done! Saved to ' + file_name)

    def parse_url(self):
        parser = Mp3ZingParser(strict=False)
        parser.feed(get_content(self.url))
        dom = ET.fromstring(get_content(parser.xml_url, "UTF-8", True))

        # get song informations
        self.name = dom.find('./item/title').text
        self.single = dom.find('./item/performer').text
        self.direct_url = dom.find('./item/source').text

    def parse_url_alter(self):
        song_id = self.url.split('/')[-1].split('.')[0]
        path = '/download/vip/song/' + song_id
        host = 'mp3.zing.vn'
        conn = http.client.HTTPConnection(host)
        conn.request('GET', path)
        resp = conn.getresponse()
        location = resp.getheader('Location')
        #print(location)
        # get song informations
        fields = location.split('?')
        self.direct_url = fields[0].strip()
        filename = fields[1].split('=')[1]

        self.name = filename.split('-')[0].strip()
        self.single = filename.split('-')[1].split('.')[0].strip()

    def download(self, vip=False):
        if vip:
            self.parse_url_alter()
        else:
            self.parse_url()
        print("Found MP3 file: " + self.single + " - " + self.name)
        self.save()


def is_valid_url(url):
    return (url.find('mp3.zing.vn/bai-hat') != -1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Zing MP3 downloader')
    parser.add_argument('--vip', dest='vip', const=True, default=False,
                        action='store_const',
                        help=('Use this option if you want to download '
                              '320Kbps audio file')
                        )
    parser.add_argument('url', metavar='url', type=str,
                        help="Link of Zing Mp3 song to be downloaded")
    args = parser.parse_args()
    if not is_valid_url(args.url):
        print('Invalid url. Byte!')
        sys.exit()
    try:
        song = Song()
        song.url = args.url
        song.download(vip=args.vip)
    except KeyboardInterrupt:
        print('Downloading canceled. Byte!')
