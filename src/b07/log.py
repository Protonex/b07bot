# - mode: python; coding: utf-8 -*-

# b07 bot - ingress information bot
# Copyright © 2013 b07@tormail.org
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import datetime

write = sys.stderr.write
flush = sys.stderr.flush

import time
import traceback

from twisted.python import log
from twisted.python import util

TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL = range(6)

class Observer(object):
    def __init__(self, reactor, level):
        global write
        global flush

        self.reactor = reactor
        self.level = level

        self.write = write
        self.flush = flush

    def emit(self, eventDict):
        if not eventDict.has_key('level'):
            if eventDict.has_key('isError') and eventDict['isError']:
                eventDict['level'] = ERROR

            else:
                eventDict['level'] = TRACE

        if eventDict['level'] < self.level:
            return

        text = log.textFromEventDict(eventDict)
        if text is None:
            return

        text = text.rstrip()
        text = text.expandtabs()
        text += '\n'
        text = text.encode('utf-8')

        util.untilConcludes(self.write, text)
        util.untilConcludes(self.flush)
        
        if eventDict['level'] >= CRITICAL:
            self.reactor.stop()

__all__ = ['setup',
           'trace', 'debug', 'info', 'warning', 'error', 'critical', 'log_failure',
           'TRACE', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

observer = None

def msg(*message, **kw):
    global write
    global flush

    if observer is None:
        write('logging is not set up yet!')
        flush()
        sys.exit(1)

    log.msg(*message, **kw)

def err(failure, **kw):
    global write
    global flush

    if observer is None:
        write('logging is not set up yet!')
        flush()
        sys.exit(1)

    log.err(failure, **kw)

def trace(*message, **kw):
    kw['level'] = TRACE
    kw['CODE_FILE'], kw['CODE_LINE'], kw['CODE_FUNC'] = traceback.extract_stack(limit=2)[0][:3]
    msg(*message, **kw)

def debug(*message, **kw):
    kw['level'] = DEBUG
    kw['CODE_FILE'], kw['CODE_LINE'], kw['CODE_FUNC'] = traceback.extract_stack(limit=2)[0][:3]
    msg(*message, **kw)

def info(*message, **kw):
    kw['level'] = INFO
    kw['CODE_FILE'], kw['CODE_LINE'], kw['CODE_FUNC'] = traceback.extract_stack(limit=2)[0][:3]
    msg(*message, **kw)

def warning(*message, **kw):
    kw['level'] = WARNING
    kw['CODE_FILE'], kw['CODE_LINE'], kw['CODE_FUNC'] = traceback.extract_stack(limit=2)[0][:3]
    msg(*message, **kw)

def error(*message, **kw):
    kw['level'] = ERROR
    kw['CODE_FILE'], kw['CODE_LINE'], kw['CODE_FUNC'] = traceback.extract_stack(limit=2)[0][:3]
    msg(*message, **kw)

def critical(*message, **kw):
    kw['level'] = CRITICAL
    kw['CODE_FILE'], kw['CODE_LINE'], kw['CODE_FUNC'] = traceback.extract_stack(limit=2)[0][:3]
    msg(*message, **kw)

def log_failure(failure, **kw):
    kw['level'] = CRITICAL
    kw['CODE_FILE'], kw['CODE_LINE'], kw['CODE_FUNC'] = traceback.extract_stack(limit=2)[0][:3]
    err(failure, **kw)

def setup(reactor, level = DEBUG):
    global observer

    observer = Observer(reactor, level)
    
    log.startLoggingWithObserver(observer.emit, setStdout = 1)
    
def versionCheck(version_string, nickname):
    now = datetime.datetime.now()
    try:
        versionFile = open(os.path.expanduser('~/.{}_ingress_server_version'.format(nickname)),'r')
        ver_string = versionFile.readline().strip()
        if not ver_string == version_string:
            versionFile = open(os.path.expanduser('~/.{}_ingress_server_version'.format(nickname)),'wb')
            versionFile.write(version_string+"\n")
            versionFile.close()
            versionFile = open(os.path.expanduser('~/.{}_ingress_server_version_old'.format(nickname)),'a')
            versionFile.write("Update time: {}\n{}\n".format(now, version_string))
            versionFile.close()
            return True
        else:
            return False
        
    except IOError:
        versionFile = open(os.path.expanduser('~/.{}_ingress_server_version'.format(nickname)),'wb')
        versionFile.write(version_string+"\n")
        versionFile.close()
        versionFile = open(os.path.expanduser('~/.{}_ingress_server_version_old'.format(nickname)),'a')
        versionFile.write("Update time: {}\n{}\n".format(now, version_string))
        versionFile.close()
        return True
