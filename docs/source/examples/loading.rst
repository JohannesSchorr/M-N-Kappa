.. _examples.loading:

Loading
*******

*Units: Millimeter [mm], Newton [N]*

.. altair-plot::
   :output: None
   :hide-code:

   # configuration of altair-plot
   import altair as alt
   alt.themes.enable('quartz')

.. _examples.loading.singlespan_intro:

Introduction
============

For computing deformations the loading of a beam is crucial.
Therefore, :mod:`m_n_kappa` provides currently two functions to compute the stress resultants
of single-span girders.

.. _examples.loading.singlespan_singleloads:

Single Loads
============

For computation of the stress-resultants of a single-span beam first at leas one
:py:class:`~m_n_kappa.SingleLoad` must be defined.
This :py:class:`~m_n_kappa.SingleLoad` defines the position of the load along the beam as
well as its value.
Here, :py:class:`~m_n_kappa.SingleLoad` is defined at 4000 mm, what applies to the middle of the beam.
But every other position within the beam-span (0 mm < :math:`L` < 8000 mm) is possible.

This :py:class:`~m_n_kappa.SingleLoad` (i.e. ``load_1``) is passed to :py:class:`~m_n_kappa.SingleSpanSingleLoads`
in a list, together with the ``length`` of the beam.

:py:meth:`~m_n_kappa.SingleSpanSingleLoads.maximum_moment` computes then the maximum Moment.

>>> from m_n_kappa import SingleSpanSingleLoads, SingleLoad
>>> load_1 = SingleLoad(position_in_beam=4000, value=10)
>>> single = SingleSpanSingleLoads(length=8000, loads=[load_1])
>>> single.maximum_moment
20000.0

The transversal shear at the supports is given by
:py:meth:`~m_n_kappa.SingleSpanSingleLoads.transversal_shear_support_left` for the left support and
:py:meth:`~m_n_kappa.SingleSpanSingleLoads.transversal_shear_support_right` for the right support.

>>> single.transversal_shear_support_left, single.transversal_shear_support_right
(5.0, -5.0)

The summarized loading is given by :py:meth:`~m_n_kappa.SingleSpanSingleLoads.loading`.

>>> single.loading
10

Of course, the moment may be computed at every position along the beam.

>>> single.moment(at_position=2000)
10000.0

As well as the transversal shear.

>>> single.transversal_shear(at_position=2000)
5.0

This allows to compute the course of the moment over the length of the beam.

.. altair-plot::
   :output: None
   :hide-code:

   from m_n_kappa import SingleSpanSingleLoads, SingleLoad
   load_1 = SingleLoad(position_in_beam=4000, value=10)
   single = SingleSpanSingleLoads(length=8000, loads=[load_1])

.. altair-plot::
   :alt: Moment along the beam from single load positioned in the middle

   import pandas as pd
   import altair as alt

   positions = [index*100 for index in range(0, 81, 1)]
   moments = [single.moment(at_position=position) for position in positions]

   df_moments = pd.DataFrame({'moments': moments, 'positions': positions})

   alt.Chart(df_moments, height=100.0, background='#00000000').mark_line().encode(
      x=alt.X('positions', title='Position [mm]'),
      y=alt.Y('moments', title='Moment [Nmm]', scale=alt.Scale(reverse=True)))

As well as the transversal shear over the length of the beam.

.. altair-plot::
   :alt: Transversal shear over the length of the beam

   shear = [single.transversal_shear(at_position=position) for position in positions]

   df_shear = pd.DataFrame({'shear': shear, 'positions':  positions})

   alt.Chart(df_shear, height=100.0, background='#00000000').mark_line().encode(
      x=alt.X('positions', title='Position [mm]'),
      y=alt.Y('shear', title='Transversal shear [N]'))

:py:class:`~m_n_kappa.SingleSpanSingleLoads` accepts more than one :py:class:`~m_n_kappa.SingleLoad` as
``load``-argument.
Therefore, more complicated load-scenarios are possible as only a single load.

