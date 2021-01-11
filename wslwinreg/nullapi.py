#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Package that contains stub functions for unsupported platforms.
"""

## \package wslwinreg.nullapi

# Disable camel case requirement for function names
# pylint: disable=invalid-name

# Disable reusing reserved words.
# pylint: disable=redefined-builtin
# pylint: disable=unused-argument

from .common import KEY_WRITE, KEY_WOW64_64KEY, KEY_READ

## Shared ``NotImplementedError`` for this module
_NOT_IMPL = NotImplementedError(
    'Only supported under Cygwin, MSYS2, or Windows Subsystem for Linux')

########################################


def CloseKey(hkey):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def ConnectRegistry(computer_name, key):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def CreateKey(key, sub_key):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def CreateKeyEx(key, sub_key, reserved=0, access=KEY_WRITE):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL


def DeleteKey(key, sub_key):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def DeleteKeyEx(key, sub_key, access=KEY_WOW64_64KEY, reserved=0):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def DeleteValue(key, value):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def EnumKey(key, index):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def EnumValue(key, index):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def ExpandEnvironmentStrings(str):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def FlushKey(key):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def LoadKey(key, sub_key, file_name):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def OpenKey(key, sub_key, reserved=0, access=KEY_READ):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def OpenKeyEx(key, sub_key, reserved=0, access=KEY_READ):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def QueryInfoKey(key):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def QueryValue(key, sub_key):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def QueryValueEx(key, value_name):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def SaveKey(key, file_name):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def SetValue(key, sub_key, type, value):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def SetValueEx(key, value_name, reserved, type, value):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def DisableReflectionKey(key):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def EnableReflectionKey(key):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def QueryReflectionKey(key):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    raise _NOT_IMPL

########################################


def convert_to_windows_path(path_name):
    """
    Convert pathname to Windows.

    This is the null function, it returns the path_name unchanged.

    Args:
        path_name: Absolute Windows pathname
    Return:
        path_name as is.
    """
    return path_name


########################################


def convert_from_windows_path(path_name):
    """
    Convert pathname from Windows.

    This is the null function, it returns the path_name unchanged.

    Args:
        path_name: Absolute Windows pathname
    Return:
        path_name as is.
    """
    return path_name

########################################


def get_file_info(path_name, string_name):
    """
    Not implemented.

    Args:
        path_name: Name of the windows file.
        string_name: Name of the data chunk to retrieve

    Return:
        None
    """

    return None
