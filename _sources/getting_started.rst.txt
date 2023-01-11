.. _getting_started:
Getting Started
***************

.. _getting_started.installation:
Installation
============

.. important::
   This package has not yet been published on PyPI. Therefore, the following command does not work currently.

The installation via `PyPi <https://pypi.org/>`_ runs as follows.

.. code-block::

   pip install m-n-kappa


.. _getting_started.example:
Introducing example: Computing a steel-concrete composite beam
==============================================================

The following example shows how easy and straightforward :py:mod:`m_n_kappa` is applied to
computing the deformation of a composite beam.

.. figure:: ./images/getting_started_example-dark.svg
   :class: only-dark
.. figure:: ./images/getting_started_example-light.svg
   :class: only-light

   Composite beam (Measurements are given in Millimeter)

The slab is a rectangle of concrete of type C30/35.

>>> from m_n_kappa import Rectangle, Concrete
>>> slab = Rectangle(top_edge=0.0, bottom_edge=100, width=2000)
>>> concrete = Concrete(f_cm=38)
>>> concrete_slab = concrete + slab

The girder is a HEB 200 steel-profile of type S355.

>>> from m_n_kappa import IProfile, Steel
>>> girder = IProfile(top_edge=100.0, t_w=9.5, h_w=200-2*15, t_fo=15, b_fo=200)
>>> steel = Steel(f_y=355, failure_strain=0.15)
>>> steel_girder = steel + girder

Merging the ``concrete_slab`` and the ``steel_girder`` to a composite cross-section
is accomplished also easily.

>>> composite_cross_section = concrete_slab + steel_girder

This :py:class:`~m_n_kappa.Crosssection`-object of a composite beam allows you to do several things like
computing the curvature :math:`\kappa`, the *M*-:math:`\kappa`-curve or the deformation of the beam
under a given loading. 

>>> from m_n_kappa import SingleSpanUniformLoad, Beam
>>> loading = SingleSpanUniformLoad(length=8000, load=1.0)
>>> beam = Beam(
...    cross_section=composite_cross_section,
...    length=8000,
...    element_number=10,
...    load=loading
... )
>>> deformation_at_maximum_position = beam.deformations_at_maximum_deformation_position()

The load-deformation pairs are then easily extracted as follows:

>>> for deformation in deformation_at_maximum_position:
...     f"{deformation.load*0.001:.1f}, {deformation.deformation:.1f}"
'0.0, 0.0'
'45.3, 15.6'
'45.7, 15.7'
'157.6, 58.7'
'234.0, 125.7'
'249.3, 270.9'
'249.6, 279.3'
'251.2, 354.5'
'251.9, 451.9'

For more example please refer to :ref:`examples`.