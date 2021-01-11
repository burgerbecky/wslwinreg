Functions
=========

Helper functions
----------------

wslwinreg.common.winerror_to_errno
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::common::winerror_to_errno

wslwinreg.common.convert_to_utf16
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::common::convert_to_utf16

wslwinreg.common.to_registry_bytes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::common::to_registry_bytes

wslwinreg.common.from_registry_bytes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::common::from_registry_bytes

wslwinreg.get_HKCU
^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::get_HKCU

wslwinreg.get_HKLM_32
^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::get_HKLM_32

wslwinreg.get_HKLM_64
^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::get_HKLM_64

Null implementation
-------------------

On operating systems such as macOS and Linux that doesn't have a Windows
operating system underpinning, all functions will raise a
``NotImplementedError`` exception.

wslwinreg.nullapi.CloseKey
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::CloseKey

wslwinreg.nullapi.ConnectRegistry
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::ConnectRegistry

wslwinreg.nullapi.CreateKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::CreateKey

wslwinreg.nullapi.CreateKeyEx
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::CreateKeyEx

wslwinreg.nullapi.DeleteKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::DeleteKey

wslwinreg.nullapi.DeleteKeyEx
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::DeleteKeyEx

wslwinreg.nullapi.DeleteValue
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::DeleteValue

wslwinreg.nullapi.EnumKey
^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::EnumKey

wslwinreg.nullapi.EnumValue
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::EnumValue

wslwinreg.nullapi.ExpandEnvironmentStrings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::ExpandEnvironmentStrings

wslwinreg.nullapi.FlushKey
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::FlushKey

wslwinreg.nullapi.LoadKey
^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::LoadKey

wslwinreg.nullapi.OpenKey
^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::OpenKey

wslwinreg.nullapi.OpenKeyEx
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::OpenKeyEx

wslwinreg.nullapi.QueryInfoKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::QueryInfoKey

wslwinreg.nullapi.QueryValue
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::QueryValue

wslwinreg.nullapi.QueryValueEx
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::QueryValueEx

wslwinreg.nullapi.SaveKey
^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::SaveKey

wslwinreg.nullapi.SetValue
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::SetValue

wslwinreg.nullapi.SetValueEx
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::SetValueEx

wslwinreg.nullapi.DisableReflectionKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::DisableReflectionKey

wslwinreg.nullapi.EnableReflectionKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::EnableReflectionKey

wslwinreg.nullapi.QueryReflectionKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::QueryReflectionKey

wslwinreg.nullapi.convert_to_windows_path
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::convert_to_windows_path

wslwinreg.nullapi.convert_from_windows_path
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::convert_from_windows_path

wslwinreg.nullapi.get_file_info
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::nullapi::get_file_info

Cygwin / MSYS2 implementation
-----------------------------

On Cygwin and MSYS2 platforms, the ``CDLL`` exposes the Windows
API directly so these python functions mimic the C code from 
Python for Windows and calls the Windows API to perform the low
level work.

wslwinreg.cygwinapi.CloseKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::CloseKey

wslwinreg.cygwinapi.ConnectRegistry
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::ConnectRegistry

wslwinreg.cygwinapi.CreateKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::CreateKey

wslwinreg.cygwinapi.CreateKeyEx
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::CreateKeyEx

wslwinreg.cygwinapi.DeleteKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::DeleteKey

wslwinreg.cygwinapi.DeleteKeyEx
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::DeleteKeyEx

wslwinreg.cygwinapi.DeleteValue
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::DeleteValue

wslwinreg.cygwinapi.EnumKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::EnumKey

wslwinreg.cygwinapi.EnumValue
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::EnumValue

wslwinreg.cygwinapi.ExpandEnvironmentStrings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::ExpandEnvironmentStrings

wslwinreg.cygwinapi.FlushKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::FlushKey

wslwinreg.cygwinapi.LoadKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::LoadKey

wslwinreg.cygwinapi.OpenKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::OpenKey

wslwinreg.cygwinapi.OpenKeyEx
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::OpenKeyEx

wslwinreg.cygwinapi.QueryInfoKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::QueryInfoKey

wslwinreg.cygwinapi.QueryValue
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::QueryValue

wslwinreg.cygwinapi.QueryValueEx
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::QueryValueEx

wslwinreg.cygwinapi.SaveKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::SaveKey

wslwinreg.cygwinapi.SetValue
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::SetValue

wslwinreg.cygwinapi.SetValueEx
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::SetValueEx

wslwinreg.cygwinapi.DisableReflectionKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::DisableReflectionKey

wslwinreg.cygwinapi.EnableReflectionKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::EnableReflectionKey

wslwinreg.cygwinapi.QueryReflectionKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::QueryReflectionKey

wslwinreg.cygwinapi.convert_to_windows_path
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::convert_to_windows_path

wslwinreg.cygwinapi.convert_from_windows_path
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::convert_from_windows_path

wslwinreg.cygwinapi.get_file_info
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::cygwinapi::get_file_info

Windows Subsystem for Linux implementation
------------------------------------------

On Windows Subsystem for Windows, the calls are sent to a server
that will issue the calls directly in the Windows host which
performs the actual the low level work.

wslwinreg.wslapi.CloseKey
^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::CloseKey

wslwinreg.wslapi.ConnectRegistry
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::ConnectRegistry

wslwinreg.wslapi.CreateKey
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::CreateKey

wslwinreg.wslapi.CreateKeyEx
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::CreateKeyEx

wslwinreg.wslapi.DeleteKey
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::DeleteKey

wslwinreg.wslapi.DeleteKeyEx
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::DeleteKeyEx

wslwinreg.wslapi.DeleteValue
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::DeleteValue

wslwinreg.wslapi.EnumKey
^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::EnumKey

wslwinreg.wslapi.EnumValue
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::EnumValue

wslwinreg.wslapi.ExpandEnvironmentStrings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::ExpandEnvironmentStrings

wslwinreg.wslapi.FlushKey
^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::FlushKey

wslwinreg.wslapi.LoadKey
^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::LoadKey

wslwinreg.wslapi.OpenKey
^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::OpenKey

wslwinreg.wslapi.OpenKeyEx
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::OpenKeyEx

wslwinreg.wslapi.QueryInfoKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::QueryInfoKey

wslwinreg.wslapi.QueryValue
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::QueryValue

wslwinreg.wslapi.QueryValueEx
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::QueryValueEx

wslwinreg.wslapi.SaveKey
^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::SaveKey

wslwinreg.wslapi.SetValue
^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::SetValue

wslwinreg.wslapi.SetValueEx
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::SetValueEx

wslwinreg.wslapi.DisableReflectionKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::DisableReflectionKey

wslwinreg.wslapi.EnableReflectionKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::EnableReflectionKey

wslwinreg.wslapi.QueryReflectionKey
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::QueryReflectionKey

wslwinreg.wslapi.convert_to_windows_path
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::convert_to_windows_path

wslwinreg.wslapi.convert_from_windows_path
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::convert_from_windows_path

wslwinreg.wslapi.get_file_info
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. doxygenfunction:: wslwinreg::wslapi::get_file_info