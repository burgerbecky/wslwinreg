#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Windows constants and function common to both WSL and Cygwin implementaions.

This module contains numerous constants for Windows and functions common to
both the WSL bridge and the Cygwin/MSYS2 cdll implementations of the wslwinreg
module.
"""

## \package wslwinreg.common

# Disable camel case requirement for function names
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods

import sys
import platform
from struct import pack, unpack_from
from locale import getpreferredencoding
from errno import EINVAL

# Types needed for C calls
from ctypes import (
    POINTER,
    sizeof,
    Structure,
    create_string_buffer,
    c_char_p,
    c_int,
    c_uint,
    c_long,
    c_ulong,
    c_ulonglong,
    c_ushort,
    c_void_p,
    c_wchar_p)

## Items to import on "from .common import *"
__all__ = [
    'builtins',
    'PY2',
    'IS_LINUX',
    'IS_CYGWIN',
    'IS_MSYS',
    'IS_WSL',
    'ERROR_SUCCESS',
    'ERROR_FILE_NOT_FOUND',
    'ERROR_MORE_DATA',
    'HKEY_CLASSES_ROOT',
    'HKEY_CURRENT_USER',
    'HKEY_LOCAL_MACHINE',
    'HKEY_USERS',
    'HKEY_PERFORMANCE_DATA',
    'HKEY_CURRENT_CONFIG',
    'HKEY_DYN_DATA',
    'KEY_QUERY_VALUE',
    'KEY_SET_VALUE',
    'KEY_CREATE_SUB_KEY',
    'KEY_ENUMERATE_SUB_KEYS',
    'KEY_NOTIFY',
    'KEY_CREATE_LINK',
    'KEY_WOW64_32KEY',
    'KEY_WOW64_64KEY',
    'KEY_WOW64_RES',
    'KEY_WRITE',
    'KEY_EXECUTE',
    'KEY_READ',
    'KEY_ALL_ACCESS',
    'REG_OPTION_RESERVED',
    'REG_OPTION_NON_VOLATILE',
    'REG_OPTION_VOLATILE',
    'REG_OPTION_CREATE_LINK',
    'REG_OPTION_BACKUP_RESTORE',
    'REG_OPTION_OPEN_LINK',
    'REG_LEGAL_OPTION',
    'REG_CREATED_NEW_KEY',
    'REG_OPENED_EXISTING_KEY',
    'REG_WHOLE_HIVE_VOLATILE',
    'REG_REFRESH_HIVE',
    'REG_NO_LAZY_FLUSH',
    'REG_NOTIFY_CHANGE_NAME',
    'REG_NOTIFY_CHANGE_ATTRIBUTES',
    'REG_NOTIFY_CHANGE_LAST_SET',
    'REG_NOTIFY_CHANGE_SECURITY',
    'REG_LEGAL_CHANGE_FILTER',
    'REG_NONE',
    'REG_SZ',
    'REG_EXPAND_SZ',
    'REG_BINARY',
    'REG_DWORD',
    'REG_DWORD_LITTLE_ENDIAN',
    'REG_DWORD_BIG_ENDIAN',
    'REG_LINK',
    'REG_MULTI_SZ',
    'REG_RESOURCE_LIST',
    'REG_FULL_RESOURCE_DESCRIPTOR',
    'REG_RESOURCE_REQUIREMENTS_LIST',
    'REG_QWORD',
    'REG_QWORD_LITTLE_ENDIAN',
    'FORMAT_MESSAGE_ALLOCATE_BUFFER',
    'FORMAT_MESSAGE_IGNORE_INSERTS',
    'FORMAT_MESSAGE_FROM_STRING',
    'FORMAT_MESSAGE_FROM_HMODULE',
    'FORMAT_MESSAGE_FROM_SYSTEM',
    'FORMAT_MESSAGE_ARGUMENT_ARRAY',
    'FORMAT_MESSAGE_MAX_WIDTH_MASK',
    'LANG_NEUTRAL',
    'SUBLANG_DEFAULT',
    'LPCVOID',
    'LPVOID',
    'BOOL',
    'WORD',
    'DWORD',
    'PDWORD',
    'LPDWORD',
    'QWORD',
    'PQWORD',
    'LPQWORD',
    'LONG',
    'PLONG',
    'PBYTE',
    'LPBYTE',
    'LPSTR',
    'LPWSTR',
    'LPCWSTR',
    'HANDLE',
    'HKEY',
    'PHKEY',
    'HLOCAL',
    'REGSAM',
    'FILETIME',
    'PFILETIME',
    'winerror_to_errno',
    'convert_to_utf16',
    'to_registry_bytes',
    'from_registry_bytes'
]

## Type long for Python 2 compatibility
try:
    long
except NameError:
    # Fake it for Python 3
    long = int
    __all__.append('long')

## Type basestring for Python 2 compatibility
try:
    basestring
except NameError:
    # Fake it for Python 3
    basestring = str
    __all__.append('basestring')

# Force Python2 to use builtins
try:
    import builtins
except ImportError:
    # Try the Python 2 version
    import exceptions as builtins

## True if the interpreter is Python 2.x
PY2 = sys.version_info[0] == 2

## Running on linux?
IS_LINUX = sys.platform.startswith('linux')

## Running on Cygwin
IS_CYGWIN = sys.platform.startswith('cygwin')

## Running on MSYS
IS_MSYS = sys.platform.startswith('msys')

## Running on Windows Subsystem for Linux
IS_WSL = IS_LINUX and 'icrosoft' in platform.platform()

## The operation completed successfully.
ERROR_SUCCESS = 0x00000000

## The system cannot find the file specified.
ERROR_FILE_NOT_FOUND = 0x00000002

## More data is available.
ERROR_MORE_DATA = 0x000000ea

## Registry entries subordinate to this key define types
# (or classes) of documents and the properties associated with those types.
HKEY_CLASSES_ROOT = 0x80000000

## Registry entries subordinate to this key define the preferences of the
# current user.
HKEY_CURRENT_USER = 0x80000001

## Registry entries subordinate to this key define the physical state of
# the computer, including data about the bus type, system memory, and
# installed hardware and software.
HKEY_LOCAL_MACHINE = 0x80000002

## Registry entries subordinate to this key define the default user
# configuration for new users on the local computer and the user
# configuration for the current user.
HKEY_USERS = 0x80000003

## Registry entries subordinate to this key reference the text strings
# that describe counters in US English.
HKEY_PERFORMANCE_DATA = 0x80000004

## Contains information about the current hardware profile of the local
# computer system.
HKEY_CURRENT_CONFIG = 0x80000005

## Windows registry hive that contains information about hardware devices,
# including Plug and Play and network performance statistics.
HKEY_DYN_DATA = 0x80000006

## Required to query the values of a registry key.
KEY_QUERY_VALUE = 0x00000001

## Required to create, delete, or set a registry value.
KEY_SET_VALUE = 0x00000002

## Required to create a subkey of a registry key.
KEY_CREATE_SUB_KEY = 0x00000004

## Required to enumerate the subkeys of a registry key.
KEY_ENUMERATE_SUB_KEYS = 0x00000008

## Required to request change notifications for a registry key or for
# subkeys of a registry key.
KEY_NOTIFY = 0x00000010

## Reserved for system use.
KEY_CREATE_LINK = 0x00000020

## Indicates that an application on 64-bit Windows should operate on
# the 32-bit registry view.
KEY_WOW64_32KEY = 0x00000200

## Indicates that an application on 64-bit Windows should operate on
# the 64-bit registry view.
KEY_WOW64_64KEY = 0x00000100

## Mask for common.KEY_WOW64_32KEY or'd with common.KEY_WOW64_64KEY
KEY_WOW64_RES = 0x00000300

## Combines the STANDARD_RIGHTS_WRITE, common.KEY_SET_VALUE, and
# common.KEY_CREATE_SUB_KEY access rights.
KEY_WRITE = 0x00020006

## Equivalent to KEY_READ.
KEY_EXECUTE = 0x00020019

## Combines the STANDARD_RIGHTS_READ, common.KEY_QUERY_VALUE,
# common.KEY_ENUMERATE_SUB_KEYS, and common.KEY_NOTIFY values.
KEY_READ = 0x00020019

## Combines the STANDARD_RIGHTS_REQUIRED, common.KEY_QUERY_VALUE,
# common.KEY_SET_VALUE, common.KEY_CREATE_SUB_KEY,
# common.KEY_ENUMERATE_SUB_KEYS, common.KEY_NOTIFY,
# and common.KEY_CREATE_LINK access rights.
KEY_ALL_ACCESS = 0x000f003f

## Default key option, same as common.REG_OPTION_NON_VOLATILE
REG_OPTION_RESERVED = 0x00000000

## This key is not volatile; this is the default.
REG_OPTION_NON_VOLATILE = 0x00000000

## All keys created by the function are volatile.
REG_OPTION_VOLATILE = 0x00000001

## This key is a symbolic link.
REG_OPTION_CREATE_LINK = 0x00000002

## If this flag is set, the function ignores the samDesired parameter
# and attempts to open the key with the access required to backup or
# restore the key.
REG_OPTION_BACKUP_RESTORE = 0x00000004

## The key to be opened is a symbolic link.
REG_OPTION_OPEN_LINK = 0x00000008

## Mask for all registry key option flags.
REG_LEGAL_OPTION = REG_OPTION_RESERVED | \
    REG_OPTION_NON_VOLATILE | \
    REG_OPTION_VOLATILE | \
    REG_OPTION_CREATE_LINK | \
    REG_OPTION_BACKUP_RESTORE | \
    REG_OPTION_OPEN_LINK

## The key did not exist and was created.
REG_CREATED_NEW_KEY = 0x00000001

## The key existed and was simply opened without being changed.
REG_OPENED_EXISTING_KEY = 0x00000002

## If specified, a new, volatile (memory only) set of registry
# information, or hive, is created.
REG_WHOLE_HIVE_VOLATILE = 0x00000001

## If set, the location of the subtree that the hKey parameter
# points to is restored to its state immediately following the
# last flush.
REG_REFRESH_HIVE = 0x00000002

## If set, disable lazy flushing.
REG_NO_LAZY_FLUSH = 0x00000004

## Notify the caller if a subkey is added or deleted.
REG_NOTIFY_CHANGE_NAME = 0x00000001

## Notify the caller of changes to the attributes of the key,
# such as the security descriptor information.
REG_NOTIFY_CHANGE_ATTRIBUTES = 0x00000002

## Notify the caller of changes to a value of the key.
REG_NOTIFY_CHANGE_LAST_SET = 0x00000004

## Notify the caller of changes to the security descriptor of the
# key.
REG_NOTIFY_CHANGE_SECURITY = 0x00000008

## Mask for all REG_NOTIFY flags
REG_LEGAL_CHANGE_FILTER = REG_NOTIFY_CHANGE_NAME | \
    REG_NOTIFY_CHANGE_ATTRIBUTES | \
    REG_NOTIFY_CHANGE_LAST_SET | \
    REG_NOTIFY_CHANGE_SECURITY

## No defined value type.
REG_NONE = 0x000000000

## A null-terminated string.
REG_SZ = 0x000000001

## A null-terminated string that contains unexpanded references to
# environment variables (for example, "%PATH%")
REG_EXPAND_SZ = 0x000000002

## Binary data in any form.
REG_BINARY = 0x000000003

## A 32-bit number.
REG_DWORD = 0x000000004

## A 32-bit number in little-endian format.
REG_DWORD_LITTLE_ENDIAN = 0x000000004

## A 32-bit number in big-endian format.
REG_DWORD_BIG_ENDIAN = 0x000000005

## A null-terminated Unicode string that contains the target path
# of a symbolic link that was created by calling the RegCreateKeyEx
# function with common.REG_OPTION_CREATE_LINK.
REG_LINK = 0x000000006

## A sequence of null-terminated strings, terminated by an empty
# string (\0).
REG_MULTI_SZ = 0x000000007

## Device-driver resource list.
REG_RESOURCE_LIST = 0x000000008

## A list of hardware resources that a physical device is using,
# detected and written into the \\HardwareDescription tree by the
# system
REG_FULL_RESOURCE_DESCRIPTOR = 0x000000009

## A device driver's list of possible hardware resources it or one
# of the physical devices it controls can use, from which the
# system writes a subset into the \\ResourceMap tree
REG_RESOURCE_REQUIREMENTS_LIST = 0x00000000a

## A 64-bit number.
REG_QWORD = 0x0000000b

## A 64-bit number in little-endian format.
REG_QWORD_LITTLE_ENDIAN = 0x0000000b

## The function allocates a buffer large enough to hold the formatted
# message, and places a pointer to the allocated buffer at the address
# specified by lpBuffer.
FORMAT_MESSAGE_ALLOCATE_BUFFER = 256

## Insert sequences in the message definition such as %1 are to be
# ignored and passed through to the output buffer unchanged.
FORMAT_MESSAGE_IGNORE_INSERTS = 512

## The lpSource parameter is a pointer to a null-terminated string
# that contains a message definition.
FORMAT_MESSAGE_FROM_STRING = 1024

## The lpSource parameter is a module handle containing the
# message-table resource(s) to search.
FORMAT_MESSAGE_FROM_HMODULE = 2048

## The function should search the system message-table resource(s)
# for the requested message.
FORMAT_MESSAGE_FROM_SYSTEM = 4096

## The Arguments parameter is not a va_list structure, but is a pointer
# to an array of values that represent the arguments.
FORMAT_MESSAGE_ARGUMENT_ARRAY = 8192

## The function ignores regular line breaks in the message definition
# text.
FORMAT_MESSAGE_MAX_WIDTH_MASK = 255

## String has no associated language.
LANG_NEUTRAL = 0x00

## User default sub language
SUBLANG_DEFAULT = 0x01

## ``const void *`` C void pointer
LPCVOID = c_void_p

## ``void *`` C void pointer
LPVOID = c_void_p

## BOOL 32 bit C integer type
BOOL = c_long

## ``short int`` 16 bit C integer type
WORD = c_ushort

## ``unsigned int`` 32 bit C integer type
DWORD = c_ulong

## ``unsigned int *`` 32 bit C integer pointer
PDWORD = POINTER(DWORD)

## ``FAR unsigned int *`` 32 bit C pointer
LPDWORD = PDWORD

## ``unsigned long long`` 64 bit C integer type
QWORD = c_ulonglong

## ``unsigned long long *`` 64 bit C integer pointer
PQWORD = POINTER(QWORD)

## ``FAR unsigned long long *`` 64 bit C integer pointer
LPQWORD = PQWORD

## ``signed int`` 32 bit signed C integer type
LONG = c_int

## ``signed int *`` 32 bit signed C integer pointer
PLONG = POINTER(LONG)

## ``signed char`` 8 bit signed C integer type
PBYTE = c_char_p

## ``unsigned char`` 8 bit unsigned C integer type
LPBYTE = PBYTE

## ``char *`` C string pointer
LPSTR = c_char_p

## ``wchar_t *`` C string pointer (16-bit)
LPWSTR = c_wchar_p

## ``FAR wchar_t *`` C string pointer (16-bit)
LPCWSTR = LPWSTR

## ``HANDLE`` C data type from Windows (void *)
HANDLE = c_void_p

## ``HKEY`` C data type for Windows registry keys (void *)
HKEY = HANDLE

## ``HKEY *`` C pointer to Windows HKEY (void **)
PHKEY = POINTER(HKEY)

## ``HLOCAL`` Windows HLOCAL data type (void *)
HLOCAL = c_void_p

## ``REGSAM`` Windows REGSAM C data type (unsigned int)
REGSAM = c_uint

########################################


class FILETIME(Structure):
    """
    Structure to mimic the Windows FILETIME data type.

    Args:
        None
    """

    _fields_ = [("low", DWORD), ("high", DWORD)]


## ``FILETIME *`` pointer to Windows FILETIME structure
PFILETIME = POINTER(FILETIME)

########################################

## Map for convert Windows error codes to ``errno`` codes.
_winerror_to_errno = {2: 2,
                      3: 2,
                      4: 24,
                      5: 13,
                      6: 9,
                      7: 12,
                      8: 12,
                      9: 12,
                      10: 7,
                      11: 8,
                      15: 2,
                      16: 13,
                      17: 18,
                      18: 2,
                      19: 13,
                      20: 13,
                      21: 13,
                      22: 13,
                      23: 13,
                      24: 13,
                      25: 13,
                      26: 13,
                      27: 13,
                      28: 13,
                      29: 13,
                      30: 13,
                      31: 13,
                      32: 13,
                      33: 13,
                      34: 13,
                      35: 13,
                      36: 13,
                      53: 2,
                      65: 13,
                      67: 2,
                      80: 17,
                      82: 13,
                      83: 13,
                      89: 11,
                      108: 13,
                      109: 32,
                      112: 28,
                      114: 9,
                      128: 10,
                      129: 10,
                      130: 9,
                      132: 13,
                      145: 41,
                      158: 13,
                      161: 2,
                      164: 11,
                      167: 13,
                      183: 17,
                      188: 8,
                      189: 8,
                      190: 8,
                      191: 8,
                      192: 8,
                      193: 8,
                      194: 8,
                      195: 8,
                      196: 8,
                      197: 8,
                      198: 8,
                      199: 8,
                      200: 8,
                      201: 8,
                      202: 8,
                      206: 2,
                      215: 11,
                      1816: 12}


def winerror_to_errno(winerror):
    """
    Convert a Windows error code into the matching errno code.

    Args:
        winerror: Integer error code number returned by Windows

    Returns:
        Corresponding errno error code or EINVAL if no match.

    """

    return _winerror_to_errno.get(winerror, EINVAL)

########################################


def convert_to_utf16(input_string):
    """
    Convert the input string into utf-16-le.

    Args:
        input_string: string encoded in locale.getpreferredencoding()

    Returns:
        Byte array in little endian UTF-16
    """
    if PY2 and isinstance(input_string, str):
        input_string = input_string.decode(getpreferredencoding())
    return input_string.encode('utf-16-le')

########################################


def to_registry_bytes(value, typ):
    """
    Convert input data into appropriate Windows registry type

    Args:
        value: Value to convert
        typ: Windows registry type to convert to (Example REG_DWORD)
    Returns:
        A ctypes.c_char array.
    Exception:
        ``ValueError`` for invalid input or ``TypeError`` for bad type.
    """

    # pylint: disable=too-many-branches

    # 32 bit integer?
    if typ == REG_DWORD:
        if value is None:
            value = 0
        return create_string_buffer(pack('I', value), sizeof(c_uint))

    # 64 bit integer?
    if typ == REG_QWORD:
        if value is None:
            value = 0
        return create_string_buffer(pack('Q', value), sizeof(QWORD))

    # Simple string?
    if typ in (REG_SZ, REG_EXPAND_SZ):
        # Convert None to empty string
        if value is None:
            value = u''

        # Sanity check
        if not isinstance(value, basestring):
            raise ValueError("Value must be None, string or a unicode object.")
        return create_string_buffer(convert_to_utf16(value))

    # Sequence of strings?
    if typ == REG_MULTI_SZ:
        # Convert None to empty list
        if value is None:
            value = []

        # Sanity check
        if not hasattr(value, '__iter__'):
            raise ValueError("Value must be a sequence or iterable.")

        result = []
        count = 0
        for item in value:
            if not isinstance(item, basestring):
                raise ValueError("Element %d must be a string or a unicode "
                                 "object." % count)
            if item is None:
                result.append(convert_to_utf16(u''))
            else:
                result.append(convert_to_utf16(item))
            count += 1
        # Windows expects an empty string at the end.
        result.append(convert_to_utf16(u''))

        result = b'\x00\x00'.join(result)
        return create_string_buffer(result, len(result))

    # Assume it's REG_BINARY at this point
    if value is None:
        return create_string_buffer(0)

    try:
        if not isinstance(value, (bytes, basestring)):
            # Convert integers, floats to a string.
            value = str(value)
        # Do, or do not. There is no try.
        return create_string_buffer(value, len(value))
    except TypeError:
        # pylint: disable=raise-missing-from
        raise TypeError("Objects of type '%s' can not be used as "
                        "binary registry values" % type(value))

########################################


def from_registry_bytes(input_data, input_size, typ):
    """
    Convert raw Windows registry data into an appropriate Python object.

    Args:
        input_data: Raw binary data
        input_size: Size in bytes of the input data
        typ: Windows registry type to convert from (Example REG_DWORD)

    Returns:
        Data converted to appropriate Python object, or None.
    """

    # pylint: disable=too-many-return-statements
    # pylint: disable=too-many-branches

    # If the input is a c_type, pull in the value
    if hasattr(input_size, 'value'):
        input_size = input_size.value

    # If the data type is a c_type, pull in the value
    if hasattr(typ, 'value'):
        typ = typ.value

    # 32 bit integer?
    if typ == REG_DWORD:
        if input_size == 0:
            return long(0)
        return unpack_from('I', input_data)[0]

    # 64 bit integer?
    if typ == REG_QWORD:
        if input_size == 0:
            return long(0)
        return unpack_from('Q', input_data)[0]

    # Single UTF-16 string?
    if typ in (REG_SZ, REG_EXPAND_SZ):
        # Input must be 16 bit chunks
        if input_size & 1:
            input_size -= 1

        # Sanity check on buffer size
        if hasattr(input_data, 'raw'):
            buf = input_data.raw
        else:
            buf = input_data
        if len(buf) > input_size:
            buf = buf[:input_size]

        # Convert to preferred encoding
        buf = buf.decode('utf-16-le')
        # If there is a null character in the string,
        # terminate the string there.
        input_size = buf.find('\0')
        if input_size != -1:
            return buf[:input_size]
        return buf

    # List of UTF-16 strings?
    if typ == REG_MULTI_SZ:
        # Input must be 16 bit chunks
        if input_size & 1:
            input_size -= 1

        # Sanity check on the buffer size
        if hasattr(input_data, 'raw'):
            buf = input_data.raw
        else:
            buf = input_data
        if len(buf) > input_size:
            buf = buf[:input_size]

        # Convert the entire string to preferred encoding.
        buf = buf.decode('utf-16-le')
        # Remove trailing zero, if any.
        if len(buf) == 0:
            return []

        if buf[-1] == '\0':
            buf = buf[:-1]

        # Split the string by nulls.
        return buf.split('\0')

    # Assume it's a binary data type, return as is.
    if not input_size:
        return None
    return input_data[:input_size]
