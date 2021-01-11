Why wslwinreg?
==============

Python runs on several Windows hosted platforms such as Windows
itself, Cygwin, MSYS2 and Windows Subsystem for Linux (WSL).
Each of these platforms has a Windows Subsystem which contains
the Windows registry. Under Windows native versions of Python,
the module ``winreg`` allows access to the Windows Registry API.
However, this API exists under the other three platforms, but
winreg is not available.

That's where ``wslwinreg`` comes in!

This module will grant access to all ``winreg`` calls on Windows
native platforms, either by passing through calls to ``winreg``
or implementing custom code to grant access.

---

Windows support
---------------

On Windows native platform, ``winreg`` is directly imported and all
calls simple are passed through so the native implementation is
used instead of the alternate versions.

Cygwin and MSYS2 support
------------------------

CDLL on Cygwin and MSYS2 versions of Python allow access to the
underlying native Windows APIs, so ``wslwinreg`` implements
``winreg`` calls through Python code that calls the native
Windows API as needed.

Windows Subsystem for Linux support
-----------------------------------

Ubuntu and other distributions of Linux running under WSL run
in a virtual machine that is isolated from the Window host
machine to the point that native calls are not possible. To
solve this issue, a Windows native backend is launched and
through a loopback TCP/IP socket communication is established
so remote procedure calls can be issued and results returned to
``wslwinreg`` to allow access to the native Windows registry.

---

Testing
-------

A unit test package, lovingly ripped off from Python 3.9.1 is
run on all four platforms to ensure the same behavior is
exhibited across all supported platforms. It is located in the
folder ``unittests`` in the github source code tree.

---

Building the backend
--------------------

To build the C++ backend, use Visual Studio 2019 with the 2017
XP compiler for x86 and x64 compilation. ARM and ARM64 are
built with the 2019 C++ tool chain. The Release target will
place the executables in the wslwinreg/bin folder for you. This
backend is only used when running ``wslwinreg`` under WSL. It's
not used on any other platform.

---

Credits
-------

``wslwinreg`` is the insane creation of Rebecca Ann Heineman.
If bugs are found, please send all information on how to
recreate the bug to
[becky@burgerbecky.com](mailto:becky@burgerbecky.com)
