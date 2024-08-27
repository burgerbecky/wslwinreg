#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Package that implements winreg for MSYS and Cygwin
"""

## \package wslwinreg.cygwinapi

# Disable camel case requirement for function names
# pylint: disable=invalid-name
# pylint: disable=useless-object-inheritance
# pylint: disable=unused-argument
# pylint: disable=broad-except

from re import sub as re_sub
import array
import os.path
import subprocess
from ctypes import cdll, create_unicode_buffer, c_void_p, c_ulong, byref, \
    cast, sizeof, create_string_buffer, wstring_at, string_at, RTLD_LOCAL

from .common import PY2, builtins, ERROR_SUCCESS, ERROR_FILE_NOT_FOUND, \
    ERROR_MORE_DATA, KEY_WOW64_64KEY, KEY_WRITE, KEY_READ, REG_SZ, \
    FORMAT_MESSAGE_ALLOCATE_BUFFER, FORMAT_MESSAGE_IGNORE_INSERTS, \
    FORMAT_MESSAGE_FROM_SYSTEM, LANG_NEUTRAL, LPCVOID, LPVOID, DWORD, PDWORD, \
    LPDWORD, LONG, PLONG, PBYTE, LPBYTE, LPWSTR, LPCWSTR, HKEY, PHKEY, \
    HLOCAL, REGSAM, FILETIME, PFILETIME, SUBLANG_DEFAULT, \
    to_registry_bytes, from_registry_bytes, winerror_to_errno, BOOL

# Test kernel32 in case cdll is the broken version
try:
    cdll.kernel32
except OSError:
    from ctypes import CDLL

    ## Loaded instance of the Windows dll kernel32
    cdll.kernel32 = CDLL("Kernel32.dll", RTLD_LOCAL, None, True)

    ## Loaded instance of the Windows dll advapi32
    cdll.advapi32 = CDLL("advapi32.dll", RTLD_LOCAL, None, True)

    ## Loaded instance of the Windows dll version
    cdll.version = CDLL("version.dll", RTLD_LOCAL, None, True)

## Type long for Python 2 compatibility
try:
    long
except NameError:
    # Fake it for Python 3
    long = int

## Hack to allow Sphinx to not crash
PROPERTY_HACK = property

########################################

# Windows functions extracted from cdll

## WINBASEAPI DWORD WINAPI FormatMessageW(DWORD,LPCVOID,DWORD,DWORD,LPWSTR,
#                                         DWORD, va_list*)
FormatMessageW = cdll.kernel32.FormatMessageW
## Returns DWORD
FormatMessageW.restype = DWORD
## Argument list for FormatMessageW()
FormatMessageW.argtypes = [DWORD, LPCVOID, DWORD, DWORD, LPCVOID, DWORD,
                           c_void_p]

## WINBASEAPI DWORD WINAPI GetLastError(void);
GetLastError = cdll.kernel32.GetLastError
GetLastError.restype = DWORD
GetLastError.argtypes = []

## WINBASEAPI HLOCAL WINAPI LocalFree(HLOCAL);
LocalFree = cdll.kernel32.LocalFree
LocalFree.restype = HLOCAL
LocalFree.argtypes = [HLOCAL]

## WINBASEAPI DWORD WINAPI ExpandEnvironmentStringsW(LPCWSTR lpSrc, LPWSTR
#                                                   lpDst, DWORD nSize);
ExpandEnvironmentStringsW = cdll.kernel32.ExpandEnvironmentStringsW
ExpandEnvironmentStringsW.restype = DWORD
ExpandEnvironmentStringsW.argtypes = [LPCWSTR, LPWSTR, DWORD]

## WINADVAPI LONG WINAPI RegCloseKey(HKEY);
RegCloseKey = cdll.advapi32.RegCloseKey
RegCloseKey.restype = LONG
RegCloseKey.argtypes = [HKEY]

## WINADVAPI LONG WINAPI RegConnectRegistryW(LPCWSTR,HKEY,PHKEY);
RegConnectRegistryW = cdll.advapi32.RegConnectRegistryW
RegConnectRegistryW.restype = LONG
RegConnectRegistryW.argtypes = [LPCWSTR, HKEY, PHKEY]

## WINADVAPI LONG WINAPI RegCreateKeyW(HKEY,LPCWSTR,PHKEY);
RegCreateKeyW = cdll.advapi32.RegCreateKeyW
RegCreateKeyW.restype = LONG
RegCreateKeyW.argtypes = [HKEY, LPCWSTR, PHKEY]

## WINADVAPI LONG WINAPI RegCreateKeyW(HKEY,LPCWSTR,DWORD, LPWSTR, DWORD,
#                                     REGSAM, LPCVOID, PHKEY, LPDWORD);
RegCreateKeyExW = cdll.advapi32.RegCreateKeyExW
RegCreateKeyExW.restype = LONG
RegCreateKeyExW.argtypes = [
    HKEY,
    LPCWSTR,
    DWORD,
    LPWSTR,
    DWORD,
    REGSAM,
    LPCVOID,
    PHKEY,
    LPDWORD]

## WINADVAPI LONG WINAPI RegDeleteKeyW(HKEY,LPCWSTR);
RegDeleteKeyW = cdll.advapi32.RegDeleteKeyW
RegDeleteKeyW.restype = LONG
RegDeleteKeyW.argtypes = [HKEY, LPCWSTR]

## WINADVAPI LONG WINAPI RegDeleteKeyW(HKEY,LPCWSTR,REGSAM,DWORD);
RegDeleteKeyExW = cdll.advapi32.RegDeleteKeyExW
RegDeleteKeyExW.restype = LONG
RegDeleteKeyExW.argtypes = [HKEY, LPCWSTR, REGSAM, DWORD]

## WINADVAPI LONG WINAPI RegDeleteValueW(HKEY,LPCWSTR);
RegDeleteValueW = cdll.advapi32.RegDeleteValueW
RegDeleteValueW.restype = LONG
RegDeleteValueW.argtypes = [HKEY, LPCWSTR]

## WINADVAPI LONG WINAPI RegEnumKeyExW(HKEY,DWORD,LPWSTR,PDWORD,PDWORD,
#                                     LPWSTR,PDWORD,PFILETIME);
RegEnumKeyExW = cdll.advapi32.RegEnumKeyExW
RegEnumKeyExW.restype = LONG
RegEnumKeyExW.argtypes = [HKEY, DWORD, LPWSTR, PDWORD, PDWORD, LPWSTR,
                          PDWORD, c_void_p]

## WINADVAPI LONG WINAPI RegQueryInfoKeyW(HKEY,LPWSTR,PDWORD,PDWORD,PDWORD,
#                                        PDWORD,PDWORD,PDWORD,PDWORD,PDWORD,
#                                        PDWORD,PFILETIME);
RegQueryInfoKeyW = cdll.advapi32.RegQueryInfoKeyW
RegQueryInfoKeyW.restype = LONG
RegQueryInfoKeyW.argtypes = [HKEY, LPWSTR, PDWORD, PDWORD, PDWORD, PDWORD,
                             PDWORD, PDWORD, PDWORD, PDWORD, PDWORD, PFILETIME]

## WINADVAPI LONG WINAPI RegEnumValueW(HKEY,DWORD,LPWSTR,PDWORD,PDWORD,PDWORD,
#                                     LPBYTE,PDWORD);
RegEnumValueW = cdll.advapi32.RegEnumValueW
RegEnumValueW.restype = LONG
RegEnumValueW.argtypes = [HKEY, DWORD, LPWSTR, PDWORD, PDWORD, PDWORD,
                          LPBYTE, PDWORD]

## WINADVAPI LONG WINAPI RegFlushKey(HKEY);
RegFlushKey = cdll.advapi32.RegFlushKey
RegFlushKey.restype = LONG
RegFlushKey.argtypes = [HKEY]

## WINADVAPI LONG WINAPI RegLoadKeyW(HKEY,LPCWSTR,LPCWSTR)
RegLoadKeyW = cdll.advapi32.RegLoadKeyW
RegLoadKeyW.restype = LONG
RegLoadKeyW.argtypes = [HKEY, LPCWSTR, LPCWSTR]

## WINADVAPI LONG WINAPI RegOpenKeyExW(HKEY,LPCWSTR,DWORD,REGSAM,PHKEY)
RegOpenKeyExW = cdll.advapi32.RegOpenKeyExW
RegOpenKeyExW.restype = LONG
RegOpenKeyExW.argtypes = [HKEY, LPCWSTR, DWORD, REGSAM, PHKEY]

## WINADVAPI LONG RegQueryReflectionKey(HKEY, LPDWORD)
RegQueryReflectionKey = cdll.advapi32.RegQueryReflectionKey
RegQueryReflectionKey.restype = LONG
RegQueryReflectionKey.argtypes = [HKEY, PDWORD]

## WINADVAPI LONG RegDisbleReflectionKey(HKEY)
RegDisableReflectionKey = cdll.advapi32.RegDisableReflectionKey
RegDisableReflectionKey.restype = LONG
RegDisableReflectionKey.argtypes = [HKEY]

## WINADVAPI LONG RegEnableReflectionKey(HKEY)
RegEnableReflectionKey = cdll.advapi32.RegEnableReflectionKey
RegEnableReflectionKey.restype = LONG
RegEnableReflectionKey.argtypes = [HKEY]

## WINADVAPI LONG WINAPI RegQueryValueW(HKEY,LPCWSTR,LPWSTR,PLONG);
RegQueryValueW = cdll.advapi32.RegQueryValueW
RegQueryValueW.restype = LONG
RegQueryValueW.argtypes = [HKEY, LPCWSTR, LPWSTR, PLONG]

## WINADVAPI LONG WINAPI RegQueryValueExW(HKEY,LPCWSTR,LPDWORD,LPDWORD,LPBYTE,
#                                        LPDWORD);
RegQueryValueExW = cdll.advapi32.RegQueryValueExW
RegQueryValueExW.restype = LONG
RegQueryValueExW.argtypes = [HKEY, LPCWSTR, LPDWORD, LPDWORD, LPBYTE, LPDWORD]

## WINADVAPI LONG WINAPI RegSaveKeyW(HKEY,LPCWSTR,LPSECURITY_ATTRIBUTES);
RegSaveKeyW = cdll.advapi32.RegSaveKeyW
RegSaveKeyW.restype = LONG
RegSaveKeyW.argtypes = [HKEY, LPCWSTR, c_void_p]

## WINADVAPI LONG WINAPI RegSetValueW(HKEY,LPCWSTR,DWORD,LPCWSTR,DWORD);
RegSetValueW = cdll.advapi32.RegSetValueW
RegSetValueW.restype = LONG
RegSetValueW.argtypes = [HKEY, LPCWSTR, DWORD, LPCWSTR, DWORD]

## WINADVAPI LONG WINAPI RegSetValueExW(HKEY,LPCWSTR,DWORD,DWORD,const BYTE*,
#                                      DWORD);
RegSetValueExW = cdll.advapi32.RegSetValueExW
RegSetValueExW.restype = LONG
RegSetValueExW.argtypes = [HKEY, LPCWSTR, DWORD, DWORD, PBYTE, DWORD]

## WINADVAPI DWORD WINAPI GetFileVersionInfoSizeW(LPCWSTR, LPDWORD);
GetFileVersionInfoSizeW = cdll.version.GetFileVersionInfoSizeW
GetFileVersionInfoSizeW.restype = DWORD
GetFileVersionInfoSizeW.argtypes = [LPCWSTR, LPDWORD]

## WINADVAPI BOOL WINAPI GetFileVersionInfoW(LPCWSTR, DWORD, DWORD, LPVOID);
GetFileVersionInfoW = cdll.version.GetFileVersionInfoW
GetFileVersionInfoW.restype = BOOL
GetFileVersionInfoW.argtypes = [LPCWSTR, DWORD, DWORD, LPVOID]

## WINADVAPI BOOL WINAPI VerQueryValueW(LPCVOID, LPCWSTR, LPVOID, PUINT);
VerQueryValueW = cdll.version.VerQueryValueW
VerQueryValueW.restype = BOOL
VerQueryValueW.argtypes = [LPCVOID, LPCWSTR, LPVOID, PLONG]

########################################


def winerror_to_string(winerror):
    """
    Convert a windows integer error code into a descriptive string.

    Call FormatMessageW() in Windows to perform the actual work.

    Args:
        winerror: Integer error code from Windows

    Returns:
        String describing the error.
    """

    # buf is actually a string, but is initially set to NULL
    buf = c_void_p(None)
    msg_len = FormatMessageW(
        # Error API error
        FORMAT_MESSAGE_ALLOCATE_BUFFER |
        FORMAT_MESSAGE_FROM_SYSTEM |
        FORMAT_MESSAGE_IGNORE_INSERTS,
        # Message source
        None,
        c_ulong(winerror),
        # Use the user's default language
        (LANG_NEUTRAL << 10) + SUBLANG_DEFAULT,
        byref(buf),
        # Size is not used
        0,
        # No arguments
        None)

    if msg_len == 0:
        # Only seen this in out of mem situations
        return "Windows Error 0x%X" % winerror

    result = cast(buf, LPWSTR).value
    LocalFree(buf)

    # Clean up the string before returning
    return re_sub(r"[\s.]*$", "", result)

########################################


def check_LRESULT(return_code):
    """
    Test LRESULT for an error code and raise exception on error condition.

    If the input value is zero, return the value. If the input is a non-zero
    code, raise a WindowsError() exception unless it's ERROR_FILE_NOT_FOUND.
    In the latter case, raise a ``FileNotFoundError``.

    Args:
        return_code: Windows integer error code.
    Returns:
        Error code, usually zero.
    Exception:
        ``WindowsError`` or ``FileNotFoundError``
    """

    # Make sure it's not a ctype class
    if not isinstance(return_code, (int, long)):
        return_code = return_code.value

    # Was there an error?
    if return_code != ERROR_SUCCESS:
        # Special case, unit tests require a FileNotFoundError
        if return_code == ERROR_FILE_NOT_FOUND:
            raise FileNotFoundError(winerror_to_string(return_code))

        # Throw a WindowsError exception
        raise WindowsError(return_code)

    # Return the zero.
    return return_code

########################################


# pylint: disable=redefined-builtin

class WindowsError(OSError):
    """
    This exception doesn't exist in Cygwin/MSYS, provide it.
    """

    # pylint: disable=super-init-not-called
    def __init__(self, winerror, strerror=None, filename=None):
        """
        Initialize a WindowsError exception

        Args:
            winerror: The windows error code
            strerror: The string describing the error
            filename: Name of the file that caused this error, if applicable.
        """

        # Check if an error was provided
        if winerror == 0:
            # Call GetLastError() in windows to make sure
            winerror = GetLastError()

        ## Windows error code
        self.winerror = winerror

        ## Linux style error code
        self.errno = winerror_to_errno(winerror)

        if strerror is None:
            strerror = winerror_to_string(winerror)

        ## Description string of the error
        self.strerror = strerror

        ## Name of the responsible file for this error
        self.filename = filename

    def __str__(self):
        """
        Convert the class into a string.

        Returns:
            String describing the error contained.
        """
        if self.filename is not None:
            return "[Error %s] %s: %s" % (self.winerror, self.strerror,
                                          repr(self.filename))
        return "[Error %s] %s" % (self.winerror, self.strerror)


# Ensure this exception is available globally.
builtins.WindowsError = WindowsError

########################################


class PyHKEY(object):
    """
    A Python object representing a win32 registry key.

    This object wraps a Windows HKEY object, automatically closing it when the
    object is destroyed. To guarantee cleanup, you can call either the Close()
    method on the object, or the CloseKey() function.

    All registry functions in this module return one of these objects.

    All registry functions in this module which accept a handle object also
    accept an integer, however, use of the handle object is encouraged.

    Handle objects provide semantics for __bool__() – thus

    @code
        if handle:
            print("Yes")
    @endcode

    will print Yes if the handle is currently valid (has not been closed or
    detached).

    The object also support comparison semantics, so handle objects will compare
    true if they both reference the same underlying Windows handle value.

    Handle objects can be converted to an integer (e.g., using the built-in
    int() function), in which case the underlying Windows handle value is
    returned. You can also use the Detach() method to return the integer handle,
    and also disconnect the Windows handle from the handle object.
    """

    def __init__(self, hkey, null_ok=False):
        """
        Initialize the PyHKEY class.

        Args:
            hkey: Integer value representing the pointer to the HKEY
            null_ok: True if None is acceptable.
        """
        if not isinstance(hkey, (int, long)):
            if not null_ok or not isinstance(hkey, type(None)):
                raise TypeError("A handle must be an integer")

        ## Integer that represents the HANDLE pointer
        self.hkey = hkey

    def __del__(self):
        """
        Called when this object is garbage collected.
        """
        if self.hkey:
            # Ignore errors.
            try:
                self.Close()
            except BaseException:
                pass

    def Close(self):
        """
        Closes the underlying Windows handle.

        Note:
            If the handle is already closed, no error is raised.
        """
        if self.hkey:
            check_LRESULT(RegCloseKey(self.hkey))
        self.hkey = 0

    def Detach(self):
        """
        Detaches the Windows handle from the handle object.

        Note:
        The result is the value of the handle before it is detached. If the
        handle is already detached, this will return zero.

        After calling this function, the handle is effectively invalidated,
        but the handle is not closed.  You would call this function when you
        need the underlying win32 handle to exist beyond the lifetime of the
        handle object.

        On 64 bit windows, the result of this function is a long integer.

        Returns:
            Previous HKEY integer.
        """
        hkey = self.hkey
        self.hkey = 0
        return hkey

    def _handle(self):
        """
        The integer Win32 handle.
        """
        return self.hkey

    ## The integer Win32 handle. Actually ``property(_handle)``
    handle = PROPERTY_HACK(_handle)

    def __enter__(self):
        """
        Called when object is entered.

        Note:
            Needed for the Python ``with`` statement.
        """
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Release handle on class destruction.

        Note:
            Needed for the Python ``with`` statement.
        """
        self.Close()
        return False

    def __hash__(self):
        """
        Convert the object into a hash.

        Note:
            The implementation returns the id, which should be
            random enough.
        """
        return id(self)

    def __int__(self):
        """
        Converting a handle to an integer returns the Win32 handle.
        """
        return self.hkey

    if PY2:
        def __nonzero__(self):
            """
            Handles with an open object return true, otherwise false.
            """
            return bool(self.hkey)
    else:
        def __bool__(self):
            """
            Handles with an open object return true, otherwise false.
            """
            return bool(self.hkey)

    def __repr__(self):
        """
        Return descriptive string for the class object.
        """
        return "<PyHKEY at %08X (%08X)>" % (id(self), self.hkey)

    def __str__(self):
        """
        Return short string for the handle object.
        """
        return "<PyHKEY:%08X>" % self.hkey

    ## Python sort description.
    _as_parameter_ = property(lambda self: self.hkey)

    @staticmethod
    def make(hkey, null_ok=None):
        """
        Convert a pointer into a PyHKEY object.
        """

        # Already converted?
        if isinstance(hkey, PyHKEY):
            return hkey

        # Is it a valid integer?
        if isinstance(hkey, (int, long)):
            return PyHKEY(hkey)

        # None, if None is allowed.
        if null_ok and isinstance(hkey, type(None)):
            return PyHKEY(None)

        # This didn't end well.
        raise TypeError("A handle must be a HKEY object or an integer")


