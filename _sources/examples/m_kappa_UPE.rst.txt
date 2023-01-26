.. _examples.m_kappa_UPE:

Single span slim-floor beam with :math:`M`-:math:`\kappa`-Curve
***************************************************************

*Units: Millimeter [mm], Newton [N]*

.. altair-plot::
   :output: None
   :hide-code:

   # configuration of altair-plot
   import altair as alt
   alt.themes.enable('quartz')

.. _examples.m_kappa_UPE.intro:

Introduction
============
The slim-floor beam in this example consists of a :ref:`examples.m_kappa_UPE.input.upe200` steel-profile welded onto a
:ref:`examples.m_kappa_UPE.input.bottom_flange`.
The created steel-beam is integrated into a :ref:`examples.m_kappa_UPE.input.concrete_slab`.
Within in the :ref:`examples.m_kappa_UPE.input.concrete_slab` also some
:ref:`examples.m_kappa_UPE.input.reinforcement`-Layers are integrated.
Geometry- and material-values are defined hereafter and build later on to a
:ref:`cross-section <examples.m_kappa_UPE.input.reinforcement>`.

.. _examples.m_kappa_UPE.input:

Cross-section
=============

.. _examples.m_kappa_UPE.input.bottom_flange:

Bottom-flange
-------------
The bottom-flange is an ordinary rectangle and located at the bottom-edge of the concrete slab.
It has a thickness :math:`t_\mathrm{f}` = 10 mm and a width :math:`b_\mathrm{f}` = 400 mm.
The corresponding geometry is defined as :py:class:`~m_n_kappa.Rectangle`:

.. altair-plot::
   :output: repr

   from m_n_kappa import Rectangle
   plate_geometry = Rectangle(top_edge=220.0, bottom_edge=220.0+10., width=400.0)

The material of the bottom-flange is steel with following characteristic material values:

- Yield-strength:  :math:`f_\mathrm{y}` = 313 N/mm²
- Tensile-strength:  :math:`f_\mathrm{u}` = 460 N/mm²
- Tensile-strain:  :math:`\varepsilon_\mathrm{u}` = 15 %

Using these values the corresponding material may be defined using :py:class:`~m_n_kappa.Steel`:

.. altair-plot::
   :output: repr

   from m_n_kappa import Steel
   bottom_flange_material = Steel(f_y=313, f_u=460, failure_strain=0.15)

The modulus of elasticity is assumed to be :math:`E_\mathrm{a}` = 210000 N/mm².
The strain at yielding may be derived by :math:`\varepsilon_\mathrm{y} = f_\mathrm{y} / E_\mathrm{a}`.
This is applied automatically by the :py:class:`~m_n_kappa.Steel`.
Changes to the modulus of elasticity may be applied by passing the corresponding argument to the
:py:class:`~m_n_kappa.Steel` (``E_a``).

A :py:class:`~m_n_kappa.Section` of the bottom-flange is created by simply adding
``plate_geometry`` and ``bottom_flange_material`` to each other:

.. altair-plot::
   :output: repr

   bottom_flange = plate_geometry + bottom_flange_material

.. _examples.m_kappa_UPE.input.upe200:

UPE 200
-------
The m-n-kappa-package provides the :py:class:`~m_n_kappa.UPEProfile` to create an UPE 200 profile easily.
The ``top_edge`` must be computed accordingly:

.. altair-plot::
   :output: repr

   from m_n_kappa import UPEProfile
   upe200_geometry = UPEProfile(top_edge=144, t_f=5.2, b_f=76, t_w=9.0, h=200)

:py:class:`~m_n_kappa.UPEProfile` is derived from the :py:class:`~m_n_kappa.geometry.ComposedGeometry`.
Therefore, it consists of a set of basic geometry-instances (e.g. several :py:class:`~m_n_kappa.Rectangle`):

.. altair-plot::
   :output: repr

   upe200_geometry.geometries

The material of the UPE-profile is also created using :py:class:`~m_n_kappa.Steel` analogous to the creation of the 
material for the :ref:`examples.m_kappa_UPE.input.bottom_flange`:

.. altair-plot::
   :output: repr

   from m_n_kappa import Steel
   upe200_material = Steel(f_y=293, f_u=443, failure_strain=0.15)

Geometry and material are merged easily to a :py:class:`~m_n_kappa.Crosssection` by addition:

.. altair-plot::
   :output: repr

   upe200 = upe200_geometry + upe200_material


.. _examples.m_kappa_UPE.input.concrete_slab:

