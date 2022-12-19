Slim-Floor Beam with :math:`M`-:math:`\kappa`-Curve
***************************************************

Introduction
============
The slim-floor beam in this example consists of a :ref:`m_kappa_example_input_upe200` steel-profile welded onto a :ref:`m_kappa_example_input_bottom_flange`.
The created steel-beam is integrated into a :ref:`m_kappa_example_input_concrete_slab`.
Within in the :ref:`m_kappa_example_input_concrete_slab` also some :ref:`m_kappa_example_input_reinforcement`-Layers are integrated.
Geometry- and material-values are defined hereafter and build later on to a :ref:`cross-section <m_kappa_example_input_reinforcement>`.

Cross-section
=============

.. _m_kappa_example_input_bottom_flange:

Bottom-flange
-------------
The bottom-flange is an ordinary rectangle and located at the bottom-edge of the concrete slab.
It has a thickness :math:`t_\mathrm{f}` = 10 mm and a width :math:`b_\mathrm{f}` = 400 mm.
The corresponding geometry is defined as :py:class:`~m_n_kappa.Rectangle`:

.. plot::
   :nofigs:
   :context:

   from m_n_kappa import Rectangle
   plate_geometry = Rectangle(top_edge=220.0, bottom_edge=220.0+10., width=400.0)

The material of the bottom-flange is steel with following characteristic material values:

- Yield-strength:  :math:`f_\mathrm{y}` = 313 N/mm²
- Tensile-strength:  :math:`f_\mathrm{u}` = 460 N/mm²
- Tensile-strain:  :math:`\varepsilon_\mathrm{u}` = 15 %

Using these values the corresponding material may be defined using :py:class:`~m_n_kappa.Steel`:

.. plot::
   :nofigs:
   :context:

   from m_n_kappa import Steel
   bottom_flange_material = Steel(f_y=313, f_u=460, epsilon_u=0.15)

The modulus of elasticity is assumed to be :math:`E_\mathrm{a}` = 210000 N/mm².
The strain at yielding may be derived by :math:`\varepsilon_\mathrm{y} = f_\mathrm{y} / E_\mathrm{a}`.
This is applied automatically by the :py:class:`~m_n_kappa.Steel`.
Changes to the modulus of elasticity may be applied by passing the corresponding argument to the :py:class:`~m_n_kappa.Steel` (``E_a``).

A :py:class:`~m_n_kappa.Section` of the bottom-flange is created by simply adding ``plate_geometry`` and ``bottom_flange_material`` to each other:

.. plot::
   :nofigs:
   :context:

   bottom_flange = plate_geometry + bottom_flange_material

.. _`m_kappa_example_input_upe200`:

UPE 200
-------
The m-n-kappa-package provides the :py:class:`~m_n_kappa.UPEProfile` to create an UPE 200 profile easily.
The ``top_edge`` must be computed accordingly:

.. plot::
   :nofigs:
   :context:

   from m_n_kappa import UPEProfile
   upe200_geometry = UPEProfile(top_edge=144, t_f=5.2, b_f=76, t_w=9.0, h=200)

:py:class:`~m_n_kappa.UPEProfile` is derived from the :py:class:`~m_n_kappa.ComposedGeometry`.
Therefore, it consists of a set of basic geometry-instances (e.g. several :py:class:`~m_n_kappa.Rectangle`):

> upe200_geometry.geometries

The material of the UPE-profile is also created using :py:class:`~m_n_kappa.Steel` analogous to the creation of the material for the :ref:`m_kappa_example_input_bottom_flange`:

.. plot::
   :nofigs:
   :context:

   from m_n_kappa import Steel
   upe200_material = Steel(f_y=293, f_u=443, epsilon_u=0.15)

Geometry and material are merged easily to a :py:class:`~m_n_kappa.Section` by adding one to the other:

.. plot::
   :nofigs:
   :context:

   upe200 = upe200_geometry + upe200_material


.. _m_kappa_example_input_concrete_slab:

Concrete slab
-------------
The concrete-slab composes of three :py:class:`~m_n_kappa.Rectangle`-instances to consider the integrated steel-profile:

.. plot::
   :nofigs:
   :context:

   concrete_left = Rectangle(top_edge=0.00, bottom_edge=220.00, width=1650.00, left_edge=-1750.00, right_edge=-100.00)
   concrete_middle = Rectangle(top_edge=0.00, bottom_edge=144.00, width=200.00, left_edge=-100.00, right_edge=100.00)
   concrete_right = Rectangle(top_edge=0.00, bottom_edge=220.00, width=1650.00, left_edge=100.00, right_edge=1750.00)
   concrete_geometry = concrete_left + concrete_middle + concrete_right

The material-behaviour of the concrete slab is considered by the :py:class:`~m_n_kappa.Concrete`-instance as follows:

.. plot::
   :nofigs:
   :context:

   from m_n_kappa import Concrete
   concrete_material = Concrete(
      f_cm=29.5,
      f_ctm=2.8,
      compression_stress_strain_type='Nonlinear',
      tension_stress_strain_type='consider opening behaviour'
   )

The full concrete cross-section may be created by adding the material to the created concrete-slab geometries:

.. plot::
   :nofigs:
   :context:

   concrete_slab = concrete_geometry + concrete_material


.. _m_kappa_example_input_reinforcement:

Reinforcement
-------------
Reinforcement-bars may be created by :py:class:`~m_n_kappa.Circle`-class.
The simplify this process :py:class:`~m_n_kappa.RebarLayer` may be used as follows, creating a set of reinforcement-bar cross-sections:

