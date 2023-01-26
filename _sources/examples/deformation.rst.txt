.. _examples.deformation:

Deformation
***********

*Units: Millimeter [mm], Newton [N]*

.. altair-plot::
   :output: None
   :hide-code:

   # configuration of altair-plot
   import altair as alt
   alt.themes.enable('quartz')

To compute deformations we first create a :py:class:`~m_n_kappa.Crosssection`.
Our ``cross_section`` is a composite beam composed of a rectangular concrete-slab
with two reinforcement-layers and concrete of type C30/35.
A HEB 200 steel profile is positioned at the bottom of the concrete slab.
For more details regarding the cross-section see :ref:`here <cross_section_template.composite_beam>`.

.. altair-plot::
   :output: repr

   from m_n_kappa import IProfile, Steel, Rectangle, Concrete, RebarLayer, Reinforcement
   concrete_slab = Rectangle(top_edge=0.0, bottom_edge=100, width=2000)
   concrete = Concrete(f_cm=30+8, )
   concrete_section = concrete_slab + concrete
   reinforcement = Reinforcement(f_s=500, f_su=550, failure_strain=0.15)
   top_layer = RebarLayer(
      centroid_z=25, width=2000, rebar_horizontal_distance=200, rebar_diameter=10)
   top_rebar_layer = reinforcement + top_layer
   bottom_layer = RebarLayer(
      centroid_z=75, width=2000, rebar_horizontal_distance=100, rebar_diameter=10)
   bottom_rebar_layer = reinforcement + bottom_layer
   i_profile = IProfile(
      top_edge=100.0, b_fo=200, t_fo=15, h_w=200-2*15, t_w=15, centroid_y=0.0)
   steel = Steel(f_y=355.0, f_u=400, failure_strain=0.15)
   steel_section = i_profile + steel
   cross_section = concrete_section + top_rebar_layer + bottom_rebar_layer + steel_section

As deformations depend on the type of loading we create a :py:class:`~m_n_kappa.SingleSpanUniformLoad`-instance
that represents a uniform loading of our beam.
The ``length``-parameter describes the length of our single-span beam and applies here to 8000 mm = 8 m.

.. altair-plot::
   :output: repr

   from m_n_kappa import SingleSpanUniformLoad
   loading = SingleSpanUniformLoad(length=8000)

The beam is computed by the :py:class:`~m_n_kappa.Beam` class.
:py:class:`~m_n_kappa.Beam` takes the ``cross_section``, the number of elements the
beam shall be at least split into and the ``loading`` as arguments.
The ``consider_width``-argument is optional and leads to a consideration of the effective widths,
if set to ``True``.

.. altair-plot::
   :output: repr

   from m_n_kappa import Beam
   beam = Beam(
       cross_section=cross_section, element_number=10, load=loading, consider_widths=False)

The :py:meth:`~m_n_kappa.Beam.deformation`-method gives you the deformation at the given position (``at_position``)
under the given load ``loading_for_deformation``.

.. altair-plot::
   :output: repr

   loading_for_deformation = SingleSpanUniformLoad(length=8000, load=10)
   beam.deformation(at_position=4000, load=loading_for_deformation)

With :py:meth:`~m_n_kappa.Beam.deformations_at_maximum_deformation_position` you get the maximum deformation
per loading.
In case of a single-span girder the corresponding position is in the middle of the beam (4000 mm).

.. altair-plot::

   maximum_deformation = beam.deformations_at_maximum_deformation_position()

   import pandas as pd
   df = pd.DataFrame(
        {'loadings': maximum_deformation.loadings(factor=0.001),
         'deformations': maximum_deformation.values()})

   import altair as alt
   alt.Chart(df, background='#00000000').mark_line().encode(
      x=alt.X('deformations', title='Deformation [mm]'),
      y=alt.Y('loadings', title='Loading [kN]'))

:py:meth:`~m_n_kappa.Beam.deformation_over_beam_length` computes the deformation by the given ``loading``.
Plotted the computed values look as follows:

.. altair-plot::

   deformations_over_length = beam.deformation_over_beam_length(load_step=loading_for_deformation)

   df = pd.DataFrame(
        {'positions': deformations_over_length.positions(),
         'deformations': deformations_over_length.values()})

   alt.Chart(df, height=100.0, background='#00000000').mark_line().encode(
       x=alt.X('positions', title='Beam position [mm]'),
       y=alt.Y('deformations', title='Deformation [mm]', scale=alt.Scale(reverse=True)))