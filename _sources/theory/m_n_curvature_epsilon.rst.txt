.. _theory.m_n_curvature_epsilon:

:math:`M`-:math:`N`-:math:`\kappa`-:math:`\varepsilon_\mathrm{\Delta}`-curve
****************************************************************************

.. _theory.m_n_curvature_epsilon.general:

General
=======

The :math:`M`-:math:`N`-:math:`\kappa`-:math:`\varepsilon_\mathrm{\Delta}`-curve of a cross-section is described by
the moment :math:`M`, the axial-force between the sub-cross-sections :math:`N`, the curvature :math:`\kappa`
and the strain-difference :math:`\varepsilon_\mathrm{\Delta}`.
It assumes the cross-section has two sub-cross-sections that move independently from each other.

The :math:`M`-:math:`N`-:math:`\kappa`-:math:`\varepsilon_\mathrm{\Delta}`-curve composes in general
of three types of points:

1. :math:`M`-:math:`N`: where :math:`\kappa = 0` and the rest is unequal zero
2. :math:`M`-:math:`\kappa`: where :math:`N = 0` and the rest is unequal zero
3. :math:`M`-:math:`N`-:math:`\kappa`: where all of the three parameters are unequal zero

Due to this definitions these points are computed independently from each other.
Their computation is described hereafter.


.. _theory.m_n_curvature_epsilon.m_n_curve:

:math:`M`-:math:`N`-curve
=========================

:math:`M`-:math:`N` points assume zero curvature and therefore an uniform axial-force on each of both
sub-cross-sections, but with reverse sign.

.. figure:: ../images/theory_m_n_kappa_m_n-dark.svg
   :class: only-dark
.. figure:: ../images/theory_m_n_kappa_m_n-light.svg
   :class: only-light

   computation of :math:`M`-:math:`N`-points

The strain-difference :math:`\varepsilon_\mathrm{\Delta}` is then computed by adding
the strain that occurs by the axial-force on each of the sub-cross-sections.
In case each sub-cross-section consists of a number of sub-sections an equilibrium must be found.

An axial-force :math:`N` is computed for each strain-point :math:`\varepsilon` of the materials denoted
to the given sub-(cross-)sections.
After the axial-force :math:`N` is computed for the first sub-cross-section
from the given strain :math:`\varepsilon` the same axial-force is applied to
the other sub-cross-section, but with reversed sign.

The moment is computed by the multiplying the computed axial-force of each sub-section with the
corresponding lever-arm.
The lever-arm is in each case the distance between the top of the cross-section and the
centroid of the axial-force on this sub-section.


.. _theory.m_n_curvature_epsilon.m_kappa_curve:

:math:`M`-:math:`\kappa`-curve
==============================

A :math:`M`-:math:`\kappa`-point assumes that no axial-force :math:`N` is transferred between the
sub-cross-sections.
Therefore, each sub-cross-section adds its individual resisting moment to the overall resisting moment.
No composite-effect is considered.

.. figure:: ../images/theory_m_n_kappa_m_kappa-dark.svg
   :class: only-dark
.. figure:: ../images/theory_m_n_kappa_m_kappa-light.svg
   :class: only-light

   computation of :math:`M`-:math:`\kappa`-points

To compute the full :math:`M`-:math:`\kappa`-curve first the :math:`M`-:math:`\kappa`-curves of the
sub-cross-sections are computed as described :ref:`here <theory.m_kappa>`.
Afterwards for each computed curvature :math:`\kappa` the moment :math:`M` of the other
sub-cross-section is computed.
Adding the corresponding moments of the sub-cross-sections results in the moment of this point.

The strain-difference :math:`\varepsilon_\mathrm{\Delta}` is computed by evaluation of the strain
of both sub-cross-sections at the same vertical position.


.. _theory.m_n_curvature_epsilon.m_n_kappa_curve:

:math:`M`-:math:`N`-:math:`\kappa`-curve
========================================

The :math:`M`-:math:`N`-curve and the :math:`M`-:math:`\kappa`-curve are edge-cases whereas the
:math:`M`-:math:`N`-:math:`\kappa`-curve describes most of the points.
All values (:math:`M`, :math:`N`, :math:`\kappa` and :math:`\varepsilon_\mathrm{\Delta}`
are unequal zero.

.. figure:: ../images/theory_m_n_kappa_m_n_kappa-dark.svg
   :class: only-dark
.. figure:: ../images/theory_m_n_kappa_m_n_kappa-light.svg
   :class: only-light

   computation of :math:`M`-:math:`N`-:math:`\kappa`-points

In this case for each axial-force :math:`N` computed for the :ref:`theory.m_n_curvature_epsilon.m_n_curve`
the corresponding material-point is used to compute first a curvature :math:`\kappa_\mathrm{fail}` leading to
a failure of the sub-cross-section considering also this axial-force :math:`N`.

Then, all material-points are collected that are include between :math:`\kappa_\mathrm{fail}` and
zero curvature also considering the axial-force.

This procedure is repeated for each material-point of both sub-cross-sections.
In each case the computed curvature :math:`\kappa` and the reversed axial-force :math:`N`
are applied to the other sub-cross-section.
The resulting moments are then summed up forming an individual
:math:`M`-:math:`N`-:math:`\kappa`-:math:`\varepsilon_\mathrm{\Delta}`-point.


.. _theory.m_n_curvature_epsilon.summary:

Summary
=======

The :ref:`theory.m_n_curvature_epsilon.m_n_curve`, :ref:`theory.m_n_curvature_epsilon.m_kappa_curve`,
:ref:`theory.m_n_curvature_epsilon.m_n_kappa_curve` form together the
:math:`M`-:math:`N`-:math:`\kappa`-:math:`\varepsilon_\mathrm{\Delta}`-curve.
This curve (or more precise 'surface') describes the relationship between moment :math:`M`,
axial-force :math:`N`, curvature :math:`\kappa` and strain-difference :math:`\varepsilon_\mathrm{\Delta}`
for the given cross-section.

This relationship allows to consider the behaviour of the cross-section under considering the effect
of slip, shear-connectors and axial-force in the sub-cross-sections.
