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
