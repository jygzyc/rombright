
from __future__ import print_function

import base64
import binascii
import collections
import errno
import getpass
import grp
import logging
import os
import platform
import re
import shlex
import shutil
import signal
import struct
import socket
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import uuid
import webbrowser
import zipfile



def Decompress(sourcefile, dest=None):
    """Decompress .zip or .tar.gz.

    Args:
        sourcefile: A string, a source file path to decompress.
        dest: A string, a folder path as decompress destination.

    Raises:
        errors.UnsupportedCompressionFileType: Not supported extension.
    """
    logger.info("Start to decompress %s!", sourcefile)
    dest_path = dest if dest else "."
    if sourcefile.endswith(".tar.gz"):
        with tarfile.open(sourcefile, "r:gz") as compressor:
            compressor.extractall(dest_path)
    elif sourcefile.endswith(".zip"):
        with zipfile.ZipFile(sourcefile, 'r') as compressor:
            compressor.extractall(dest_path)
    else:
        raise errors.UnsupportedCompressionFileType(
            "Sorry, we could only support compression file type "
            "for zip or tar.gz.")


# pylint: disable=no-init
class TextColors:
    """A class that defines common color ANSI code."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[33m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def IsCommandRunning(command):
    """Check if command is running.

    Args:
        command: String of command name.

    Returns:
        Boolean, True if command is running. False otherwise.
    """
    try:
        with open(os.devnull, "w") as dev_null:
            subprocess.check_call([constants.CMD_PGREP, "-af", command],
                                  stderr=dev_null, stdout=dev_null)
        return True
    except subprocess.CalledProcessError:
        return False

# pylint: disable=no-member,import-outside-toplevel
def FindExecutable(filename):
    """A compatibility function to find execution file path.

    Args:
        filename: String of execution filename.

    Returns:
        String: execution file path.
    """
    try:
        from distutils.spawn import find_executable
        return find_executable(filename)
    except ImportError:
        return shutil.which(filename)
    
def _ExecuteCommand(cmd, args):
    """Execute command.

    Args:
        cmd: Strings of execute binary name.
        args: List of args to pass in with cmd.

    Raises:
        errors.NoExecuteBin: Can't find the execute bin file.
    """
    bin_path = FindExecutable(cmd)
    if not bin_path:
        raise errors.NoExecuteCmd("unable to locate %s" % cmd)
    command = [bin_path] + args
    logger.debug("Running '%s'", ' '.join(command))
    with open(os.devnull, "w") as dev_null:
        subprocess.check_call(command, stderr=dev_null, stdout=dev_null)

def CheckOutput(cmd, **kwargs):
    """Call subprocess.check_output to get output.

    The subprocess.check_output return type is "bytes" in python 3, we have
    to convert bytes as string with .decode() in advance.

    Args:
        cmd: String of command.
        **kwargs: dictionary of keyword based args to pass to func.

    Return:
        String to command output.
    """
    return subprocess.check_output(cmd, **kwargs).decode()


def Popen(*command, **popen_args):
    """Execute subprocess.Popen command and log the output.

    This method waits for the process to terminate. It kills the process
    if it's interrupted due to timeout.

    Args:
        command: Strings, the command.
        popen_kwargs: The arguments to be passed to subprocess.Popen.

    Raises:
        errors.SubprocessFail if the process returns non-zero.
    """
    proc = None
    try:
        logger.info("Execute %s", command)
        popen_args["stdin"] = subprocess.PIPE
        popen_args["stdout"] = subprocess.PIPE
        popen_args["stderr"] = subprocess.PIPE

        # Some OTA tools are Python scripts in different versions. The
        # PYTHONPATH for acloud may be incompatible with the tools.
        if "env" not in popen_args and "PYTHONPATH" in os.environ:
            popen_env = os.environ.copy()
            del popen_env["PYTHONPATH"]
            popen_args["env"] = popen_env

        proc = subprocess.Popen(command, **popen_args)
        stdout, stderr = proc.communicate()
        logger.info("%s stdout: %s", command[0], stdout)
        logger.info("%s stderr: %s", command[0], stderr)

        if proc.returncode != 0:
            raise errors.SubprocessFail("%s returned %d." %
                                        (command[0], proc.returncode))
    finally:
        if proc and proc.poll() is None:
            logger.info("Kill %s", command[0])
            proc.kill()


def SetExecutable(path):
    """Grant the persmission to execute a file.

    Args:
        path: String, the file path.

    Raises:
        OSError if any file operation fails.
    """
    mode = os.stat(path).st_mode
    os.chmod(path, mode | (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH |
                           stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH))

