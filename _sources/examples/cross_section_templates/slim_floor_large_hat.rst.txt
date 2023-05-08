.. _cross_section_template.slim_floor_large_hat:

Slim-floor beam with large hat profile
**************************************

*Units: Millimeter [mm], Newton [N]*

Geometries and materials
========================

The code below creates the ``cross_section`` of a slim-floor beam with the following parts:

- large hat steel profile with :math:`f_\mathrm{y}` = 355 N/mm² and :math:`f_\mathrm{u}`
  = 500 N/mm²
- bottom steel flange with 400x12 mm with :math:`f_\mathrm{y}` = 460 N/mm² and
  :math:`f_\mathrm{u}` = 500 N/mm²
- concrete slab with concrete compressive strength :math:`f_\mathrm{cm} = 38` N/mm²
- top-rebar-layer 10/100, :math:`c_\mathrm{nom}` = 10 mm,
  with :math:`c_\mathrm{nom} = 10` mm from the top-edge of the concrete-slab
- bottom-rebar-layer 12/100, :math:`c_\mathrm{nom}` = 12 mm,
  with :math:`c_\mathrm{nom} = 10` mm from the bottom-edge of the concrete-slab

The hat profile is positioned on top of the bottom-flange forming the steel girder.
The steel girder is integrated into the concrete slab.
Therefore, the concrete slab is situated around the steel-beam, what is done by splitting
the concrete slab in appropriate pieces.

.. grid:: 1 2 2 2

   .. grid-item::

      .. figure:: ../../images/template_geometry_slim_floor_large_hat_profile-light.svg
         :class: only-light
         :alt: Geometry of the slim-floor beam with large hat profile
         :width: 250
      .. figure:: ../../images/template_geometry_slim_floor_large_hat_profile-dark.svg
         :class: only-dark
         :alt: Geometry of the slim-floor beam with large hat profile
         :width: 250

         Geometry: Slim-Floor beam with large hat profile

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


Slim-Floor cross-section
========================

>>> from m_n_kappa import Rectangle, Steel, UPEProfile, Concrete, RebarLayer, Reinforcement
>>> plate_geometry = Rectangle(top_edge=220.0, bottom_edge=220.0+12., width=400.0)
>>> bottom_flange_material = Steel(f_y=355, f_u=500, failure_strain=0.15)
>>> bottom_flange = plate_geometry + bottom_flange_material
>>> hat_geometry = UPEProfile(
...     top_edge=50, t_f=5.2, b_f=plate_geometry.top_edge, t_w=9.0, h=300)
>>> hat_material = Steel(f_y=460, f_u=500, failure_strain=0.15)
>>> hat = hat_geometry + hat_material
>>> concrete_left = Rectangle(
...     top_edge=0.0, bottom_edge=plate_geometry.top_edge, width=1600.0,
...     left_edge=-1750.0, right_edge=-150.0)
>>> concrete_middle = Rectangle(
...     top_edge=0.0, bottom_edge=hat_geometry.top_edge, width=hat_geometry.h,
...     left_edge=-150.0, right_edge=150.0)
>>> concrete_right = Rectangle(
...     top_edge=0.00, bottom_edge=plate_geometry.top_edge, width=1600.00,
...     left_edge=150.0, right_edge=1750.00)
>>> concrete_geometry = concrete_left + concrete_middle + concrete_right
>>> concrete_material = Concrete(
...     f_cm=38.9,
...     compression_stress_strain_type='Nonlinear')
>>> concrete_slab = concrete_geometry + concrete_material
>>> rebar_top_layer_geometry = RebarLayer(
...     rebar_diameter=12., centroid_z=10.0, width=3500, rebar_horizontal_distance=100.)
>>> rebar_bottom_layer_left_geometry = RebarLayer(
...	    rebar_diameter=10., centroid_z=220-10, width=1600.0,
...     rebar_horizontal_distance=100., left_edge=-1740.,)
>>> rebar_bottom_layer_right_geometry = RebarLayer(
...	    rebar_diameter=10., centroid_z=220-10, width=1600.0,
...     rebar_horizontal_distance=100., right_edge=1740.,)
>>> rebar10_material = Reinforcement(f_s=500, f_su=550, failure_strain=0.25, E_s=200000)
>>> rebar12_material = Reinforcement(f_s=500, f_su=550, failure_strain=0.25, E_s=200000)
>>> rebar_top_layer = rebar_top_layer_geometry + rebar12_material
>>> rebar_bottom_layer_left = rebar_bottom_layer_left_geometry + rebar10_material
>>> rebar_bottom_layer_right = rebar_bottom_layer_right_geometry + rebar10_material
>>> rebar_layer = rebar_top_layer + rebar_bottom_layer_left + rebar_bottom_layer_right
>>> cross_section = bottom_flange + hat + concrete_slab + rebar_layer

.. include:: cross_section_computation.rst

References
==========
.. [1] EN 1992-1-1: Eurocode 2: Design of concrete structures - Part 1-1: General rules and rules
   for buildings, European Committee of Standardization (CEN), 2004