########################################


def CloseKey(hkey):
    """
    Closes a previously opened registry key.

    The hkey argument specifies a previously opened key.

    Args:
        hkey: PyHKEY object or None.

    Note:
        If hkey is not closed using this method (or via hkey.Close()),
        it is closed when the hkey object is destroyed by Python.

    """
    PyHKEY.make(hkey).Close()

########################################


def ConnectRegistry(computer_name, key):
    """
    Establishes a connection to a predefined registry handle.

    Establishes a connection to a predefined registry handle on another
    computer, and returns a handle object.

    Args:
        computer_name: Is the name of the remote computer, of the form
            ``r"\\computername"``. If ``None``, the local computer is used.
        key: Is the predefined handle to connect to.
    Returns:
        PyHKEY object
    Exception:
        ``WindowsError`` or ``FileNotFileError``
    """

    result = HKEY()
    rc = RegConnectRegistryW(computer_name, PyHKEY.make(key), byref(result))
    if rc != ERROR_SUCCESS:
        check_LRESULT(rc)
    return PyHKEY(result.value)

########################################


def CreateKey(key, sub_key):
    """
    Creates or opens the specified key.

    If key is one of the predefined keys, sub_key may be None. In that case,
    the handle returned is the same key handle passed in to the function.

    If the key already exists, this function opens the existing key.

    Args:
        key: Is an already open key, or one of the predefined HKEY_* constants.
        sub_key: Is a string that names the key this method opens or creates.
    Returns:
        Handle of the opened key.
    Exception:
        ``WindowsError`` or ``FileNotFileError``
    """

    result = HKEY()
    rc = RegCreateKeyW(PyHKEY.make(key), sub_key, byref(result))
    if rc != ERROR_SUCCESS:
        check_LRESULT(rc)
    return PyHKEY(result.value)

