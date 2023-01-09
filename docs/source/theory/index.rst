:html_theme.sidebar_secondary.remove:

.. _theory:

Theory guide
************

The Theory guide gives background-information to the applied processes working under
the hood of this program.

.. grid:: 1 2 3 4
   :gutter: 3

   .. grid-item-card::
      :link: theory.symbols
      :link-type: ref
      :text-align: center
      :img-top: ../images/theory_symbols_icon.svg

      **Symbols**
      ^^^^^^^^^^^
      overview over all symbols with short description

   .. grid-item-card::
      :link: theory.coordinates
      :link-type: ref
      :text-align: center
      :img-top: ../images/theory_coordinates_icon.svg

      **Coordinates**
      ^^^^^^^^^^^^^^^
      assumed coordinates

   .. grid-item-card::
      :link: theory.units
      :link-type: ref
      :text-align: center
      :img-top: ../images/theory_units_icon.svg

      **Units**
      ^^^^^^^^^
      Recommended units to use for input

   .. grid-item-card::
      :link: theory.general
      :link-type: ref
      :text-align: center
      :img-top: ../images/theory_general_icon.svg

      **General**
      ^^^^^^^^^^^

      Relationship between curvature, strain at a position and neutral axis

   .. grid-item-card::
      :link: theory.geometries
      :link-type: ref
      :text-align: center
      :img-top: ../images/theory_geometries_icon.svg

      **Geometries**
      ^^^^^^^^^^^^^^

      Geometries are a very define a very important part

   .. grid-item-card::
      :link: theory.materials
      :link-type: ref
      :text-align: center
      :img-top: ../images/theory_materials_icon.svg

      **Materials**
      ^^^^^^^^^^^^^^

      Background to the implemented material-models

   .. grid-item-card::
      :link: theory.sections
      :link-type: ref
      :text-align: center
      :img-top: ../images/theory_sections_icon.svg

      **Sections**
      ^^^^^^^^^^^^

      computation of axial-force and moment of sections and cross-sections under a given strain-distribution

   .. grid-item-card::
      :link: theory.strain_based_design
      :link-type: ref
      :text-align: center

      **Strain based design**
      ^^^^^^^^^^^^^^^^^^^^^^^

      determine moment and curvature of a cross-section given a strain at a position by iteration

   .. grid-item-card::
      :link: theory.m_kappa
      :link-type: ref
      :text-align: center
      :img-top: ../images/theory_moment_curvature_icon.svg

      **Moment-Curvature-Curve**
      ^^^^^^^^^^^^^^^^^^^^^^^^^^

      Procedure to compute the moment-curvature-curve

   .. grid-item-card::
      :link: theory.effective_widths
      :link-type: ref
      :text-align: center
      :img-top: ../images/theory_effective_widths_icon.svg

      **Effective widths**
      ^^^^^^^^^^^^^^^^^^^^

      Computations of effective widths under bending and axial loading

   .. grid-item-card::
      :link: theory.loading
      :link-type: ref
      :text-align: center
      :img-top: ../images/theory_loading_icon.svg

      **Loading**
      ^^^^^^^^^^^^^^^^



   .. grid-item-card::
      :link: theory.deformations
      :link-type: ref
      :text-align: center
      :img-top: ../images/theory_deformation_icon.svg

      **Deformations**
      ^^^^^^^^^^^^^^^^

      Computing deformation under given loading using the moment-curvature-curve

.. toctree::
   :hidden:

   symbols
   coordinates
   units
   general
   geometries
   materials
   sections
   strain_based_design
   m_kappa_curve
   effective_widths
   loading
   deformations
