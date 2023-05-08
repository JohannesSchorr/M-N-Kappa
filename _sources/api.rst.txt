.. _api:

API reference
*************

.. seealso::

   :ref:`api_developers` : overview of all functions

.. currentmodule:: m_n_kappa

.. _api.geometry:

Geometry
========
.. currentmodule:: m_n_kappa

.. rubric:: Basic geometries

.. autosummary::
   :toctree: api/

   Geometry
   Rectangle
   Circle
   Trapezoid

.. rubric:: Composed geometries

.. autosummary::
   :toctree: api/

   geometry.ComposedGeometry
   IProfile
   UPEProfile
   RebarLayer

.. _api.material:

Material
========
.. currentmodule:: m_n_kappa

.. autosummary::
   :toctree: api/

   StressStrain
   Material
   Concrete
   Steel
   Reinforcement

.. _api.sections:

Sections and Cross-section
==========================
.. currentmodule:: m_n_kappa

.. autosummary::
   :toctree: api/

   Section
   Crosssection

.. no need to show here ComputationCrosssectionStrain, ComputationCrosssectionCurvature
   as only a single value is computed and no equilibrium of horizontal forces reached.

.. _api.strain_based_design:

Strain-based-design
===================
.. currentmodule:: m_n_kappa

.. autosummary::
   :toctree: api/

   MKappaByStrainPosition
   MKappaByConstantCurvature
   MomentAxialForce
   MomentAxialForceCurvature

.. _api.moment_curvature_curve:

Moment-Curvature-Curve
======================
.. currentmodule:: m_n_kappa

.. autosummary::
   :toctree: api/

   MKappaCurve
   curves_m_kappa.MKappaCurvePoint
   curves_m_kappa.MKappaCurvePoints

.. _api.moment_axial_force_curvature_curve:

Moment-Axial-Force-Curvature Curve
==================================

.. currentmodule:: m_n_kappa

.. autosummary::
   :toctree: api/

   MNCurve
   MNKappaCurve

.. _api.shear_connector:

Shear connector
===============

.. currentmodule:: m_n_kappa

.. autosummary::
   :toctree: api/

   LoadSlip
   ShearConnector
   HeadedStud

.. _api.loading:

Loading
=======
.. currentmodule:: m_n_kappa

.. autosummary::
   :toctree: api/

   SingleSpanUniformLoad
   SingleLoad
   SingleSpanSingleLoads
   SingleSpan

.. _api.beam:

Beam
====
.. currentmodule:: m_n_kappa

.. autosummary::
   :toctree: api/

   Beam
   Node

.. _api.developers:

API for developers
==================

For a more in-depth study of the internals of the program, beside the :ref:`theory`,
the :ref:`api_developers` guide gives further information.