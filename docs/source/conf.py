# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'M-N-Kappa'
copyright = '2022, Johannes Schorr'
author = 'Johannes Schorr'
release = 'v2022.12.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# --- Code execution during build --------------------------------------------
import pathlib
import sys
sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix())

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.napoleon',
    'nbsphinx',
]


templates_path = ['_templates']
exclude_patterns = ['**.ipynb_checkpoints']

# autodoc
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
extensions.append('sphinx.ext.autodoc')
autoclass_content = 'both'
autodoc_typehints = 'description'
autodoc_default_options = {
    'members': True,
    'member-order': 'groupwise'
}

# autosummary - sphinx.ext.autosummary
# https://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html
extensions.append('sphinx.ext.autosummary')
autosummary_generate = True

# Matplotlib - matplotlib.sphinxext.plot_directive
# https://matplotlib.org/stable/api/sphinxext_plot_directive_api.html
extensions.append('matplotlib.sphinxext.plot_directive')
plot_html_show_source_link = False
plot_include_source = True

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

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# Furo
# https://pradyunsg.me/furo/
html_theme = "furo"

html_static_path = ['_static']