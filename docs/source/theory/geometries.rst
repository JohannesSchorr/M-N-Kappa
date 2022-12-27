.. _theory_geometry:

Geometries
**********

.. todo::

   theory - geometries: draw figure(s)

Introduction
============
Within this section the computation of the width :math:`b(x)` of rectangles and the area of circles
:math:`A_\mathrm{circle}` is presented.
Combined with stress-values from :ref:`theory_materials` the axial force :math:`N_i`, the lever arm :math:`z_i` and
the moment :math:`M_i` are computed (see :ref:`theory_sections`).

.. _theory_geometry_rectangle_and_rectangle:

Rectangle
=========

Width
-----
For computation of arbitrary small layers of an rectangle or a trapezoid their width :math:`b` at each vertical position
is defined as given in formula :math:numref:`eq:rectangle_width`.

.. math::
   :label: eq:rectangle_width

   b(z) = m_\mathrm{b} \cdot z + c_\mathrm{b}

The slope :math:`m_\mathrm{b}` in :math:numref:`eq:rectangle_width` is therefore computed using formula
:math:numref:`eq:rectangle_width_slope`.
Where :math:`b_\mathrm{top}` is the width on the top-edge,
:math:`b_\mathrm{bottom}` is the width on the bottom-edge,
:math:`z_\mathrm{top}` is the vertical position of the top-edge and
:math:`z_\mathrm{bottom}` is the vertical position of the bottom-edge of rectangle or trapezoid.

.. math::
   :label: eq:rectangle_width_slope

   m_\mathrm{b} = \frac{b_\mathrm{top} - b_\mathrm{bottom}}{z_\mathrm{top} - z_\mathrm{bottom}}

In case of a rectangle the width-slope :math:`m_\mathrm{b} = 0.0`.

The interception-value :math:`c_\mathrm{b}` is therefore determined by rearranging formula
:math:numref:`eq:rectangle_width` to formula :math:numref:`eq:rectangle_width_interception` and applying known values,
like :math:`b(z_\mathrm{top}) = b_\mathrm{top}`.

.. math::
   :label: eq:rectangle_width_interception

   c_\mathrm{b} = b(z) - m_\mathrm{b} \cdot z

In case of rectangles :math:`c_\mathrm{b}` by formula :math:numref:`eq:rectangle_width_interception` applies to
:math:`c_\mathrm{b} = b_\mathrm{top}`.

Implementation
--------------
The above given formulas are implemented in :py:class:`~m_n_kappa.Rectangle` and :py:class:`~m_n_kappa.Trapezoid`
and used to compute axial-force, the lever-arm of the axial-force and therefore the moment of arbitrary small layers of
the rectangle or the trapezoid.


.. _theory_geometry_circle:

Circle
======

Area
----
The circles are intended for use as reinforcement-bars and therefore in most applications small in comparison
with other geometric instances.
Therefore, computation is reduced to the cross-sectional area of the circle :math:`A_\mathrm{circle}` as shown
in :math:numref:`eq:circle_area`.

.. math::
   :label: eq:circle_area

   A_\mathrm{circle} = \frac{\pi \cdot d}{4}

Where :math:`d` is the diameter of the reinforcement bar.

Implementation
--------------
Formula :math:numref:`eq:circle_area` is implemented in :py:class:`~m_n_kappa.Circle`.
Combined with the vertical position of the centroid the moment may be computed as well.

