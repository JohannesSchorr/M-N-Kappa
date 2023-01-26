.. _examples.moment_curvature_curve:

Moment-Curvature-Curve
**********************

*Units: Millimeter [mm], Newton [N]*

.. altair-plot::
   :output: None
   :hide-code:

   # configuration of altair-plot
   import altair as alt
   alt.themes.enable('quartz')

.. _examples.moment_curvature_curve.intro:

Introducing the cross-section
=============================

Our ``cross_section`` is a composite beam with a HEB 200 steel girder and a 2000x100 concrete slab.
The concrete is of type C30/35 with :math:`f_\mathrm{cm} = 38` N/mm².
The steel is of type S355 (:math:`f_\mathrm{y} = 355` N/mm²)
A top- and a bottom-layer of reinforcement is introduced into the concrete slab with concrete cover
:math:`c_\mathrm{nom}` on each side.
All reinforcement bars have diameter 10 and a strength :math:`f_\mathrm{s} = 500` N/mm².

You can build this cross-section in :py:mod:`m_n_kappa` as follows.

.. altair-plot::
   :output: repr

   from m_n_kappa import IProfile, Steel, Rectangle, Concrete, RebarLayer, Reinforcement
   concrete_slab = Rectangle(top_edge=0.0, bottom_edge=100, width=2000)
   concrete = Concrete(f_cm=30+8)
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


:ref:`examples.moment_curvature_curve.positive` shows how to compute the relationship of moments and curvatures
assuming positive curvature and positive moments.
Negative curvature and negative moments are given in :ref:`examples.moment_curvature_curve.negative`.
:ref:`examples.moment_curvature_curve.full` shows positive and negative moment-curvature values.

The following method reduces the process of putting the moment-curvature values into a moment-curvature-curve
diagram to a minimum.
The expected ``results``-dictionary must have the keys ``'Moment'`` and ``'Curvature'`` with the corresponding
values as lists tied to these keywords.
Other keys will appear in the tooltip.

.. altair-plot::
   :output: None

   import pandas as pd
   import altair as alt
   def m_kappa_diagram(results: dict) -> alt.Chart:
       """create moment-curvature diagram by passing moments and curvatures"""
       df = pd.DataFrame(results)

       line_chart = alt.Chart(df).mark_line().encode(
           y=alt.Y('Moment', title='Moment [kNm]'),
           x=alt.X('Curvature', title='Curvature [-]'),
       )

       circle_chart = alt.Chart(df).mark_point().encode(
           y=alt.Y('Moment'),
           x=alt.X('Curvature'),
           tooltip=list(results.keys()),
       )

       return alt.layer(line_chart, circle_chart, background='#00000000')

.. _examples.moment_curvature_curve.positive:

Moment-Curvature-Curve with positive values
===========================================

The moment-curvature curve is computed in :py:mod:`m_n_kappa` while
initializing :py:class:`~m_n_kappa.MKappaCurve`.
The computation of the positive values is set as the default, therefore only ``cross_section`` must be
passed to :py:class:`~m_n_kappa.MKappaCurve`.

The :py:meth:`~m_n_kappa.MKappaCurve.not_successful` returns those :py:class:`~m_n_kappa.StrainPosition` points
that have not lead to an equilibrium in horizontal forces.
The :py:class:`~m_n_kappa.StrainPosition` is given with a message that gives us information
why equilibrium has not been found.

.. altair-plot::
   :output: repr

   from m_n_kappa import MKappaCurve
   positive_m_kappa_curve_computation = MKappaCurve(cross_section=cross_section)
   positive_m_kappa_curve_computation.not_successful

The Moment-Curvature points may be extracted calling :py:meth:`~m_n_kappa.MKappaCurve.m_kappa_points`.

.. altair-plot::
   :output: repr

   positive_m_kappa_curve = positive_m_kappa_curve_computation.m_kappa_points

:py:meth:`~m_n_kappa.MKappaCurve.m_kappa_points` returns an :py:class:`~m_n_kappa.curves_m_kappa.MKappaCurvePoints`
object that has the method :py:meth:`~m_n_kappa.curves_m_kappa.MKappaCurvePoints.results_as_dict`.
It provides the moment-curvature-curve points as dictionary with keys ``'Moment'``, ``'Curvature'``,
``'Strain'``, ``'Position'`` and ``'Material'``.
These allow us to easily create the corresponding Moment-Curvature diagram with descriptive tooltips.

.. altair-plot::
   :alt: Moment-Curvature-Curve with positive values

   m_kappa_diagram(results=positive_m_kappa_curve.results_as_dict(moment_factor=0.001*0.001))

The diagram shows a maximum moment of :math:`M_\mathrm{max} \approx 550` kNm.

.. The plastic moment :math:`M_\mathrm{pl,Rd}`, computed by hand, shows a smaller value.

.. .. math::

..   N_\mathrm{pl,a,Rd} & = A_\mathrm{a} \cdot f_\mathrm{y} = 78.08 \cdot 35.5 = 2771,8 \text{ kN}

..   x_\mathrm{pl} & = \frac{N_\mathrm{pl,a,Rd}}{b \cdot f_\mathrm{c}} = \frac{2771,8}{200 \cdot 3,8} = 3.6 \text{ cm}

..   M_\mathrm{pl,Rd} & = N_\mathrm{pl,a,Rd} \cdot (h_\mathrm{c} + \frac{h_\mathrm{a}}{2} - \frac{x_\mathrm{pl}}{2}
   = 2771,8 \cdot \left(10 + \frac{20}{2} - \frac{3.6}{2}\right) = 45457,5 \text{ kNcm} = 454,6 \text{ kNm}


.. _examples.moment_curvature_curve.negative:

Moment-Curvature-Curve with negative values
===========================================

Computing the Moment-Curvature curve with negative values is similar to the :ref:`examples.moment_curvature_curve.positive`,
but ``include_positive_curvature=False`` (default: ``True``) and ``include_negative_curvature=True`` (default: ``False``)
must be passed to :py:class:`~m_n_kappa.MKappaCurve`.

.. altair-plot::
   :output: repr

   negative_m_kappa_curve_computation = MKappaCurve(
       cross_section=cross_section,
       include_positive_curvature=False,
       include_negative_curvature=True,
   )
   negative_m_kappa_curve = negative_m_kappa_curve_computation.m_kappa_points

The corresponding Moment-Curvature-curve diagram is given hereafter.

.. altair-plot::
   :alt: Moment-Curvature-Curve with negative values

   m_kappa_diagram(results=negative_m_kappa_curve.results_as_dict(moment_factor=0.001*0.001))

The diagram shows in absolute values a smaller maximum moment than the cross-section under positive curvature.
But the maximum curvatures are in absolute values much higher.
This is related to the higher strains the reinforcement and the steel-material can bear as the concrete in compression.


.. _examples.moment_curvature_curve.full:

Full Moment-Curvature-Curve
===========================

In case you want to compute all values at once you only have to pass your ``cross_section`` and
``include_negative_curvature=True`` to :py:meth:`~m_n_kappa.MKappaCurve`.

.. altair-plot::
   :alt: Full Moment-Curvature-Curve with positive and negative values

   full_m_kappa_curve_computation = MKappaCurve(
       cross_section=cross_section,
       include_negative_curvature=True,
   )
   full_m_kappa_curve = full_m_kappa_curve_computation.m_kappa_points

   m_kappa_diagram(results=full_m_kappa_curve.results_as_dict(moment_factor=0.001*0.001))

As shown the moment-curvature curve is easily computed using :py:mod:`m_n_kappa`.
The classes and methods shown here, are building the basis to compute the deformation of a beam.