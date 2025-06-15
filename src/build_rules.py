#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration file on how to build and clean projects in a specific folder.

This file is parsed by the cleanme, buildme, rebuildme and makeprojects
command line tools to clean, build and generate project files.
"""

# pylint: disable=global-statement
# pylint: disable=unused-argument
# pylint: disable=consider-using-f-string

from __future__ import absolute_import, print_function, unicode_literals

import os

from burger import clean_directories, clean_files
from makeprojects import ProjectTypes, IDETypes, PlatformTypes

# Name of the project, default is the directory name
PROJECT_NAME = "backend"

# Type of the project, default is ProjectTypes.tool
PROJECT_TYPE = ProjectTypes.tool

# Recommended IDE for the project. Default is IDETypes.default()
PROJECT_IDE = IDETypes.vs2022

# Recommend target platform for the project.
PROJECT_PLATFORM = PlatformTypes.windows

# ``cleanme`` will assume only the function ``clean()`` is used if False.
# Overrides PROCESS_PROJECT_FILES
CLEANME_PROCESS_PROJECT_FILES = False

# Check if .git is found (Olde Skuul uses Perforce)
_GIT_FOUND = os.path.isdir(
    os.path.join(
        os.path.dirname(
            os.path.dirname(__file__)), ".git"))

# List of projects to generate if makeprojects is invoked
# without any parameters, default create recommended
# project for the host machine

# Create windows projects for Watcom, VS 2022, and Codewarrior
MAKEPROJECTS = [
    {"name": "backend",
     "platform": "windows",
     "ide": "vs2022",
     "type": "tool",
     "configuration": "Release_LTCG"}
]

########################################


def clean(working_directory):
    """
    Delete temporary files.

    This function is called by ``cleanme`` to remove temporary files.

    On exit, return 0 for no error, or a non zero error code if there was an
    error to report.

    Args:
        working_directory
            Directory this script resides in.

    Returns:
        None if not implemented, otherwise an integer error code.
    """

    clean_directories(
        working_directory, (
            ".vscode",
            "temp",
            "ipch",
            "bin",
            ".vs",
            "__pycache__"))

    clean_files(
        working_directory, (
            ".DS_Store",
            "*.suo",
            "*.user",
            "*.ncb",
            "*.err",
            "*.sdf",
            "*.layout.cbTemp",
            "*.VC.db",
            "*.pyc",
            "*.pyo"))

    # No error
    return 0


# Suffixes for each CPU
CPU_LIST = {
    PlatformTypes.win32: "x86",
    PlatformTypes.win64: "x64",
    PlatformTypes.winarm32: "arm",
    PlatformTypes.winarm64: "arm64"
}

########################################


def configuration_settings(configuration):
    """
    Set the custom attributes for each configuration.

    Args:
        configuration: Configuration to modify.
    """

    # Which of the 4 CPUs are being built?
    platform = configuration.platform

    # Disable perforce support if git is present
    configuration.project.solution.perforce = not _GIT_FOUND

    # Intel platforms should run on Windows XP
    # Arm will require Windows 10 or higher
    if platform in (PlatformTypes.win32, PlatformTypes.win64):
        configuration.vs_platform_toolset = "v141_xp"

    # Determine the CPU suffix
    cpu = CPU_LIST.get(platform)

    # After building, copy the exe to the final folder
    source = "\"$(TargetPath)\""
    dest = "\"$(ProjectDir)..\\wslwinreg\\bin\\backend-{}.exe\"".format(cpu)

    # Commands for the batch file
    command_list = [
        # Make the destination folder, and suppress messages
        "mkdir \"$(ProjectDir)..\\wslwinreg\\bin\" 2>nul",
        # Perform the copy
        "copy /Y " + source + " " + dest
    ]

    # Create the Visual Studio post build event
    description = "Copying $(TargetPath) to " + dest
    command = "\n".join(command_list) + "\n"
    configuration.post_build = (description, command)

    return 0
