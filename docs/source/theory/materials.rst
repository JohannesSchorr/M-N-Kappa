.. _theory.materials:

Materials
*********

.. _theory.m_kappa.basis:

Basic functionality, concept and integration
============================================

In steel-concrete composite structures :ref:`theory.materials.concrete`, :ref:`theory.materials.steel` and
:ref:`theory.materials.reinforcement` are relevant materials.
For these materials sophisticated material models are available to describe their behaviour under loading
(see for example formula :math:numref:`eq:theory.materials.concrete.compression.nonlinear`).

For integration into the program these -- in part discrete -- formulas need to be abstracted to multi-linear
stress-strain relationships.

.. _theory.materials.concrete:

Concrete
========

.. _theory.materials.concrete.general:

General
-------
Concrete is in general characterised by it class.
The classes describe the characteristic concrete compressive strength :math:`f_\mathrm{ck}`.
Following :cite:t:`EN1992-1-1` most of the mechanical characteristic are derived from :math:`f_\mathrm{ck}`.

The mean concrete compressive strength :math:`f_\mathrm{cm}` according to :cite:t:`EN1992-1-1` is given in formula
:math:numref:`eq:theory.materials_f_cm`.

.. math::
   :label: eq:theory.materials_f_cm

   f_\mathrm{cm} = f_\mathrm{ck} + 8 \text{ in N/mm²}

The modulus of elasticity :math:`E_\mathrm{cm}` by :cite:t:`EN1992-1-1` is given in formula
:math:numref:`eq:theory.materials_E_cm`.

.. math::
   :label: eq:theory.materials_E_cm

   E_\mathrm{cm} = 22000 \cdot \left(\frac{f_\mathrm{cm}}{10} \right)^{0.3}

.. _theory.materials.concrete.compression:

Compression
-----------

.. _theory.materials.concrete.intro:

Introduction
^^^^^^^^^^^^
:cite:t:`EN1992-1-1` provides three material models to define the stress-strain-relationship of concrete in
compression.
These are :ref:`theory.materials.concrete.compression.nonlinear`, :ref:`theory.materials.concrete.compression.parabola`
and :ref:`theory.materials.concrete.compression.bi_linear`.
Every of these three stress-strain-relationships of the concrete according to :cite:t:`EN1992-1-1` is implemented
in :py:class:`~m_n_kappa.Concrete` and may be chosen argument ``compression_stress_strain_type``.

.. _theory.materials.concrete.compression.nonlinear:

Stress-strain-relationship for non-linear determination of stress-resultants and deformations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The stresses according to the non-linear determination of stress-resultants and deformations are computed by
formula :math:numref:`eq:theory.materials.concrete.compression.nonlinear` in the range
:math:`0 < | \varepsilon_\mathrm{c1} | < | \varepsilon_\mathrm{cu1} |`.

.. math::
   :label: eq:theory.materials.concrete.compression.nonlinear

   \sigma_\mathrm{c} = \frac{k \cdot \eta - \eta^{2}}{1 + (k - 2) \cdot \eta} \cdot f_\mathrm{cm}

Where:

.. math::

   \eta & = \varepsilon_\mathrm{c} / \varepsilon_\mathrm{c1}

   \varepsilon_\mathrm{c1} & = 0.7 \cdot f_\mathrm{cm}^{0.31} \leq 2.8

   k & = 1.05 \cdot E_\mathrm{cm} \cdot | \varepsilon_\mathrm{c1} | / f_\mathrm{cm}

   \varepsilon_\mathrm{cu1} & = 2.8 + 27 \cdot \left[\frac{98-f_\mathrm{cm}}{100}\right]^{4}

:math:`\varepsilon_\mathrm{c1}` is the strain at maximum stress, whereas :math:`\varepsilon_\mathrm{cu1}` is the
strain at failure.

The above given nonlinear stress-strain-relationship is implemented by passing
``compression_stress_strain_type='Nonlinear'`` to :py:class:`~m_n_kappa.Concrete`.
Formula :math:numref:`eq:theory.materials.concrete.compression.nonlinear` is approximated by a multi-linear curve in
:py:class:`~m_n_kappa.Concrete`.

.. _theory.materials.concrete.compression.parabola:

Stress-strain-relationship for section-design
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. math::
   :label: eq:theory.materials.concrete.compression.parabola

   \sigma_\mathrm{c} & = f_\mathrm{ck} \cdot \left[1 - \left(1 - \frac{\varepsilon_\mathrm{c}}{\varepsilon_\mathrm{c2}} \right)^{n} \right] & & \text{ for } 0 \leq \varepsilon_\mathrm{c} \leq \varepsilon_\mathrm{c2}

   \sigma_\mathrm{c} & = f_\mathrm{ck} & & \text{ for } \varepsilon_\mathrm{c2} \leq \varepsilon_\mathrm{c} \leq \varepsilon_\mathrm{cu2}

