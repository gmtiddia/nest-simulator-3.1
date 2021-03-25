# -*- coding: utf-8 -*-
#
# conf.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.


import sys
import os
import re
import pip
import subprocess

from pathlib import Path
from shutil import copyfile

from subprocess import check_output, CalledProcessError
from mock import Mock as MagicMock


source_dir = os.environ.get('NESTSRCDIR', False)
if source_dir:
    source_dir = Path(source_dir)
else:
    source_dir = Path(__file__).resolve().parent.parent.parent.resolve()

doc_build_dir = Path(os.environ['OLDPWD']) / 'doc/userdoc'

if os.environ.get('READTHEDOCS', 'False') == 'True':
    doc_build_dir = source_dir / 'doc/userdoc'

print("doc_build_dir", str(doc_build_dir))
print("source_dir", str(source_dir))

source_suffix = '.rst'
master_doc = 'contents'

# Create the mockfile for extracting the PyNEST

excfile = source_dir / "pynest/nest/lib/hl_api_exceptions.py"
infile = source_dir / "pynest/pynestkernel.pyx"
outfile = doc_build_dir / "pynestkernel_mock.py"

sys.path.insert(0, str(source_dir))
sys.path.insert(0, str(source_dir / 'doc'))
sys.path.insert(0, str(source_dir / 'pynest'))
sys.path.insert(0, str(source_dir / 'pynest/nest'))
sys.path.insert(0, str(doc_build_dir))

from mock_kernel import convert  # noqa

with open(excfile, 'r') as fexc, open(infile, 'r') as fin, open(outfile, 'w') as fout:
    mockedmodule = fexc.read() + "\n\n"
    mockedmodule += "from mock import MagicMock\n\n"
    mockedmodule += convert(fin)

    fout.write(mockedmodule)

import pynestkernel_mock  # noqa

sys.modules["nest.pynestkernel"] = pynestkernel_mock
sys.modules["nest.kernel"] = pynestkernel_mock

# -- General configuration ------------------------------------------------
extensions = [
    'sphinx_gallery.gen_gallery',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx_tabs.tabs',
    'nbsphinx'
]

mathjax_path = "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-AMS-MML_HTMLorMML"  # noqa

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

sphinx_gallery_conf = {
     # 'doc_module': ('sphinx_gallery', 'numpy'),
     # path to your examples scripts
     'examples_dirs': source_dir / 'pynest/examples',
     # path where to save gallery generated examples
     'gallery_dirs': doc_build_dir / 'auto_examples',
     # 'backreferences_dir': False
     'plot_gallery': 'False'
}

# General information about the project.
project = u'NEST simulator user documentation'
copyright = u'2004, nest-simulator'
author = u'nest-simulator'


# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '3.0'
# The full version, including alpha/beta/rc tagss
release = '3.0'
# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['Thumbs.db', '.DS_Store', 'nest_by_example', 'README.md']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'manni'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# add numbered figure link
numfig = True

numfig_secnum_depth = (2)
numfig_format = {'figure': 'Figure %s', 'table': 'Table %s',
                 'code-block': 'Code Block %s'}
# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
html_logo = str(doc_build_dir / 'static/img/nest_logo.png')
html_theme_options = {'logo_only': True,
                      'display_version': False}

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = [str(doc_build_dir / 'static')]

rst_prolog = ".. warning:: \n  This is A PREVIEW for NEST 3.0 and NOT an OFFICIAL RELEASE! \
             Some functionality may not be available and information may be incomplete!"
rst_epilog = ""
# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'NESTsimulatordoc'

html_show_sphinx = False
html_show_copyright = False

# This way works for ReadTheDocs
# With this local 'make html' is broken!
github_doc_root = ''

intersphinx_mapping = {'https://docs.python.org/': None}

from doc.extractor_userdocs import ExtractUserDocs, relative_glob  # noqa


def config_inited_handler(app, config):
    ExtractUserDocs(
        listoffiles=relative_glob("models/*.h", "nestkernel/*.h", basedir=source_dir),
        basedir=source_dir,
        outdir=str(doc_build_dir / "models")
    )


nitpick_ignore = [('py:class', 'None'),
                  ('py:class', 'optional'),
                  ('py:class', 's'),
                  ('cpp:identifier', 'CommonSynapseProperties'),
                  ('cpp:identifier', 'Connection<targetidentifierT>'),
                  ('cpp:identifier', 'ArchivingNode'),
                  ('cpp:identifier', 'DeviceNode'),
                  ('cpp:identifier', 'Node'),
                  ('cpp:identifier', 'ClopathArchivingNode'),
                  ('cpp:identifier', 'MessageHandler'),
                  ('cpp:identifer', 'CommonPropertiesHomW')]


def setup(app):
    app.add_css_file('css/custom.css')
    app.add_css_file('css/pygments.css')
    app.add_js_file("js/copybutton.js")
    app.add_js_file("js/custom.js")

    # for events see
    # https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx-core-events
    app.connect('config-inited', config_inited_handler)

# -- Options for LaTeX output ---------------------------------------------


latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'NESTsimulator.tex', u'NEST Simulator Documentation',
     u'NEST Developer Community', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'nestsimulator', u'NEST simulator Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'NESTsimulator', u'NEST simulator Documentation',
     author, 'NESTsimulator', 'One line description of project.',
     'Miscellaneous'),
]


def copy_example_file(src):
    copyfile(src, doc_build_dir / "examples" / src.parts[-1])


def copy_acknowledgments_file(src):
    copyfile(src, doc_build_dir / src.parts[-1])


# -- Copy Acknowledgments file ----------------------------
copy_acknowledgments_file(source_dir / "ACKNOWLEDGMENTS.md")

# -- Copy documentation for Microcircuit Model ----------------------------
copy_example_file(source_dir / "pynest/examples/Potjans_2014/box_plot.png")
copy_example_file(source_dir / "pynest/examples/Potjans_2014/raster_plot.png")
copy_example_file(source_dir / "pynest/examples/Potjans_2014/microcircuit.png")
copy_example_file(source_dir / "pynest/examples/Potjans_2014/README.rst")
