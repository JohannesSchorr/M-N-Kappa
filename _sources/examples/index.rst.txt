.. _examples:

Examples
========

The following examples help you understanding how the API of :mod:`m_n_kappa` works.
:ref:`Geometries <examples.geometry>` and :ref:`Materials <examples.material>` form
the basis for creating :ref:`Sections <examples.section>` and :ref:`Cross-sections <examples.cross_section>`.
Then again :ref:`Moment-Curvature points <examples.moment_curvature>`,
:ref:`Moment-Curvature- <examples.moment_curvature_curve>` and
:ref:`Moment-Axial-Force-Curvature curves <examples.moment_axial_force_curvature_curve>`
are computed using :ref:`Cross-sections <examples.cross_section>`.
The curves and the :ref:`Loading <examples.loading>` are needed to compute the
:ref:`Deformation <examples.deformation>` of your beam.

Due to nature of the problem of computing deformations using the :math:`M`-:math:`N`-:math:`\kappa`-method
all of the mentioned points are related to each other hierarchically.
Therefore, the downstream articles repeat some of the basic concepts in short, i.e. for computing
:ref:`Deformations <examples.deformation>` a cross-section is created.

In case you have a specific cross-section in mind, but you do not know how to build it, check out
the :ref:`cross_section_template`.
You may find what you need there.

.. grid:: 1 2 3 4
   :gutter: 3

   .. grid-item-card:: Create Geometries
      :link: examples.geometry
      :link-type: ref
      :text-align: center
      :img-top: ../images/theory_geometries_icon.svg

   .. grid-item-card:: Create Materials
      :link: examples.material
      :link-type: ref
      :text-align: center
      :img-top: ../images/theory_materials_icon.svg

   .. grid-item-card:: Build a section
      :link: examples.section
      :link-type: ref
      :text-align: center
      :img-top: ../images/theory_sections_icon.svg

   .. grid-item-card:: Build a cross-section
      :link: examples.cross_section
      :link-type: ref
      :text-align: center
      :img-top: ../images/template_composite_beam_icon.svg

   .. grid-item-card:: Compute Moment-Curvature point
      :link: examples.moment_curvature
      :link-type: ref
      :text-align: center
      :img-top: ../images/theory_strain_based_design_icon.svg

   .. grid-item-card:: Compute Moment-Curvature Curve
      :link: examples.moment_curvature_curve
      :link-type: ref
      :text-align: center
      :img-top: ../images/theory_moment_curvature_icon.svg

   .. grid-item-card:: Compute Moment-Axial-Force-Curvature Curve
      :link: examples.moment_axial_force_curvature_curve
      :link-type: ref
      :text-align: center
      :img-top: ../images/theory_moment_axial_force_curvature_icon.svg

   .. grid-item-card:: Create loading
      :link: examples.loading
      :link-type: ref
      :text-align: center
      :img-top: ../images/theory_loading_icon.svg

   .. grid-item-card:: Compute deformation
      :link: examples.deformation
      :link-type: ref
      :text-align: center
      :img-top: ../images/theory_deformation_icon.svg


.. toctree::
   :titlesonly:
   :hidden:

   geometry
   material
   section
   cross_section
   moment_curvature
   moment_curvature_curve
   moment_axial_force_curvature_curve
   loading
   deformation
   Single span slim-floor beam with Moment-Curvature-Curves <m_kappa_UPE>
   Single span slim-floor beam with Moment-Axial force-Curvature-Curves <m_n_kappa_UPE>


.. _cross_section_template:

Templates
---------

The following templates show you a way to model specific cross-section-types with
:py:mod:`m_n_kappa`.
Besides the corresponding code also short-descriptions of the used geometric and material
instances are given.

The icons indicate what type of cross-section may be build here.
Currently, these templates focus on steel, concrete and steel-concrete-composite cross-sections.
Of course, due to the general approach of :py:mod:`m_n_kappa` using multi-linear stress-strain-relationships
a variety of other cross-sections using other materials and other geometries are conceivable.
In case you have a specific idea please consider :ref:`Contributing`.

.. grid:: 2 3 4 5
   :gutter: 3

   .. grid-item-card:: Symmetric steel profile
      :link: cross_section_template.symmetric_steel_profile
      :link-type: ref
      :text-align: center
      :img-top: ../images/template_symmetric_steel_profile_icon.svg

   .. grid-item-card:: Asymmetric steel profile
      :link: cross_section_template.asymmetric_steel_profile
      :link-type: ref
      :text-align: center
      :img-top: ../images/template_asymmetric_steel_profile_icon.svg

   .. grid-item-card:: Composite beam
      :link: cross_section_template.composite_beam
      :link-type: ref
      :text-align: center
      :img-top: ../images/template_composite_beam_icon.svg

   .. grid-item-card:: Composite beam with parallel sheeting
      :link: cross_section_template.composite_beam_with_longitudinal_steel_profile
      :link-type: ref
      :text-align: center
      :img-top: ../images/template_composite_beam_parallel_sheeting_icon.svg

   .. grid-item-card:: Slim-Floor beam with I-profile and solid slab
      :link: cross_section_template.slim_floor_i_profile
      :link-type: ref
      :text-align: center
      :img-top: ../images/template_slim_floor_i_profile_solid_slab_icon.svg

   .. grid-item-card:: Slim-Floor beam with I-profile and concrete flanges
      :link: cross_section_template.slim_floor_i_profile_with_concrete_flanges
      :link-type: ref
      :text-align: center
      :img-top: ../images/template_slim_floor_i_profile_flanges_icon.svg

   .. grid-item-card:: Slim-Floor beam with T-profile
      :link: cross_section_template.slim_floor_t_profile
      :link-type: ref
      :text-align: center
      :img-top: ../images/template_slim_floor_t_profile_icon.svg

   .. grid-item-card:: Slim-Floor beam with double T-profile
      :link: cross_section_template.slim_floor_double_t_profile
      :link-type: ref
      :text-align: center
      :img-top: ../images/template_slim_floor_double_t_profile_icon.svg

   .. grid-item-card:: Slim-Floor beam with small hat profile
      :link: cross_section_template.slim_floor_small_hat
      :link-type: ref
      :text-align: center
      :img-top: ../images/template_slim_floor_small_hat_icon.svg

   .. grid-item-card:: Slim-Floor beam with large hat profile
      :link: cross_section_template.slim_floor_large_hat
      :link-type: ref
      :text-align: center
      :img-top: ../images/template_slim_floor_large_hat_icon.svg

   .. grid-item-card:: Reinforced concrete beam
      :link: cross_section_template.concrete_beam
      :link-type: ref
      :text-align: center
      :img-top: ../images/template_concrete_beam_icon.svg

   .. grid-item-card:: Concrete beam with flanges
      :link: cross_section_template.concrete_beam_with_flanges
      :link-type: ref
      :text-align: center
      :img-top: ../images/template_concrete_beam_with_flanges_icon.svg

.. toctree::
   :caption: Templates
   :hidden:

   cross_section_templates/index


