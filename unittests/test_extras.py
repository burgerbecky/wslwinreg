#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Test the windows specific extra functions

import os
import sys
import unittest

# Use abspath() because msys2 only returns the module filename
# instead of the full path

# Insert the location of wslwinreg at the begining so it's the first
# to be processed
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wslwinreg import convert_from_windows_path, convert_to_windows_path, \
    get_file_info, IS_CYGWIN, IS_MSYS, IS_WSL

########################################


class TestExtras(unittest.TestCase):
    """
    Test extra functions.
    """

    def test_convert_to_windows_path(self):
        """
        Test convert_to_windows_path and convert_from_windows_path
        """

        result = convert_from_windows_path("C:\\Windows\\Notepad.exe")
        if IS_CYGWIN or IS_MSYS or IS_WSL:
            self.assertNotEqual(result, "C:\\Windows\\Notepad.exe")
        else:
            self.assertEqual(result, "C:\\Windows\\Notepad.exe")

        # Check if it converted back
        result2 = convert_to_windows_path(result)
        self.assertEqual(result2, "C:\\Windows\\Notepad.exe")

    def test_get_file_info(self):
        """
        Test get_file_info()
        """
        result = get_file_info("C:\\Windows\\Notepad.exe", "FileVersion")
        self.assertIsNotNone(result)

        result = get_file_info("C:\\Windows\\Notepad.exe", "ProductVersion")
        self.assertIsNotNone(result)

        linux_name = convert_from_windows_path("C:\\Windows\\Notepad.exe")
        result = get_file_info(linux_name, "FileVersion")
        self.assertIsNotNone(result)

        result = get_file_info(linux_name, "ProductVersion")
        self.assertIsNotNone(result)

########################################


if __name__ == "__main__":
    unittest.main()
