.. _theory_strain_based_design:

Strain based design
*******************

.. todo::

   theory - strain based design
   - draw figure(s)

Introduction
============

:ref:`theory_sections` indicates how axial force and moment are computed for a :ref:`theory_sections_sections` and
:ref:`theory_sections_cross_sections` under a given strain-distribution.


.. _theory_strain_based_design_aim:

Aim
===

The aim is to find a distribution of strains over a beam cross-section leading to an equilibrium of the horizontal forces
:math:`H` (see Formula :math:numref:`eq:theory_strain_based_design_equilibrium`).
In consequence the summarized axial forces of all sub-sections :math:`N_i` must become zero.

.. math::
   :label: eq:theory_strain_based_design_equilibrium

   H = \sum N_i = 0

The strain-distribution leading to equilibrium of the axial-forces is found by iteration.


.. _theory_strain_based_design_boundary_values:

Boundary values
===============

.. figure:: ../images/max_curvature.png

   Computation of maximum possible curvature

Before the iteration is started boundary-values are determined.
In case the iteration aims to determine the neutral-axis :math:`z_\mathrm{n}`
and the curvature :math:`\kappa` this means a maximum curvature :math:`\kappa_\mathrm{max}`
and a minimum curvature  :math:`\kappa_\mathrm{min}`.

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


.. _theory_strain_based_design_equilibrium:

Finding equilibrium of axial forces
===================================

To find the equilibrium of axial forces a Newton-algorithm is used
as given in formula :math:numref:`eq:theory_strain_based_design_newton`.
As variable the neutral axis :math:`z_\mathrm{n}` was used.

.. math::
   :label: eq:theory_strain_based_design_newton

   x_\mathrm{n+1} = x_\mathrm{n} - \frac{f(x_\mathrm{n})}{f'(x_\mathrm{n})}

where :math:`x_\mathrm{n}` is the original variable value and
:math:`x_\mathrm{n+1}` the new iteration value, i.e. the new value
of the neutral axis :math:`z_\mathrm{n}`.

In case the Newton-Algorithm does not find a solution a Bisection-algorithm
is implemented as fallback.

.. math::
   :label: eq:theory_strain_based_design_bisection

   x_\mathrm{n+1} = \frac{x_{f(x)>0} + x_{f(x)<0}}{2}

where :math:`x_\mathrm{n+1}` is the new iteration value,
:math:`x_{f(x)>0}` is the variable-value with the smallest resulting
value :math:`f(x)>0` greater zero and :math:`x_{f(x)<0}` is the
variable-value with the smallest absolut resulting value smaller zero.
:math:`f(x)` may therefore be given as axial force depending on
neutral axis :math:`N(z_\mathrm{n})`.

The fallback-mechanism also strikes in case the Newton-Algorithm
computes the same value twice.

The :ref:`theory_strain_based_design_boundary_values` are used on the
one hand as starting values and on the other hand to make sure that
strains stay within the minimal and maximal strains of the
material models.