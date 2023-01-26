.. _examples.moment_curvature:

Moment-Curvature
****************

*Units: Millimeter [mm], Newton [N]*

In case you have a strain :math:`\varepsilon` at a vertical position
:math:`z` and you want to know what curvature leads to this strain
in a cross-section, then you can ease your life and use
:py:class:`~m_n_kappa.MKappaByStrainPosition`.

As ``cross_section`` a composite beam consisting of a HEB200 (S355) and
a rectangular concrete-slab (C30/35) with a top and a bottom
reinforcement layer is defined.

>>> from m_n_kappa import IProfile, Steel, Rectangle, Concrete, RebarLayer, Reinforcement
>>> concrete_slab = Rectangle(top_edge=0.0, bottom_edge=100, width=2000)
>>> concrete = Concrete(f_cm=30+8, )
>>> concrete_section = concrete_slab + concrete
>>> reinforcement = Reinforcement(f_s=500, f_su=550, failure_strain=0.15)
>>> top_layer = RebarLayer(
...     centroid_z=25, width=2000, rebar_horizontal_distance=200, rebar_diameter=10)
>>> top_rebar_layer = reinforcement + top_layer
>>> bottom_layer = RebarLayer(
...     centroid_z=75, width=2000, rebar_horizontal_distance=100, rebar_diameter=10)
>>> bottom_rebar_layer = reinforcement + bottom_layer
>>> i_profile = IProfile(
...     top_edge=100.0, b_fo=200, t_fo=15, h_w=200-2*15, t_w=15, centroid_y=0.0)
>>> steel = Steel(f_y=355.0, f_u=400, failure_strain=0.15)
>>> steel_section = i_profile + steel
>>> cross_section = concrete_section + top_rebar_layer + bottom_rebar_layer + steel_section

The strain and its position is defined using
:py:class:`~m_n_kappa.StrainPosition`.
For our example the strain is defined to :math:`\varepsilon` = 0.0035
and its' position :math:`z` = 0.0 is used, what denotes to the top-edge
of the cross-section.

>>> from m_n_kappa import StrainPosition
>>> strain_position = StrainPosition(
...     strain=-0.002, position=0.0, material='Concrete'
... )

To find equilibrium axial-forces ``strain_position`` is to be passed to
:py:class:`~m_n_kappa.MKappaByStrainPosition` as well as the
``cross-section``.
By default the positive curvature is computed.
In case you want to compute the negative curvature, you only have to
pass argument ``positive_curvature=False``.

The finding of the horizontal equilibrium :math:`\sum N_i = 0` is
conducted during initialization.
If the property ``successful=True`` then horizontal equilibrium of
axial forces is found.

>>> from m_n_kappa import MKappaByStrainPosition
>>> m_kappa_point = MKappaByStrainPosition(
...     cross_section=cross_section,
...     strain_position=strain_position,
...     positive_curvature=True)  # default
>>> m_kappa_point.successful
True

The computed sum of axial-forces you may control by calling
``axial_force``, that is near zero.

>>> m_kappa_point.axial_force
-4.133298293221742

Moment and curvature are extracted by calling the corresponding
properties of ``m_kappa_point``.

>>> m_kappa_point.moment, m_kappa_point.curvature
(532345821.77170306, 3.26619749682544e-05)

As well as the vertical position of the ``neutral_axis``.

>>> m_kappa_point.neutral_axis
61.233284329679606

Further details regarding the computation are described by
:py:class:`~m_n_kappa.MKappaByStrainPosition`.

:py:class:`~m_n_kappa.MKappaByStrainPosition` serves to compute single
moment-curvature points of the :ref:`examples.moment_curvature_curve`.