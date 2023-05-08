# Configuration file for the Sphinx documentation builder.

from datetime import datetime
import pathlib
import sys

# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "M-N-Kappa"
copyright = "2023, Johannes Schorr"
author = "Johannes Schorr"
release = "0.2.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# --- Code execution during build --------------------------------------------
sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix())
extensions = []
exclude_patterns = []

# Duration
# measures durations of Sphinx processing
# https://www.sphinx-doc.org/en/master/usage/extensions/duration.html
extensions.append("sphinx.ext.duration")

# Doctest
# https://www.sphinx-doc.org/en/master/usage/extensions/doctest.html
extensions.append("sphinx.ext.doctest")

# Napoleon
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
extensions.append("sphinx.ext.napoleon")

# nbsphinx
# https://nbsphinx.readthedocs.io/en/0.8.11/
# provides a source parser for *.ipynb files
extensions.append("nbsphinx")
exclude_patterns.append("_build")
exclude_patterns.append("**.ipynb_checkpoints")

templates_path = ["_templates"]

# autodoc
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
extensions.append("sphinx.ext.autodoc")
autoclass_content = "both"
autodoc_typehints = "description"
autodoc_default_options = {
    "members": True,
    "member-order": "groupwise",
    "show-inheritance": True,
    "inherited-members": True,
}

# autosummary - sphinx.ext.autosummary
# https://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html
extensions.append("sphinx.ext.autosummary")
autosummary_generate = True

# Matplotlib - matplotlib.sphinxext.plot_directive
# https://matplotlib.org/stable/api/sphinxext_plot_directive_api.html
# extensions.append('matplotlib.sphinxext.plot_directive')
# plot_html_show_source_link = False
# plot_include_source = True

# Altair
# https://altair-viz.github.io/
extensions.append("altair.sphinxext.altairplot")

# sphinx.ext.todo
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html
extensions.append("sphinx.ext.todo")
todo_include_todos = True

# Bibliography
# https://sphinxcontrib-bibtex.readthedocs.io/en/latest/
extensions.append("sphinxcontrib.bibtex")
bibtex_bibfiles = ["literature.bib"]
bibtex_default_style = "plain"

# Sphinx-design
# https://sphinx-design.readthedocs.io/en/latest/
extensions.append("sphinx_design")

# Sphinx-Copybutton
# https://github.com/executablebooks/sphinx-copybutton
extensions.append("sphinx_copybutton")

# Sphinx-Toggleprompt
# https://sphinx-toggleprompt.readthedocs.io/en/latest/
extensions.append("sphinx_toggleprompt")
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
    # "announcement": "<em>Important</em> ",
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/JohannesSchorr/M-N-Kappa",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
}
html_static_path = ["_static"]
html_logo = "_static/logo/m_n_kappa_logo.png"
html_title = "<i>M</i>-<i>N</i>-<i>&#954</i>"
html_css_files = [
    "css/custom.css",
]

# https://stackoverflow.com/questions/34006784/how-do-i-access-a-variable-in-sphinx-conf-py-from-my-rst-file'
# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-rst_epilog
rst_epilog = f"""
.. |Versioning| replace:: Latest version: {release} 
.. |Documentation| replace::  Documentation build: {datetime.today().strftime('%d.%m.%Y')}
"""