where

.. math::

   \varepsilon_\mathrm{c2} & = 2.0 + 0.085 \cdot (f_\mathrm{ck} - 50)^{0.53}

   \varepsilon_\mathrm{cu2} & = 2.6 + 35 \cdot \left[\frac{90 - f_\mathrm{ck}}{100}\right]^{4}

   n & = 1.4 + 23.4 \cdot \left[\frac{90 - f_\mathrm{ck}}{100}\right]^{4}

:math:`\varepsilon_\mathrm{c2}` is the strain at maximum stress and :math:`\varepsilon_\mathrm{cu2}` is the strain at failure.

This stress-strain-relationship is applied by passing ``compression_stress_strain_type='Parabola'`` to :py:class:`~m_n_kappa.Concrete`.


.. _theory.materials.concrete.compression.bi_linear:

Stress-strain-relationship for section-design
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. math::
   :label: eq:theory.materials.concrete.compression.bi_linear

   \sigma_\mathrm{c} & = f_\mathrm{ck} \cdot \frac{\varepsilon_\mathrm{c}}{\varepsilon_\mathrm{c2}} & & \text{ for } 0 \leq \varepsilon_\mathrm{c} \leq \varepsilon_\mathrm{c3}

   \sigma_\mathrm{c} & = f_\mathrm{ck} & & \text{ for } \varepsilon_\mathrm{c3} \leq \varepsilon_\mathrm{c} \leq \varepsilon_\mathrm{cu3}

where

.. math::

   \varepsilon_\mathrm{c3} & = 1.75 + 0.55 \cdot (\frac{f_\mathrm{ck} - 50}{40})

   \varepsilon_\mathrm{cu3} & = \varepsilon_\mathrm{cu2}

The bi-linear stress-strain-relationship is applied by passing ``compression_stress_strain_type='Bilinear'`` to :py:class:`~m_n_kappa.Concrete`.

.. _theory.materials.concrete.tension:

Tension
-------

For a realistic load-carrying behaviour of the concrete the behaviour under tension is crucial.

If the tensile strength of the concrete :math:`f_\mathrm{ctm}` is not given, it may be computed by formula
:math:numref:`eq:theory.materials.concrete_f_ctm`.

.. math::
   :label: eq:theory.materials.concrete_f_ctm

   f_\mathrm{ctm} & = 0.3 \cdot f_\mathrm{ck}^{2/3} & & \leq \text{ C50/60}

   f_\mathrm{ctm} & = 2.12 \cdot \ln\left[1 + \frac{f_\mathrm{cm}}{10}\right] & & > \text{ C50/60}

The strain when :math:`f_\mathrm{ctm}` is reached may than be computed by formula :math:numref:`eq:theory.materials.concrete_epsilon_ct`.

.. math::
   :label: eq:theory.materials.concrete_epsilon_ct

   \varepsilon_\mathrm{ct} = \frac{f_\mathrm{ctm}}{E_\mathrm{cm}}

where :math:`E_\mathrm{cm}` is the modulus of elasticity according to formula :math:numref:`eq:theory.materials_E_cm`.

As soon as the strain reaches :math:`\varepsilon_\mathrm{ctm}` the concrete starts to break.
Different post-failure behaviours are possible in :py:class:`~m_n_kappa.Concrete` if :math:`\varepsilon_\mathrm{c} > \varepsilon_\mathrm{ct}`.

1. The resisting stresses drop immediately to :math:`\sigma_\mathrm{c} = 0`.
2. The crack-opening behaviour follows the recommendations by :cite:t:`FIB2010`.

:cite:t:`FIB2010` defines the crack-opening behaviour as described in formula :math:numref:`eq:theory.materials.concrete_crack_opening`.

.. math::
   :label: eq:theory.materials.concrete_tensile

   \sigma_\mathrm{ct} & = f_\mathrm{ctm} \cdot \left(1.0 - 0.8 \cdot \frac{w}{w_1}\right) & & \text{ for } w \leq w_1

   \sigma_\mathrm{ct} & = f_\mathrm{ctm} \cdot \left(0.25 - 0.05 \cdot \frac{w}{w_1}\right) & & \text{ for } w_1 < w \leq w_\mathrm{c}

where :math:`w` is the crack opening in mm and :math:`w_1` and :math:`w_\mathrm{c}` are defined in :math:numref:`theory.materials.concrete_crack_opening_values`.

