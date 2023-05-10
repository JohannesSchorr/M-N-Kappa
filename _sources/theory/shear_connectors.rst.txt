.. _theory.shear_connectors:

Shear-Connectors
****************

.. _theory.shear_connectors.general:

General
=======

Shear-connectors are considered by their load-slip-relationship as well as their position along
the beam.

The load-slip relationship is crucial as it assigns a load to a given slip.
The position of the shear-connector along the beam matters as in most cases
the amount of slip :math:`s` depends on the position of the shear-connector within the beam.

.. _theory.shear_connectors.headed_stud:

Headed Studs
============

Headed studs are standardized by Eurocode 4 [1]_ and implemented in :mod:`m_n_kappa`.
For implementation in :mod:`m_n_kappa` a bi-linear load-slip relationship of the headed studs
is assumed.

.. figure:: ../images/theory_headed_stud_load_slip_relationship-dark.svg
   :class: only-dark
   :width: 300
.. figure:: ../images/theory_headed_stud_load_slip_relationship-light.svg
   :class: only-light
   :width: 300

   Assumed load-slip-relationsship of headed stud in :mod:`m_n_kappa`

Where the transition between the linear and the plastic part is assumed
at :math:`s = 0.5` mm and the maximum slip at :math:`s_\mathrm{max} = 6.0` mm.

The maximum resistance of the headed stud is assumed to be the minimum value of the
resistance at steel-failure and at concrete failure.

.. math::
   :label: eq:shear_connectors.headed_studs.resistance

   P_\mathrm{R} = \min\{P_\mathrm{m,c}; P_\mathrm{m,s}\}

The values for steel- and concrete-failure are assumed to be the mean-values according to
Roik et al. [2]_.

.. math::

   P_\mathrm{m,c} &= 0.374 \cdot d^{2} \cdot \alpha \sqrt{f_\mathrm{c} \cdot E_\mathrm{cm}}

   P_\mathrm{m,s} &= f_\mathrm{u} \cdot \pi \cdot \frac{d^{2}}{4}

where :math:`d` is the diameter of the shank of the headed stud.
:math:`f_\mathrm{c}` is the concrete cylinder compressive strength and :math:`E_\mathrm{cm}`
is the mean secant-modulus of the concrete.
:math:`f_\mathrm{u}` is the tensile strength of the material of the shank of the headed stud.
The factor :math:`\alpha` depends on the ratio :math:`h_\mathrm{sc} / d` as follows:

.. math::

   \alpha = \begin{cases}
               0.2 \cdot \left( \frac{h_\mathrm{sc}}{d} + 1 \right) & \text{ if } 3 \leq \frac{h_\mathrm{sc}}{d} < 4 \\
               1 & \text{ if } \frac{h_\mathrm{sc}}{d} \geq 4
            \end{cases}

.. _theory.shear_connectors.headed_stud_transverse_profile:

Headed studs with profiled steel sheeting transverse to the supporting beam
===========================================================================

Profiled steel sheeting positioned transverse to the supporting beam reduce the shear-load resistance
of the headed studs.
Therefore, the shear resistance :math:`P_\mathrm{R}` computed in Formula
:math:numref:`shear_connectors.headed_studs.resistance` is reduced by factor
:math:`k_\mathrm{t}` according to EN 1994-1-1 [1]_.

.. math::

   k_\mathrm{t} = \frac{0.7}{n_\mathrm{r}} \cdot \frac{b_\mathrm{o}}{h_\mathrm{p}} \left(
   \frac{b_\mathrm{sc}}{h_\mathrm{p}} - 1\right) \leq 1

where :math:`n_\mathrm{r}` is the number of headed studs in a row, :math:`b_\mathrm{o}`
is the decisive concrete with in the trough of the profiled steel sheeting,
:math:`h_\mathrm{p}` is the height of the profiled steel sheeting and
:math:`b_\mathrm{sc}` is the height of the headed stud.

As indicated above the shear resistance considering the effect of the profiled steel sheeting
transverse to the supporting beam is then computed as follows.

.. math::

   P_\mathrm{R,t} = k_\mathrm{t} \cdot P_\mathrm{R}


References
==========

.. [1] EN 1994-1-1: Eurocode 4: Design of composite steel and concrete structures - Part 1-1:
       General rules and rules for buildings, European Committee of Standardization (CEN), 2004

.. [2] Roik, K.-H.; Hanswille, G. ; Cunze, 0. (1988) Hintergrundbericht zu Eurocode 4 - Abschnitt 6.3.2:
       Bolzendübel. Harmonisierung der europäischen Baubestimmungen – Minister für Raumordnung, Bauwesen und Städtebau