Concrete slab
-------------
The concrete-slab composes of three :py:class:`~m_n_kappa.Rectangle`-instances to consider the integrated steel-profile:

.. altair-plot::
   :output: repr

   concrete_left = Rectangle(top_edge=0.00, bottom_edge=220.00, width=1650.00, left_edge=-1750.00, right_edge=-100.00)
   concrete_middle = Rectangle(top_edge=0.00, bottom_edge=144.00, width=200.00, left_edge=-100.00, right_edge=100.00)
   concrete_right = Rectangle(top_edge=0.00, bottom_edge=220.00, width=1650.00, left_edge=100.00, right_edge=1750.00)
   concrete_geometry = concrete_left + concrete_middle + concrete_right

The material-behaviour of the concrete slab is considered by the :py:class:`~m_n_kappa.Concrete`-instance as follows:

.. altair-plot::
   :output: repr

   from m_n_kappa import Concrete
   concrete_material = Concrete(
      f_cm=29.5,
      f_ctm=2.8,
      compression_stress_strain_type='Nonlinear',
      tension_stress_strain_type='consider opening behaviour'
   )

The full concrete cross-section may be created by adding the material to the created concrete-slab geometries:

.. altair-plot::
   :output: repr

   concrete_slab = concrete_geometry + concrete_material


.. _examples.m_kappa_UPE.input.reinforcement:

Reinforcement
-------------
Reinforcement-bars may be created by :py:class:`~m_n_kappa.Circle`-class.
The simplify this process :py:class:`~m_n_kappa.RebarLayer` may be used as follows, creating a set of reinforcement-bar
cross-sections:

.. altair-plot::
   :output: repr

   from m_n_kappa import RebarLayer
   rebar_top_layer_geometry = RebarLayer(rebar_diameter=12., centroid_z=10.0, width=3500, rebar_horizontal_distance=100.)
   rebar_bottom_layer_left_geometry = RebarLayer(
	   rebar_diameter=10., centroid_z=220-10, width=1650.0, rebar_horizontal_distance=100., left_edge=-1740.,
   )
   rebar_bottom_layer_right_geometry = RebarLayer(
	   rebar_diameter=10., centroid_z=220-10, width=1650.0, rebar_horizontal_distance=100., right_edge=1740.,
   )

The bottom-reinforcement-layer must be split into two layers to consider the recess in the concrete-slab due to the
UPE-steel profile.

The material-behaviour of the reinforcement :py:class:`~m_n_kappa.Reinforcement` derives
from the :py:class:`~m_n_kappa.Steel`-class:

.. altair-plot::
   :output: repr

   from m_n_kappa import Reinforcement
   rebar10_material = Reinforcement(f_s=594, f_su=685, failure_strain=0.25, E_s=200000)
   rebar12_material = Reinforcement(f_s=558, f_su=643, failure_strain=0.25, E_s=200000)

For combination of ``Geometry`` and ``Material`` both instance only need to be added to each other.
By adding the resulting :py:class:`~m_n_kappa.Section` instance to each other a :py:class:`~m_n_kappa.Crosssection`
of rebars is created:

.. altair-plot::
   :output: repr

   rebar_top_layer = rebar_top_layer_geometry + rebar12_material
   rebar_bottom_layer_left = rebar_bottom_layer_left_geometry + rebar10_material
   rebar_bottom_layer_right = rebar_bottom_layer_right_geometry + rebar10_material
   rebar_layer = rebar_top_layer + rebar_bottom_layer_left + rebar_bottom_layer_right

.. _examples.m_kappa_UPE.input.building_cross_section:

Building the cross-section
--------------------------
The overall :py:class:`~m_n_kappa.Crosssection` is created by adding all parts together:

.. altair-plot::
   :output: repr

   cross_section = bottom_flange + upe200 + concrete_slab + rebar_layer

.. _examples.m_kappa_UPE.loading:

Loading
=======
The loading of the beam is considered by :py:class:`~m_n_kappa.SingleSpan`-class.
The :py:class:`~m_n_kappa.SingleSpan`-class accepts either a uniform load or a list of
:py:class:`~m_n_kappa.SingleLoad`.
The ``uniform_load``-argument accepts a float that describes a line-load that is applied uniformly over the
length of the girder.
The :py:class:`~m_n_kappa.SingleLoad`-class represents a single load applied at a specific position along
the beam:

.. altair-plot::
   :output: repr

   from m_n_kappa import SingleLoad, SingleSpan
   single_load_left = SingleLoad(position_in_beam=1375., value=1.0)
   single_load_right = SingleLoad(position_in_beam=1375. + 1250., value=1.0)
   loading = SingleSpan(length=4000.0, uniform_load=None, loads=[single_load_left, single_load_right])

