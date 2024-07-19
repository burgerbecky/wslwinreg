# -*- coding: utf-8 -*-

"""
Configuration file for the Sphinx documentation builder.
"""

# pylint: disable=consider-using-f-string
# pylint: disable=redefined-builtin
# pylint: disable=invalid-name

from __future__ import absolute_import, unicode_literals

import subprocess
import os
import sys
import errno
import sphinx_rtd_theme

# Determine if running on "ReadTheDocs.org"

_ON_RTD = os.environ.get("READTHEDOCS", None) == "True"
CWD = os.path.dirname(os.path.abspath(__file__))

# Add this folder to python so it can find the new file
sys.path.append(os.path.dirname(CWD))

tempmodule = __import__("wslwinreg")

# Restore the pathnames
sys.path.pop()

# -- Project information -----------------------------------------------------

project = tempmodule.__title__
copyright = tempmodule.__copyright__
author = tempmodule.__author__

# The short X.Y version
version = ".".join([str(num) for num in tempmodule.__numversion__[:2]])
# The full version, including alpha/beta/rc tags
release = tempmodule.__version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx.ext.imgconverter",
    # rst2pdf has a conflict with sphinx.ext.mathjax
    # "rst2pdf.pdfbuilder",
    "breathe",
    "recommonmark"
]

# Add any paths that contain templates here, relative to this directory.
templates_path = []

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown"
}

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages. See the documentation for
# a list of builtin themes.

html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = ["_themes",]
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Theme options are theme-specific and customize the look and feel of a theme
# further. For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself. Builtin themes are using these templates by
# default: ``["localtoc.html", "relations.html", "sourcelink.html",
# "searchbox.html"]``.
#
# html_sidebars = {}
html_show_sourcelink = False

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = project + "doc"


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ("letterpaper" or "a4paper").
    #
    # "papersize": "letterpaper",

    # The font size ("10pt", "11pt" or "12pt").
    #
    # "pointsize": "10pt",

    # Additional stuff for the LaTeX preamble.
    #
    # "preamble": "",

    # Latex figure (float) alignment
    #
    # "figure_align": "htbp",
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
# author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, project + ".tex", project + " Documentation",
     author, "manual"),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, project, project + " Documentation", [author], 1)
]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
# dir menu entry, description, category)
texinfo_documents = [
    (master_doc, project, project + " Documentation",
     author, project, tempmodule.__summary__,
     "Miscellaneous"),
]


# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ""

# A unique identification for the text.
#
# epub_uid = ""

# A list of files that should not be packed into the epub file.
epub_exclude_files = ["search.html"]

# -- Options for PDF output -------------------------------------------------

# pdf_documents = \
# [
#    ("index", u"rst2pdf", project + " doc", author)
# ]

# rst2pdf has a bug where indexes can't build, this is a workaround
# pdf_use_index = False

# -- Extension configuration -------------------------------------------------

breathe_projects = {
    project: "temp/xml/"
}

breathe_default_project = project

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {"https://docs.python.org/": None}

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

########################################


def generate_doxygen_xml(app):
    """
    Run the doxygen make commands if we're on the ReadTheDocs server
    """

    # pylint: disable=unused-argument

    # Doxygen can't create a nested folder. Help it by
    # creating the first folder

    try:
        os.makedirs(os.path.join(CWD, "temp"))
    except OSError as error:
        if error.errno != errno.EEXIST:
            raise

    # Invoke the prebuild python script to create the README.html
    # file if needed using pandoc
    sys.path.append(CWD)
    build_rules = __import__("build_rules")
    sys.path.pop()
    build_rules.build(CWD, "all")

    # Read the docs has an old version of doxygen, upgrade it.
    if _ON_RTD:
        doxygen = os.path.join(CWD, "doxygen")
        if not os.path.isfile(doxygen):
            try:
                subprocess.call(("curl -O "
                    "http://logicware.com/downloads/linux/doxygen-1.11.0.tgz"),
                    cwd=CWD,
                    shell=True)
                subprocess.call("tar -xvf doxygen-1.11.0.tgz", cwd=CWD,
                    shell=True)
            except OSError as error:
                sys.stderr.write("doxygen download error: %s" % error)
    else:
        doxygen = "doxygen"

    # Call Doxygen to build the documentation
    try:
        # Log the Doxygen version number
        subprocess.call(doxygen + " -v", cwd=CWD, shell=True)
        retcode = subprocess.call(doxygen, cwd=CWD, shell=True)
        if retcode < 0:
            sys.stderr.write("doxygen terminated by signal %s" % (-retcode))
    except OSError as error:
        sys.stderr.write("doxygen execution failed: %s" % error)

    # If on ReadTheDocs.org, copy doxygen to public folder
    if _ON_RTD:
        try:
            retcode = subprocess.call(
                "cp -r temp/html ../_readthedocs/html/doxygen",
                cwd=".",
                shell=True)
            if retcode < 0:
                sys.stderr.write("cp terminated by signal %s" % (-retcode))
        except OSError as error:
            sys.stderr.write("cp execution failed: %s" % error)

########################################


def setup(app):
    """
    Called by breathe to create the doxygen docs
    """

    # Add hook for building doxygen xml when needed
    app.connect("builder-inited", generate_doxygen_xml)
