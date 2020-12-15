#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Windows constants and function common to both WSL and Cygwin implementaions.

This module contains numerous constants for Windows and functions common to
both the WSL bridge and the Cygwin/MSYS2 cdll implementations of the wslwinreg
module.
"""

## \package wslwinreg.common

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
