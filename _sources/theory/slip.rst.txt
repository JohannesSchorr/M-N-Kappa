.. _theory.slip:

Slip
****

.. _theory.slip.general:

General
=======

For determination of the slip :math:`s` the following equation needs to be solved.

.. math::
   :label: eq:theory.slip.moment_aim

   \vec{M}_\mathrm{R} - \vec{M}_\mathrm{E} = 0

Where :math:`\vec{M}_\mathrm{R}` describes the resisting moments of the cross-section and
:math:`\vec{M}_\mathrm{E}` stands for the external moments that
occur if a beam is loaded perpendicular to the beam axis.
The :math:`\vec{\text{arrow}}` above the moment symbols indicates a vector or a single
columned matrix.
Each entry in the vector stands for one computed point along the beam.

The computation of the external Moment :math:`\vec{M}_\mathrm{E}` is
technical mechanics (Force times lever arm) and described under :ref:`theory.loading`.

The resisting Moment :math:`\vec{M}_\mathrm{R}` is computed as described in the following.

.. _theory.slip.computations:

Computations
============

.. _theory.slip.computations.general:

General
-------

In case the cross-section consists of two parts that move relatively to each
other and that are connected by shear connectors the resisting moment :math:`\vec{M}_\mathrm{R}`
depends on the :ref:`theory.slip.computations.strain_difference` :math:`\vec{\varepsilon_\mathrm{\Delta}}` and
the :ref:`axial force<theory.slip.computations.axial_forces>` along the beam :math:`N`.
The computation of this values is described hereafter.

.. _theory.slip.computations.strain_difference:

Strain-difference
-----------------

The strain difference at a specific point along the beam :math:`\vec{\varepsilon_{\mathrm{\Delta}i}}`
depends on the slip :math:`s` and is computed as follows.

.. math::
   :label: eq:strain-difference

   \varepsilon_{i} = \frac{s_{i}}{x_{i} - x_\mathrm{s=0}}

Where :math:`s_{i}` is the slip at a position :math:`x_{i}` along the beam and
:math:`x_\mathrm{s=0}` is the position where the slip is zero.

.. figure:: ../images/theory_strain_difference-dark.svg
   :class: only-dark
   :width: 400
.. figure:: ../images/theory_strain_difference-light.svg
   :class: only-light
   :width: 400

    Slip along the beam

.. _theory.slip.computations.axial_forces:

Axial- and Shear-Forces at Shear connectors
-------------------------------------------

The axial-force :math:`N_{i}` at a position :math:`x_{i}` results from the sum of the transferred
shear forces by the shear connectors :math:`P_{j}`.
The relevant shear connectors :math:`P_{j}` are those between the position :math:`x_\mathrm{s=0}`
where the slip is zero and the given position.

.. math::

   N_{i} = \sum_{j=1}^{i} P_{j}

The transferred shear force of a shear connector at a position along the beam :math:`P_{i}` depends
on the slip at this position.

.. figure:: ../images/theory_load_slip_relationship-dark.svg
   :class: only-dark
   :width: 300
.. figure:: ../images/theory_load_slip_relationship-light.svg
   :class: only-light
   :width: 300

   Exemplary load-slip relationship of a shear connector

.. _theory.slip.computations.resisting_moment:

Determination of the resisting moment
-------------------------------------

The resisting moment :math:`M_\mathrm{R}` at a position :math:`i` is determined by finding  the moment
that is associated with the axial-force :math:`N_{i}` and the strain-difference
:math:`\vec{\varepsilon_\mathrm{\Delta}}` in the corresponding
:math:`M`-:math:`N`-:math:`\kappa`-:math:`\varepsilon_\mathrm{\Delta}`-relationship.

.. note::

   For computation of the :math:`M`-:math:`N`-:math:`\kappa`-:math:`\varepsilon_\mathrm{\Delta}`-relationship please
   refer to :ref:`theory.m_n_curvature_epsilon`.


.. _theory.slip.computations.slip:

