.. summarizing overview over all given variables

.. _theory.symbols:

Symbols
*******

Latin letters
=============

.. list-table::
   :widths: 20 40 40

   * - :math:`A`
     - cross-sectional area
     - :math:`A_\mathrm{circle} = \frac{\pi \cdot d}{4}` or :math:`A_\mathrm{rectangle} = h \cdot b`
   * - :math:`b`
     - width
     -
   * - :math:`b(z)`
     - width at a vertical position :math:`z`
     - Formula :math:numref:`eq:rectangle_width` in :ref:`theory.geometries`
   * - :math:`b_\mathrm{top}`
     - width at the top edge of a rectangle or trapezoid
     -
   * - :math:`b_\mathrm{bottom}`
     - width at the bottom edge of a rectangle or trapezoid
     -
   * - :math:`c_\mathrm{b}`
     - interception of the width of a rectangle or trapezoid
     - Formula :math:numref:`eq:rectangle_width_interception` in :ref:`theory.geometries`
   * - :math:`c_\mathrm{\sigma}`
     - interception of stress of linear relationship between two material points
     - Formula :math:numref:`eq:theory_section_stress_interception` in :ref:`theory.sections.sections.stress_distribution`
   * - :math:`d`
     - diameter of a reinforcement bar
     -
   * - :math:`E`
     - modulus of elasticity
     -
   * - :math:`E_\mathrm{a}`
     - modulus of elasticity of structural steel
     -
   * - :math:`E_\mathrm{cm}`
     - mean modulus of elasticity of concrete
     - Formula :math:numref:`eq:theory_materials_E_cm` in :ref:`theory.materials.concrete`
   * - :math:`E_\mathrm{s}`
     - modulus of elasticity of reinforcement steel
     -
   * - :math:`f_\mathrm{cm}`
     - mean concrete cylinder compressive strength
     - Formula :math:numref:`eq:theory_materials_f_cm` in :ref:`theory.materials.concrete`
   * - :math:`f_\mathrm{ck}`
     - characteristic concrete cylinder compressive strength
     -
   * - :math:`f_\mathrm{ctm}`
     - mean concrete tensile strength
     - Formula :math:numref:`eq:theory.materials.concrete_f_ctm` in :ref:`theory.materials.concrete`
   * - :math:`f_\mathrm{s}`
     - reinforcement yield strength
     -
   * - :math:`f_\mathrm{su}`
     - reinforcement tensile strength
     -
   * - :math:`f_\mathrm{y}`
     - steel yield strength
     -
   * - :math:`f_\mathrm{u}`
     - steel tensile strength
     -
   * - :math:`G_\mathrm{F}`
     - concrete fracture energy
     - Formula :math:numref:`eq:theory.materials.concrete_fracture_energy` in :ref:`theory.materials.concrete`
   * - :math:`I_\mathrm{y}`
     - second moment of area around the Y-Axis
     - :math:`I_\mathrm{y} = \frac{b \cdot h^{3}}{12}` for a rectangle of size :math:`b \cdot h`
   * - :math:`I_\mathrm{z}`
     - second moment of area around the Z-Axis
     - :math:`I_\mathrm{z} = \frac{b^{3} \cdot h}{12}` for a rectangle of size :math:`b \cdot h`
   * - :math:`M`
     - moment
     - :math:`M = N \cdot z`
   * - :math:`M_\mathrm{E}`
     - external moment
     -
   * - :math:`M_\mathrm{cs}`
     - moment of a cross-section under a given strain-distribution
     - Formula :math:numref:`eq:theory_crosssection_moment` in :ref:`theory.sections.cross_section`
   * - :math:`M_\mathrm{E}`
     - external moment occuring by loading of the beam
     -
   * - :math:`M_i`
     - moment of a sub-section under a given strain-distribution
     - Formula :math:numref:`eq:theory_section_moment` in :ref:`theory.sections.sections.moment`
     -
   * - :math:`M_\mathrm{R}`
     - resistance moment
     -
   * - :math:`m_\mathrm{b}`
     - slope of the width of a rectangle or trapezoid
     - Formula :math:numref:`eq:rectangle_width_slope` in :ref:`theory.geometries`
   * - :math:`m_\mathrm{\sigma}`
     - slope of stress from linear relationship between two points of stress-strain-curve
     - Formula :math:numref:`eq:theory_section_stress_slope` in :ref:`theory.sections.sections.stress_distribution`
   * - :math:`N`
     - axial force
     -
   * - :math:`N_\mathrm{cs}`
     - axial force of a cross-section under a given strain-distribution
     - Formula :math:numref:`eq:theory_crosssection_axial_force` in :ref:`theory.sections.cross_section`
   * - :math:`N_i`
     - axial force of a sub-section under a given strain-distribution
     - Formulas :math:numref:`eq:theory_section_axial_force_rectangle` and :math:numref:`eq:theory_section_axial_force_circle` in :ref:`theory.sections.sections.axial_force`
   * - :math:`P`
     - Transferred shear force by a shear connector
     -
   * - :math:`r_i`
     - lever arm of axial force :math:`N_i` of a sub-section under a given strain-distribution
     - Formulas :math:numref:`eq:theory_section_lever_arm_rectangle` and :math:numref:`eq:theory_section_lever_arm_circle` in :ref:`theory.sections.sections.lever_arm`
   * - :math:`s`
     - slip between two parts of a cross-section
     - see :ref:`theory.slip`
   * - :math:`x`
     - point along the beam (X-Axis)
     -
   * - :math:`y`
     - point at a distance perpendicular to :math:`x` in horizontal direction (Y-Axis)
     -
   * - :math:`z`
     - point at a distance perpendicular to :math:`x` in vertical direction (Z-Axis)
     -
   * - :math:`z_\mathrm{n}`
     - neutral axis as point in z-direction where strains are zero
     -
   * - :math:`z_\mathrm{top}`
     - vertical position of the top edge of a rectangle or trapezoid
     -
   * - :math:`z_\mathrm{bottom}`
     - vertical position of the bottom edge of a rectangle or trapezoid
     -
   * - :math:`w`
     - crack opening width of concrete
     - Formula :math:numref:`eq:theory.materials.concrete_crack_opening` in  :ref:`theory.materials.concrete`


