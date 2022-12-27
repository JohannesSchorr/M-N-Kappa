.. _users_material:

Materials
*********

Introduction
============

.. _users_material_steel:
Structural Steel
================

:py:class:`m_n_kappa.Steel`

.. _users_material_reinforcement:
Reinforcement
=============

:py:class:`m_n_kappa.Reinforcement`

.. _users_material_concrete:
Concrete
========

:py:class:`m_n_kappa.Concrete`

.. _users_material_base:
Base class and adding new materials
===================================

Base class
----------
All material-models needs inheritance from :py:class:`~m_n_kappa.material.Material` to achieve basic functionality.

:py:class:`m_n_kappa.material.Material`

Stress-strain-points in the stress-strain-relationships need to be defined by :py:class:`m_n_kappa.material.StressStrain`.

:py:class:`m_n_kappa.material.StressStrain`

Adding new materials
--------------------

A new material must inherit from :py:class:`~m_n_kappa.material.Material`.

The following code implements an arbitrary material model that act linear-elastic under compression and ideal-plastic
under tension loading.

Two class-properties must be defined after initialization of the material:

1. ``stress_strain`` (``_stress_strain`` at initialization): stress-strain-relationship as a list of :py:class:`~m_n_kappa.material.StressStrain`
2. ``section_type``: defining the section-type this material is applied to. Possible values are:

   - ``'girder'``
   - ``'slab'``

.. testcode::

   from m_n_kappa.material import Material, StressStrain

   class Arbitrary(Material):

      """arbitrary material"""

      def __init__(self):
         self._stress_strain = [
            StressStrain(stress=-10.0, strain=-0.001),
            StressStrain(stress=0.0, strain=0.0),
            StressStrain(stress=10.0, strain=0.001),
            StressStrain(stress=10.0, strain=0.01),
         ]

      @property
      def section_type(self):
         return "girder"

