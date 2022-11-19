from unittest import TestCase, main

from m_n_kappa.curvature_boundaries import MaximumCurvature, MinimumCurvature


class TestMaximumCurvature(TestCase):
    def setUp(self):
        self.maximum_curvature = MaximumCurvature()


if __name__ == '__main__':
    main()