Greek letters
=============

.. list-table::
   :widths: 20 40 40

   * - :math:`\varepsilon`
     - strain
     -
   * - :math:`\varepsilon_\mathrm{c}`
     - concrete strain
     -
   * - :math:`\varepsilon_\mathrm{c1}`
     - concrete strain at maximum stress
     - :ref:`theory.materials.concrete.compression.nonlinear`
   * - :math:`\varepsilon_\mathrm{cu1}`
     - concrete strain at failure
     - :ref:`theory.materials.concrete.compression.nonlinear`
   * - :math:`\varepsilon_\mathrm{c2}`
     - concrete strain at maximum stress
     - :ref:`theory.materials.concrete.compression.parabola`
   * - :math:`\varepsilon_\mathrm{cu2}`
     - concrete strain at failure
     - :ref:`theory.materials.concrete.compression.parabola`
   * - :math:`\varepsilon_\mathrm{c3}`
     - concrete strain at maximum stress
     - :ref:`theory.materials.concrete.compression.bi_linear`
   * - :math:`\varepsilon_\mathrm{cu3}`
     - concrete strain at failure
     - :ref:`theory.materials.concrete.compression.bi_linear`
   * - :math:`\kappa`
     - curvature
     - :math:`\kappa = \frac{1}{r} = \frac{M}{E \cdot I}`
   * - :math:`\kappa_\mathrm{fail}`
     - curvature at failure
     - see :ref:`theory.m_kappa.failure`
   * - :math:`\sigma`
     - stress
     -
   * - :math:`\sigma_\mathrm{a}`
     - steel stresses
     - Formula :math:numref:`eq:theory_materials_steel_bilinear` in :ref:`theory.materials.steel`
   * - :math:`\sigma_\mathrm{c}`
     - concrete stress under compression
     - Formulas :math:numref:`eq:theory.materials.concrete.compression.nonlinear`,
       :math:numref:`eq:theory.materials.concrete.compression.parabola`,
       :math:numref:`eq:theory.materials.concrete.compression.bi_linear` in  :ref:`theory.materials.concrete`
   * - :math:`\sigma_\mathrm{ct}`
     - concrete stress under tension
     - Formula :math:numref:`eq:theory.materials.concrete_tensile` in  :ref:`theory.materials.concrete`
   * - :math:`\sigma_\mathrm{s}`
     - reinforcement stresses
     -
   * - :math:`\sigma_\mathrm{\varepsilon}`
     - stress depending on strain :math:`\varepsilon`
     - Formula :math:numref:`eq:theory_material_line`