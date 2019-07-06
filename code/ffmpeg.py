# Copyright 2016 Antony Lee. All rights reserved.

# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:

#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.

#    2. Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY ANTONY LEE ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL ANTONY LEE OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of Antony Lee.

from contextlib import contextmanager
import logging
import shutil
from subprocess import Popen, PIPE
from tempfile import TemporaryFile

from PyQt4.QtGui import QImage


LOGGER = logging.getLogger(__name__)


class FFMpegWriter:
    def __init__(self, path, *, fps=24, quality=1):
        self._path = path
        self._fps = fps
        self._quality = quality
        self._tempfile = None
        self._popen = None

    def __enter__(self):
        self._tempfile = TemporaryFile()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            popen = self._popen
            if not popen:
                return
            self._tempfile.seek(0)
            shutil.copyfileobj(self._tempfile, popen.stdin)
            popen.stdin.close()
            popen.wait()
            out = popen.stdout.read()
            if out:
                LOGGER.warning("ffmpeg stdout: %s", out)
            err = popen.stderr.read()
            if err:
                LOGGER.warning("ffmpeg stderr: %s", err)
            if popen.returncode:
                raise RuntimeError("ffmpeg failed")
        finally:
            self._tempfile.close()
            self._tempfile = self._popen = None

    def _create_popen(self, qsize):
        self._size = qsize
        args = ["ffmpeg",
                "-loglevel", "warning",
                "-y", # Overwrite existing.
                "-f", "rawvideo",
                "-vcodec", "rawvideo",
                "-s", "{}x{}".format(qsize.width(), qsize.height()), # Size.
                "-pix_fmt", "bgra", # Format.
                "-r", str(self._fps), # FPS.
                "-i", "-", # Input pipe.
                "-an", # No audio.
                "-vcodec", "mpeg4",
                "-q", str(self._quality), # Quality.
                str(self._path)]
        self._popen = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    def add_qimage(self, qimage):
        if self._popen is None:
            self._create_popen(qimage.size())
        else:
            if self._size != qimage.size():
                raise ValueError("Image size changed: was {}, now {}".format(
                    self._size, qimage.size()))
        bits = qimage.convertToFormat(QImage.Format_RGB32).constBits()
        bits.setsize(qimage.byteCount())
        self._tempfile.write(bytes(bits))