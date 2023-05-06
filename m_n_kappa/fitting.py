# ---
"""
fitting.py

provide methods fit result of the slip-distribution to a given moment
"""
from typing import Callable
from collections import Counter
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
        "_line_search_step_size", 
        "_exceptions_to_catch"
    )

    @log.init
    def __init__(
        self,
        f_i: list[Callable],
        x_0: list[float],
        maximum_iterations: int = 20,
        tolerance: float = 0.1,
        max_line_search_iterations: int = 100,
        minimum_residuum_change: float = 0.000000001,
        exceptions_to_catch: tuple[Exception] | Exception = IndexError, 
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
            maximum nuumber of line-search iterations (Default: 100)
        minimum_residuum_change : float
            Iteration stops in case the residuum changes less than the given value
            (Default: 0.000000001)
        exceptions_to_catch : tuple[Exception] | Exception
            Exceptions that may arise during a run of the problem and that 
            must be caught (Default: IndexError)

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
        self._exceptions_to_catch = exceptions_to_catch
        self._line_search_step_size = 1.0
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
        """boundary condition regarding the minimum residuum"""
        return self._minimum_residuum_change

    @property
    def successful(self) -> bool:
        """indicates the success of the computation"""
        return self._successful
    
    @property
    def line_search_step_size(self) -> float:
        """current step-size of the line-search"""
        return self._line_search_step_size

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
            elif self._residuum_has_not_changed() and self.iteration > 1:
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
                f"Iteration stopped due to minor change of residuum ({residuum_change=}, residuum={self._residuum[-1]})"
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
        delta_x = self._compute_delta_x()
        self._line_search(delta_x)

    def _compute_delta_x(self) -> Vector:
        """
        Compute the new delta of x_i

        delta-x describes the difference between the current
        and the previous iteration-step.

        Returns
        -------
        Vector
            newly computed delta-x
        """
        jacobian = Jacobian(self.f_i, self.x_i, self.f_x)
        A = jacobian.transpose()
        A = A.multiply_by(jacobian)
        b = jacobian.transpose()
        b = b.multiply_by(self.f_x)
        delta_x = LinearEquationsSystem(coefficients=A, constants=b).solve()
        log.info(f"{delta_x=}")
        return delta_x

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
        self._line_search_step_size = 1.0
        for _ in range(self.max_line_search_iterations):
            x_i_plus_1 = self.x_i - delta_x.multiply_scalar(self.line_search_step_size)
            try:
                f_x = self._substituting(x_i_plus_1)
            except self._exceptions_to_catch:
                self._reduce_line_search_step_size()
                continue

            residuum = f_x.norm()
            if residuum > self._residuum[-1]:
                self._reduce_line_search_step_size()
            else:
                self._x_i.append(x_i_plus_1)
                self._f_x.append(f_x)
                self._residuum.append(residuum)
                log.info(f"Line-Search: successful with step-size = {self.line_search_step_size}")
                log.info(f"{x_i_plus_1=},\n\t{residuum=}")
                return
        log.warning(
            f"Line-search-algorithm reached the maximum number of line-search-iterations "
            f"(={self._max_line_search_iterations})"
        )
        
    def _reduce_line_search_step_size(self):
        """halfs the step-size of the line-search algorithm"""
        self._line_search_step_size = self.line_search_step_size * 0.5
        log.debug(
            f"Line-Search: reduce step-size: -> {2. * self.line_search_step_size} * 0.5"
            f" = {self.line_search_step_size}"
        )

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


class LevenbergMarquardt(GaussNewton):

    """ 
    Levenberg-Marquardt algorithm
    
    .. versionadded:: 0.2.0
    
    Enhances the :py:class:`~m_n_kappa.fitting.GaussNewton` algorithm, 
    especially in cases when the starting-conditions are poor. 
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
        "_line_search_step_size",
        "_exceptions_to_catch",
        "_damping_factor"
    )
    
    @log.init
    def __init__(
        self,
        f_i: list[Callable],
        x_0: list[float],
        maximum_iterations: int = 100,
        tolerance: float = 0.1,
        max_line_search_iterations: int = 100,
        minimum_residuum_change: float = 0.000000001,
        initial_damping_factor: float = 1.0,
        exceptions_to_catch: tuple | Exception = IndexError,
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
            maximum nuumber of line-search iterations (Default: 100)
        minimum_residuum_change : float
            Iteration stops in case the residuum changes less than the given value
            (Default: 0.000000001)
        exceptions_to_catch : tuple[Exception] | Exception
            Exceptions that may arise during a run of the problem and that 
            must be caught (Default: IndexError)
            
        Notes
        -----
        To enhance the :py:class:`~m_n_kappa.fitting.GaussNewton` algorithm the 
        damping-factor :math:`\\lambda \\cdot diag(\\mathbf{J}^T \\mathbf{J})` is 
        added to :math:`\\Delta \\vec{x}_{n}`. 
        The full problem to solve by the Levenberg-Marquardt algorithm is then given as follows. 
        
        .. math::

           A \\Delta \\vec{x}_{n} & = b

           \\left[\\mathbf{J}^T \\mathbf{J})^{-1} + \\lambda^{2} \\cdot diag(\\mathbf{J}^T \\mathbf{J}) \\right]
           \\Delta \\vec{x}_{n} & = - \\mathbf{J}^T f(x_{n})
        
        where :math:`\\lambda`` is a factor increasing the dumping factor.
        :math:`diag(\\mathbf{J}^T \\mathbf{J})` describes the 
        `main diagonal <https://en.wikipedia.org/wiki/Main_diagonal>`_ of :math:`\\mathbf{J}^T \\mathbf{J}`. 
        
        :math:`diag(\\mathbf{J}^T \\mathbf{J})` allows that the damping-factor scales with 
        the `Jacobian Matrix <https://en.wikipedia.org/wiki/Jacobian_matrix_and_determinant>`_ 
        :math:`\\mathbf{J}` and makes sure that proportions between damping-factor
        and rest of the problem are kept (see *Fletcher (1971)*).
         
        Factor :math:`\\lambda`` is initially chosen by the user and adapted during the iterative process
        depending on the step-size of the line-search :math:`\\alpha_\\mathrm{n}`` in the previous iteration.
        
        - :math:`\\alpha_\\mathrm{n} < 0.1``: :math:`\\lambda_{n+1} = 2.0 \\cdot \\lambda_{n}`` 
          if :math:`\\lambda_{n} > 1.0`` or :math:`\\lambda_{n+1} = 2.0`` if :math:`\\lambda_{n} \\leq 1.0``
        - :math:`\\alpha_\\mathrm{n} = 1.0``: :math:`\\lambda_{n+1} = 0.5 \\cdot \\lambda_{n}``
        
        With increasing damping-factor the method moves from a
        `Gauss-Newton algorithm <https://en.wikipedia.org/wiki/Gauss%E2%80%93Newton_algorithm>`_
        to a method of `gradient descent <https://en.wikipedia.org/wiki/Gradient_descent>`_. 
        
        References
        ----------
        - Marquardt, D. W. (1963). An algorithm for least-squares estimation of nonlinear parameters. 
          Journal of the society for Industrial and Applied Mathematics, 11(2), 431-441. 
        - Fletcher, R. (1971) A modified Marquardt subroutine for non-linear least squares, 
          report, Theoretical Physics Division, Atomic Energy Research Establishement, Harwell, Berkshire
        """
        self._damping_factor = initial_damping_factor
        super().__init__(
            f_i=f_i,
            x_0=x_0,
            maximum_iterations=maximum_iterations,
            tolerance=tolerance,
            max_line_search_iterations=max_line_search_iterations,
            minimum_residuum_change=minimum_residuum_change,
            exceptions_to_catch=exceptions_to_catch,
        )

    @property
    def damping_factor(self) -> float:
        """Damping factor"""
        return self._damping_factor

    def _compute_delta_x(self) -> Vector:
        """
        Compute the new delta of x_i

        delta-x describes the difference between the current
        and the previous iteration-step.

        Returns
        -------
        Vector
            newly computed delta-x
        """
        jacobian = Jacobian(self.f_i, self.x_i, self.f_x)
        A = jacobian.transpose()
        A = A.multiply_by(jacobian)
        damping_factor = self.damping_factor**2.0
        damping_matrix = A.diagonal()
        damping_matrix = damping_matrix.multiply_by(damping_factor)
        A = A + damping_matrix
        b = jacobian.transpose()
        b = b.multiply_by(self.f_x)
        delta_x = LinearEquationsSystem(coefficients=A, constants=b).solve()
        log.info(f"{delta_x=}")
        return delta_x

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
            self._update_damping_factor()
        self._not_successful_reason = NotSuccessfulReason(
            reason="Succeeded the maximum number of iterations"
        )
        log.warning(
            f"Not Successful: {self.not_successful_reason}, Residuum={self._residuum[-1]}"
        )
        
    def _update_damping_factor(self) -> None:
        """
        Update of the damping-factor depending on the step-size
        of the line-search algorithm.
        
        The step-size of the line-search-algorithm of the previous iteration step
        is used as indicator for adapting the damping-factor: 
        
        - line-search step-size <= 0.1: double damping-factor if damping-factor is greater 1.0 or 
          set damping-factor to 2.0 in case it is smaller 1.0
        - line-search step-size = 1.0: half damping-factor
        
        Reducing the damping-factor moves method to Gauss-Newton algorithm. 
        Increasing the damping-factor moves method in direction of Gradient-descent.
        """
        if self.line_search_step_size <= 0.1:
            if self._damping_factor > 1.0: 
                self._damping_factor = self.damping_factor * 2.0
                log.info(
                    f"Damping-factor: increased by factor 2.0 = {self.damping_factor}"
                )
            else:
                self._damping_factor = 2.0
                log.info(
                    f"Damping-factor: set to {self.damping_factor}"
                )
        elif self.line_search_step_size == 1.0:
            self._damping_factor = self.damping_factor * 0.5
            log.info(
                f"Damping-factor: decreased by factor 0.5 = {self.damping_factor}"
            )
            
    def _residuum_has_not_changed(self) -> bool:
        """
        Control the change of the residuum.

        In case the change of the residuum is minimal it is assumed
        that the further iterations will not improve the result significantly.
        To reduce computation time the iterations will be stopped.

        For example the case when the more equations than variables are given (over-fitting).
        """
        residuum_counter = Counter(self._residuum)[self._residuum[-1]]
        if residuum_counter == 5:
            log.info(
                f"Iteration stopped as residuum has not changed for {residuum_counter} iterations."
                f'{self.info()}'
            )
            return True
        else:
            return False
        
    def info(self) -> str:
        """
        print info regarding iterations
        """
        message = [
            "\t\nComputation-Info", 
            "----------------", 
            f'damping-factor: {self.damping_factor}', 
            f'results: {self.f_x}', 
            f'variables: {self.x_i}'
        ]
        return "\t\n".join(message)