from dateutil.parser import parse as parse_date
from abc import ABCMeta, abstractmethod
import json

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

    @abstractmethod
    def process_line(self, data, line):
        pass

class YoutubeHandler(HandlerBase):
    def __init__(self):
        self.__cid = None

    def process_line(self, data, line):
        if 'content_type' not in data:
            return None
        if data['content_type'] != 'x-youtube/video':
            return None
        if data['content_id'] == self.__cid:
            return None
        self.__cid = data['content_id']
        title = data['media_metadata']['title']
        return '%s: https://www.youtube.com/watch?v=%s "%s"' % (line[:23], self.__cid, title)