########################################


def CreateKeyEx(key, sub_key, reserved=0, access=KEY_WRITE):
    """
    Creates or opens the specified key.

    If key is one of the predefined keys, sub_key may be None. In that case,
    the handle returned is the same key handle passed in to the function.

    If the key already exists, this function opens the existing key.

    Args:
        key: Is an already open key, or one of the predefined HKEY_* constants
        sub_key: Is a string that names the key this method opens or creates.
        reserved: Is a reserved integer, and must be zero. The default is zero.
        access: Os an integer that specifies an access mask that describes the
            desired security access for the key. Default is common.KEY_WRITE.

    Returns:
        Handle of the opened key.
    Exception:
        ``WindowsError`` or ``FileNotFileError``
    """

    result = HKEY()
    rc = RegCreateKeyExW(
        PyHKEY.make(key),
        sub_key,
        reserved,
        None,
        0,
        access,
        None,
        byref(result),
        None)
    if rc != ERROR_SUCCESS:
        check_LRESULT(rc)
    return PyHKEY(result.value)

########################################


def DeleteKey(key, sub_key):
    """
    Deletes the specified key.

    If the method succeeds, the entire key, including all of its values,
    is removed.

    Note:
        This method can not delete keys with subkeys.

    Args:
        key: Is an already open key, or one of the predefined HKEY_* constants.
        sub_key: Is a string that must be a subkey of the key identified by the
            key parameter. This value must not be ``None``, and the key may not
            have subkeys.
    Exception:
        ``WindowsError``
    """

    rc = RegDeleteKeyW(PyHKEY.make(key), sub_key)
    if rc != ERROR_SUCCESS:
        check_LRESULT(rc)

