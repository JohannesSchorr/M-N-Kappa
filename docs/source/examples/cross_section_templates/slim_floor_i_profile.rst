.. _cross_section_template.slim_floor_i_profile:

I-Profile slim-floor beam
*************************

*Units: Millimeter [mm], Newton [N]*

Geometry and materials
======================

The code below creates a ``cross_section`` that represents a slim-floor-beam where
a steel I-profile (HEB 200) is integrated into a solid concrete-slab of type C30/35.

The ``concrete_slab`` is split into five parts:

- concrete-slab left and right of the steel-beam
- concrete within each of the two chambers
- concrete-cover above the steel-profile

Each of these parts is an individual :py:class:`~m_n_kappa.Rectangle`.
The overall bottom-edge of the concrete-slab is similar to the bottom-edge
of the I-profile.
The non-linear relationship is used to model the stress-strain-relationship
of the used :py:class:`~m_n_kappa.Concrete`.

Also integrated into the concrete-slab are ``rebar_layer``s, consisting
of a number of reinforcement bars.
The bi-linear stress-strain-relationship with hardening is used for the
reinforcement-bars as well as for the I-profile (see
:py:class:`~m_n_kappa.Reinforcement`, :py:class:`~m_n_kappa.Steel`).

.. grid:: 1 2 2 2

   .. grid-item::

      .. figure:: ../../images/template_geometry_slim_floor_i_profile_solid_slab-light.svg
         :class: only-light
         :alt: Cross-section of slim-floor beam with I-profile and solid slab
         :width: 250
      .. figure:: ../../images/template_geometry_slim_floor_i_profile_solid_slab-dark.svg
         :class: only-dark
         :alt: Cross-section of slim-floor beam with I-profile and solid slab
         :width: 250

         Geometry: Cross-section of slim-floor beam with I-profile and solid slab

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

>>> from m_n_kappa import IProfile, Steel, Rectangle, Concrete, RebarLayer, Reinforcement
>>> concrete_slab_left = Rectangle(top_edge=0.0, bottom_edge=240, width=0.5*(2000-200), left_edge=-1000)
>>> concrete_slab_right = Rectangle(top_edge=0.0, bottom_edge=240, width=0.5*(2000-200), right_edge=1000)
>>> concrete_top_cover = Rectangle(top_edge=0.0, bottom_edge=50, width=200)
>>> concrete_left_chamber = Rectangle(top_edge=50+15.4, bottom_edge=50+200-15.4, width=(200-9.5)/2, left_edge=-200/2)
>>> concrete_right_chamber = Rectangle(top_edge=50+15.4, bottom_edge=50+200-15.4, width=(200-9.5)/2, right_edge=200/2)
>>> concrete_slab = concrete_slab_left + concrete_slab_right + concrete_top_cover + concrete_left_chamber + concrete_right_chamber
>>> concrete = Concrete(f_cm=30+8, )
>>> concrete_section = concrete_slab + concrete
>>> reinforcement = Reinforcement(f_s=500, f_su=550, failure_strain=0.15)
>>> top_layer = RebarLayer(
...     centroid_z=0.5*50, width=2000, rebar_horizontal_distance=200, rebar_diameter=10)
>>> top_rebar_layer = reinforcement + top_layer
>>> bottom_layer_left = RebarLayer(
...     centroid_z=240-10, width=2000, rebar_horizontal_distance=100, rebar_diameter=10, left_edge=-2000/2+10)
>>> bottom_layer_right = RebarLayer(
...     centroid_z=240-10, width=(2000-200-2*10)/2, rebar_horizontal_distance=100, rebar_diameter=10, right_edge=2000/2+10)
>>> bottom_rebar_layer_left = reinforcement + bottom_layer_left
>>> bottom_rebar_layer_right = reinforcement + bottom_layer_right
>>> rebar_layer = top_rebar_layer + bottom_rebar_layer_left + bottom_rebar_layer_right
>>> i_profile = IProfile(
...     top_edge=100.0, b_fo=200, t_fo=15, h_w=200-2*15, t_w=15, centroid_y=0.0)
>>> steel = Steel(f_y=355.0, f_u=400, failure_strain=0.15)
>>> steel_section = i_profile + steel
>>> cross_section = concrete_section + rebar_layer + steel_section

.. include:: cross_section_computation.rst

References
==========

.. [1] EN 1992-1-1: Eurocode 2: Design of concrete structures - Part 1-1: General rules and rules
   for buildings, European Committee of Standardization (CEN), 2004