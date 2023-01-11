.. _contributing:

Contributing
************

Contributes to :py:mod:`m_n_kappa` are highly appreciated.

.. _contributing.bug:

Found a bug?
============

Please open an issue in the `GitHub-Repository <https://github.com/JohannesSchorr/M-N-Kappa/issues>`_.

.. _contributing.commit:

Make a commit
=============
In case you commit to the project please follow the recommendations for the
`Perfect Commit <https://simonwillison.net/2022/Oct/29/the-perfect-commit/>`_.

The following four points must be considered in the commit:

1. Implementation
2. Tests (`unittest <https://docs.python.org/3/library/unittest.html>`_ is the used testing-framework)
3. :ref:`contributing.doc`
4. Issue thread (see also :ref:`contributing.bug`)

.. _contributing.doc:

Documentation
=============

.. _contributing.theory:

Theory guide
------------
In case the newly implemented object introduces a new behavior that is not covered by the :ref:`theory` than a
description of the theoretical background must be given.
The basic concept as well as the underlying assumption should be outlined.
Furthermore an explanation should be given how the new concept fits into the current program.


.. _contributing.doc.code:

Code / Doc-Strings
------------------

The format of the doc-strings of an object may in general follow the recommendations by
the `Numpy style-guide <https://numpydoc.readthedocs.io/en/latest/format.html#sections>`_.

Each object may at least comprise of the following sections:

1. `Short summary <https://numpydoc.readthedocs.io/en/latest/format.html#short-summary>`_
2. Version this object is

   - added (``.. versionadded::``,
     see `Sphinx-doc .. versionadded:: <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-versionadded>`_)
   - changed (``.. versionchanged::``,
     see `Sphinx-doc .. versionchanged:: <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-versionchanged>`_)
   - deprecated (``.. deprecated::``,
     see `Sphinx-doc .. deprecated:: <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-deprecated>`_)

3. `Extended Summary <https://numpydoc.readthedocs.io/en/latest/format.html#extended-summary>`_
4. `Parameters <https://numpydoc.readthedocs.io/en/latest/format.html#parameters>`_:
   sometimes a descriptive figure is useful this may be included using the ``.. figure::``-directive
5. `Returns <https://numpydoc.readthedocs.io/en/latest/format.html#returns>`_ in case the object returns a value
6. `Raises <https://numpydoc.readthedocs.io/en/latest/format.html#raises>`_ in case the object raises an exception.
   An appropriate description may be given, when an exception is raised.
7. `See Also <https://numpydoc.readthedocs.io/en/latest/format.html#see-also>`_ to give cross-references to similar
   objects if available.
8. `Notes <https://numpydoc.readthedocs.io/en/latest/format.html#notes>`_ for additional notes and mathematical
   expression using the ``.. math::``-directive.
9. `Examples <https://numpydoc.readthedocs.io/en/latest/format.html#examples>`_ are mandatory to illustrate
   usage of the object.


.. code-block:: python

   def the_method():
       """
       Short summmary

       .. versionadded: 0.1.0

       Extended summary

       Parameters
       ----------
       parameter_1 : float
           this is the first parameter
       parameter_2 : float, default = 10.0
           this is the second parameter

       Returns
       -------
       int
           this is the return-value

       Raises
       ------
       ValueError
           Error-description

       See also
       --------
       another_method : has similar behaviour as this method

       Notes
       -----
       In mathematical notation this function may be given as follows

       .. math::

          M = \\frac{q \\cdot L^2}{8}

       Keep in mind that the backspace-character (\)
       needs to be escaped by another backspace-character (\\).

       Examples
       --------
       This is the example usage of the method.

       >>> from m_n_kappa import Rectangle
       >>> rectangle = Rectangle(top_edge=10, bottom_edge=20, width=10)
       """
