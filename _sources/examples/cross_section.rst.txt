.. _examples.cross_section:

Build a cross-section
*********************
You can imagine a cross-section to be build of a number of :py:class:`~m_n_kappa.Section`.
Each Section is constructed by a :py:class:`~m_n_kappa.geometry.Geometry` and a
:py:class:`~m_n_kappa.Material`.

.. figure:: ../images/example_cross_section-dark.svg
   :class: only-dark
.. figure:: ../images/example_cross_section-light.svg
   :class: only-light

   Structure of a cross-section

If you want to create a cross-section in :mod:`m_n_kappa` you create first at least one
:py:class:`~m_n_kappa.Section`.

>>> from m_n_kappa import Concrete, Steel, Rectangle
>>> concrete = Concrete(f_cm=35.0)
>>> concrete_geometry_1 = Rectangle(
...     top_edge=0.0, bottom_edge=10.0, width=10.0, left_edge=-10.0)
>>> concrete_section_1 = concrete + concrete_geometry_1
>>> steel = Steel()
>>> steel_geometry = Rectangle(
...     top_edge=10.0, bottom_edge=20.0, width=10.0)
>>> steel_section = steel + steel_geometry

An then the cross-section is created as follows.

>>> cross_section_1 = steel_section + concrete_section_1
>>> cross_section_1
Crosssection(sections=sections)

Or you you use :py:class:`~m_n_kappa.Crosssection` as an import from :mod:`m_n_kappa`.

>>> from m_n_kappa import Crosssection
>>> sections_list = [steel_section, concrete_section_1]
>>> cross_section_2 = Crosssection(sections=sections_list)
>>> cross_section_2
Crosssection(sections=sections)

Both procedures lead to a similar result.

>>> cross_section_1 == cross_section_2
True

If you have a predefined :py:class:`~m_n_kappa.geometry.ComposedGeometry`, like
:py:class:`~m_n_kappa.IProfile`, :py:class:`~m_n_kappa.UPEProfile` or :py:class:`~m_n_kappa.RebarLayer`
it is done similarly.

>>> from m_n_kappa import IProfile
>>> i_profile = IProfile(top_edge=0.0, b_fo=200, t_fo=15, h_w=200-2*15, t_w=9.5)
>>> cross_section_3 = i_profile + steel
>>> cross_section_3
Crosssection(sections=sections)

.. seealso::
   :ref:`cross_section_template`: here you can find a variety of templates for characteristic cross-sections

The cross-section forms the basis for all further operations, like computation of
:ref:`a single moment-curvature-point <examples.moment_curvature>`,
:ref:`examples.moment_curvature_curve` or the :ref:`deformation of a beam <examples.deformation>`.