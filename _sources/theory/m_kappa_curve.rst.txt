.. _theory.m_kappa:

:math:`M`-:math:`\kappa`-curve
******************************

.. _theory.m_kappa.definition:

Definition
==========

.. todo::
   add figure of a Moment-Curvature-Curve

The :math:`M`-:math:`\kappa`-curve shows the relationship between the moment :math:`M` and the curvature
:math:`\kappa` of a given cross-section.
The curve considers the non-linear stress-strain relationships of the :ref:`theory.materials` of the cross-section.
Therefore, each :math:`M`-:math:`\kappa`-point is computed using :ref:`theory.strain_based_design`.

The following sections outline the process of computing the :math:`M`-:math:`\kappa`-curve as implemented.


.. _theory.m_kappa.procedure:

Procedure
=========

The overall procedure to compute the :math:`M`-:math:`\kappa`-curve is as follows:
   1. compute the :math:`M`-:math:`\kappa`-point under failure
   2. determine all position-strain-values between the failure-curvature and zero curvature
   3. use these position-strain-values to compute all intermediate :math:`M`-:math:`\kappa`-points

The outlined process is applied for positive and negative curvatures.


.. _theory.m_kappa.failure:

Failure
=======

.. todo::
   create figure

The curvature at failure :math:`\kappa_\mathrm{fail}` is crucial for an efficient computation
of the full :math:`M`-:math:`\kappa`-curve.
The position-strain-pair at failure is a value of the cross-section and therefore computed
during determination of the :ref:`theory.strain_based_design.boundary_values`.

In case the position-strain-pair at failure is known it is used to compute :math:`\kappa_\mathrm{fail}` by
:ref:`Iteration <theory.strain_based_design.equilibrium>`.

.. _theory.m_kappa.intermediate:

Intermediate values
===================

.. todo::
   create figure

Between the curvature at failure :math:`\kappa_\mathrm{fail}` and no curvature of the cross-section at all,
various position-strain-points are passed.
These position-strain-points are determined and allow therefore a computation of a holistic of the
full :math:`M`-:math:`\kappa`-curve also by :ref:`Iteration <theory.strain_based_design.equilibrium>`.

The full :math:`M`-:math:`\kappa`-curve is used to compute the
:ref:`non-linear load-deformation-behaviour of a beam <theory.deformations>`.