from dateutil.parser import parse as parse_date
from abc import ABCMeta, abstractmethod
from datetime import datetime
import json
import os
import sys

data_marker = 'new status: '

class FileProcessor(object):

    def __init__(self, handler):
        self._handler = handler

    def process(self, file, start_time):
        for line in file:
            date = parse_date(line[:19])
            if date < start_time:
                continue
            data_start = line.find(data_marker)
            if data_start == -1:
                continue
            try:
                data = json.loads(line[data_start+len(data_marker):])
            except ValueError:
                print line
                raise
            result = self._handler.process_line(data['data'], line)
            if result is not None:
                yield result


class HandlerBase(object):
    __metaclass__ = ABCMeta

    formatters = dict()

    @abstractmethod
    def process_line(self, data, line):
        pass

class OutputFormatterBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def add_track_entry(self, entry):
        pass

    @abstractmethod
    def finalize(self):
        pass

class YoutubeOutputFormatter(object):

    def add_track_entry(self, entry):
        print('{time}: https://www.youtube.com/watch?v={id} "{title}"'.format(**entry))

    def finalize(self):
        pass

class YoutubeOutputFormatterHTML(OutputFormatterBase):

    def __init__(self):
        self.__templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.__entries = ""
        with open(os.path.join(self.__templates_dir, 'youtube.entry.html')) as f:
            self.__entry_template = f.read()
        html = ""
        with open(os.path.join(self.__templates_dir, 'youtube.site.html')) as f:
            html = f.read()
        html_parts = html.split('{content}')
        self.__footer = html_parts[1]
        print(html_parts[0])

    def add_track_entry(self, entry):
        entry['title'] = entry['title'].replace("'", "&apos;")
        print(self.__entry_template.format(**entry))

    def finalize(self):
        print(self.__footer)


class YoutubeHandler(HandlerBase):
    formatters = dict(
        simple = YoutubeOutputFormatter,
        html = YoutubeOutputFormatterHTML,
    )

    def __init__(self):
        self.__cid = None

    def process_line(self, data, line):
        if 'content_type' not in data:
            return None
        if data['content_type'] != 'x-youtube/video':
            return None
        if data['player_state'] != 'PLAYING':
            return None
        if 'title' not in data['media_metadata']:
            return None
        if data['content_id'] == self.__cid:
            return None
        self.__cid = data['content_id']
        title = data['media_metadata']['title']

        return dict(time = line[:19], id = self.__cid, title = title.encode('utf-8'))
