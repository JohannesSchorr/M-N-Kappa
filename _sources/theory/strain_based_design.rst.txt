.. _theory.strain_based_design:

Strain based design
*******************

.. _theory.strain_based_design.intro: 

Introduction
============

:ref:`theory.sections` indicates how axial force and moment are
computed for a :ref:`theory.sections.sections` and
:ref:`theory.sections.cross_section` under a given strain-distribution.


.. _theory.strain_based_design.aim:

Aim
===

The aim is to find a distribution of strains over a beam cross-section
leading to an equilibrium of the horizontal forces :math:`H` (see Formula
:math:numref:`eq:theory.strain_based_design.equilibrium`).
In consequence the summarized axial forces of all sub-sections :math:`N_i`
must become zero.
This may also consider an applied axial-force :math:`N_\mathrm{applied}`.

.. math::
   :label: eq:theory.strain_based_design.equilibrium

   H = \sum N_i - N_\mathrm{applied} = 0

The strain-distribution leading to equilibrium of the axial-forces is found
by :ref:`iteration <theory.strain_based_design.equilibrium>`.


.. _theory.strain_based_design.boundary_values:

Boundary values
===============

.. _theory.strain_based_design.boundary_values.curvature:

Curvature
---------

.. figure:: ../images/strain_based_design_max_curvature-light.svg
   :class: only-light
.. figure:: ../images/strain_based_design_max_curvature-dark.svg
   :class: only-dark

   Computation of maximum possible curvature

Before the iteration is started boundary-values are determined.
In case the iteration aims to determine the neutral-axis
:math:`z_\mathrm{n}` and the curvature :math:`\kappa` this means
a maximum curvature :math:`\kappa_\mathrm{max}` and a minimum
curvature  :math:`\kappa_\mathrm{min}`.

For the maximum curvature :math:`\kappa_\mathrm{max}` (positive or negative)
first the maximum and minimum strains at bottom- and top-edge of each
section are determined.
By computing the curvature from these (position | strain)-values with the
input (position | strain)-value the maximum positive or the maximum negative
curvature may be determined by taking the minimum positive or
the maximum negative curvature.

The minimum curvature is defined in general as zero curvature.
In case this zero curvature leads to a strain in the several sections
that is above the maximum or below the minium strain then the
minimum curvature is adapted appropriately.

.. _theory.strain_based_design.boundary_values.neutral_axis:

Position of neutral axis
------------------------

Nevertheless if the curvature :math:`\kappa` is given, a prevention from
exceeding maximum positive and negative strains is needed.
This is the case if the overall cross-section consists of two subsidiary
cross-sections, i.e. concrete-slab and steel-girder, and one cross-
section has already been computed and therefore a curvature is available.

For this case another boundary function is implemented that considers the
maximum and minimum positive and negative strains.
Taking into account a given **positive** curvature the boundary neutral axes are:

- the lower position of the neutral axis from the curvature and maximum
  **positive** strains
- the higher position of the neutral from the curvature and the maximum
  **negative** strains

.. figure:: ../images/theory_boundaries_neutral_axis-light.svg
   :class: only-light
.. figure:: ../images/theory_boundaries_neutral_axis-dark.svg
   :class: only-dark

   Boundary values for the neutral axis :math:`z_\mathrm{m}` under positive
   curvature

In case the given curvature is negative it is vice versa and the boundary neutral
axes are:

- the lower position of the neutral axis from the curvature and maximum
  **negative** strains
- the higher position of the neutral from the curvature and the maximum
  **positive** strains

The resulting neutral axis must lie between these computed boundary neutral
axes.
Otherwise, no equilibrium of forces may be found.

.. _theory.strain_based_design.equilibrium:

Finding equilibrium of axial forces
===================================

To find the equilibrium of axial forces a Newton-algorithm is used
as given in formula :math:numref:`eq:theory.strain_based_design_newton`.
The neutral axis :math:`z_\mathrm{n}` is used as variable :math:`x`.

.. math::
   :label: eq:theory.strain_based_design_newton

   x_\mathrm{n+1} = x_\mathrm{n} - \frac{f(x_\mathrm{n})}{f'(x_\mathrm{n})}

where :math:`x_\mathrm{n}` is the original variable value and
:math:`x_\mathrm{n+1}` the new iteration value, i.e. the new value
of the neutral axis :math:`z_\mathrm{n}`.

In case the Newton-Algorithm does not find a solution a Bisection-algorithm
is implemented as fallback.

.. math::
   :label: eq:theory.strain_based_design_bisection

   x_\mathrm{n+1} = \frac{x_{f(x)>0} + x_{f(x)<0}}{2}

where :math:`x_\mathrm{n+1}` is the new iteration value,
:math:`x_{f(x)>0}` is the variable-value with the smallest resulting
value :math:`f(x)>0` greater zero and :math:`x_{f(x)<0}` is the
variable-value with the smallest absolut resulting value smaller zero.
:math:`f(x)` may therefore be given as axial force depending on
neutral axis :math:`N(z_\mathrm{n})`.

The fallback-mechanism also strikes in case the Newton-Algorithm
computes the same value twice.

The :ref:`theory.strain_based_design.boundary_values` are used on the
one hand as starting values and on the other hand to make sure that
strains stay within the minimal and maximal strains of the
material models.