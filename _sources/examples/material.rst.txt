.. _examples.material:

Creating materials
******************
The definition of an appropriate material-model is - beside the geometry - another basic component
for building a cross-section in :mod:`m_n_kappa`.
In succession it is crucial for a successful computation.

For steel-concrete composite structures :ref:`examples.material.concrete`, :ref:`examples.material.steel`
and :ref:`examples.material.reinforcement` are pre-defined materials you can use right away.
If these materials do not fit your needs.
No problem!
:ref:`You can create your own material <examples.material.create>`.


.. _examples.material.concrete:

Concrete
========
For creating :py:class:`~m_n_kappa.Concrete` you can choose between different material-models
under compression and under tension.

In any case you have to pass the mean concrete compressive strength ``f_cm`` to :py:class:`~m_n_kappa.Concrete`

**Under compression** you may decide if the stress-strain-relationship is ``Nonlinear``,
``Parabola``-Rectangle or ``Bilinear`` shaped.
This is controlled by argument ``compression_stress_strain_type``.
The default-value is ``compression_stress_strain_type='Nonlinear'``.

>>> from m_n_kappa import Concrete
>>> nonlinear_no_tension = Concrete(f_cm=30.0, use_tension=False)
>>> parabola_no_tension = Concrete(f_cm=30.0, use_tension=False,
...                                compression_stress_strain_type='Parabola')
>>> bilinear_no_tension = Concrete(f_cm=30.0, use_tension=False,
...                                compression_stress_strain_type='Bilinear')

.. grid:: 1 2 3 3

    .. grid-item::

      .. figure:: ../images/material_concrete_nonlinear-light.svg
         :class: only-light
      .. figure:: ../images/material_concrete_nonlinear-dark.svg
         :class: only-dark

         ``Nonlinear`` stress-strain-relationship of concrete under compression acc. EN 1992-1-1 (Default)

    .. grid-item::

      .. figure:: ../images/material_concrete_parabola_rectangle-light.svg
         :class: only-light
      .. figure:: ../images/material_concrete_parabola_rectangle-dark.svg
         :class: only-dark

         ``Parabola``-Rectangle stress-strain-relationship of concrete under compression acc. EN 1992-1-1

    .. grid-item::

      .. figure:: ../images/material_concrete_bilinear-light.svg
         :class: only-light
      .. figure:: ../images/material_concrete_bilinear-dark.svg
         :class: only-dark

         ``Bilinear`` stress-strain-relationship of concrete under compression acc. EN 1992-1-1

The behaviour **under tension** is first controlled by argument ``use_tension``.
In case ``use_tension`` is set to ``False`` no tensile capacity is defined, but a single stress-strain-point
(0.0 | 10.0) is applied.

>>> nonlinear_no_tension.tension.stress_strain()
[[0.0, 10.0]]

This value makes sure, that :mod:`m_n_kappa` does not stop computing if the concrete starts cracking
due exceeding the maximum tensile strain under tensile loading.

If you want to apply concrete tensile behaviour set ``use_tension=True``.
The tensile strength may be controlled by argument ``f_ctm``.
If not provided it may be computed using the given mean concrete compressive strength.

The tensile behaviour is controlled by argument ``tension_stress_strain_type``.
By default ``tension_stress_strain_type='Default'`` is set, that leads to an immediate drop of the stresses
after the maximum tensile stress has been reached.
In contrary ``tension_stress_strain_type='consider opening behaviour'``  leads to a post-breaking behaviour
as indicated in the following figure.

.. figure:: ../images/material_concrete_tension-light.svg
   :class: only-light
.. figure:: ../images/material_concrete_tension-dark.svg
   :class: only-dark

   Stress-strain-relationship of concrete under tension

.. seealso::
   :ref:`theory.materials.concrete`: Background how stress-strain relationships are computed


.. _examples.material.steel:

Steel
=====
The stress-strain behaviour of :py:class:`~m_n_kappa.Steel` is defined to be
`isotropic <https://en.wikipedia.org/wiki/Isotropy>`_.
In consequence it behaves under compression exactly like under tension.

In :py:class:`~m_n_kappa.Steel` is initialized without arguments pure elastic behaviour with modulus
of elasticity :math:`E_\mathrm{a}` defined as `E_a=210000.0` [N/mm²] utilizing
`Hooke's law <https://en.wikipedia.org/wiki/Hooke%27s_law`>_.
The maximum strain in this case is set to ``1.0``.

