.. _theory.general:

General
*******

.. _theory.general.intro:

Introduction
============

Here basic formulas are listed to compute the :ref:`theory.general.curvature`,
:ref:`Strain at a given vertical position <theory.general.strain>`,
:ref:`Position of a given strain <theory.general.position>` and the :ref:`theory.general.neutral_axis`.
The given formulas define the basis for this piece of software.

.. _theory.general.curvature:

Curvature
=========

Formula :math:numref:`eq:theory.general.curvature_neutral_axis` computes the curvature :math:`\kappa` given a strain
:math:`\varepsilon` at a position :math:`z` and the neutral axis :math:`z_\mathrm{m}`.

.. math::
   :label: eq:theory.general.curvature_neutral_axis

   \kappa = \frac{\varepsilon}{z - z_\mathrm{m}}

Given two points strain-position points :math:`(z_1 | \varepsilon_\mathrm{1}), (z_2 | \varepsilon_\mathrm{2})` the
curvature is computed as given in formula :math:numref:`eq:theory.general.curvature_two_points`.

.. math::
   :label: eq:theory.general.curvature_two_points

   \kappa = \frac{\varepsilon_\mathrm{1} - \varepsilon_\mathrm{2}}{z_1 - z_2}

.. _theory.general.strain:

Strain
======

The strain :math:`\varepsilon` a given position :math:`z` is computed by formula :math:numref:`eq:theory.general.strain`,
that is a rearrangement of formula :math:numref:`eq:theory.general.curvature_neutral_axis`.

.. math::
   :label: eq:theory.general.strain

   \varepsilon = \kappa \cdot (z - z_\mathrm{m})

.. _theory.general.position:

Position
========

The vertical position :math:`z` of a given strain :math:`\varepsilon` and the vertical position of the neutral axis
:math:`z_\mathrm{m}` is computed using formula :math:numref:`eq:theory.general.position_strain`.

.. math::
   :label: eq:theory.general.position_strain

   z = \frac{\varepsilon}{\kappa} + z_\mathrm{m}

.. _theory.general.neutral_axis:

Neutral axis
============

The neutral axis :math:`z_\mathrm{m}` under a given curvature :math:`\kappa` and a strain :math:`\varepsilon` at
a position :math:`z` is computed by formula :math:numref:`eq:theory.general.neutral_axis`.

.. math::
   :label: eq:theory.general.neutral_axis

   z_\mathrm{m} = z - \frac{\varepsilon}{\kappa}