Assuming new distribution of slip
---------------------------------
The above given computations base on the slip along the beam :math:`\vec{s}`.
At the beginning of the computation :math:`\vec{s}` is unknown.
The aim of the computation is to find a distribution of slip along the beam that leads to a similar
distribution of moment like the moment from the applied load as indicated in
Formula :math:numref:`eq:theory.slip.moment_aim`.

Therefore, between each iteration a new guess is made on the slip along the beam :math:`\vec{s}`
using the `Levenberg-Marquardt algorithm <https://en.wikipedia.org/wiki/Levenberg%E2%80%93Marquardt_algorithm>`_.
Therefore one iteration-step looks as given in Formula :math:numref:`eq:levenberg-marquardt-iteration`.

.. math::
   :label: eq:levenberg-marquardt-iteration

   \vec{s}_\mathrm{n+1} = \vec{s}_\mathrm{n} - \alpha_{n} \left( (\mathbf{J}_\mathrm{n})^\mathrm{T}
   \mathbf{J}_\mathrm{n} + \lambda~\mathrm{diag}(\mathbf{J}_\mathrm{n}^\mathrm{T}
   \mathbf{J}_\mathrm{n}) \right)^{-1} (\mathbf{J}_\mathrm{n})^\mathrm{T} f(\vec{s}_\mathrm{n})

where :math:`s_\mathrm{n+1}` describes the new guess of the distribution of slip.
The subscript :math:`\mathrm{n}` stands for the current iteration-step.
Therefore, :math:`s_\mathrm{n}` is the slip at the current step of the iteration-process.
:math:`\alpha_{n}` controls the size of the increment and must be greater zero (:math:`\alpha_{n} > 0`).
:math:`\mathbf{J}_\mathrm{n}` is the Jacobian-Matrix, that includes all first-order partial derivates of
the function :math:`f(s_\mathrm{n})` as indicated in Formula :math:numref:`eq:jacobian-matrix`.
:math:`\lambda` is the damping-factor, that is multiplied by the diagonal of
:math:`\mathbf{J}_\mathrm{n}^\mathrm{T}\mathbf{J}_\mathrm{n}`.

.. math::
   :label: eq:jacobian-matrix

   \mathrm{J} = \begin{bmatrix}
       \frac{\partial f_{1}}{\partial s_{1}} & \dots & \frac{\partial f_{1}}{\partial s_{i}} \\
       \vdots & \ddots & \vdots \\
       \frac{\partial f_{j}}{\partial s_{1}} & \dots & \frac{\partial f_{j}}{\partial s_{i}}
       \end{bmatrix}

.. dropdown:: Determining the Jacobian-Matrix using numerical differentiation

   As the determination of the resistance Moment :math:`M_\mathrm{R}` from the
   :math:`M`-:math:`N`-:math:`\kappa`-:math:`\varepsilon_\mathrm{\Delta}`-relationship depends
   on a number of factors that depend for themselves again on various factors a deterministic
   formula is assumed to be not available.
   Or at least possible only under high effort.

   Therefore, the Jacobian Matrix is determined by
   `numerical differentiation <https://en.wikipedia.org/wiki/Numerical_differentiation>`_.
   The forward difference quotient is used as given in Formula
   :ref:`eq:forward_differentiation_coefficient`.

   .. math::
      :label: eq:forward_differentiation_coefficient

      \frac{f(s_{i} + h) - f(s_{i})}{h}

   where :math:`f(s_{i})` describes the function the difference quotient is to be determined of
   and :math:`h` is the interval length.

   The theory is that in case :math:`h` is sufficiently small the difference quotient denotes to the derivate of
   :math:`f` at the distribution of slip :math:`s_i` as indicated in Formula
   :math:numref:`eq:forward_differentation_derivate`.

   .. math::
      :label: eq:forward_differentation_derivate

      f'(s_{i}) = \lim_{h \rightarrow 0} \frac{f(s_{i} + h) - f(xs_{i})}{h}

