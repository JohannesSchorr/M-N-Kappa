.. _cross_section_template.symmetric_steel_profile:

Symmetric steel profile
***********************
This template creates a HEB 200 steel-profile of steel-grade S355.

Units: Millimeter [mm], Newton [N]

The geometry-values are:

- ``b_fo=200``: width of the top-flange :math:`b_\mathrm{fo} = 200` mm (and the bottom-flange)
- ``t_fo=15``: thickness of the top-flange :math:`t_\mathrm{fo} = 15` mm (and the bottom-flange)
- ``h_w=200-2*15``: height of the steel web :math:`h_\mathrm{w} = 200-2 \cdot 15 = 170` mm
- ``t_w=9.5``: thickness of the steel web :math:`t_\mathrm{w} = 9.5` mm

The material-model is isotropic steel using following values:

- ``f_y=355``: yield strength of the steel :math:`f_\mathrm{y} = 355` N/mm²
- ``f_y=400``: tensile strength of the steel :math:`f_\mathrm{u} = 400` N/mm²
- ``failure_strain=0.15``: failure strain of the steel :math:`\varepsilon_\mathrm{u} = 15` %

>>> from m_n_kappa import IProfile, Steel
>>> i_profile = IProfile(top_edge=0.0, b_fo=200, t_fo=15, h_w=200-2*15, t_w=15, centroid_y=0.0)
>>> steel = Steel(f_y=355.0, f_u=400, failure_strain=0.15)
>>> cross_section = i_profile + steel


.. grid:: 1 2 2 2

   .. grid-item::

      .. figure:: ../../images/template_geometry_symmetric_steel_profile-light.svg
         :class: only-light
         :width: 400
      .. figure:: ../../images/template_geometry_symmetric_steel_profile-dark.svg
         :class: only-dark
         :width: 400

         Geometry: Symmetric I-profile

   .. grid-item::

      .. figure:: ../../images/material_steel_trilinear-light.svg
         :class: only-light
         :width: 250
      .. figure:: ../../images/material_steel_trilinear-dark.svg
         :class: only-dark
         :width: 250

         Material: Bi-linear stress-strain-relationship with hardening of steel

.. include:: cross_section_computation.rst
