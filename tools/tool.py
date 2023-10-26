
"""Tools class."""

import logging
import os
import tempfile

from tools import errors
from tools import utils

_BIN_DIR_NAME = "bin"
_LIB_DIR_NAME = "lib"

_JADX = "jadx"
_APKTOOL = "apktool"
_LPUNPACK = "lpunpack"
_FUSEEXT2 = "fuse-ext2"
_AXMLPRINTER = "AXMLPrinter2"


class Tool:

    def __init__(self, tools_dir):
        self._tools_dir = os.path.abspath(tools_dir)

    def _GetBinary(self, name):
        """Get an executable file from _tools_dir.

        Args:
            name: String, the file name.

        Returns:
            String, the absolute path.

        Raises:
            errors.NoExecuteBin if the file does not exist.
        """
        path = os.path.join(self._tools_dir, _BIN_DIR_NAME, name)
        if not os.path.isfile(path):
            raise errors.NoExecuteCmd(_MISSING_OTA_TOOLS_MSG %
                                      {"tool_name": name})
        utils.SetExecutable(path)
        return path
    
