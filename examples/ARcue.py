# -*- Mode: Python; test-case-name: morituri.test.test_header -*-
# vi:si:et:sw=4:sts=4:ts=4

# Morituri - for those about to RIP

# Copyright (C) 2009 Thomas Vander Stichele

# This file is part of morituri.
# 
# morituri is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# morituri is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with morituri.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys

from morituri.image import cue
from morituri.common import task

import gobject
gobject.threads_init()

def main(path):
    cuefile = cue.Cue(path)
    cuefile.parse()

    for trackIndex, track in enumerate(cuefile.tracks):
        index = track._indexes[1]
        length = cuefile.getTrackLength(track)
        file = index[1]
        offset = index[0]

        # find an actual potential file
        crctask = None

        # .cue FILE statements have Windows-style path separators
        path = os.path.join(*file.path.split('\\'))
        noext, _ = os.path.splitext(path)
        for ext in ['wav', 'flac']:
            path = '%s.%s' % (noext, ext)
            if os.path.exists(path):
                print 'CRCing %s from CD frame %r for %r' % (path, offset, length)
                crctask = task.CRCAudioRipTask(path,
                    trackNumber=trackIndex + 1, trackCount=len(cuefile.tracks),
                    frameStart=offset * task.FRAMES_PER_DISC_FRAME,
                    frameLength=length * task.FRAMES_PER_DISC_FRAME)

        if not crctask:
            print 'ERROR: path %s not found' % file.path
            continue

        runner = task.SyncRunner(crctask)
        runner.run()

        print "%08x" % crctask.crc

path = 'test.cue'

try:
    path = sys.argv[1]
except IndexError:
    pass

main(path)