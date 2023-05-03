# ---
"""
fitting.py

provide methods fit result of the slip-distribution to a given moment
"""
from typing import Callable
from .matrices import Vector, Jacobian, LinearEquationsSystem
from .general import NotSuccessfulReason

from .log import LoggerMethods

log = LoggerMethods(__name__)


class GaussNewton:

    """
    Gauss-Newton Solver for finding zero in a system of equations

    .. versionadded:: 0.2.0

    """

    __slots__ = (
        "_f_i",
        "_x_0",
        "_maximum_iterations",
        "_tolerance",
        "_x_i",
        "_iteration",
        "_f_x",
        "_residuum",
        "_successful",
        "_not_successful_reason",
        "_max_line_search_iterations",
        "_minimum_residuum_change",
    )

    @log.init
    def __init__(
        self,
        f_i: list[Callable],
        x_0: list[float],
        maximum_iterations: int = 20,
        tolerance: float = 0.1,
        max_line_search_iterations: int = 10,
        minimum_residuum_change: float = 0.000000001,
    ):
        """
        Parameters
        ----------
        f_i : list[Callable]
            Number of methods representing a system of equations.
            Each method must ...

            - ... accept a ``list[float]`` that is in size equal to
              :py:attr:`~m_n_kappa.fitting.GaussNewton.x_0`.
            - ... be of the form f(x) = 0

        x_0 : list[float]
            starting-values for the iteration
        maximum_iterations : int
            maximum number of iterations (must be greater zero, Default: 20)
        tolerance : float
            tolerance-limit, must be greater zero (Default: 1.0).
        max_line_search_iterations : int
            maximum nuumber of line-search iterations (Default: 10)

        Notes
        -----
        The result of a Gauss-Newton iteration step is given as follows.

        .. math::

           \\vec{x}_{n+1} = \\vec{x}_{n} - \\alpha_{n} \\Delta \\vec{x}_{n}

        where :math:`\\vec{x}_{n}` is the result of the previous iteration step.
        The Index :math:`n` stands for the current iteration-number.
        \\alpha_{n} is a `line search <https://en.wikipedia.org/wiki/Line_search>`_
        parameter, making sure that the result of the current step :math:`f(x_{n})`
        is smaller than the result of the previous step.

        :math:`\\Delta \\vec{x}_{n}` indicates the difference between the current and
        the next iteration-step :math:`\\vec{x}_{n+1}`.
        It is given as follows.

        .. math::

           \\Delta \\vec{x}_{n} = -(\\mathbf{J}^T \\mathbf{J})^{-1} \\mathbf{J}^T f(x_{n})

        where :math:`\\mathbf{J}` is the
        `Jacobian Matrix <https://en.wikipedia.org/wiki/Jacobian_matrix_and_determinant>`_
        at the current point :math:`\\vec{x}_{n}`.

        :math:`\\Delta \\vec{x}_{n}` is found by bringing the formula in the form
        :math:`Ax = b` and solved applying
        `QR decomposition <https://en.wikipedia.org/wiki/QR_decomposition>`_.

        .. math::

           A \\Delta \\vec{x}_{n} & = b

           (\\mathbf{J}^T \\mathbf{J})^{-1} \\Delta \\vec{x}_{n} & = - \\mathbf{J}^T f(x_{n})

        As the Gauss-Newton algorithm finds only local minimums the initial values
        :math:`\\vec{x_{0}}` must be chosen appropriatly.

        Examples
        --------

        The `Rosenbrock function <https://en.wikipedia.org/wiki/Rosenbrock_function>`_
        is a performance test problem for optimization algorithms.
        It is defined as follows:

        .. math::

           f(x, y) = (a - x)^{2} + b(y - x^{2})^{2}

        Usually the constants are defined as :math:`a = 1`, :math:`b = 100`.
        Given these constants the optimum applies to :math:`\\vec{x} = [1, 1]^{T}`.

        For sueing the Gauss-Newton algorithm the Rosenbrock function :math:`f(x, y)`
        must be reshaped as follows:

        .. math::

           \\begin{pmatrix} f_{1}(x) \\\\ f_{2}(x) \\end{pmatrix} =
           \\begin{bmatrix} \\sqrt{2}(a - x_{1}) \\\\ \\sqrt{2b}(x_{2} - x_{1}^{2} \\end{bmatrix}

        To pass this system of linear equations to :py:class:`~m_n_kappa.fitting.GaussNewton`
        these functions need to be defined taking :math:`x_{1}` and :math:`x_{2}` as arguments
        wrapped by a ``list``.

        >>> def f_1(variables: list[float, float]):
        ...    x_1, x_2 = variables
        ...    return 2.0**0.5*(1.0 - x_1)
        >>> def f_2(variables: list[float, float]):
        ...    x_1, x_2 = variables
        ...    return (2.0*100.0)**0.5*(x_2 - x_1**2.0)
        >>> rosenbrock = [f_1, f_2]


        Furthermore, an initial guess of the result must be given.
        It denotes normally to :math:`\\vec{x}_{0} = [0, -0.1]^{T}`.

        >>> x_0 = [0.0, -0.1]

        >>> from m_n_kappa.fitting import GaussNewton
        >>> gauss_newton = GaussNewton(f_i=rosenbrock, x_0=x_0)

        The result is computed by initializing :py:class:`~m_n_kappa.fitting.GaussNewton`.
        The attribute :py:attr:`~m_n_kappa.fitting.GaussNewton.successful` indicates if a
        result is available.

        >>> gauss_newton.successful
        True

        In that case the result may be obtained as follows.

        >>> gauss_newton.x_i
        Vector([1.0, 1.0])

        What is the optimal result as indicated above.
        """
        self._f_i = f_i
        self._x_0 = x_0
        self._maximum_iterations = maximum_iterations
        self._tolerance = tolerance
        self._max_line_search_iterations = max_line_search_iterations
        self._minimum_residuum_change = minimum_residuum_change
        self._x_i = [Vector(self._x_0)]
        self._iteration = 0
        self._f_x = [self._substituting(self._x_i[-1])]
        self._residuum = [self.f_x.norm()]
        self._successful = False
        self._not_successful_reason = None
        self._compute()

    def __repr__(self) -> str:
        return f"GaussNewton(f_i=[{len(self._f_i)} functions given], x_0={self._x_0})"

    @property
    def f_i(self) -> list[Callable]:
        """Number of methods representing a system of equations"""
        return self._f_i

    @property
    def x_0(self) -> list[float]:
        """starting-values for the iteration"""
        return self._x_0

    @property
    def x_i(self) -> Vector:
        """computed variables at iteration-step :math:`i`"""
        return self._x_i[-1]

    @property
    def f_x(self) -> Vector:
        """Most recent result of the iterations"""
        return self._f_x[-1]

    @property
    def tolerance(self) -> float:
        """tolerance-limit"""
        return self._tolerance

    @property
    def maximum_iterations(self) -> int:
        """maximum number of iterations"""
        return self._maximum_iterations

    @property
    def minimum_residuum_change(self) -> float:

        return self._minimum_residuum_change

    @property
    def successful(self) -> bool:
        """indicates the success of the computation"""
        return self._successful

    @property
    def not_successful_reason(self) -> None | NotSuccessfulReason:
        """
        gives a reason if the computation was not successful

        Returns
        -------
        None | :py:class:`~m_n_kappa.general.NotSuccessfulReason`
            Reason why computation was not successful
        """
        return self._not_successful_reason

    @property
    def iteration(self) -> int:
        """current iteration"""
        return self._iteration

    @property
    def max_line_search_iterations(self) -> int:
        """maximum number of iterations during the line-search"""
        return self._max_line_search_iterations

    def _compute(self) -> None:
        """conducts the iteration process"""
        for _ in range(self.maximum_iterations):
            self._iterate()
            if self._is_residuum_smaller_tolerance():
                self._successful = True
                return
            elif self._residuum_has_not_changed():

                self._successful = True
                return
        self._not_successful_reason = NotSuccessfulReason(
            reason="Succeeded the maximum number of iterations"
        )
        log.warning(
            f"Not Successful: {self.not_successful_reason}, Residuum={self._residuum[-1]}"
        )

    def _residuum_has_not_changed(self) -> bool:
        """
        Control the change of the residuum. 
        
        In case the change of the residuum is minimal it is assumed 
        that the further iterations will not improve the result significantly. 
        To reduce computation time the iterations will be stopped.
        
        For example the case when the more equations than variables are given (over-fitting).
        """
        residuum_change = abs(self._residuum[-1] - self._residuum[-2])
        if residuum_change < self.minimum_residuum_change:
            log.info(
                f"Iteration stopped due to minor change of residuum ({residuum_change=})"
            )
            return True
        else:
            return False

    def _iterate(self) -> None:
        """
        conducts one iteration (full process)
        """
        self._iteration += 1
        log.info(f"Iteration: {self.iteration}")
        jacobian = Jacobian(self.f_i, self.x_i, self.f_x)
        A = jacobian.transpose()
        A = A.multiply_by(jacobian)
        b = jacobian.transpose()
        b = b.multiply_by(self.f_x)
        les = LinearEquationsSystem(coefficients=A, constants=b)
        delta_x = les.solve()
        log.debug(f"{delta_x=}")
        self._line_search(delta_x)

    def _line_search(self, delta_x: Vector) -> None:
        """
        Line-Search

        Forces the result of
        :math:`\\vec{x}_{n+1} = \\vec{x}_{n} - \\alpha_{n} \\Delta \\vec{x}_{n}`
        being nearer to the optimum than the previous result.

        At the beginning of the iteration step the step-size is :math:`\\alpha_{n} = 1.0`
        In case :math:`\\vec{x}_{n+1}` does not lead to to :math:`f(x_{n+1}) < f(x_{n})`, i.e.
        that the result is nearer to the optimum, then :math:`\\alpha_{n}` is
        multiplied by :math:`0.5`.
        The bisection of the step-size :math:`\\alpha_{n}` is repeated until
        :math:`f(x_{n+1}) < f(x_{n})` is fulfilled.

        Parameters
        ----------
        delta_x : Vector
            Computed difference between the current and the next
            iteration step.

        Returns
        -------
        None
        """
        log.info("Start Line-Search")
        step_size = 1.0
        for _ in range(self.max_line_search_iterations):
            x_i_plus_1 = self.x_i - delta_x.multiply_scalar(step_size)
            f_x = self._substituting(x_i_plus_1)
            residuum = f_x.norm()
            if residuum > self._residuum[-1]:
                step_size = step_size * 0.5
                log.debug(
                    f"Line-Search: reduce step-size: -> {2.*step_size} * 0.5 = {step_size}"
                )
            else:
                self._x_i.append(x_i_plus_1)
                self._f_x.append(f_x)
                self._residuum.append(residuum)
                log.info(f"Line-Search: successful with step-size = {step_size}")
                log.info(f"{x_i_plus_1=},\n\t{residuum=}")
                break

    def _is_residuum_smaller_tolerance(self) -> bool:
        """check if residuum is smaller than the given tolerance"""
        if self._residuum[-1] < self.tolerance:
            return True
        else:
            return False

    @log.result
    def _residuals(self) -> float:
        """computes the residuals of the current computation"""
        return sum((x**2.0 for x in self.f_x.entries))

    @log.result
    def _substituting(self, x: Vector) -> Vector:
        """
        substituting variables ``x`` into the list of functions
        given in :py:attr:`~m_n_kappa.fitting.GaussNewton.f_i`

        Parameters
        ----------
        x : list[float]
            variable

        Returns
        -------
        Vector
            Result of substituting ``x`` in the given functions.
        """
        return Vector([equation(x.entries) for equation in self.f_i])
