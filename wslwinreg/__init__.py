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
# Module list
# ===========
#
# - \ref wslwinreg
# - \ref wslwinreg.common
# - \ref wslwinreg.cygwinapi
# - \ref wslwinreg.wslapi
# - \ref wslwinreg.nullapi
#


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
    FORMAT_MESSAGE_MAX_WIDTH_MASK, LANG_NEUTRAL, PCVOID, WORD, DWORD, PDWORD, \
    LPDWORD, QWORD, PQWORD, LPQWORD, LONG, PLONG, PBYTE, LPBYTE, LPSTR, \
    LPWSTR, LPCWSTR, HANDLE, HKEY, PHKEY, HLOCAL, REGSAM, FILETIME, \
    PFILETIME, SUBLANG_DEFAULT

## Numeric version
__numversion__ = (0, 5, 0)

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
__copyright__ = 'Copyright 2020 Rebecca Ann Heineman'

# Load in the proper implementation based on the
# underlying operating system

if IS_CYGWIN or IS_MSYS:
    from .cygwinapi import CloseKey, ConnectRegistry, CreateKey, CreateKeyEx, \
        DeleteKey, DeleteKeyEx, DeleteValue, EnumKey, EnumValue, \
        ExpandEnvironmentStrings, FlushKey, LoadKey, OpenKey, OpenKeyEx, \
        QueryInfoKey, QueryValue, QueryValueEx, SaveKey, SetValue, SetValueEx, \
        DisableReflectionKey, EnableReflectionKey, QueryReflectionKey
elif IS_WSL:
    from .wslapi import *
else:
    from .nullapi import CloseKey, ConnectRegistry, CreateKey, CreateKeyEx, \
        DeleteKey, DeleteKeyEx, DeleteValue, EnumKey, EnumValue, \
        ExpandEnvironmentStrings, FlushKey, LoadKey, OpenKey, OpenKeyEx, \
        QueryInfoKey, QueryValue, QueryValueEx, SaveKey, SetValue, SetValueEx, \
        DisableReflectionKey, EnableReflectionKey, QueryReflectionKey
