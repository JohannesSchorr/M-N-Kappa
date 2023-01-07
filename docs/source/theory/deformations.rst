.. _theory.deformations:

Deformations
************

.. todo::

   Documentation of computation of deformations

.. _theory.deformations.intro:

Introduction
============

In the following the computation of deformations from curvatures are described in :ref:`general <theory_deformations_general>`.
Further detailed description is given for deformation computation of composite structures acting as a solid section and under consideration of the load-slip-behaviour of the shear connectors.

.. _theory.deformations.general:

General
=======

The deformation of an infinite small beam-element is computed as given by formula :math:numref:`eq:theory_deformation_basis`
taking into account the moment acting at the element :math:`M(x)` as well as the corresponding .

.. math::
   :label: eq:theory_deformation_basis

   w(x) = - \int\int \frac{M(x)}{E \cdot I_\mathrm{y}}dx


Using the principle of virtual forces formula :math:numref:`eq:theory_deformation_basis` changes to formula :math:numref:`eq:theory_deformation_povf`.

.. math::
   :label: eq:theory_deformation_povf

   w(x) = \int \frac{M(x) \cdot \overline{M}(x)}{E \cdot I_\mathrm{y}}dx

Where term in formula :math:numref:`eq:theory_deformation_curvature` applies to the curvature :math:`\kappa` at the given position.

.. math::
   :label: eq:theory_deformation_curvature

   \frac{M(x)}{E \cdot I} = \kappa(x)
