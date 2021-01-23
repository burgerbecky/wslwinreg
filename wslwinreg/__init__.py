#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A drop in replacement for winreg for Cygwin, MSYS2 and Windows Subsystem for
Linux.
"""

## \package wslwinreg
#
# This module provides access to the Windows registry API.
#

#
## \mainpage
#
# \htmlinclude README.html
#
# Chapter list
# ============
#
# - \subpage md_why_wslwinreg
#
# Module list
# ===========
#
# - \ref wslwinreg
# - \ref wslwinreg.common
# - \ref wslwinreg.cygwinapi
# - \ref wslwinreg.wslapi
# - \ref wslwinreg.nullapi
# - \ref wslwinreg.WinRegKey
#

import itertools
import os.path

# pylint: disable=useless-object-inheritance
# pylint: disable=invalid-name

from .common import IS_CYGWIN, IS_MSYS, IS_WSL, ERROR_SUCCESS, \
    ERROR_FILE_NOT_FOUND, ERROR_MORE_DATA, HKEY_CLASSES_ROOT, \
    HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE, HKEY_USERS, HKEY_PERFORMANCE_DATA, \
    HKEY_CURRENT_CONFIG, HKEY_DYN_DATA, KEY_QUERY_VALUE, KEY_SET_VALUE, \
    KEY_CREATE_SUB_KEY, KEY_ENUMERATE_SUB_KEYS, KEY_NOTIFY, KEY_CREATE_LINK, \
    KEY_WOW64_32KEY, KEY_WOW64_64KEY, KEY_WOW64_RES, KEY_WRITE, KEY_EXECUTE, \
    KEY_READ, KEY_ALL_ACCESS, REG_OPTION_RESERVED, REG_OPTION_NON_VOLATILE, \
    REG_OPTION_VOLATILE, REG_OPTION_CREATE_LINK, REG_OPTION_BACKUP_RESTORE, \
    REG_OPTION_OPEN_LINK, REG_LEGAL_OPTION, REG_CREATED_NEW_KEY, \
    REG_OPENED_EXISTING_KEY, REG_WHOLE_HIVE_VOLATILE, REG_REFRESH_HIVE, \
    REG_NO_LAZY_FLUSH, REG_NOTIFY_CHANGE_NAME, REG_NOTIFY_CHANGE_ATTRIBUTES, \
    REG_NOTIFY_CHANGE_LAST_SET, REG_NOTIFY_CHANGE_SECURITY, \
    REG_LEGAL_CHANGE_FILTER, REG_NONE, REG_SZ, REG_EXPAND_SZ, REG_BINARY, \
    REG_DWORD, REG_DWORD_LITTLE_ENDIAN, REG_DWORD_BIG_ENDIAN, REG_LINK, \
    REG_MULTI_SZ, REG_RESOURCE_LIST, REG_FULL_RESOURCE_DESCRIPTOR, \
    REG_RESOURCE_REQUIREMENTS_LIST, REG_QWORD, REG_QWORD_LITTLE_ENDIAN, \
    FORMAT_MESSAGE_ALLOCATE_BUFFER, FORMAT_MESSAGE_IGNORE_INSERTS, \
    FORMAT_MESSAGE_FROM_STRING, FORMAT_MESSAGE_FROM_HMODULE, \
    FORMAT_MESSAGE_FROM_SYSTEM, FORMAT_MESSAGE_ARGUMENT_ARRAY, \
    FORMAT_MESSAGE_MAX_WIDTH_MASK, LANG_NEUTRAL, LPCVOID, BOOL, WORD, DWORD, \
    PDWORD, LPDWORD, QWORD, PQWORD, LPQWORD, LONG, PLONG, PBYTE, LPBYTE, \
    LPSTR, LPWSTR, LPCWSTR, HANDLE, HKEY, PHKEY, HLOCAL, REGSAM, FILETIME, \
    PFILETIME, SUBLANG_DEFAULT

## Numeric version
__numversion__ = (1, 0, 4)

## Current version of the library
__version__ = '.'.join([str(num) for num in __numversion__])

## Author's name
__author__ = 'Rebecca Ann Heineman'

## Name of the module
__title__ = 'wslwinreg'

## Summary of the module's use
__summary__ = 'Drop in replacement for winreg for Cygwin, MSYS2 and WSL'

## Home page
__uri__ = 'http://wslwinreg.readthedocs.io'

## Email address for bug reports
__email__ = 'becky@burgerbecky.com'

## Type of license used for distribution
__license__ = 'MIT License'

## Copyright owner
__copyright__ = 'Copyright 2020-2021 Rebecca Ann Heineman'

# Load in the proper implementation based on the
# underlying operating system

if IS_CYGWIN or IS_MSYS:
    from .cygwinapi import CloseKey, ConnectRegistry, CreateKey, CreateKeyEx, \
        DeleteKey, DeleteKeyEx, DeleteValue, EnumKey, EnumValue, \
        ExpandEnvironmentStrings, FlushKey, LoadKey, OpenKey, OpenKeyEx, \
        QueryInfoKey, QueryValue, QueryValueEx, SaveKey, SetValue, SetValueEx, \
        DisableReflectionKey, EnableReflectionKey, QueryReflectionKey, \
        get_file_info, convert_to_windows_path, convert_from_windows_path
elif IS_WSL:
    from .wslapi import CloseKey, ConnectRegistry, CreateKey, CreateKeyEx, \
        DeleteKey, DeleteKeyEx, DeleteValue, EnumKey, EnumValue, \
        ExpandEnvironmentStrings, FlushKey, LoadKey, OpenKey, OpenKeyEx, \
        QueryInfoKey, QueryValue, QueryValueEx, SaveKey, SetValue, SetValueEx, \
        DisableReflectionKey, EnableReflectionKey, QueryReflectionKey, \
        get_file_info, convert_to_windows_path, convert_from_windows_path
else:
    from .nullapi import convert_to_windows_path, convert_from_windows_path
    try:
        # Attempt importing the current name
        from winreg import *
        from .cygwinapi import get_file_info
    except ImportError:
        try:
            # Attempt importing the old name
            from _winreg import *
            from .cygwinapi import get_file_info
        except ImportError:
            # For unsupported platforms, create null apis that always
            # throw exceptions when called
            from .nullapi import CloseKey, ConnectRegistry, CreateKey, \
                CreateKeyEx, DeleteKey, DeleteKeyEx, DeleteValue, EnumKey, \
                EnumValue, ExpandEnvironmentStrings, FlushKey, LoadKey, \
                OpenKey, OpenKeyEx, QueryInfoKey, QueryValue, QueryValueEx, \
                SaveKey, SetValue, SetValueEx, DisableReflectionKey, \
                EnableReflectionKey, QueryReflectionKey, get_file_info

########################################


class WinRegKey(object):
    """
    Registry key helper class.

    Manage entries in a registy key by using indexing and scanning.
    """

    def __init__(self, root_key, subkey, access):
        """
        Initialize the class

        Args:
            root_key: Root key enumeration
            subkey: String or None for name of sub key
            access: Access flags to pass to OpenKeyEx()
        """

        # If there is a sub key, open it, can throw an exception
        if subkey:
            root_key = OpenKeyEx(root_key, subkey, 0, access)

        ## Key handle of opened key
        self.key = root_key

        ## Access used to open this key, used as default to open sub keys
        self.access = access

    def __enter__(self):
        """
        Enable enter/exit functionality
        """
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """
        Release resources on class release

        Args:
            exception_type: Ignored
            exception_value: Ignored
            traceback: Ignored
        """
        self.close()

    def close(self):
        """
        Release existing key, if any.
        """
        CloseKey(self.key)

    def open_subkey(self, subkey, access=None):
        """
        Open a sub key.

        Args:
            subkey: Name of the subkey to open
            access: Desired access to the subkey.
        Returns:
            An instance of the WinRegKey of the new key.
        """

        # Use the default access?
        if access is None:
            access = self.access
        return type(self)(self.key, subkey, access)

    def get_subkeys(self):
        """
        Return the list of all of the sub key names.

        Iterate over all of the sub keys and place their names in a list.
        Return the list. Unicode is properly handled.

        Returns:
            list of names of all the subkeys.
        """
        subkey_names = []
        try:
            for item in itertools.count():
                subkey_names.append(EnumKey(self.key, item))

        # Exception is fired once the list end is reached
        except OSError:
            pass
        return subkey_names

    def get_value(self, value_name=None):
        """
        Read a value from a registry key.

        Note:
            If the type returned is REG_SZ, scan for a null and trucate.
            If the type returned is REG_EXPAND_SZ, call
            ExpandEnvironmentStrings()

        Args:
            value_name: String of the name of the value, None for default.
        Returns:
            Value returned from QueryValueEx()
        """
        value, value_type = QueryValueEx(self.key, value_name)
        if value_type == REG_SZ:
            # Failsafe, truncate at null
            index = value.find('\0')
            if index != -1:
                value = value[:index]
        elif value_type == REG_EXPAND_SZ:
            # Perform expansion
            value = ExpandEnvironmentStrings(value)
        return (value, value_type)

    def get_all_values(self):
        """
        Return a dict of all key name and associated values.

        Returns:
            dict with each item is the returned value from QueryValueEx()
        """
        value_names = []
        try:
            for i in itertools.count():
                value_names.append(EnumValue(self.key, i))

        # Exception is fired once the list end is reached
        except OSError:
            pass

        # Convert the list to a dict
        return {k[0]: self.get_value(k[0]) for k in value_names}

    def __getitem__(self, subkey):
        """
        Call open_subkey() with subscript.

        Uses the access flags from this key to open the sub key.

        Args:
            subkey: Requested sub key.
        Returns:
            An instance of the WinRegKey of the new key.
        """
        return self.open_subkey(subkey)

    def __iter__(self):
        """
        Iterator of the sub keys.

        Call get_subkeys() and encapsulate the value in an iter()

        Returns:
            iter of get_subkeys()
        """
        return iter(self.get_subkeys())


########################################

def get_HKCU():
    """
    Open HKEY_CURRENT_USER.

    Returns:
        Read only WinRegKey for HKEY_CURRENT_USER
    """
    return WinRegKey(HKEY_CURRENT_USER, None, KEY_READ)

########################################


def get_HKLM_32():
    """
    Open HKEY_LOCAL_MACHINE, 32 bit view.

    Returns:
        Read only WinRegKey for HKEY_LOCAL_MACHINE with KEY_WOW64_32KEY
    """
    return WinRegKey(HKEY_LOCAL_MACHINE, None, KEY_READ | KEY_WOW64_32KEY)

########################################


def get_HKLM_64():
    """
    Open HKEY_LOCAL_MACHINE, 64 bit view.

    Returns:
        Read only WinRegKey for HKEY_LOCAL_MACHINE with KEY_WOW64_64KEY
    """
    return WinRegKey(HKEY_LOCAL_MACHINE, None, KEY_READ | KEY_WOW64_64KEY)