.. math::
   :label: eq:theory.materials.concrete_crack_opening

   w_1 & = \frac{G_\mathrm{f}}{f_\mathrm{ctm}} & & \text{ if } \sigma_\mathrm{ct} = 0.2 \cdot f_\mathrm{ctm}

   w_\mathrm{c} & = 5 \cdot \frac{G_\mathrm{f}}{f_\mathrm{ctm}} & & \text{ if } \sigma_\mathrm{ct} = 0

The fracture energy :math:`G_\mathrm{F}` is computed by :math:numref:`eq:theory.materials.concrete_fracture_energy`.

.. math::
   :label: eq:theory.materials.concrete_fracture_energy

   G_\mathrm{F} = 73 \cdot f_\mathrm{cm}^{0.18}

where :math:`f_\mathrm{cm}` is the mean concrete compressive strength in N/mm².

The crack opening is considered by passing ``tension_stress_strain_type='consider opening behaviour'`` to py:class:`~m_n_kappa.Concrete`.


.. _theory.materials.steel:

Steel
=====

The stress-strain-relationship of structural steel is assumed to be point-symmetric around the origin.
It may may be determined by one of following three ways:

1. Linear-elastic behaviour :math:`\sigma_\mathrm{a} = \varepsilon_\mathrm{a} \cdot E_\mathrm{a}`.

   Achieved if ``f_u = None`` and ``epsilon_u = None`` are passed to :py:class:`~m_n_kappa.Steel`.

2. Bi-linear behaviour where :math:`f_\mathrm{y} = f_\mathrm{u}`

   .. math::
      :label: eq:theory.materials.steel_bilinear

      \sigma_\mathrm{a} & = \varepsilon_\mathrm{a} \cdot E_\mathrm{a} & & \text{ if } 0 < | \varepsilon_\mathrm{a} | \leq | \varepsilon_\mathrm{y} |

      \sigma_\mathrm{a} & = f_\mathrm{y} & & \text{ if } | \frac{f_\mathrm{y}}{E_\mathrm{a}} | < | \varepsilon_\mathrm{a} | < | \varepsilon_\mathrm{u} |

   where :math:`f_\mathrm{y}` is the yield strength of the steel and :math:`\varepsilon_\mathrm{y} = \frac{f_\mathrm{y}}{E_\mathrm{a}}`
   is the strain at yielding and :math:`\varepsilon_\mathrm{u}` is the strain at failure.

   Achieved if and ``epsilon_u != None`` is passed to :py:class:`~m_n_kappa.Steel`.

3. Bi-linear behaviour where :math:`f_\mathrm{y} < f_\mathrm{u}`

   .. math::
      :label: eq:theory.materials.steel_bilinear_2

      \sigma_\mathrm{a} & = \varepsilon_\mathrm{a} \cdot E_\mathrm{a} & & \text{ if } 0 < | \varepsilon_\mathrm{a} | \leq | \varepsilon_\mathrm{y} |

      \sigma_\mathrm{a} & = f_\mathrm{y} + (f_\mathrm{u} - f_\mathrm{y}) \cdot \frac{\varepsilon_\mathrm{a} - \varepsilon_\mathrm{y}}{\varepsilon_\mathrm{u} - \varepsilon_\mathrm{y}} & & \text{ if } | \varepsilon_\mathrm{y} | < | \varepsilon_\mathrm{a} | < | \varepsilon_\mathrm{u} |

   where :math:`f_\mathrm{y}` is the yield strength of the steel, :math:`\varepsilon_\mathrm{y} = \frac{f_\mathrm{y}}{E_\mathrm{a}}`
   is the strain at yielding, :math:`\varepsilon_\mathrm{u}` is the strain at failure and
   :math:`f_\mathrm{u}` is the stress at failure.

The above given three ways are implemented in :py:class:`~m_n_kappa.Steel`.

.. _theory.materials.reinforcement:

Reinforcement
=============

The characteristics of the stress-strain-relationship of reinforcement steel is similar to those of :ref:`theory.materials.steel`.
Solely the input-parameters change in :py:class:`~m_n_kappa.Reinforcement` as follows:

- Yield strength :math:`f_\mathrm{s}`: ``f_s`` (eqivalent to ``f_y`` in :py:class:`~m_n_kappa.Steel`)
- Failure strain :math:`\varepsilon_\mathrm{su}`: ``epsilon_su``  (eqivalent to ``epsilon_u`` in :py:class:`~m_n_kappa.Steel`)
- Failure strength :math:`f_\mathrm{su}`: ``f_su`` (eqivalent to ``f_u`` in :py:class:`~m_n_kappa.Steel`)

.. rubric:: References

.. bibliography::