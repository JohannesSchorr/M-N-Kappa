.. _api:

API reference
*************

.. seealso::

   :ref:`api_developers` : overview of all functions

.. currentmodule:: m_n_kappa

.. _api.geometry:

Geometry
========
.. currentmodule:: m_n_kappa.geometry

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

   ComposedGeometry
   IProfile
   UPEProfile
   RebarLayer

.. _api.material:

Material
========
.. currentmodule:: m_n_kappa

.. autosummary::
   :toctree: api/

   Material
   Concrete
   Steel
   Reinforcement

.. _api.sections:

Sections and Cross-section
=========================

.. autosummary::
   :toctree: api/

   Section
   Crosssection

.. _api.strain_based_design:

Strain-based-design
===================

.. autosummary::
   :toctree: api/

   MKappaByStrainPosition
   MKappaByConstantCurvature

Loading
=======

.. autosummary::
   :toctree: api/

   SingleSpanUniformLoad
   SingleLoad
   SingleSpanSingleLoads
   SingleSpan

.. _api.beam:

Beam
====

.. autosummary::
   :toctree: api/

   Beam
   Node

.. _api.developers:

API for developers
==================

For a more in-depth study of the internals of the program, beside the :ref:`theory_guide`,
the :ref:`api_developers` guide gives further information.