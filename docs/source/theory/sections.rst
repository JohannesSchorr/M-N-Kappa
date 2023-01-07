.. _theory.sections:

Sections and cross-sections
***************************

.. _theory.sections.intro:

Introduction
============
Concept and process of computing the axial-force and moment of the cross-section under a given distribution of strain
is described.

.. _theory.sections.sections:

Sections
========

.. _theory.sections.sections.general:

General
-------
Sections consist of:
  - :ref:`geometric instance <theory.geometries>`
  - :ref:`material instance <theory.materials>`

The characteristics of geometry and material are combined to computed the :ref:`axial force <theory.sections.sections.axial_force>`,
the :ref:`lever arm <theory.sections.sections.lever_arm>` and the :ref:`moment <theory.sections.sections.moment>`
corresponding with an applied :ref:`theory.general.curvature` or constant strain.

.. _theory.sections.sections.procedure:

Procedure
---------
To compute axial force, lever arm and moment of a section first the following steps are conducted,
assuming that curvature :math:`\kappa` and neutral-axis :math:`z_\mathrm{n}` are known.

1. mapping strain-distribution onto the section considering curvature :math:`\kappa` and :math:`z_\mathrm{n}`
2. split section at material curve points into sub-sections
3. map stresses on top- and bottom-edge of the sub-section

As the procedure above ensures that no material points - and therefore no change in stress-strain slope - are
within each sub-section a linear relationship between vertical position :math:`z` and stress :math:`\sigma` is present.
This allows to determine a :ref:`theory.sections.sections.stress_distribution` of each sub-section.

.. _theory.sections.sections.stress_distribution:

Linear stress-distribution over height
--------------------------------------

The linear stress-distribution over the height of a sub-section is computed by formula :math:numref:`eq:theory_section_stress`. 

.. math::
   :label: eq:theory_section_stress

   \sigma(z) = m_\mathrm{\sigma} \cdot \varepsilon + c_\mathrm{\sigma}

where the slope :math:`m_\mathrm{\sigma}` and the interception :math:`c_\mathrm{\sigma}` is computed as follows
assuming two stress-vertical-position points (:math:`\sigma_\mathrm{top}` | :math:`z_\mathrm{top}` )
and (:math:`\sigma_\mathrm{bottom}` | :math:`z_\mathrm{bottom}` ).

.. math::
   :label: eq:theory_section_stress_slope

   m_\mathrm{\sigma} = \frac{\sigma_\mathrm{bottom} - \sigma_\mathrm{top}}{z_\mathrm{bottom} - z_\mathrm{top}}

.. math::
   :label: eq:theory_section_stress_interception

   c_\mathrm{\sigma} = \sigma_\mathrm{top} - m_\mathrm{\sigma} \cdot z_\mathrm{top}

Linear distributions allow easy integration, giving the opportunity to determine :ref:`theory.sections.sections.axial_force`,
:ref:`theory.sections.sections.lever_arm` and :ref:`theory.sections.sections.moment` in conclusion.

.. _theory.sections.sections.axial_force:

Axial force
-----------

The axial force :math:`N_i` of each rectangular sub-section with index :math:`i` is computed according to formula :math:numref:`eq:theory_section_axial_force_rectangle`.
It assumes that the stress distribution over its height is distributed linearly.

.. math::
   :label: eq:theory_section_axial_force_rectangle

   N_i = \int_{z_\mathrm{top}}^{z_\mathrm{bottom}} \sigma(z) \cdot b(z) dz
   = \int_{z_\mathrm{top}}^{z_\mathrm{bottom}} (m_\mathrm{\sigma} \cdot \varepsilon + c_\mathrm{\sigma}) \cdot (m_\mathrm{b} \cdot z + c_\mathrm{b}) dx

with :math:`\sigma(z)` given in formula :math:numref:`eq:theory_section_stress` and :math:`b(z)`
by formula :math:numref:`eq:rectangle_width` in :ref:`theory.geometries.rectangle_and_rectangle`.
The axial-force :math:`N_i` of the sub-section is achieved by integration between the vertical position of the top-edge
:math:`z_\mathrm{top}` and the vertical position of the bottom-edge :math:`z_\mathrm{bottom}`.

