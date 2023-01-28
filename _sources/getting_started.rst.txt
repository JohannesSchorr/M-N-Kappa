.. _getting_started:

Getting Started
***************

.. _getting_started.installation:
Installation
============

The installation via `PyPi <https://pypi.org/>`_ runs as follows.

.. code-block::

   pip install m-n-kappa


.. _getting_started.example:
Introducing example: Computing a steel-concrete composite beam
==============================================================

.. altair-plot::
   :output: None
   :hide-code:

   # configuration of altair-plot
   import altair as alt
   alt.themes.enable('quartz')

The following example shows how easy and straightforward :py:mod:`m_n_kappa` is
applied to computing the deformation of a composite beam.

.. figure:: ./images/getting_started_example-dark.svg
   :class: only-dark
.. figure:: ./images/getting_started_example-light.svg
   :class: only-light

   Composite beam (Measurements are given in Millimeter)

The slab is a rectangle of concrete of type C30/35.

.. altair-plot::
   :output: repr

   from m_n_kappa import Rectangle, Concrete
   slab = Rectangle(top_edge=0.0, bottom_edge=100, width=2000)
   concrete = Concrete(f_cm=38)
   concrete_slab = concrete + slab

The girder is a HEB 200 steel-profile of type S355.

.. altair-plot::
   :output: repr

   from m_n_kappa import IProfile, Steel
   girder = IProfile(top_edge=100.0, t_w=9.5, h_w=200-2*15, t_fo=15, b_fo=200)
   steel = Steel(f_y=355, failure_strain=0.15)
   steel_girder = steel + girder

Merging the ``concrete_slab`` and the ``steel_girder`` to a composite cross-section
is accomplished also easily.

.. altair-plot::
   :output: repr

   composite_cross_section = concrete_slab + steel_girder

This :py:class:`~m_n_kappa.Crosssection`-object of a composite beam allows you to do several things like
computing the curvature :math:`\kappa`, the *M*-:math:`\kappa`-curve or the deformation of the beam
under a given loading. 

.. altair-plot::
   :output: repr

   from m_n_kappa import SingleSpanUniformLoad, Beam
   loading = SingleSpanUniformLoad(length=8000)
   beam = Beam(
       cross_section=composite_cross_section,
       element_number=10,
       load=loading
    )


The load-deformation-curve is then created as follows, using the plotting library
`Altair <https://altair-viz.github.io/>`_.

.. altair-plot::

   deformation_at_maximum_position = beam.deformations_at_maximum_deformation_position()

   import pandas as pd
   df = pd.DataFrame(
        {'loadings': deformation_at_maximum_position.loadings(factor=0.001),
         'deformations': deformation_at_maximum_position.values()})

   import altair as alt
   alt.Chart(df, background='#00000000').mark_line().encode(
      x=alt.X('deformations', title='Deformation [mm]'),
      y=alt.Y('loadings', title='Loading [kN]'))

The deformation along the beam under a given load is then computed as follows.

.. altair-plot::

   deformation_load = SingleSpanUniformLoad(length=8000, load=1.0)
   deformations_over_length = beam.deformation_over_beam_length(
       load_step=deformation_load)

   df = pd.DataFrame(
        {'positions': deformations_over_length.positions(),
         'deformations': deformations_over_length.values()})

   alt.Chart(df, height=100.0, background='#00000000').mark_line().encode(
       x=alt.X('positions', title='Beam position [mm]'),
       y=alt.Y('deformations', title='Deformation [mm]', scale=alt.Scale(reverse=True)))

:ref:`examples` gives you detailed instructions how to build a cross-section,
computing a single :ref:`examples.moment_curvature` point,
a :ref:`examples.moment_curvature_curve` or the :ref:`examples.deformation` of
a beam, to name a few.