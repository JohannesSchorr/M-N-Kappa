.. _api_developers:

API for developers
******************

.. _api_developers.general:

General
=======
.. currentmodule:: m_n_kappa.general

.. rubric:: Classes

.. autosummary::
   :toctree: api/

   StrainPosition
   EffectiveWidths
   NotSuccessfulReason

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

.. _api_developers.geometries:

Geometries
==========
.. currentmodule:: m_n_kappa.geometry

.. autosummary::
   :toctree: api/

   check_width

.. _api_developers.material:

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

.. _api_developers.sections:

Sections
========
.. currentmodule:: m_n_kappa.section

.. autosummary::
   :toctree: api/

   ComputationSection
   ComputationSectionCurvature
   ComputationSectionStrain

.. _api_developers.cross_section:

Cross-sections
==============

.. currentmodule:: m_n_kappa.crosssection

.. rubric:: Classes

.. autosummary::
   :toctree: api/

   ComputationCrosssection
   ComputationCrosssectionStrain
   ComputationCrosssectionCurvature
   ComputationCrosssectionStrainAdd
   EdgeStrains
   CrossSectionBoundaries

.. rubric:: Methods

.. autosummary::
   :toctree: api/

   axial_force
   moment
   determine_curvatures
   compute_neutral_axis

.. _api_developers.cross_section_boundaries:

Cross-section boundaries
========================

.. currentmodule:: m_n_kappa.boundaries

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
   get_higher_positions

.. _api_developers.strain_based_design:

Strain-based design
===================

.. currentmodule:: m_n_kappa.points

.. autosummary::
   :toctree: api/

   Point
   Computation
   MKappa
   MNByStrain
   AxialForcePoint

.. _api_developers.moment_axial_force_curvature_curve:

Moment-Axial-Force-Curvature Curve
==================================

.. currentmodule:: m_n_kappa.curves_m_n_kappa

.. autosummary::
   :toctree: api/

   MNKappaCurvePoint
   MNKappaCurvePoints
   MNCurvatureCurve

.. _api_developers.solver:

Solver
======

.. currentmodule:: m_n_kappa.solver

.. autosummary::
   :toctree: api/

   Solver
   Bisection
   Newton

Fitting
=======

.. currentmodule:: m_n_kappa.fitting

.. autosummary::
   :toctree: api/

   GaussNewton

Matrices
========

.. currentmodule:: m_n_kappa.matrices

.. autosummary::
   :toctree: api/

   Vector
   Matrix
   Jacobian
   LinearEquationsSystem

.. _api_developers.loading:

Loading
=======

.. currentmodule:: m_n_kappa.loading

.. autosummary::
   :toctree: api/

   ABCSingleSpan