>>> from m_n_kappa import Steel
>>> elastic_steel = Steel()
>>> for point in elastic_steel.stress_strain:
...     print(point.stress, point.strain)
-210000.0 -1.0
-0.0 -0.0
210000.0 1.0

If you want to apply bi-linear ideal-plastic stress-strain behaviour of steel you must pass the yield strength
``f_y`` as well as the ``failure_strain`` to :py:class:`~m_n_kappa.Steel`.

>>> bilinear_steel = Steel(f_y=355, failure_strain=0.15)
>>> for point in bilinear_steel.stress_strain:
...     print(point.stress, round(point.strain, 4))
-355.0 -0.15
-355.0 -0.0017
-0.0 -0.0
355.0 0.0017
355.0 0.15

If additional harding shall be applied you only have to pass the tensile stress ``f_u`` to the
:py:class:`~m_n_kappa.Steel`.

>>> bilinear_hardening_steel = Steel(f_y=355, f_u=400, failure_strain=0.15)


.. grid:: 1 2 3 3

   .. grid-item::

      .. figure:: ../images/material_steel_elastic-light.svg
         :class: only-light
      .. figure:: ../images/material_steel_elastic-dark.svg
         :class: only-dark

         Elastic stress-strain-relationship of steel

   .. grid-item::

      .. figure:: ../images/material_steel_bilinear-light.svg
         :class: only-light
      .. figure:: ../images/material_steel_bilinear-dark.svg
         :class: only-dark

         Bi-linear stress-strain-relationship of steel

   .. grid-item::

      .. figure:: ../images/material_steel_trilinear-light.svg
         :class: only-light
      .. figure:: ../images/material_steel_trilinear-dark.svg
         :class: only-dark

         Bi-linear stress-strain-relationship with hardening of steel

.. _examples.material.reinforcement:

Reinforcement
=============
:py:class:`~m_n_kappa.Reinforcement` works similar as :py:class:`~m_n_kappa.Steel`, but the arguments switch as follows:

- ``f_s``: yield strength
- ``f_su``: tensile strength
- ``E_s``: modulus of elasticity

The following code therefore describes bi-linear behaviour of the reinforcement with hardening.
Linear-elastic and ideal-plastic behaviour are of course also possible.
`Isotropy <https://en.wikipedia.org/wiki/Isotropy>`_ applies similarly to :py:class:`~m_n_kappa.Steel`.

>>> from m_n_kappa import Reinforcement
>>> reinforcement = Reinforcement(f_s=500.0, f_su=550.0, failure_strain=0.25)


.. _examples.material.create:

Nothing found for your needs? Create your own material!
=======================================================
.. note::
   You should have a basic understanding of `python classes <https://docs.python.org/3/tutorial/classes.html>`_
   to create your own material.

All materials you create must fulfil the following requirements to have the full functionality for computation
in :mod:`m_n_kappa`:

- inherit from :py:class:`~m_n_kappa.Material`
- feeding the ``_stress_strain``-Attribute with a list of :py:class:`~m_n_kappa.material.StressStrain`.

Beside its functionality for computation the inheritance from :py:class:`~m_n_kappa.Material` is also needed to merge
your material with geometric instances to a :py:class:`~m_n_kappa.Section` (see :ref:`examples.section`).

The following example creates a new material called ``Arbitrary``.

.. testcode::

    from m_n_kappa.material import Material, StressStrain

    class Arbitrary(Material):

        """arbitrary material"""

        def __init__(self):
            self._stress_strain = [
                StressStrain(stress=-10.0, strain=-0.001),
                StressStrain(stress=0.0, strain=0.0),
                StressStrain(stress=10.0, strain=0.001),
                StressStrain(stress=10.0, strain=0.01),
            ]

        @property
        def section_type(self):
            return "girder"

Of course, you can produce the stress-strain-relationship programmatically i.e. by using models
from literature.

.. important::
   Please be aware that :mod:`m_n_kappa` is not able to compute strains that exceed the maximum strain
   or fall below the minium strain of a material model. See also :ref:`examples.material.concrete`.

If you implemented your :py:class:`~m_n_kappa.Material` successfully, please consider
:ref:`contributing` it to help others.