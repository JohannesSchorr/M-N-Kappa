Computation
===========

The ``cross_section`` you created above is the basis to do a variety of computations:

.. tab-set::

   .. tab-item:: Curvature

      In case you want to compute a single curvature-value from a given strain at a given position, you
      first have to define strain and its position using :py:class:`~m_n_kappa.StrainPosition`
      ``strain_position`` is the boundary-condition, that is passed to :py:class:`~m_n_kappa.MKappaByStrainPosition`
      that is computing the curvature.

      >>> from m_n_kappa import StrainPosition, MKappaByStrainPosition
      >>> strain_position = StrainPosition(strain=-0.01, position=0.0, material="")
      >>> computation = MKappaByStrainPosition(
      ...     cross_section=cross_section,
      ...     strain_position = strain_position,
      ...     positive_curvature=True)


      After computation you can extract the results as follows:

      - ``computation.successful``: if ``True`` equilibrium of horizontal forces has been achieved during computation
      - ``computation.axial_force``: computed axial forces that should be near zero as this is what the computation
        is aimed at
      - ``computation.moment``: computed moment
      - ``computation.curvature``: computed curvature
      - ``computation.neutral_axis``: vertical position of the neutral axis (strain :math:`\varepsilon=0`)

      .. seealso::
         :ref:`examples.moment_curvature_curve`: further explanations regarding computation of a single
         moment-curvature-point

   .. tab-item:: M-:math:`\kappa`-curve

      The :math:`M`-:math:`\kappa`-curve is easily computed by passing the created ``cross_section`` to
      :py:class:`~m_n_kappa.MKappaCurve`.
      You only have to decide if you want only the positive moment-curvature-points,
      the negative moment-curvature-points or both.

      >>> from m_n_kappa import MKappaCurve
      >>> positive_m_kappa = MKappaCurve(cross_section=cross_section)
      >>> negative_m_kappa = MKappaCurve(
      ...     cross_section=cross_section,
      ...     include_positive_curvature=False,
      ...     include_negative_curvature=True)
      >>> full_m_kappa = MKappaCurve(
      ...     cross_section=cross_section,
      ...     include_positive_curvature=True,
      ...     include_negative_curvature=True)


      The computed points are then stored in the attribute ``m_kappa_points`` that returns
      :py:class:`~m_n_kappa.curves_m_kappa.MKappaCurvePoints`-object.

      .. seealso::
         :ref:`examples.moment_curvature_curve` : further explanation regarding computation of the Moment-
         Curvature-Curve

   .. tab-item:: Beam-Deformation

      For computation of the :math:`M`-:math:`\kappa`-curves in a beam you need the loading-scenario
      beside your ``cross_section``.
      And you should decide in how many elements the beam shall be split into (see ``element_number``).
      In case you also want to consider the effective widths you may set ``consider_widths=True``.

      >>> from m_n_kappa import SingleSpanUniformLoad, Beam
      >>> loading = SingleSpanUniformLoad(length=8000, load=1.0)
      >>> beam = Beam(cross_section=cross_section, element_number=10, load=loading)
      >>> beam_consider_widths = Beam(
      ...     cross_section=cross_section,
      ...     element_number=10,
      ...     load=loading,
      ...     consider_widths=True)


      The computed beams allow you to do a number of analysis, like:

      - ``beam.deformation_over_length(loading)``: computes the deformation at each node along the beam
        under the given load
      - ``beam.deformations(at_position)``: computes the deformation at the given position for the relevant load-steps
      - ``beam.deformations_at_maximum_deformation_position()``: same like ``beam.deformations(at_position)`` but
        at the position of the beam where the maximum deformation occurred under the given ``loading``.

      .. seealso::
         :ref:`examples.loading`: further explanation of loading scenarios

         :ref:`examples.deformation` : further explanation regarding computation of beam-deformation