########################################


def DeleteKeyEx(key, sub_key, access=KEY_WOW64_64KEY, reserved=0):
    """
    Deletes the specified key.

    If the method succeeds, the entire key, including all of its values,
    is removed.

    Note:
        This method can not delete keys with subkeys.

    Args:
        key: Is an already open key, or any one of the predefined
            HKEY_* constants.

        sub_key: Os a string that must be a subkey of the key identified by the
            key parameter. This value must not be ``None``, and the key may not
            have subkeys.

        access: Is an integer that specifies an access mask that describes the
            desired security access for the key. Default
            is common.KEY_WOW64_64KEY.

        reserved: Is a reserved integer, and must be zero. The default is zero.
    Exception:
        ``WindowsError``
    """

    rc = RegDeleteKeyExW(PyHKEY.make(key), sub_key, access, reserved)
    if rc != ERROR_SUCCESS:
        check_LRESULT(rc)

########################################


def DeleteValue(key, value):
    """
    Removes a named value from a registry key.

    Args:
        key: Is an already open key, or any one of the predefined
            HKEY_* constants.
        value: Is a string that identifies the value to remove.
    Exception:
        ``WindowsError`` or ``FileNotFileError``
    """

    rc = RegDeleteValueW(PyHKEY.make(key), value)
    if rc != ERROR_SUCCESS:
        check_LRESULT(rc)

