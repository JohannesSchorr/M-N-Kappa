# Configuration file for the Sphinx documentation builder.

from datetime import datetime
import pathlib
import sys

# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'M-N-Kappa'
copyright = '2023, Johannes Schorr'
author = 'Johannes Schorr'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# --- Code execution during build --------------------------------------------
sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix())
extensions = []
exclude_patterns = []

# Duration
# measures durations of Sphinx processing
# https://www.sphinx-doc.org/en/master/usage/extensions/duration.html
extensions.append('sphinx.ext.duration')

# Doctest
# https://www.sphinx-doc.org/en/master/usage/extensions/doctest.html
extensions.append('sphinx.ext.doctest')

# Napoleon
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
extensions.append('sphinx.ext.napoleon')

# nbsphinx
# https://nbsphinx.readthedocs.io/en/0.8.11/
# provides a source parser for *.ipynb files
extensions.append('nbsphinx')
exclude_patterns.append('_build')
exclude_patterns.append('**.ipynb_checkpoints')

templates_path = ['_templates']

# autodoc
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
extensions.append('sphinx.ext.autodoc')
autoclass_content = 'both'
autodoc_typehints = 'description'
autodoc_default_options = {
    'members': True,
    'member-order': 'groupwise',
    'show-inheritance': True,
    'inherited-members': True,
}

# autosummary - sphinx.ext.autosummary
# https://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html
extensions.append('sphinx.ext.autosummary')
autosummary_generate = True

# Matplotlib - matplotlib.sphinxext.plot_directive
# https://matplotlib.org/stable/api/sphinxext_plot_directive_api.html
#extensions.append('matplotlib.sphinxext.plot_directive')
#plot_html_show_source_link = False
#plot_include_source = True

# Altair
# https://altair-viz.github.io/
extensions.append('altair.sphinxext.altairplot')

# sphinx.ext.todo
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html
extensions.append('sphinx.ext.todo')
todo_include_todos = True

# Bibliography
# https://sphinxcontrib-bibtex.readthedocs.io/en/latest/
extensions.append('sphinxcontrib.bibtex')
bibtex_bibfiles = ['literature.bib']
bibtex_default_style = 'plain'

# Sphinx-design
# https://sphinx-design.readthedocs.io/en/latest/
extensions.append('sphinx_design')

# Sphinx-Copybutton
# https://github.com/executablebooks/sphinx-copybutton
extensions.append('sphinx_copybutton')

# Sphinx-Toggleprompt
# https://sphinx-toggleprompt.readthedocs.io/en/latest/
extensions.append('sphinx_toggleprompt')
toggleprompt_offset_right = 30  # prevents overlapping with copybutton
toggleprompt_default_hidden = "true"


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# Furo
# https://pradyunsg.me/furo/
html_theme = "furo"
html_theme_options = {
    "source_repository": "https://github.com/JohannesSchorr/M-N-Kappa/",
    "source_branch": "master",
    "source_directory": "docs/source/",
    "announcement": "<em>Important</em> "
                    "This 'm_n_kappa'-package has not yet been published on PyPI! "
                    "This documentation is also currently under development. "
                    "Plaese keep that in mind, while reading and testing. "
                    "Thank you.",
}
html_static_path = ['_static']
html_logo = '_static/logo/m_kappa_logo.png'
html_title = f"<i>M</i>-<i>N</i>-<i>&#954</i>"
html_css_files = [
    'css/custom.css',
]