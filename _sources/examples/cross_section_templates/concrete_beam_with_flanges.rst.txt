.. _cross_section_template.concrete_beam_with_flanges:

Concrete beam with flanges
**************************

*Units: Millimeter [mm], Newton [N]*

Geometries and materials
========================

A concrete beam with concrete flanges positioned at the top is given here.

The beam has a width of 200 mm and a height of 400 mm.
The concrete flanges are positioned at the top of the beam an have an overall width of 2000 mm.
The concrete material is of type C30/35 with a mean compressive strength of :math:`f_\mathrm{cm} = 38`
N/mm² [1]_.

The concrete flanges are reinforced with a with a top- and a bottom-reinforcement-layer.
Within these layer diameter 10 mm reinforcement-bars are used with a distance of 100 mm.

At the bottom-edge of the concrete beam ``4`` reinforcement-bars of diameter 20 mm are introduced.
The reinforcement has a yield strength of :math:`f_\mathrm{s} = 500` N/mm² and a tensile strength
:math:`f_\mathrm{su} = 550` N/mm².
At failure a strain of 2.5 % is assumed.
The concrete-cover of the reinforcement-bars applies to :math:`c_\mathrm{nom} = 15` mm.

.. grid:: 1 2 2 2

   .. grid-item::

      .. figure:: ../../images/template_geometry_concrete_beam_with_flanges-light.svg
         :class: only-light
         :alt: Geometry of the reinforced concrete beam with concrete flanges
         :width: 400
      .. figure:: ../../images/template_geometry_concrete_beam_with_flanges-dark.svg
         :class: only-dark
         :alt: Geometry of the reinforced concrete beam with concrete flanges
         :width: 400

         Geometry: Reinforced concrete beam with concrete flanges

   .. grid-item::

      .. figure:: ../../images/material_steel_trilinear-light.svg
         :class: only-light
         :alt: Defined stress-strain-relationship of reinforcement
         :width: 250
      .. figure:: ../../images/material_steel_trilinear-dark.svg
         :class: only-dark
         :alt: Defined stress-strain-relationship of reinforcement
         :width: 250

         Material: Bi-linear stress-strain-relationship of reinforcement

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


Concrete beam with flanges cross-section
========================================

>>> from m_n_kappa import Rectangle, Concrete, RebarLayer, Reinforcement
>>> flanges = Rectangle(top_edge=0.0, bottom_edge=100., width=2000.0)
>>> beam = Rectangle(top_edge=flanges.bottom_edge, bottom_edge=400.0, width=200.0)
>>> concrete_geometry = flanges + beam
>>> concrete = Concrete(38.0)
>>> concrete_beam = concrete_geometry + concrete
>>> flange_concrete_cover = 15.0 + 0.5 * 10.0
>>> flange_top_rebars = RebarLayer(
...     centroid_z=flange_concrete_cover, width=flanges.width - 2.*flange_concrete_cover,
...     rebar_horizontal_distance=100.0, rebar_diameter=10.0)
>>> flange_bottom_rebars = RebarLayer(
...     centroid_z=flanges.bottom_edge - flange_concrete_cover, width=flanges.width - 2.*flange_concrete_cover,
...     rebar_horizontal_distance=100.0, rebar_diameter=10.0)
>>> beam_concrete_cover = 15.0 + 0.5 * 20.0
>>> beam_rebars = RebarLayer(
...     centroid_z=beam.bottom_edge - beam_concrete_cover, width=beam.width - 2.*beam_concrete_cover,
...     rebar_number=4, rebar_diameter=20.0)
>>> rebars = flange_top_rebars + flange_bottom_rebars + beam_rebars
>>> reinforcing_steel = Reinforcement(f_s=500.0, f_su=550.0, failure_strain=0.25)
>>> reinforcement = rebars + reinforcing_steel
>>> cross_section = concrete_beam + reinforcement

.. include:: cross_section_computation.rst


References
==========
.. [1] EN 1992-1-1: Eurocode 2: Design of concrete structures - Part 1-1: General rules and rules
   for buildings, European Committee of Standardization (CEN), 2004