########################################


def EnumKey(key, index):
    """
    Enumerates subkeys of an open registry key, returning a string.

    The function retrieves the name of one subkey each time it is called.
    It is typically called repeatedly until an ``OSError`` exception is
    raised, indicating no more values are available.

    Args:
        key: Is an already open key, or any one of the predefined
            HKEY_* constants.
        index: Is an integer that identifies the index of the key to retrieve.

    Exception:
        ``WindowsError`` or ``FileNotFileError``
    """

    # max key name length is 256 if unterminated
    tmpbuf = create_unicode_buffer(257)
    length = DWORD(sizeof(tmpbuf))
    rc = RegEnumKeyExW(PyHKEY.make(key), index, tmpbuf, byref(length),
                       None, None, None, None)
    if rc != ERROR_SUCCESS:
        check_LRESULT(rc)
    return tmpbuf[:length.value]

########################################


def EnumValue(key, index):
    # pylint: disable=line-too-long
    """
    Enumerates values of an open registry key, returning a tuple.

    The function retrieves the name of one subkey each time it is called.
    It is typically called repeatedly, until an ``OSError`` exception is
    raised, indicating no more values.

    | Index | Meaning |
    | ----- | ------- |
    | 0 | A string that identifies the value. |
    | 1 | An object that holds the value data, and whose type depends on the underlying registry type |
    | 2 | An integer that identifies the type of the value data |

    Args:
        key: Is an already open key, or any one of the predefined
            HKEY_* constants.
        index: Is an integer that identifies the index of the value to retrieve.
    Returns:
       A tuple of 3 items.
    Exception:
        ``WindowsError`` or ``FileNotFileError``
    """

    # Check the key
    hkey = PyHKEY.make(key)

    # Get information from the key
    value_size = DWORD()
    data_size = DWORD()
    check_LRESULT(
        RegQueryInfoKeyW(
            hkey,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            byref(value_size),
            byref(data_size),
            None,
            None))

    # Include null terminators
    value_size.value += 1
    data_size.value += 1

    value_buf = create_unicode_buffer(value_size.value)
    data_buf = create_string_buffer(data_size.value)
    save_data_size = data_size.value
    save_value_size = value_size.value
    typ = DWORD()
    while True:
        rc = RegEnumValueW(hkey, index, value_buf, byref(value_size), None,
                          byref(typ), data_buf, byref(data_size))
        if rc != ERROR_MORE_DATA:
            break
        del data_buf
        save_data_size = save_data_size * 2
        data_size.value = save_data_size
        data_buf = create_string_buffer(save_data_size)
        value_size.value = save_value_size

    # Throw if the error code is not ERROR_SUCCESS
    check_LRESULT(rc)
    return (value_buf[:value_size.value],
            from_registry_bytes(data_buf, data_size, typ),
            typ.value)

########################################