.. dropdown:: Levenberg-Marquardt algorithm

   For each step in the iteration-process the last term in Formula
   :math:numref:`eq:levenberg-marquardt-iteration` is solved on its own as follows.

   .. math::
      :label: eq:levenberg-marquardt-last-term

      \Delta s_{n} = \left[ (\mathbf{J}_\mathrm{n})^\mathrm{T} \mathbf{J}_\mathrm{n} +
      \lambda~\mathrm{diag}(\mathbf{J}_\mathrm{n}^\mathrm{T} \mathbf{J}_\mathrm{n}) \right]^{-1}
      (\mathbf{J}_\mathrm{n})^\mathrm{T} f(\vec{s}_\mathrm{n})

   To compute :math:`\Delta s_{n}` Formula :math:numref:`eq:levenberg-marquardt-last-term`
   is transformed to match a linear system of equations (:math:`\mathbf{A}x = \vec{b}`).

   .. math::
      :label: eq:levenberg-marquardt-qr-decomposition

      \left[(\mathbf{J}_\mathrm{n})^\mathrm{T} \mathbf{J}_\mathrm{n} + \lambda~\mathrm{diag}(\mathbf{J}_\mathrm{n}^\mathrm{T}
      \mathbf{J}_\mathrm{n})\right] \Delta s_{n} = (J_\mathrm{n})^\mathrm{T} f(\vec{s}_\mathrm{n})

   where
   :math:`\mathbf{A} = (\mathbf{J}_\mathrm{n})^\mathrm{T} \mathbf{J}_\mathrm{n}+ \lambda~\mathrm{diag}(\mathbf{J}_\mathrm{n}^\mathrm{T} \mathbf{J}_\mathrm{n})`,
   :math:`b = (J_\mathrm{n})^{T} f(\vec{s}_\mathrm{n})` and
   :math:`x = \Delta s_{n}`.

   This form allows `QR-decomposition <https://en.wikipedia.org/wiki/QR_decomposition>`_ to
   solve this set of linear equations.

The overall procedure is given in the following section.

.. _theory.slip.procedure:

Procedure
=========
The computation of the slip in the composite joint requires the following preparations:

- Definition of cross-section, load-slip relationship of the shear connector(s), positioning, beam-length, loading
  by the user
- Computation of the :math:`M`-:math:`N`-:math:`\kappa`-:math:`\varepsilon_\mathrm{\Delta}`-relationships of
  the given cross-section at each position
- Computation of the moment :math:`M_\mathrm{E}` by the applied load along the beam

The procedure to compute the slip in the composite joint along the of a beam considering slip in the composite joint is
as follows.

#. assume distribution of slip :math:`s` along the beam
#. compute the :ref:`theory.slip.strain_difference` :math:`\varepsilon_\mathrm{\Delta}`
   at each position considering the slip :math:`s`
#. compute the :ref:`transferred shear force <theory.slip.axial_forces>` of each shear connector :math:`P_{i}`
   and sum it up to compute the resulting axial forces :math:`N_{i}` at each position
#. use axial force :math:`N` and strain-difference :math:`\varepsilon_\mathrm{\Delta}` to determine the
   resisting moment :math:`M_\mathrm{R}` at each position
#. compare :math:`\vec{M}_\mathrm{R}` and applied Moment :math:`\vec{M}_\mathrm{E}`
#. if the difference of :math:`\vec{M}_\mathrm{R}` and :math:`\vec{M}_\mathrm{E}` are outside a given tolerance
   then restart procedure by assuming a new distribution of slip, else the correct distribution
   of slip :math:`s` is found

The correct distribution of slip is then used to compute curvature :math:`\kappa` and subsequently
the deformation of the beam under the given load.

The following figure describes the process of computing the slip as it is described above graphically.

.. figure:: ../images/theory_slip_flowchart-dark.svg
   :class: only-dark
   :width: 500
.. figure:: ../images/theory_slip_flowchart-light.svg
   :class: only-light
   :width: 500

   Procedure to compute the deformation considering slip
