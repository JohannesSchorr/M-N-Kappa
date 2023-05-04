
from .crosssection import Crosssection
from .curves_m_kappa import MKappaCurvePoints, MKappaCurve
from .curves_m_n_kappa import MNKappaCurvePoints, MNKappaCurve
from .loading import ABCSingleSpan, SingleSpanSingleLoads
from .shearconnector import ShearConnector

from .log import LoggerMethods

log = LoggerMethods(__name__)


class Node:

    """
    Beam-Node

    .. versionadded:: 0.1.0

    stores the cross-section, the position_value in the beam and the computed M-Kappa-Curve
    """

    __slots__ = (
        "_cross_section",
        "_curve_points",
        "_position",
        "_number",
        "_consider_slip",
        "_shear_connector",
    )

    node_number: int = 0

    @log.init
    def __init__(
        self,
        cross_section: Crosssection,
        position: float,
        m_kappa_curve: MKappaCurvePoints | MNKappaCurvePoints = None,
    ):
        """
        Parameters
        ----------
        cross_section : :py:class:`~m_n_kappa.Crosssection`
            Cross-section at this node
        position : float
            position of the node along the beam
        m_kappa_curve : :py:class:`~m_n_kappa.curves_m_kappa.MKappaCurvePoints`
            if moment-curvature-curve has already been computed,
            then this may be passed here

        Examples
        --------
        For computation of a Node, first a :py:class.`~m_n_kappa.Crosssection` is needed.

        >>> from m_n_kappa import Concrete, Steel, Rectangle
        >>> concrete = Concrete(f_cm=35.0)
        >>> concrete_geometry_1 = Rectangle(
        ...     top_edge=0.0, bottom_edge=10.0, width=20.0)
        >>> concrete_section_1 = concrete + concrete_geometry_1
        >>> steel = Steel(f_y=355.0)
        >>> steel_geometry = Rectangle(
        ...     top_edge=10.0, bottom_edge=20.0, width=10.0)
        >>> steel_section = steel + steel_geometry
        >>> cross_section = concrete_section_1 + steel_section
        >>> cross_section
        Crosssection(sections=sections)

        The node is initialized by:

        >>> from m_n_kappa import Node
        >>> node = Node(cross_section=cross_section, position=0.0)

        During initialization the Moment-Curvature-Curve is computed.
        :py:meth:`~m_n_kappa.Node.curvature` allows us to determine the corresponding curvature
        to a given moment

        >>> node.curvature_by(moment=100)
        1.4443096916449083e-07

        For computation of the incremental deformation at this node use
        :py:meth:`~m_n_kappa.Node.incremental_deformation`.
        """
        self._cross_section = cross_section
        self._position = position
        if m_kappa_curve is None:
            self._curve_points = MKappaCurve(
                self.cross_section, include_positive_curvature=True
            ).m_kappa_points
        else:
            self._curve_points = m_kappa_curve
        Node.node_number += 1
        self._number = Node.node_number

    def __repr__(self):
        return f"Node(cross_section, position={self.position})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Node):
            if (
                self.cross_section == other.cross_section
                and self.curve_points == self.curve_points
            ):
                return True
        return False

    @property
    def cross_section(self) -> Crosssection:
        """:py:class:`Crosssection` at the node"""
        return self._cross_section

    @property
    def curve_points(self) -> MKappaCurvePoints | MNKappaCurvePoints:
        """computed Moment-Curvature-Curve at the node"""
        return self._curve_points

    @property
    def position(self) -> float:
        """position of the node along the beam"""
        return self._position

    @property
    def number(self) -> int:
        """number of the node"""
        return self._number

    def curvature_by(self, moment: float) -> float:
        """
        compute curvature

        Parameters
        ----------
        moment : float
             moment that is associated with the curvature

        Returns
        -------
        float
        """
        return self.curve_points.curvature(moment)

    def incremental_deformation(
        self, load: ABCSingleSpan, single_load: SingleSpanSingleLoads
    ) -> float:
        """
        determine incremental deformation at this node

        for the deformation the curvature and single-load-moment at the node under given loading
        are computed

        Parameters
        ----------
        load : :py:class:`~m_n_kappa.loading.ABCSingleSpan`
           load applied to the beam
        single_load : :py:class:`~m_n_kappa.SingleSpanSingleLoads`
            single-load applied at the point, where deformation is computed

        Returns
        -------
        float
            product from curvature and moment of the single-load at this node
        """
        moment = load.moment(self.position)
        curvature = self.curvature_by(moment)
        single_load_moment = single_load.moment(self.position)
        return curvature * single_load_moment


class CompositeNode(Node):

    """
    Beam-Node for Composite sections

    .. versionadded:: 0.2.0

    Composite section means that two parts of the overall cross-section
    are moving relatively to each other.
    For example in steel-concrete-composite-cross-sections a steel girder and the
    concrete slab are moving relatively to each other.
    """

    def __init__(
        self,
        cross_section: Crosssection,
        position: float,
        m_n_kappa_curve: MNKappaCurvePoints = None,
        shear_connectors: ShearConnector | list[ShearConnector] = None,
    ):
        """
        Parameters
        ----------
        cross_section : :py:class:`~m_n_kappa.Crosssection`
            Cross-section at this node
        position : float
            position of the node along the beam
        m_n_kappa_curve : :py:class:`~m_n_kappa.curves_m_n_kappa.MNKappaCurvePoints`
            if moment-axial-force-curvature-curve has already been computed,
            then this may be passed here
        shear_connectors : :py:class:`~m_n_kappa.ShearConnector` | list[:py:class:`~m_n_kappa.ShearConnector`]
            shear-connectors (Default: ``None``)
        """
        if m_n_kappa_curve is None:
            m_n_kappa_curve = MNKappaCurve(
                cross_section, include_positive_curvature=True
            ).points
        super().__init__(cross_section, position, m_n_kappa_curve)
        if isinstance(shear_connectors, ShearConnector):
            self._shear_connectors = [shear_connectors]
        elif isinstance(shear_connectors, list):
            self._shear_connectors = shear_connectors
        elif shear_connectors is None:
            self._shear_connectors = []
        else:
            raise ValueError(
                'Argument "shear_connectors must be of type ShearConnector or list[ShearConnector],'
                + f" is of type {type(shear_connectors)}"
            )

    @property
    def shear_connectors(self) -> list[ShearConnector]:
        """shear-connector(s) at this node"""
        return self._shear_connectors

    def shear_force(self, slip: float) -> float:
        """
        compute the shear-force transferred by the shear-connectors at this position

        Parameters
        ----------
        slip : float
            slip at this node

        Returns
        -------
        float
            shear-force transferred by the shear-connectors at this position under
            the given slip
        """
        sign = slip / abs(slip)
        slip = abs(slip)
        return sign * sum(
            (
                shear_connector.shear_load(slip)
                for shear_connector in self.shear_connectors
            )
        )

    def curvature_by(self, moment: float, axial_force: float) -> float:
        """
        compute curvature

        Parameters
        ----------
        moment : float
            moment that is associated with the curvature
        axial_force : float
            axial-force that is also associated with the searched curvature

        Returns
        -------
        float
            curvature by the moment and the axial_force
        """
        return self.curve_points.curvature(moment, axial_force)