Due to the very limited size of the :ref:`theory.geometries.circle` its axial force :math:`N_i` is computed according
Formula :math:numref:`eq:theory_section_axial_force_circle`.

.. math::
   :label: eq:theory_section_axial_force_circle

   N_i = A_\mathrm{circle} \cdot \sigma(z_\mathrm{circle-centroid})

where :math:`A_\mathrm{circle}` is the cross-sectional area of the circle (see formula :math:numref:`eq:circle_area` in
:ref:`theory.geometries.circle`) and the stress is obtained at the vertical position of the circle's centroid
:math:`z_\mathrm{circle-centroid}`.

Similar procedure is conducted for the :ref:`theory.sections.sections.lever_arm` and the :ref:`theory.sections.sections.moment`.

.. _theory.sections.sections.lever_arm:

Lever arm
---------

The distance between the origin and the vertical point of the axial force is the lever arm of a sub-section :math:`r_i` under a given
stress-distribution :math:`\sigma(z)`.

.. math::
   :label: eq:theory_section_lever_arm_rectangle

   r_i = \frac{1}{N_i} \int_{z_\mathrm{top}}^{z_\mathrm{bottom}} \sigma(z) \cdot b(z) \cdot z~dz

where :math:`N_i` is the axial force of the sub-section (see Formula :math:numref:`eq:theory_section_axial_force_rectangle`),
:math:`\sigma(z)` (see Formula :math:numref:`eq:theory_section_stress`) and :math:`b(z)` the width of the geometry at the vertical
position :math:`z` (see formula :math:numref:`eq:rectangle_width` in :ref:`theory.geometries.rectangle_and_rectangle`).

For circles the lever arm applies to the geometrical centroid in vertical direction, that is an input-parameter.

.. math::
   :label: eq:theory_section_lever_arm_circle

   r_i = z_\mathrm{centroid}

The lever arm is used to compute the moment the sub-section contributes to the overall moment of the cross-section under
a given stress-distribution.

.. _theory.sections.sections.moment:

Moment
------

The moment of each sub-section :math:`M_i` is computed taking the :ref:`theory.sections.sections.axial_force` and
the :ref:`theory.sections.sections.lever_arm` into account as given in formula :math:numref:`eq:theory_section_moment`.

.. math::
   :label: eq:theory_section_moment

   M_i = N_i \cdot r_i

Implementation
--------------

These functionalities are part of :py:class:`~m_n_kappa.section.ComputationSection`,
:py:class:`~m_n_kappa.section.ComputationSectionCurvature` and :py:class:`~m_n_kappa.section.ComputationSectionStrain`.

.. _theory.sections.cross_section:

Cross-section
=============

A cross-section consist of a number of sections, that result during computation under a given strain-distribution
to a number of sub-sections (index :math:`i`).
Total axial force :math:`N_\mathrm{cs}` and moment :math:`M_\mathrm{cs}` under a given cross-section are therefore
computed by summing axial forces :math:`N_i` and moment :math:`M_i` of the given sub-section up as shown in formulas
:math:numref:`eq:theory_crosssection_axial_force` and :math:numref:`eq:theory_crosssection_moment`.

.. math::
   :label: eq:theory_crosssection_axial_force

   N_\mathrm{cs} = \sum_i N_i

.. math::
   :label: eq:theory_crosssection_moment

   M_\mathrm{cs} = \sum_i M_i

Summary
=======
For computation of a cross-section's axial force :math:`N_\mathrm{cs}` and moment :math:`M_\mathrm{cs}` each section is
split into appropriate sub-sections considering the stress-strain-relationship of its material.
The split is conducted in a way that each sub-section has a linear stress-distribution allowing to normalize the process
of computing axial force, lever-arm and moment of each sub-section and in turn of the overall cross-section.

The computation of a cross-section under a given strain-distribution is required for :ref:`theory.strain_based_design`.