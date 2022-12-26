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
extensions.append('sphinx.ext.autodoc')
autoclass_content = 'both'
autodoc_typehints = 'description'
autodoc_default_options = {
    'members': True,
    'member-order': 'groupwise'
}

# autosummary - sphinx.ext.autosummary
extensions.append('sphinx.ext.autosummary')
autosummary_generate = True

# Matplotlib - matplotlib.sphinxext.plot_directive
extensions.append('matplotlib.sphinxext.plot_directive')
plot_html_show_source_link = False
plot_include_source = True

# sphinx.ext.todo
extensions.append('sphinx.ext.todo')
todo_include_todos = True

# Bibliography
extensions.append('sphinxcontrib.bibtex')
bibtex_bibfiles = ['literature.bib']
bibtex_default_style = 'plain'


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']