:hide-toc:

.. image:: ./_static/logo/m_kappa_logo.svg

M-N-Kappa
*********
|Versioning| | |Documentation|

Computing beam-deformations considering non-linear materials
============================================================

:mod:`m_n_kappa` is an open source library for using the strain-based method
to compute the stress-distribution of a cross-section considering multi-linear
material models.

The resulting relationship between bending moment *M* and curvature :math:`\kappa`
empowers to compute the deformation of a beam under a given load considering
non-linear effects like cracking of concrete, plasticizing of steel, etc.

Furthermore, you may compute a composite-cross-section with two sub-cross-sections, where
also axial-forces *N* and strain-differences :math:`\varepsilon_\mathrm{\Delta}`
are considered.
By this approach you may also consider the slip in the composite joint, the multi-linear
load-slip-behaviour of shear-connectors and its effect on the deformation of the composite beam.

**Features**

- strain-based method considering multi-linear material models
- distinction between bending and membran width of the concrete-slab
- consideration of the multi-line shear-connector behaviour

**Planned**

- computation of for beams with more than one span as well as cantilever beams

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card::
      :link: getting_started
      :link-type: ref
      :text-align: center

      **Getting started**
      ^^^^^^^^^^^^^^^^^^^

      Installation and introductory example

   .. grid-item-card::
      :link: examples
      :link-type: ref
      :text-align: center

      **Examples**
      ^^^^^^^^^^^^

      Want to know how to apply :mod:`m_n_kappa`
      Here a bunch of tutorials are given.

   .. grid-item-card::
      :link: theory
      :link-type: ref
      :text-align: center

      **Theory Guide**
      ^^^^^^^^^^^^^^^^

      Methodology and theoretical background of the :math:`M`-:math:`\kappa` and
      the :math:`M`-:math:`N`-:math:`\kappa`-method

   .. grid-item-card::
      :link: verification
      :link-type: ref
      :text-align: center

      **Verification**
      ^^^^^^^^^^^^^^^^

      :mod:`m_n_kappa` is verified using experimental investigations

.. toctree::
   :hidden:

   getting_started
   examples/index
   theory/index
   verification/index

.. toctree::
   :hidden:
   :caption: Development

   api
   api_developers
   roadmap
   contributing
   whatsnew/index
   license

.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
