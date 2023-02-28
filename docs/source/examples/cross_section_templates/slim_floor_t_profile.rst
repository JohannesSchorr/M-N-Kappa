.. _cross_section_template.slim_floor_t_profile:

T-profile slim-floor beam
*************************

*Units: Millimeter [mm], Newton [N]*

Geometry and materials
======================

The code below creates a ``cross_section`` that represents a slim-floor-beam where
a T-profile of steel is integrated into a solid concrete-slab of type C30/35.

The ``concrete_slab`` is split into three parts:

- concrete-slab above the steel profile
- concrete-slab left and right of the steel-beam

Each of these parts is an individual :py:class:`~m_n_kappa.Rectangle`.
The overall bottom-edge of the concrete-slab is similar to the top-edge
of the I-profile.
The non-linear relationship is used to model the stress-strain-relationship
of the used :py:class:`~m_n_kappa.Concrete`.

Also integrated into the concrete-slab are ``rebar_layer`` s, consisting
of a number of reinforcement bars.
The bi-linear stress-strain-relationship with hardening is used for the
reinforcement-bars as well as for the I-profile (see
:py:class:`~m_n_kappa.Reinforcement`, :py:class:`~m_n_kappa.Steel`).

.. grid:: 1 2 2 2

   .. grid-item::

       .. figure:: ../../images/template_geometry_slim_floor_t_profile-light.svg
         :class: only-light
         :alt: Cross-section of slim-floor beam with T-shaped steel profile
         :width: 250
      .. figure:: ../../images/template_geometry_slim_floor_t_profile-dark.svg
         :class: only-dark
         :alt: Cross-section of slim-floor beam with T-shaped steel profile
         :width: 250

         Geometry: Cross-section of slim-floor beam with T-shaped steel profile

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
>>> t_profile = IProfile(top_edge=50.0, t_w=10.0, h_w=200.0, b_fu=200.0, t_fu=15.0, has_top_flange=False)
>>> steel = Steel(f_y=355.0, f_u=400, failure_strain=0.15)
>>> steel_profile = t_profile + steel
>>> concrete_top_cover = Rectangle(top_edge=0.0, bottom_edge=t_profile.top_edge, width=2000)
>>> concrete_left = Rectangle(
...     top_edge=concrete_top_cover.bottom_edge, bottom_edge=t_profile.top_edge + t_profile.h_w,
...     width=0.5*(2000-t_profile.t_w), left_edge=-1000)
>>> concrete_right = Rectangle(
...     top_edge=concrete_top_cover.bottom_edge, bottom_edge=t_profile.top_edge + t_profile.h_w,
...     width=0.5*(2000-t_profile.t_w), right_edge=1000)
>>> slab = concrete_top_cover + concrete_left + concrete_right
>>> concrete = Concrete(f_cm=30+8, )
>>> concrete_slab = slab + concrete
>>> reinforcement = Reinforcement(f_s=500, f_su=550, failure_strain=0.15)
>>> top_layer = RebarLayer(
...     centroid_z=0.5*50, width=2000, rebar_horizontal_distance=200, rebar_diameter=10)
>>> top_rebar_layer = reinforcement + top_layer
>>> bottom_layer_left = RebarLayer(
...     centroid_z=t_profile.top_edge + t_profile.h_w - 25, width=0.5*(2000 - t_profile.t_w),
...     right_edge=-0.5*t_profile.t_w, rebar_horizontal_distance=200, rebar_diameter=10)
>>> bottom_layer_right = RebarLayer(
...     centroid_z=t_profile.top_edge + t_profile.h_w - 25, width=0.5*(2000 - t_profile.t_w),
...     left_edge=0.5*t_profile.t_w, rebar_horizontal_distance=200, rebar_diameter=10)
>>> rebar_layer = top_layer + bottom_layer_left + bottom_layer_right
>>> rebar = rebar_layer + reinforcement
>>> cross_section = steel_profile + concrete_slab + rebar

.. include:: cross_section_computation.rst

References
==========

.. [1] EN 1992-1-1: Eurocode 2: Design of concrete structures - Part 1-1: General rules and rules
   for buildings, European Committee of Standardization (CEN), 2004ss_section_computation.rst