.. plot::
   :nofigs:
   :context:

   from m_n_kappa import RebarLayer
   rebar_top_layer_geometry = RebarLayer(rebar_diameter=12., centroid=10.0, width=3500, rebar_horizontal_distance=100.)
   rebar_bottom_layer_left_geometry = RebarLayer(
	   rebar_diameter=10., centroid=220-10, width=1650.0, rebar_horizontal_distance=100., left_edge=-1740.,
   )
   rebar_bottom_layer_right_geometry = RebarLayer(
	   rebar_diameter=10., centroid=220-10, width=1650.0, rebar_horizontal_distance=100., right_edge=1740.,
   )

The bottom-reinforcement-layer must be split into two layers to consider the recess in the concrete-slab due to the UPE-steel profile.

The material-behaviour of the reinforcement :py:class:`~m_n_kappa.Reinforcement` derives from the :py:class:`~m_n_kappa.Steel`-class:

.. plot::
   :nofigs:
   :context:

   from m_n_kappa import Reinforcement
   rebar10_material = Reinforcement(f_s=594, f_su=685, epsilon_su=0.25, E_s=200000)
   rebar12_material = Reinforcement(f_s=558, f_su=643, epsilon_su=0.25, E_s=200000)

For combination of ``Geometry`` and ``Material`` both instance only need to be added to each other.
By adding the resulting :py:class:`~m_n_kappa.Section`s to each other a rebar-:py:class:`~m_n_kappa.Crosssection` is created:

.. plot::
   :nofigs:
   :context:

   rebar_top_layer = rebar_top_layer_geometry + rebar12_material
   rebar_bottom_layer_left = rebar_bottom_layer_left_geometry + rebar10_material
   rebar_bottom_layer_right = rebar_bottom_layer_right_geometry + rebar10_material
   rebar_layer = rebar_top_layer + rebar_bottom_layer_left + rebar_bottom_layer_right

.. _m_kappa_example_input_building_cross_section:

Building the cross-section
--------------------------
The overall :py:class:`~m_n_kappa.Crosssection` is created by adding all parts together:

.. plot::
   :nofigs:
   :context:

   cross_section = bottom_flange + upe200 + concrete_slab + rebar_layer

.. _m_kappa_loading:

Loading
=======
The loading of the beam is considered by :py:class:`~m_n_kappa.SingleSpan`-class.
The :py:class:`~m_n_kappa.SingleSpan`-class accepts either a uniform load or a list of :py:class:`~m_n_kappa.SingleLoad`.
The ``uniform_load``-argument accepts a float that describes a line-load that is applied uniformly over the length of the girder.
``SingleLoad``-class represents a single load applied at a specific position along the beam:

.. plot::
   :nofigs:
   :context:

   from m_n_kappa import SingleLoad, SingleSpan
   single_load_left = SingleLoad(position_in_beam=1375., value=1.0)
   single_load_right = SingleLoad(position_in_beam=1375. + 1250., value=1.0)
   loading = SingleSpan(length=4000.0, uniform_load=None, loads=[single_load_left, single_load_right])

.. _m_kappa_computation:

Computation
===========
For computation of its reaction behaviour in form of moment-curvature-curves (:math:`M`-:math:`\kappa`) along the beam the :py:class:`~m_n_kappa.Beam`-class is provided.

.. plot::
   :nofigs:
   :context:

   from m_n_kappa import Beam
   beam = Beam(
      cross_section=cross_section,
      length=4000.,
      element_number=20,
      load=loading,
      consider_widths=False
   )

At initialization the :py:class:`~m_n_kappa.Beam`-class does following things:

1. split beam into elements along the length
2. create a :py:class:`~m_n_kappa.deformation.Node` between these elements
3. compute load-steps by determination of the decisive :py:class:`~m_n_kappa.deformation.Node` and its :math:`M`-:math:`\kappa`-curve

.. _m_kappa_analysis:

Analysis
========
Introduction
------------
Using ``beam`` several analyses of the resistance behaviour of the composite beam are possible.

Load-deformation-curve at point of maximum deformation
------------------------------------------------------
The load-bearing behaviour of beams is often characterised by the load-deformation-curve at the point of maximum deformation under the given loading.
``beam.deformations_at_maximum_deformation_position()`` returns the deformations for the decisive load-steps at this point:

.. plot::
   :nofigs:
   :context:

   beam_deformations = beam.deformations_at_maximum_deformation_position()

The resulting deformations may be visualized by choosing an appropriate visualization-library, e.g. `Matplotlib <https://matplotlib.org/>`_, `Altair <https://altair-viz.github.io/>`_ or other.
The following example uses Matplotlib:

.. plot::
   :context:

   import matplotlib.pyplot as plt
   deformations = [deformation.deformation for deformation in beam_deformations]
   loads = [deformation.load*0.001 for deformation in beam_deformations]

   fig,ax = plt.subplots()
   ax.plot(deformations, loads, marker='.')
   for deformation in beam_deformations:
       if deformation.m_kappa_point.strain_position is not None:
           plt.text(
               deformation.deformation,
               10.,
               f'{deformation.m_kappa_point.strain_position.material}'
               f'(pos.={deformation.m_kappa_point.strain_position.position})',
               va='bottom',
               rotation=90
           )
   ax.set_xlim(0,)
   ax.set_ylim(0, )
   ax.set_xlabel('Deformation')
   ax.set_ylabel('Vertical Force')
   ax.grid('major')
   plt.show()
