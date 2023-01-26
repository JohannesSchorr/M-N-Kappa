.. _cross_section_template.slim_floor_upe:

UPE slim-floor beam
*******************

.. todo::
   document examples/cross_section_templates/slim_floor_upe

Geometries and materials
========================

This template creates the ``cross_section`` of a slim-floor beam with the following parts:

- UPE 200 steel profile with :math:`f_\mathrm{y}` = 293 N/mm² and :math:`f_\mathrm{u}` = 443 N/mm²
- bottom steel flange with 400x10 with :math:`f_\mathrm{y}` = 313 N/mm² and :math:`f_\mathrm{u}` = 460 N/mm²
- concrete slab with concrete compressive strength :math:`f_\mathrm{cm} = 29.5` N/mm²
- top-rebar-layer 10/100, :math:`c_\mathrm{nom}` = 10 mm
- bottom-rebar-layer 12/100, :math:`c_\mathrm{nom}` = 12 mm

The UPE 200 profile is positioned on top of the bottom-flange.
In reality the UPE-profile is welded on top of the bottom-flange steel-plate,
what is assumed by the :py:mod:`m_n_kappa` by default.

This steel girder is integrated into the concrete slab.
Therefore, the concrete slab is situated around the steel-beam, what is done by splitting
the concrete slab in appropriate pieces.

Slim-Floor cross-section
========================

>>> from m_n_kappa import Rectangle, Steel, UPEProfile, Concrete, RebarLayer, Reinforcement
>>> plate_geometry = Rectangle(top_edge=220.0, bottom_edge=220.0+10., width=400.0)
>>> bottom_flange_material = Steel(f_y=313, f_u=460, failure_strain=0.15)
>>> bottom_flange = plate_geometry + bottom_flange_material
>>> upe200_geometry = UPEProfile(top_edge=144, t_f=5.2, b_f=76, t_w=9.0, h=200)
>>> upe200_material = Steel(f_y=293, f_u=443, failure_strain=0.15)
>>> upe200 = upe200_geometry + upe200_material
>>> concrete_left = Rectangle(top_edge=0.00, bottom_edge=220.00, width=1650.00, left_edge=-1750.00, right_edge=-100.00)
>>> concrete_middle = Rectangle(top_edge=0.00, bottom_edge=144.00, width=200.00, left_edge=-100.00, right_edge=100.00)
>>> concrete_right = Rectangle(top_edge=0.00, bottom_edge=220.00, width=1650.00, left_edge=100.00, right_edge=1750.00)
>>> concrete_geometry = concrete_left + concrete_middle + concrete_right
>>> concrete_material = Concrete(
...     f_cm=29.5,
...     f_ctm=2.8,
...     compression_stress_strain_type='Nonlinear',
...     tension_stress_strain_type='consider opening behaviour')
>>> concrete_slab = concrete_geometry + concrete_material
>>> rebar_top_layer_geometry = RebarLayer(rebar_diameter=12., centroid_z=10.0, width=3500, rebar_horizontal_distance=100.)
>>> rebar_bottom_layer_left_geometry = RebarLayer(
...	   rebar_diameter=10., centroid_z=220-10, width=1650.0, rebar_horizontal_distance=100., left_edge=-1740.,)
>>> rebar_bottom_layer_right_geometry = RebarLayer(
...	   rebar_diameter=10., centroid_z=220-10, width=1650.0, rebar_horizontal_distance=100., right_edge=1740.,)
>>> rebar10_material = Reinforcement(f_s=594, f_su=685, failure_strain=0.25, E_s=200000)
>>> rebar12_material = Reinforcement(f_s=558, f_su=643, failure_strain=0.25, E_s=200000)
>>> rebar_top_layer = rebar_top_layer_geometry + rebar12_material
>>> rebar_bottom_layer_left = rebar_bottom_layer_left_geometry + rebar10_material
>>> rebar_bottom_layer_right = rebar_bottom_layer_right_geometry + rebar10_material
>>> rebar_layer = rebar_top_layer + rebar_bottom_layer_left + rebar_bottom_layer_right
>>> cross_section = bottom_flange + upe200 + concrete_slab + rebar_layer


.. include:: cross_section_computation.rst