.. _examples.m_kappa_UPE.computation:

Computation
===========

Introduction
------------

For computation of its reaction behaviour in form of moment-curvature-curves (:math:`M`-:math:`\kappa`) along
the beam the :py:class:`~m_n_kappa.Beam`-class is provided.

At initialization the :py:class:`~m_n_kappa.Beam`-class does following things:

1. split beam into elements along the length
2. create a :py:class:`~m_n_kappa.deformation.Node` between these elements
3. compute load-steps by determination of the decisive :py:class:`~m_n_kappa.deformation.Node` and its
:math:`M`-:math:`\kappa`-curve

In :ref:`examples.m_kappa_UPE.geometrical_widths` the :math:`M`-:math:`\kappa`-curves are computed
neglecting the effective widths of the computation.
Whereas in :ref:`examples.m_kappa_UPE.effective_widths` effective widths are considered considering
the bending and membran effective widths.

.. _examples.m_kappa_UPE.geometrical_widths:

Considering geometrical widths
------------------------------

Considering geometrical widths and neglecting effective widths are accomplished by setting ``consider_widths=False``.
Geometrical widths are in any case greater than the effective widths.

.. altair-plot::
   :output: repr

   from m_n_kappa import Beam

   beam_geometrical_widths = Beam(
      cross_section=cross_section,
      element_number=10,
      load=loading,
      consider_widths=False
   )


.. _examples.m_kappa_UPE.effective_widths:

Considering effective widths
----------------------------

The effective widths of the concrete slab are taken into account during computation by passing ``consider_widths=True``.

.. altair-plot::
   :output: repr

   beam_effective_widths = Beam(
      cross_section=cross_section,
      element_number=10,
      load=loading,
      consider_widths=True
   )

The following graph shows how the effective widths are considered.

.. altair-plot::
   :alt: Comparing bending and membran widths

   import pandas as pd
   import altair as alt

   df = pd.DataFrame({
       'positions': beam_effective_widths.positions,
       'bending': beam_effective_widths.bending_widths(),
       'membran': beam_effective_widths.membran_widths(),
   })

   df_melt = df.melt(id_vars=['positions'], value_vars=['bending', 'membran'],
                     var_name='width_type', value_name='width')

   alt.Chart(df_melt, height=100.0, background='#00000000').mark_line().encode(
      x=alt.X('positions', title='Position along the beam [mm]'),
      y=alt.Y('width', title='Width [mm]'),
      color='width_type',
   ).configure_legend(labelColor='#979797', titleColor='#979797')

.. _examples.m_kappa_UPE.analysis:

Analysis
========
Introduction
------------
An instance of the :py:class:`~m_n_kappa.Beam`-class allows several analyses of the resistance behaviour
of the computed composite beam.

.. _examples.m_kappa_UPE.analysis.load_deformation:

Load-deformation-curve at point of maximum deformation
------------------------------------------------------
The load-bearing behaviour of beams is often characterised by the load-deformation-curve at the point
of maximum deformation under the given loading.
:py:meth:`~m_n_kappa.Beam.deformations_at_maximum_deformation_position` returns the deformations for
the decisive load-steps at this point:

.. altair-plot::
   :output: repr

   beam_deformations_geometrical_widths = beam_geometrical_widths.deformations_at_maximum_deformation_position()
   beam_deformations_effective_widths = beam_effective_widths.deformations_at_maximum_deformation_position()

The resulting deformations may be visualized as follows.
Considering the effective width leads smaller maximum resistance as well as smaller deformation-capacity.

.. altair-plot::
   :alt: Load-deformation-curves considering geometrical and effective widths

   df = pd.DataFrame({
       'deformation': (beam_deformations_geometrical_widths.values() +
                       beam_deformations_effective_widths.values()),
       'loadings': (beam_deformations_geometrical_widths.loadings(factor=0.001) +
                    beam_deformations_effective_widths.loadings(factor=0.001)),
       'Width type': (['Geometrical width']*len(beam_deformations_geometrical_widths.loadings()) +
                ["Effective width"]*len(beam_deformations_effective_widths.loadings())),
   })

   alt.Chart(df, background='#00000000').mark_line().encode(
       x=alt.X('deformation', title='Deformation [mm]'),
       y=alt.Y('loadings', title='Loading [kN]'),
       color='Width type',
   ).configure_legend(labelColor='#979797', titleColor='#979797')
