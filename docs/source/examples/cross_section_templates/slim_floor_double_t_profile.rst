.. _cross_section_template.slim_floor_double_t_profile:

Slim-Floor double T-profile
***************************

*Units: Millimeter [mm], Newton [N]*

Geometry and materials
======================

The steel-part of this slim-floor consists of a bottom-flange where two webs are welded on top.
Between these two webs a higher strength concrete is introduced that is reinforced by a top-
and a bottom-layer.

.. grid:: 1 2 2 2

   .. grid-item::

       .. figure:: ../../images/template_geometry_slim_floor_double_t_profile-light.svg
         :class: only-light
         :alt: Cross-section of slim-floor beam with double T steel profile
         :width: 500
      .. figure:: ../../images/template_geometry_slim_floor_double_t_profile-dark.svg
         :class: only-dark
         :alt: Cross-section of slim-floor beam with double T steel profile
         :width: 500

         Geometry: Cross-section of slim-floor beam with double T-steel profile

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


Slim-floor beam with I-profile cross-section
============================================

>>> from m_n_kappa import Steel, Rectangle, Concrete, RebarLayer, Reinforcement
>>> concrete_core = Rectangle(top_edge=0.0, bottom_edge=200, width=300)
>>> concrete_material = Concrete(f_cm=60)
>>> concrete_slab = concrete_core + concrete_material
>>> left_web = Rectangle(
...     top_edge=40, bottom_edge=concrete_core.bottom_edge, width=8.0, right_edge=-0.5*concrete_core.left_edge)
>>> right_web = Rectangle(
...     top_edge=40, bottom_edge=concrete_core.bottom_edge, width=8.0, left_edge=0.5*concrete_core.left_edge)
>>> bottom_flange = Rectangle(
...     top_edge=concrete_core.bottom_edge, bottom_edge=concrete_core.bottom_edge + 12.0,
...     width=596.0)
>>> girder = left_web + right_web + bottom_flange
>>> steel = Steel(f_y=460, f_u=500, failure_strain=0.15)
>>> steel_girder = girder + steel
>>> reinforcement = Reinforcement(f_s=500, f_su=550, failure_strain=0.25)
>>> rebar_top_layer = RebarLayer(rebar_diameter=20, centroid_z=38.0, rebar_number=5, width=concrete_core.width - 2 * 28)
>>> rebar_bottom_layer = RebarLayer(
...     rebar_diameter=16.0, centroid_z=bottom_flange.bottom_edge-46.0,
...     rebar_number=3, width=rebar_top_layer.width)
>>> rebar_layers = rebar_top_layer + rebar_top_layer
>>> rebars = rebar_layers + reinforcement
>>> cross_section = concrete_slab + steel_girder + rebars

.. include:: cross_section_computation.rst

References
==========

.. [1] EN 1992-1-1: Eurocode 2: Design of concrete structures - Part 1-1: General rules and rules
   for buildings, European Committee of Standardization (CEN), 2004ss_section_computation.rst