.. _examples.loading.singlespan_uniformloading:

Uniform loading
===============

The :py:class:`~m_n_kappa.SingleSpanUniformLoad` class follows a similar procedure as
:py:class:`~m_n_kappa.SingleSpanSingleLoads`, but no definition of :py:class:`~m_n_kappa.SingleLoad`
is needed.
The ``load`` is passed directly as argument to the class also with the ``length`` of the beam.

The maximum moment is then given by :py:class:`~m_n_kappa.SingleSpanUniformLoad.maximum_moment`

>>> from m_n_kappa import SingleSpanUniformLoad
>>> uniform = SingleSpanUniformLoad(length=8000, load=10.0)
>>> uniform.maximum_moment
80000000.0

Transversal shear at the support is given by :py:class:`~m_n_kappa.SingleSpanUniformLoad.transversal_shear_support_left`
and :py:class:`~m_n_kappa.SingleSpanUniformLoad.transversal_shear_support_right`.

>>> uniform.transversal_shear_support_left, uniform.transversal_shear_support_right
(40000.0, -40000.0)

The summarized loading is given as follows.

>>> uniform.loading
80000.0

Whereas, the moment is computed by :py:class:`~m_n_kappa.SingleSpanUniformLoad.moment` passing the position
where the moment needs to be obtained.

>>> uniform.moment(at_position=2000)
60000000.0

Similarly for transversal shear using :py:class:`~m_n_kappa.SingleSpanUniformLoad.transversal_shear`, what applies
to ``0.0`` in case of uniformly loaded beam.

>>> uniform.transversal_shear(at_position=4000)
0.0

:py:class:`~m_n_kappa.SingleSpanUniformLoad.moment` allows to plot the moment along the beam.

.. altair-plot::
   :output: None
   :hide-code:

   from m_n_kappa import SingleSpanUniformLoad
   uniform = SingleSpanUniformLoad(length=8000, load=10.0)

.. altair-plot::

   import pandas as pd
   import altair as alt

   positions = [index*100 for index in range(0, 81, 1)]
   moments = [uniform.moment(at_position=position)*0.001*0.001 for position in positions]

   df_moments = pd.DataFrame({'moments': moments, 'positions': positions})

   alt.Chart(df_moments, height=100.0, background='#00000000').mark_line().encode(
      x=alt.X('positions', title='Position [mm]'),
      y=alt.Y('moments', title='Moment [kNm]', scale=alt.Scale(reverse=True)))


And the transversal shear is given as follows.

.. altair-plot::

   shear = [uniform.transversal_shear(at_position=position) for position in positions]

   df_shear = pd.DataFrame({'shear': shear, 'positions': positions})

   alt.Chart(df_shear, height=100.0, background='#00000000').mark_line().encode(
      x=alt.X('positions', title='Position [mm]'),
      y=alt.Y('shear', title='Transversal shear [N]'))


.. seealso::
   :ref:`theory.loading` : Theory to the given functions

The :py:class:`~m_n_kappa.SingleSpan` class has :py:class:`~m_n_kappa.SingleSpanSingleLoads`
and :py:class:`~m_n_kappa.SingleSpanUniformLoad` implemented.

The invoked class depends on the argument that is passed.
In case ``loads`` is passed, then :py:class:`~m_n_kappa.SingleSpanSingleLoads` is initialized.
:py:class:`~m_n_kappa.SingleSpanUniformLoad` is initialized in case ``uniform_load`` is passed.
In each case the ``length`` of the beam must be passed.

>>> from m_n_kappa import SingleSpan
>>> single = SingleSpan(length=8000, loads=[load_1])
>>> uniform = SingleSpan(length=8000, uniform_load=10)
>>> single.maximum_moment, uniform.maximum_moment
(20000.0, 80000000.0)