def ExpandEnvironmentStrings(str):
    """
    Expands environment variables.

    Expands environment variable placeholders %NAME% in strings
    like REG_EXPAND_SZ.

    Args:
        str: String to expand.
    Returns:
        Expanded string
    Exception:
        ``WindowsError``
    """

    # Determine the size of the return value
    result_size = ExpandEnvironmentStringsW(str, None, 0)
    # If the return value is zero, there was an error
    if not result_size:
        raise WindowsError(0)

    # Make a buffer and call the function again
    result_size += 1
    result_buffer = create_unicode_buffer(result_size)
    length = DWORD(sizeof(result_buffer))
    result_size = ExpandEnvironmentStringsW(str, result_buffer, length)
    if not result_size:
        raise WindowsError(0)
    return result_buffer.value

########################################


def FlushKey(key):
    """
    Writes all the attributes of a key to the registry.

    It is not necessary to call ``FlushKey()`` to change a key. Registry
    changes are flushed to disk by the registry using its lazy flusher.
    Registry changes are also flushed to disk at system shutdown. Unlike
    ``CloseKey()``, the ``FlushKey()`` method returns only when all the
    data has been written to the registry. An application should only
    call ``FlushKey()`` if it requires absolute certainty that registry
    changes are on disk.

    Note:
        If you don’t know whether a ``FlushKey()`` call is required, it
        probably isn’t.
    Args:
        key: Is an already open key, or any one of the predefined
        HKEY_* constants.
    Exception:
        ``WindowsError``
    """

    rc = RegFlushKey(PyHKEY.make(key))
    if rc != ERROR_SUCCESS:
        check_LRESULT(rc)

########################################


def LoadKey(key, sub_key, file_name):
    """
    Creates a subkey under the specified key.

    Creates a subkey under the specified key and stores registration
    information from a specified file into that subkey.

    This file must have been created with the SaveKey() function.
    Under the file allocation table (FAT) file system, the filename may not
    have an extension.

    A call to ``LoadKey()`` fails if the calling process does not have the
    SE_RESTORE_PRIVILEGE privilege.

    If key is a handle returned by ``ConnectRegistry()``, then the path
    specified in fileName is relative to the remote computer.

    Args:
        key: Is a handle returned by ``ConnectRegistry()`` or one of the
            constants common.HKEY_USERS or common.HKEY_LOCAL_MACHINE.
        sub_key: Is a string that identifies the sub_key to load
        file_name: Is the name of the file to load registry data from.

    Exception:
        ``WindowsError`` or ``FileNotFileError``
    """

    rc = RegLoadKeyW(PyHKEY.make(key), sub_key, file_name)
    if rc != ERROR_SUCCESS:
        check_LRESULT(rc)

########################################


def OpenKey(key, sub_key, reserved=0, access=KEY_READ):
    """
    Opens the specified key, returning a handle object.

    Args:
        key: Is an already open key, or any one of the predefined
            HKEY_* constants.
        sub_key: Is a string that identifies the sub_key to open
        reserved: Is a reserved integer, and must be zero.
            Default is zero.
        access: Is an integer that specifies an access mask that
            describes the desired security access for the key. Default
            is KEY_READ.

    Returns:
        A new handle to the specified key.

    Exception:
        ``WindowsError`` or ``FileNotFileError``
    """

    result = HKEY()
    rc = RegOpenKeyExW(
        PyHKEY.make(key),
        sub_key,
        reserved,
        access,
        byref(result))
    if rc != ERROR_SUCCESS:
        check_LRESULT(rc)
    return PyHKEY.make(result.value)

########################################


def OpenKeyEx(key, sub_key, reserved=0, access=KEY_READ):
    """
    Opens the specified key, returning a handle object.

    Args:
        key: Is an already open key, or any one of the predefined
            HKEY_* constants.
        sub_key: Is a string that identifies the sub_key to open
        reserved: Is a reserved integer, and must be zero.
            Default is zero.
        access: Is an integer that specifies an access mask that
            describes the desired security access for the key. Default
            is KEY_READ.

    Returns:
        A new handle to the specified key.

    Exception:
        ``WindowsError`` or ``FileNotFileError``
    """
    return OpenKey(key, sub_key, reserved, access)

########################################


def QueryInfoKey(key):
    # pylint: disable=line-too-long
    """
    Returns information about a key, as a tuple.

    | Index | Meaning |
    | ----- | ------- |
    | 0 | An integer giving the number of sub keys this key has. |
    | 1 | An integer giving the number of values this key has. |
    | 2 | An integer giving when the key was last modified (if available) as 100’s of nanoseconds since Jan 1, 1601. |

    Args:
        key: Is an already open key, or any one of the predefined
            HKEY_* constants.
    Returns:
        A tuple of 3 items.
    Exception:
        ``WindowsError`` or ``FileNotFileError``
    """

    num_sub_keys = DWORD()
    num_values = DWORD()
    last_write_time = FILETIME()
    check_LRESULT(RegQueryInfoKeyW(PyHKEY.make(key), None, None, None,
                             byref(num_sub_keys), None, None,
                             byref(num_values), None, None, None,
                             byref(last_write_time)))
    last_write_time = (last_write_time.high << 32) | last_write_time.low
    return (num_sub_keys.value, num_values.value, last_write_time)

########################################


