.. _cross_section_template.composite_beam:

Composite beam
**************

*Units: Millimeter [mm], Newton [N]*

Geometries and materials
========================

This template creates a composite beam with the following parts:

- concrete slab 2000x100 with concrete of type C30/35
- with top-rebar-layer 10/200, :math:`c_\mathrm{nom}` = 25 mm
- and bottom-rebar-layer 10/100, :math:`c_\mathrm{nom}` = 25 mm
- HEB 200 steel profile of steel-grade S355

The concrete slab is an ordinary rectangle of ``width=2000`` and height=100 mm.
The concrete-material-strength is computed in line with EN 1992-1-1, Tab. 3.1 [1]_
:math:`f_\mathrm{cm} = f_\mathrm{ck} + 8 = 30 + 8 = 38` N/mm².

The geometry-values of the :ref:`cross_section_template.symmetric_steel_profile` are:

- ``top_edge=100``: applies to the height of the concrete-section as the top of the
  steel profile is arranged at the bottom of the concrete slab.
- ``b_fo=200``: width of the top-flange :math:`b_\mathrm{fo} = 200` mm (and the bottom-flange
  due to the symmetric profile)
- ``t_fo=15``: thickness of the top-flange :math:`t_\mathrm{fo} = 15` mm (and the bottom-flange
  due to the symmetric profile)
- ``h_w=200-2*15``: height of the steel web :math:`h_\mathrm{w} = 200-2 \cdot 15 = 170` mm
- ``t_w=9.5``: thickness of the steel web :math:`t_\mathrm{w} = 9.5` mm

The material-model of the HEB200-profile is isotropic steel using following values:

- ``f_y=355``: yield strength of the steel :math:`f_\mathrm{y} = 355` N/mm²
- ``f_y=400``: tensile strength of the steel :math:`f_\mathrm{u} = 400` N/mm²
- ``failure_strain=0.15``: failure strain of the steel :math:`\varepsilon_\mathrm{u} = 15` %

.. grid:: 1 2 2 2

   .. grid-item::

      .. figure:: ../../images/template_geometry_composite_beam-light.svg
         :class: only-light
      .. figure:: ../../images/template_geometry_composite_beam-dark.svg
         :class: only-dark

         Geometry: Composite beam

   .. grid-item::

      .. figure:: ../../images/material_steel_trilinear-light.svg
         :class: only-light
         :alt: Defined stress-strain-relationship of structural steel and reinforcement
         :width: 250
      .. figure:: ../../images/material_steel_trilinear-dark.svg
         :class: only-dark
         :alt: Defined stress-strain-relationship of structural steel and reinforcement
         :width: 250

         Material: Bi-linear stress-strain-relationship with hardening of steel

   .. grid-item::

      .. figure:: ../../images/material_concrete_nonlinear-light.svg
         :class: only-light
         :alt: Defined non-linear stress-strain-relationship of concrete in compression acc. to EN 1992-1-1
         :width: 250
      .. figure:: ../../images/material_concrete_nonlinear-dark.svg
         :class: only-dark
         :alt: Defined non-linear stress-strain-relationship of concrete in compression acc. to EN 1992-1-1
         :width: 250

         Material: Concrete non-linear stress-strain-relationship in compression acc. EN 1992-1-1 [1]_

   .. grid-item::

      .. figure:: ../../images/material_concrete_tension_default-light.svg
         :class: only-light
         :alt: Stress-strain-relationship of concrete in tension
         :width: 250
      .. figure:: ../../images/material_concrete_tension_default-dark.svg
         :class: only-dark
         :alt: Stress-strain-relationship of concrete in tension
         :width: 250

         Material: Stress-strain-relationship of concrete in tension

Composite cross-section
=======================

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
...     top_edge=0.0, b_fo=200, t_fo=15, h_w=200-2*15, t_w=15, centroid_y=0.0)
>>> steel = Steel(f_y=355.0, f_u=400, failure_strain=0.15)
>>> steel_section = i_profile + steel
>>> cross_section = concrete_section + top_rebar_layer + bottom_rebar_layer + steel_section

As nothing is passed to the ``compression_stress_strain``-argument of :py:class:`~m_n_kappa.Concrete`, the
``'Nonlinear'`` stress-strain-relationship is applied (default).
Tension is considered for :py:class:`~m_n_kappa.Concrete`, but may be neglected by passing ``use_tension=False``.

.. include:: cross_section_computation.rst

References
==========

.. [1] EN 1992-1-1: Eurocode 2: Design of concrete structures - Part 1-1: General rules and rules
   for buildings, European Committee of Standardization (CEN), 2004