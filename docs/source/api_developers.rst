.. _api_developers:

API for developers
******************

General
=======
.. currentmodule:: m_n_kappa.general

.. rubric:: Classes

.. autosummary::
   :toctree: api/

   StrainPosition
   EffectiveWidths

.. rubric:: Functions

.. autosummary::
   :toctree: api/

   curvature
   curvature_by_points
   strain
   position
   neutral_axis
   remove_duplicates
   positive_sign
   negative_sign
   interpolation

Geometries
==========
.. currentmodule:: m_n_kappa.geometry

.. autosummary::
   :toctree: api/

   check_width

Material
========
.. currentmodule:: m_n_kappa.material

.. autosummary::
   :toctree: api/

   StressStrain
   ConcreteCompression
   ConcreteCompressionNonlinear
   ConcreteCompressionParabolaRectangle
   ConcreteCompressionBiLinear
   ConcreteTension

Sections
========
.. currentmodule:: m_n_kappa.section

.. autosummary::
   :toctree: api/

   Section
   ComputationSection
   ComputationSectionCurvature
   ComputationSectionStrain

Cross-sections
==============

.. currentmodule:: m_n_kappa.crosssection

.. rubric:: Classes

.. autosummary::
   :toctree: api/

   ComputationCrosssection
   ComputationCrosssectionStrain
   ComputationCrosssectoinStrainAdd
   ComputationCrosssectionCurvature
   EdgeStrains
   CrossSectionBoundaries

.. rubric:: Methods

.. autosummary::
   :toctree: api/

   axial_force
   moment
   determine_curvatures
   compute_neutral_axis

Cross-section boundaries
========================

.. currentmodule:: m_n_kappa.curvature_boundaries

.. rubric:: Classes

.. autosummary::
   :toctree: api/

   MaximumCurvature
   MinimumCurvature
   BoundaryValues
   Boundaries

.. rubric:: Methods

.. autosummary::
   :toctree: api/

   compute_curvatures
   remove_higher_strains
   remove_smaller_strains
   get_lower_positions
   get_higher_positionsh

Strain-based design
===================

.. currentmodule:: m_n_kappa.points

.. autosummary::
   :toctree: api/

   Computation
   MKappa

Solver
======

.. currentmodule:: m_n_kappa.solver

.. autosummary::
   :toctree: api/

   Solver
   Bisection
   Newton

Loading
=======

.. currentmodule:: m_n_kappa.internalforces

.. autosummary::
   :toctree: api/

   ABCSingleSpan