def QueryValue(key, sub_key):
    """
    Retrieves the unnamed value for a key, as a string.

    Values in the registry have name, type, and data components. This method
    retrieves the data for a key’s first value that has a NULL name. But the
    underlying API call doesn’t return the type, so always use
    ``QueryValueEx()`` if possible.

    Args:
        key: Is an already open key, or any one of the predefined
            HKEY_* constants.
        sub_key: Is a string that holds the name of the subkey with which the
            value is associated. If this parameter is None or empty, the
            function retrieves the value set by the ``SetValue()`` method for
            the key identified by ``key``.
    Exception:
        ``WindowsError`` or ``FileNotFileError``
    """

    hkey = PyHKEY.make(key)
    buf_size = LONG()
    rc = RegQueryValueW(hkey, sub_key, None, byref(buf_size))
    if rc == ERROR_MORE_DATA:
        buf_size.value = 256
    elif rc != ERROR_SUCCESS:
        check_LRESULT(rc)

    buffer_size = buf_size.value
    buf = create_unicode_buffer(buf_size.value)
    while True:
        rc = RegQueryValueW(hkey, sub_key, buf, byref(buf_size))
        if rc != ERROR_MORE_DATA:
            break
        buffer_size = buffer_size * 2
        del buf
        buf_size.value = buffer_size
        buf = create_unicode_buffer(buf_size.value)

    check_LRESULT(rc)
    return buf.value

########################################


def QueryValueEx(key, value_name):
    """
    Retrieves the type and data for a specified value name.

    Retrieves the type and data for a specified value name associated with an
    open registry key.

    | Index | Meaning |
    | ----- | ------- |
    | 0 | The value of the registry item. |
    | 1 | An integer giving the registry type for this value. |

    Args:
        key: Is an already open key, or any one of the predefined
            HKEY_* constants.
        value_name: Is a string indicating the value to query.
    Returns:
        A tuple of 2 items.
    Exception:
        ``WindowsError`` or ``FileNotFileError``
    """

    hkey = PyHKEY.make(key)
    buf_size = DWORD()
    rc = RegQueryValueExW(hkey, value_name, None, None, None,
                          byref(buf_size))
    # Set to 256 for looping
    if rc == ERROR_MORE_DATA:
        buf_size.value = 256
    elif rc != ERROR_SUCCESS:
        check_LRESULT(rc)

    # buf is a byte array
    buffer_size = buf_size.value
    buf = create_string_buffer(buf_size.value)
    typ = DWORD()
    while True:
        rc = RegQueryValueExW(hkey, value_name, None, byref(typ), buf,
                             byref(buf_size))
        if rc != ERROR_MORE_DATA:
            break
        buffer_size = buffer_size * 2
        del buf
        buf_size.value = buffer_size
        buf = create_string_buffer(buffer_size)

    check_LRESULT(rc)
    return (from_registry_bytes(buf, buf_size, typ),
            typ.value)

########################################


def SaveKey(key, file_name):
    """
    Saves the specified key, and all its subkeys to the specified file.

    If key represents a key on a remote computer, the path described by
    file_name is relative to the remote computer. The caller of this method
    must possess the SeBackupPrivilege security privilege.

    This function passes NULL for security_attributes to the API.

    Note:
        Privileges are different than permissions.

    Args:
        key: Is an already open key, or any one of the predefined
            HKEY_* constants.
        file_name: Is the name of the file to save registry data to.
            This file cannot already exist. If this filename includes an
            extension, it cannot be used on file allocation table (FAT) file
            systems by the ``LoadKey()`` method.
    Exception:
        ``WindowsError`` or ``FileNotFileError``
    """

    rc = RegSaveKeyW(PyHKEY.make(key), file_name, None)
    if rc != ERROR_SUCCESS:
        check_LRESULT(rc)

########################################


def SetValue(key, sub_key, type, value):
    """
    Associates a value with a specified key.

    If the key specified by the sub_key parameter does not exist,
    the SetValue function creates it.

    Value lengths are limited by available memory. Long values
    (more than 2048 bytes) should be stored as files with the
    filenames stored in the configuration registry.
    This helps the registry perform efficiently.

    The key identified by the ``key`` parameter must have been
    opened with common.KEY_SET_VALUE access.

    Args:
        key: Is an already open key, or any one of the predefined
            HKEY_* constants.
        sub_key: Is a string that names the subkey with which the
            value is associated.
        type: is an integer that specifies the type of the
            data. Currently this must be REG_SZ, meaning only
            strings are supported. Use the ``SetValueEx()`` function
            for support for other data types.
        value: Is a string that specifies the new value.
    Exception:
        ``TypeError``, ``WindowsError`` or ``FileNotFileError``
    """

    if type != REG_SZ:
        raise TypeError("Type must be wslwinreg.REG_SZ")
    value_buf = create_unicode_buffer(value)
    rc = RegSetValueW(PyHKEY.make(key), sub_key,
                      REG_SZ, value_buf, sizeof(value_buf))
    if rc != ERROR_SUCCESS:
        check_LRESULT(rc)

########################################


def SetValueEx(key, value_name, reserved, type, value):
    """
    Stores data in the value field of an open registry key.

    This method can also set additional value and type information for the
    specified key.  The key identified by the key parameter must have been
    opened with KEY_SET_VALUE access.

    To open the key, use the CreateKeyEx() or OpenKeyEx() methods.

    Value lengths are limited by available memory. Long values (more than
    2048 bytes) should be stored as files with the filenames stored in
    the configuration registry.  This helps the registry perform efficiently.

    Args:
        key: Is an already open key, or any one of the predefined
            HKEY_* constants.
        value_name: Is a string that names the subkey with which
            the value is associated.
        reserved: can be anything – zero is always passed to the API.
        type: Is an integer that specifies the type of the data.
        value: Is a string that specifies the new value.
    Exception:
        ``WindowsError`` or ``FileNotFileError``
    """

    temp_buf = to_registry_bytes(value, type)
    rc = RegSetValueExW(PyHKEY.make(key), value_name, 0, type,
                        temp_buf, len(temp_buf))
    del temp_buf
    if rc != ERROR_SUCCESS:
        check_LRESULT(rc)


