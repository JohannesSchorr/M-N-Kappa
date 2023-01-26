.. _cross_section_template.asymmetric_steel_profile:

Asymmetric steel profile
************************

This template creates an asymmetric steel-profile of steel-grade S355.

Units: Millimeter [mm], Newton [N]

The geometry-values are:

- ``b_fo=100``: width of the top-flange :math:`b_\mathrm{fo} = 100` mm
- ``t_fo=15``: thickness of the top-flange :math:`t_\mathrm{fo} = 15` mm
- ``h_w=200-2*15``: height of the steel web :math:`h_\mathrm{w} = 200-2 \cdot 15 = 170` mm
- ``t_w=9.5``: thickness of the steel web :math:`t_\mathrm{w} = 9.5` mm
- ``b_fu=200``: width of the top-flange :math:`b_\mathrm{fu} = 200` mm
- ``t_fu=15``: thickness of the top-flange :math:`t_\mathrm{fu} = 15` mm

The material-model is isotropic steel using following values:

- ``f_y=355``: yield strength of the steel :math:`f_\mathrm{y} = 355` N/mm²
- ``f_y=400``: tensile strength of the steel :math:`f_\mathrm{u} = 400` N/mm²
- ``failure_strain=0.15``: failure strain of the steel :math:`\varepsilon_\mathrm{u} = 15` %

>>> from m_n_kappa import IProfile, Steel
>>> i_profile = IProfile(
...     top_edge=0.0,
...     b_fo=200, t_fo=15,
...     h_w=200-2*15, t_w=15,
...     b_fu=400, t_fu=15,
...     centroid_y=0.0)
>>> steel = Steel(f_y=355.0, f_u=400, failure_strain=0.15)
>>> cross_section = i_profile + steel


.. grid:: 1 2 2 2

   .. grid-item::

      .. figure:: ../../images/template_geometry_asymmetric_steel_profile-light.svg
         :class: only-light
         :width: 400
      .. figure:: ../../images/template_geometry_asymmetric_steel_profile-dark.svg
         :class: only-dark
         :width: 400

         Geometry: Asymmetric I-profile

   .. grid-item::

      .. figure:: ../../images/material_steel_trilinear-light.svg
         :class: only-light
         :width: 250
      .. figure:: ../../images/material_steel_trilinear-dark.svg
         :class: only-dark
         :width: 250

         Material: Bi-linear stress-strain-relationship with hardening of steel



.. include:: cross_section_computation.rst