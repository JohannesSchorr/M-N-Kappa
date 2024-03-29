from unittest import TestCase, main

from m_n_kappa.width import (
    StateMeta,
    MembranStateHarmonicLoading,
    MembranStateLineLoading,
    BendingStateHarmonicLoading,
    BendingStateLineLoading,
)


"""
References
----------
Kuhlmann, U.; Rieg, A. Mittragende Betongurtbreite niedriger Verbundträger, AiF-Forschungsvorhaben-Nr. 13460 N, 2004
"""


class TestStateMeta(TestCase):
    def setUp(self):
        self.test_state = StateMeta(
            slab_width=2.0, beam_length=1.0, mu=0.0, sequences=55
        )

    def test_sinh(self):
        self.assertEqual(self.test_state.sinh(0), 0)

    def test_cosh(self):
        self.assertEqual(self.test_state.cosh(0), 1.0)


class TestMembranStateHarmonicLoading(TestCase):
    def setUp(self):
        self.test_state_1 = MembranStateHarmonicLoading(
            slab_width=2.0, beam_length=1.0, mu=0.0
        )
        self.test_state_2 = MembranStateHarmonicLoading(
            slab_width=1.0, beam_length=1.0, mu=0.0
        )
        self.test_state_3 = MembranStateHarmonicLoading(
            slab_width=0.4, beam_length=1.0, mu=0.0
        )

    def test_b_over_l(self):
        self.assertEqual(self.test_state_2.one_web.b_over_l, 1.0)

    def test_mu(self):
        self.assertEqual(self.test_state_2.one_web.mu, 0.0)

    def test_ratio_for_multiple_webs(self):
        """
        value for comparison is obtained from Fig. 5-2 in Kuhlmann, Rieg (2004)
        """
        self.assertAlmostEqual(
            self.test_state_1.multiple_webs.ratio_beff_to_b(), 0.1, places=1
        )

    def test_ratio_for_one_web(self):
        """
        value for comparison is obtained from Fig. 5-4 in Kuhlmann, Rieg (2004)
        """
        self.assertAlmostEqual(
            self.test_state_2.one_web.ratio_beff_to_b(), 0.2, places=1
        )

    def test_compare_ratio_for_one_and_multiple_webs(self):
        """
        value for comparison is obtained from Fig. 5-4 in Kuhlmann, Rieg (2004)
        """
        self.assertAlmostEqual(
            self.test_state_2.one_web.ratio_beff_to_b(),
            self.test_state_2.multiple_webs.ratio_beff_to_b(),
            places=2,
        )

    def test_compare_2_ratio_for_one_and_multiple_webs(self):
        """
        value for comparison is obtained from Fig. 5-4 in Kuhlmann, Rieg (2004)
        """
        self.assertAlmostEqual(
            self.test_state_3.one_web.ratio_beff_to_b(),
            self.test_state_3.multiple_webs.ratio_beff_to_b(),
            places=1,
        )


class TestMembranStateLineLoading(TestCase):
    def setUp(self):
        self.test_state = MembranStateLineLoading(
            slab_width=2.0, beam_length=1.0, mu=0.0, sequences=55
        )

    def test_mu(self):
        self.assertEqual(self.test_state.multiple_webs.mu, 0)

    def test_ratio_for_multiple_webs(self):
        """
        value for comparison is obtained from Fig. 5-8 in Kuhlmann, Rieg (2004)
        """
        self.assertAlmostEqual(
            self.test_state.multiple_webs.ratio_beff_to_b(position=0.0), 0.1, places=1
        )

    def test_ratio_for_one_web(self):
        """
        value for comparison is obtained from Fig. 5-11 in Kuhlmann, Rieg (2004)
        """
        self.assertAlmostEqual(
            self.test_state.one_web.ratio_beff_to_b(position=0.0), 0.1, places=1
        )

    def test_compare_ratio_for_one_and_multiple_webs(self):
        """
        value for comparison is obtained from Fig. 5-11 in Kuhlmann, Rieg (2004)
        """
        self.assertAlmostEqual(
            self.test_state.one_web.ratio_beff_to_b(position=0.0),
            self.test_state.multiple_webs.ratio_beff_to_b(position=0.0),
            places=1,
        )

    def test_ratio_2_for_multiple_webs(self):
        test_state = MembranStateLineLoading(
            slab_width=1.0, beam_length=1.0, mu=0.0, sequences=55
        )
        self.assertAlmostEqual(
            test_state.multiple_webs.ratio_beff_to_b(0.0), 0.2, places=1
        )

    def test_ratio_3_for_multiple_webs(self):
        test_state = MembranStateLineLoading(
            slab_width=0.2, beam_length=1.0, mu=0.0, sequences=55
        )
        self.assertAlmostEqual(
            test_state.multiple_webs.ratio_beff_to_b(0.0), 0.8, places=1
        )


class TestMembranStateSingleLoading(TestCase): 
    # TODO: TestMembranStateSingleLoading
    pass 

class TestBendingStateHarmonicLoading(TestCase):

    test_state = BendingStateHarmonicLoading(slab_width=2.0, beam_length=1.0, mu=0.0)

    def test_compare_two_and_one_web(self):
        """
        comparison is obtained from Fig. 5-21 in Kuhlmann, Rieg (2004)
        """
        self.assertAlmostEqual(
            self.test_state.multiple_webs.ratio_beff_to_b(),
            self.test_state.one_web.ratio_beff_to_b(),
            2,
        )

    def test_one_web(self):
        """
        value for comparison is obtained from Fig. 5-21 in Kuhlmann, Rieg (2004)
        """
        self.assertAlmostEqual(
            self.test_state.one_web.ratio_beff_to_b(), 0.31834000523606565, 5
        )

    def test_multiple_webs(self):
        """
        value for comparison is obtained from Fig. 5-19 & 5-21 in Kuhlmann, Rieg (2004)
        """
        self.assertAlmostEqual(
            self.test_state.multiple_webs.ratio_beff_to_b(), 0.31823846936916794, 5
        )


class TestBendingStateLineLoading(TestCase):
    def setUp(self):
        self.test_state = BendingStateLineLoading(
            slab_width=2.0, beam_length=1.0, mu=0.0, sequences=30
        )
        self.position = 0.0

    def test_compare_two_and_one_web(self):
        """
        comparison is obtained from Fig. 5-29 in Kuhlmann, Rieg (2004)
        """
        self.assertAlmostEqual(
            self.test_state.multiple_webs.ratio_beff_to_b(self.position),
            self.test_state.one_web.ratio_beff_to_b(self.position),
            2,
        )

    def test_one_web(self):
        """
        value for comparison is obtained from Fig. 5-29 in Kuhlmann, Rieg (2004)
        """
        self.assertAlmostEqual(
            self.test_state.one_web.ratio_beff_to_b(self.position), 0.3, 1
        )

    def test_multiple_webs(self):
        """
        value for comparison is obtained from Fig. 5-19 & 5-29 in Kuhlmann, Rieg (2004)
        """
        self.assertAlmostEqual(
            self.test_state.multiple_webs.ratio_beff_to_b(self.position), 0.3, 1
        )


class TestBendingStateSingleLoading(TestCase):
    # TODO: TestBendingStateSingleLoading
    pass


if __name__ == "__main__":
    main()