#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Package that implements winreg for Windows Subsystem for Linux
"""

## \package wslwinreg.wslapi

# Disable camel case requirement for function names
# pylint: disable=invalid-name
# pylint: disable=useless-object-inheritance
# pylint: disable=unused-argument
# pylint: disable=broad-except
# pylint: disable=redefined-builtin
# pylint: disable=raise-missing-from

import os
import stat
import subprocess
import socket
import platform
import struct
from enum import IntEnum
from .common import KEY_WRITE, KEY_WOW64_64KEY, KEY_READ, PY2, \
    winerror_to_errno, builtins, ERROR_FILE_NOT_FOUND, from_registry_bytes, \
    REG_SZ, to_registry_bytes


## Type long for Python 2 compatibility
try:
    long
except NameError:
    # Fake it for Python 3
    long = int

## Type basestring for Python 2 compatibility
try:
    basestring
except NameError:
    # Fake it for Python 3
    basestring = str

class Commands(IntEnum):
    """
    Commands to send to the bridging executable.
    """

    ## Exit the server
    ABORT = 0

    ## Connection handshake
    CONNECT = 1

    ## Perform CloseKey()
    CLOSE_KEY = 2

    ## Perform ConnectRegistry()
    CONNECT_REGISTRY = 3

    ## Perform CreateKey()
    CREATE_KEY = 4

    ## Perform CreateKeyEx()
    CREATE_KEY_EX = 5

    ## Perform DeleteKey()
    DELETE_KEY = 6

    ## Perform DeleteKeyEx()
    DELETE_KEY_EX = 7

    ## Perform DeleteValue()
    DELETE_VALUE = 8

    ## Perform EnumKey()
    ENUM_KEY = 9

    ## Perform EnumValue()
    ENUM_VALUE = 10

    ## Perform ExpandEnvironmentStrings()
    EXPAND_ENVIRONMENTSTRINGS = 11

    ## Perform FlushKey()
    FLUSH_KEY = 12

    ## Perform LoadKey()
    LOAD_KEY = 13

    ## Perform OpenKey()
    OPEN_KEY = 14

    ## Perform OpenKeyEx()
    OPEN_KEY_EX = 15

    ## Perform QueryInfoKey()
    QUERY_INFO_KEY = 16

    ## Perform QueryValue()
    QUERY_VALUE = 17

    ## Perform QueryValueEx()
    QUERY_VALUE_EX = 18

    ## Perform SaveKey()
    SAVE_KEY = 19

    ## Perform SetValue()
    SET_VALUE = 20

    ## Perform SetValueEx()
    SET_VALUE_EX = 21

    ## Perform DisableReflectionKey()
    DISABLE_REFLECTION_KEY = 22

    ## Perform EnableReflectionKey()
    ENABLE_REFLECTION_KEY = 23

    ## Perform QueryReflectionKey()
    QUERY_REFLECTION_KEY = 24

    ## Perform get_file_into()
    GET_FILE_INFO = 25

## Loopback address
_LOCALHOST = "127.0.0.1"

## Transmission buffer size
_BUFFER_SIZE = 1024

## Directory for the windows executables
_WIN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")

## Set the exe suffix for the CPU in use
_EXESUFFIX = machine = platform.machine().lower()

# Use a common suffix for amd64 instruction sets
if _EXESUFFIX in ("amd64", "x86_64", "em64t"):
    _EXESUFFIX = "x64"

## Patch to the executable to bridge
_WIN_EXE = os.path.join(_WIN_DIR, "backend-" + _EXESUFFIX + ".exe")

# Make sure it's executable

## Saved stat for the backend server
_STAT = os.stat(_WIN_EXE)
if not _STAT.st_mode & stat.S_IEXEC:
    os.chmod(_WIN_EXE, _STAT.st_mode | stat.S_IEXEC)
del _STAT

# Prepare a socket to be waiting for the exe once it is launched

## Socket used for listening for the exe
_LISTEN_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
_LISTEN_SOCKET.bind((_LOCALHOST, 0))

## Semi-random port assigned to the socket by the operating system
_LISTEN_PORT = _LISTEN_SOCKET.getsockname()[1]

# Start listening
_LISTEN_SOCKET.listen(1)

try:
    ## Popen object for the bridge executable
    _EXEC_FP = subprocess.Popen(
        (_WIN_EXE, "-p", str(_LISTEN_PORT)),
        cwd=_WIN_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True)
except OSError:
    raise ImportError("Windows executable {} for bridging not found.".format(
        _WIN_EXE))

# At this point, the exe had started, connect to it.
_LISTEN_SOCKET.settimeout(10.0)
try:
    ## @var _CONNECTION_ADDR
    # Connection address

    ## Connection socket
    _CONNECTION_SOCKET, _CONNECTION_ADDR = _LISTEN_SOCKET.accept()
except socket.timeout:
    raise ImportError("Failure to connect with bridging executable")

# Set the timeout
_CONNECTION_SOCKET.settimeout(5.0)

if _CONNECTION_SOCKET.recv(_BUFFER_SIZE) != b"Bridge started 1.0":
    raise ImportError("Windows Bridge version mismatch")

########################################


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

        ## Windows error code
        self.winerror = winerror

        ## Linux style error code
        self.errno = winerror_to_errno(winerror)

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


def handleLRESULT():
    """
    Receive the LRESULT from the bridge.
    """

    # Get the LRESULT
    data = _CONNECTION_SOCKET.recv(4)
    # Error code
    return_code = struct.unpack("<I", data)[0]
    if return_code:

        # Parse out the utf-8 error string
        error_str = recv_string()
        # Special case, unit tests require a FileNotFoundError
        if return_code == ERROR_FILE_NOT_FOUND:
            raise FileNotFoundError(error_str)

        # Throw a WindowsError exception
        raise WindowsError(return_code, error_str)

########################################


def create_string_buffer(temp_string, is_binary=False):
    """
    Convert a string into a utf-8 byte stream

    Args:
        temp_string: String to convert
        is_binary: True if the input in binary, not a string.
    """

    # Ensure it's a string
    if temp_string:
        if not is_binary:
            temp_string = temp_string.encode("utf-8")
    else:
        temp_string = b""

    temp_string_length = len(temp_string)

    # Get the length
    buffer = struct.pack(
        "<I",
        temp_string_length)

    if not temp_string_length:
        return buffer

    # Append the string to the buffer and send the length and string
    return buffer + temp_string

########################################


def recv_string(convert_to_string=True):
    """
    Recieve a string from the socket

    Returns:
        UTF-8 string.
    """

    # Get the result string length
    data = _CONNECTION_SOCKET.recv(4)
    new_string_length = struct.unpack("<I", data)[0]

    # Get the result string
    if new_string_length:

        # Create the result buffer
        data = bytearray()
        # All data received?
        while len(data) < new_string_length:
            # Get a chunk
            packet = _CONNECTION_SOCKET.recv(new_string_length - len(data))
            if not packet:
                raise socket.timeout("Connection broken")
            data.extend(packet)
            del packet
        data = bytes(data)
    else:
        data = b""

    if convert_to_string:
        data = data.decode("utf-8")
    return data

########################################


def _RegCloseKey(hkey):
    """
    Low level function to call RegCloseKey
    """

    # Send the command and a QWORD of the pointer
    buffer = struct.pack(
        "<BQ", Commands.CLOSE_KEY.value,
        hkey)
    _CONNECTION_SOCKET.sendall(buffer)

    handleLRESULT()

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
            _RegCloseKey(self.hkey)
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

    # The integer Win32 handle.
    handle = property(_handle)

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

    # Python sort description.
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


def test_string(input_string):
    """
    Raise an exception if the input is not None or a string.

    Args:
        input_string: String to test.
    Exception:
        ``TypeError``
    """

    if input_string is None:
        return

    if not isinstance(input_string, basestring):
        raise TypeError("{} has to be None or a string".format(input_string))

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

    test_string(computer_name)
    buffer = struct.pack(
        "<BQ",
        Commands.CONNECT_REGISTRY.value,
        PyHKEY.make(key).hkey)

    _CONNECTION_SOCKET.sendall(buffer + create_string_buffer(computer_name))

    # This function CAN take a while, so allow it to take the time
    _CONNECTION_SOCKET.settimeout(20.0)
    data = _CONNECTION_SOCKET.recv(8)

    # Restore the proper timeout
    _CONNECTION_SOCKET.settimeout(3.0)
    handleLRESULT()
    return PyHKEY.make(struct.unpack("<Q", data)[0])

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

    test_string(sub_key)

    buffer = struct.pack(
        "<BQ",
        Commands.CREATE_KEY.value,
        PyHKEY.make(key).hkey)

    _CONNECTION_SOCKET.sendall(buffer + create_string_buffer(sub_key))

    data = _CONNECTION_SOCKET.recv(8)
    handleLRESULT()
    return PyHKEY.make(struct.unpack("<Q", data)[0])

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

    test_string(sub_key)

    buffer = struct.pack(
        "<BQII",
        Commands.CREATE_KEY_EX.value,
        PyHKEY.make(key).hkey, reserved, access)

    _CONNECTION_SOCKET.sendall(buffer + create_string_buffer(sub_key))

    data = _CONNECTION_SOCKET.recv(8)
    handleLRESULT()
    return PyHKEY.make(struct.unpack("<Q", data)[0])

########################################


def DeleteKey(key, sub_key):
    """
    Not implemented.

    Exception:
        ``NotImplementedError`` is always thrown.
    """

    test_string(sub_key)

    buffer = struct.pack(
        "<BQ",
        Commands.DELETE_KEY.value,
        PyHKEY.make(key).hkey)

    _CONNECTION_SOCKET.sendall(buffer + create_string_buffer(sub_key))
    handleLRESULT()

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

    test_string(sub_key)

    buffer = struct.pack(
        "<BQII",
        Commands.DELETE_KEY_EX.value,
        PyHKEY.make(key).hkey, reserved, access)

    _CONNECTION_SOCKET.sendall(buffer + create_string_buffer(sub_key))
    handleLRESULT()

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

    test_string(value)

    buffer = struct.pack(
        "<BQ",
        Commands.DELETE_VALUE.value,
        PyHKEY.make(key).hkey)

    _CONNECTION_SOCKET.sendall(buffer + create_string_buffer(value))
    handleLRESULT()

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

    buffer = struct.pack(
        "<BQI",
        Commands.ENUM_KEY.value,
        PyHKEY.make(key).hkey, index)

    _CONNECTION_SOCKET.sendall(buffer)

    new_data = recv_string()
    # Handle the error
    handleLRESULT()
    return new_data

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

    buffer = struct.pack(
        "<BQI",
        Commands.ENUM_VALUE.value,
        PyHKEY.make(key).hkey, index)

    _CONNECTION_SOCKET.sendall(buffer)

    # Get the id string, data and the type
    new_string = recv_string()
    new_data = recv_string(convert_to_string=False)
    data = _CONNECTION_SOCKET.recv(4)

    # Handle the error
    handleLRESULT()
    typ = struct.unpack("<I", data)[0]
    return (new_string,
            from_registry_bytes(new_data, len(new_data), typ),
            typ)

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

    test_string(str)

    # Send the command
    buffer = struct.pack(
        "<B",
        Commands.EXPAND_ENVIRONMENTSTRINGS.value)

    # Append the string to the buffer
    _CONNECTION_SOCKET.sendall(buffer + create_string_buffer(str))

    # Get the answer
    new_string = recv_string()

    # Get the error
    handleLRESULT()
    return new_string

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

    # Send the command and a QWORD of the pointer
    buffer = struct.pack(
        "<BQ",
        Commands.FLUSH_KEY.value,
        PyHKEY.make(key).hkey)
    _CONNECTION_SOCKET.sendall(buffer)

    handleLRESULT()

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

    test_string(sub_key)
    test_string(file_name)

    test_string(sub_key)
    buffer = struct.pack(
        "<BQ",
        Commands.LOAD_KEY.value,
        PyHKEY.make(key).hkey)

    _CONNECTION_SOCKET.sendall(
        buffer +
        create_string_buffer(sub_key) +
        create_string_buffer(file_name))
    handleLRESULT()

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

    test_string(sub_key)
    buffer = struct.pack(
        "<BQII",
        Commands.OPEN_KEY.value,
        PyHKEY.make(key).hkey,
        reserved,
        access)

    _CONNECTION_SOCKET.sendall(buffer + create_string_buffer(sub_key))

    data = _CONNECTION_SOCKET.recv(8)
    handleLRESULT()
    return PyHKEY.make(struct.unpack("<Q", data)[0])

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

    # Send the command and a QWORD of the pointer
    buffer = struct.pack(
        "<BQ",
        Commands.QUERY_INFO_KEY.value,
        PyHKEY.make(key).hkey)
    _CONNECTION_SOCKET.sendall(buffer)

    data = _CONNECTION_SOCKET.recv(4 + 4 + 8)
    handleLRESULT()
    return struct.unpack("<IIQ", data)

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

    test_string(sub_key)
    buffer = struct.pack(
        "<BQ",
        Commands.QUERY_VALUE.value,
        PyHKEY.make(key).hkey)

    _CONNECTION_SOCKET.sendall(buffer + create_string_buffer(sub_key))

    new_data = recv_string()
    handleLRESULT()
    return new_data

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

    test_string(value_name)
    buffer = struct.pack(
        "<BQ",
        Commands.QUERY_VALUE_EX.value,
        PyHKEY.make(key).hkey)

    _CONNECTION_SOCKET.sendall(buffer + create_string_buffer(value_name))

    new_data = recv_string(convert_to_string=False)
    data = _CONNECTION_SOCKET.recv(4)

    # Restore the proper timeout
    handleLRESULT()
    typ = struct.unpack("<I", data)[0]
    return (from_registry_bytes(new_data, len(new_data), typ),
            typ)

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

    test_string(file_name)
    buffer = struct.pack(
        "<BQ",
        Commands.SAVE_KEY.value,
        PyHKEY.make(key).hkey)

    _CONNECTION_SOCKET.sendall(buffer + create_string_buffer(file_name))

    handleLRESULT()

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

    test_string(sub_key)
    test_string(value)
    if type != REG_SZ:
        raise TypeError("Type must be wslwinreg.REG_SZ")

    buffer = struct.pack(
        "<BQ",
        Commands.SET_VALUE.value,
        PyHKEY.make(key).hkey)

    _CONNECTION_SOCKET.sendall(
        buffer +
        create_string_buffer(sub_key) +
        create_string_buffer(value))

    # Error code
    handleLRESULT()

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

    test_string(value_name)
    temp_buf = to_registry_bytes(value, type)
    buffer = struct.pack(
        "<BQI",
        Commands.SET_VALUE_EX.value,
        PyHKEY.make(key).hkey,
        type)

    _CONNECTION_SOCKET.sendall(
        buffer + create_string_buffer(value_name) +
        create_string_buffer(temp_buf.raw, True))

    # Error code
    handleLRESULT()

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

    # Send the command and a QWORD of the pointer
    buffer = struct.pack(
        "<BQ",
        Commands.DISABLE_REFLECTION_KEY.value,
        PyHKEY.make(key).hkey)
    _CONNECTION_SOCKET.sendall(buffer)

    handleLRESULT()

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

    # Send the command and a QWORD of the pointer
    buffer = struct.pack(
        "<BQ",
        Commands.ENABLE_REFLECTION_KEY.value,
        PyHKEY.make(key).hkey)
    _CONNECTION_SOCKET.sendall(buffer)

    handleLRESULT()

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

    # Send the command and a QWORD of the pointer
    buffer = struct.pack(
        "<BQ",
        Commands.QUERY_REFLECTION_KEY.value,
        PyHKEY.make(key).hkey)
    _CONNECTION_SOCKET.sendall(buffer)

    # Get the LRESULT
    data = _CONNECTION_SOCKET.recv(1)
    handleLRESULT()
    # Error code
    return_code = struct.unpack("<B", data)[0]
    return return_code != 0

########################################


def convert_to_windows_path(path_name):
    """
    Convert a WSL path to windows if needed.

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
    args = ("wslpath",
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
    Convert an absolute Windows path to WSL.

    If the path is already Linux format, it will be returned unchanged.

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
    args = ("wslpath", "-a", "-u", path_name)

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

    # Sanity check
    test_string(path_name)
    test_string(string_name)

    # Handle import for Cygwin
    path_name = convert_to_windows_path(path_name)

    # Send the command and the strings
    buffer = struct.pack(
        "<B",
        Commands.GET_FILE_INFO.value)

    _CONNECTION_SOCKET.sendall(
        buffer + create_string_buffer(path_name) +
        create_string_buffer(string_name))

    new_data = recv_string()
    handleLRESULT()
    return new_data