########################################


def DisableReflectionKey(key):
    """
    Disables registry reflection.

    Disables registry reflection for 32-bit processes running on a
    64-bit operating system.

    If the key is not on the reflection list, the function succeeds
    but has no effect. Disabling reflection for a key does not
    affect reflection of any subkeys.

    Args:
        key: Is an already open key, or one of the predefined
            HKEY_* constants.
    Exception:
        ``WindowsError``
    """

    check_LRESULT(RegDisableReflectionKey(PyHKEY.make(key)))

########################################


def EnableReflectionKey(key):
    """
    Restores registry reflection for the specified disabled key.

    Restoring reflection for a key does not affect reflection of any subkeys.

    Args:
        key: Is an already open key, or one of the predefined
            HKEY_* constants.
    Exception:
        ``WindowsError``
    """

    check_LRESULT(RegEnableReflectionKey(PyHKEY.make(key)))

########################################


def QueryReflectionKey(key):
    """
    Determines the reflection state for the specified key.

    Args:
        key: Is an already open key, or any one of the predefined
            HKEY_* constants.
    Returns:
        ``True`` if reflection is disabled.
    """

    is_reflection_disabled = DWORD()
    check_LRESULT(
        RegQueryReflectionKey(
            PyHKEY.make(key),
            byref(is_reflection_disabled)))
    return is_reflection_disabled != 0

########################################


def convert_to_windows_path(path_name):
    """
    Convert a MSYS/Cygwin path to windows if needed.

    If the path is already Windows format, it will be returned unchanged.

    Args:
        path_name: Windows or Linux pathname
    Return:
        Pathname converted to Windows.
    See Also:
        convert_from_windows_path
    """

    # Network drive name?
    if path_name.startswith("\\\\") or ":" in path_name:
        return path_name

    # The tool doesn't process ~ properly, help it by preprocessing here.
    args = ("cygpath",
        "-a",
        "-w",
        os.path.abspath(os.path.expanduser(path_name))
            )

    # Perform the conversion
    tempfp = subprocess.Popen(args, stdout=subprocess.PIPE,
                              stderr=None, universal_newlines=True)
    # Get the string returned by cygpath
    stdoutstr, _ = tempfp.communicate()

    # Error? Fail
    if tempfp.returncode:
        return None
    return stdoutstr.strip()

########################################


def convert_from_windows_path(path_name):
    """
    Convert an absolute Windows path to Cygwin/MSYS2.

    If the path is already Cygwin/MSYS2 format, it will be returned unchanged.

    Args:
        path_name: Absolute Windows pathname
    Return:
        Pathname converted to Linux.
    See Also:
        convert_to_windows_path
    """

    # Network drive name?
    if path_name[0] in ("~", "/"):
        return path_name

    # Create command list
    args = ("cygpath", "-a", "-u", path_name)

    # Perform the conversion
    tempfp = subprocess.Popen(args, stdout=subprocess.PIPE,
                              stderr=None, universal_newlines=True)
    # Get the string returned by cygpath
    stdoutstr, _ = tempfp.communicate()

    # Error? Fail
    if tempfp.returncode:
        return None
    return stdoutstr.strip()

########################################


def get_file_info(path_name, string_name):
    r"""
    Extract information from a windows exe file version resource.

    Given a windows exe file, extract the "StringFileInfo" resource and
    parse out the data chunk named by string_name.

    Full list of resource names:
        https://docs.microsoft.com/en-us/windows/desktop/menurc/stringfileinfo-block

    Examples:
        file_version = get_file_info("devenv.exe", "FileVersion")
        product_version =  get_file_info("devenv.exe", "ProductVersion")

    Args:
        path_name: Name of the windows file.
        string_name: Name of the data chunk to retrieve

    Return:
        None if no record found or an error, or a valid string
    """

    # Handle import for Cygwin
    path_name = convert_to_windows_path(path_name)

    # Ensure it's unicode
    wchar_filename = LPWSTR(path_name)

    # Call windows to get the data size
    size = GetFileVersionInfoSizeW(wchar_filename, None)

    # Was there no data to return?
    if size:

        # Create buffer for resource data
        res_data = create_string_buffer(size)

        # Extract the file data
        GetFileVersionInfoW(
            wchar_filename, 0, size, res_data)

        # Find the default codepage (Not everything is in English)
        record = LPVOID()
        length = LONG()
        VerQueryValueW(
            res_data,
            "\\VarFileInfo\\Translation",
            byref(record),
            byref(length))
        # Was a codepage found?
        if length.value:

            # Parse out the first found codepage (It's the default
            # language) it's in the form of two 16 bit shorts
            codepages = array.array(
                "H", string_at(
                    record.value, length.value))

            # Extract information from the version using unicode and
            # the proper codepage
            if VerQueryValueW(
                    res_data,
                    "\\StringFileInfo\\{0:04x}{1:04x}\\{2}".format(
                        codepages[0],
                        codepages[1],
                        string_name),
                    byref(record),
                    byref(length)):
                # Return the final result removing the terminating zero
                return wstring_at(record.value, length.value - 1)
    return None
