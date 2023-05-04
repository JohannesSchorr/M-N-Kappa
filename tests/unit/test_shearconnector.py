from unittest import TestCase, main

from m_n_kappa.shearconnector import (
    HeadedStud,
    equal_distanced_shear_connectors,
    LoadSlip,
)


class TestShearConnector(TestCase):

    pass


class TestHeadedStud(TestCase):
    def setUp(self) -> None:
        self.concrete_stud = HeadedStud(d=19, h_sc=100, f_u=450.0, f_cm=20.0)
        self.steel_stud = HeadedStud(d=19, h_sc=100, f_u=450.0, f_cm=80.0)

    def test_steel_p(self):
        P_sm = 127726.3125
        self.assertEqual(self.steel_stud.P, P_sm)
        self.assertEqual(self.steel_stud.P_sm(), P_sm)
        self.assertNotEqual(self.steel_stud.P_cm(), P_sm)

    def test_concrete_p(self):
        P_cm = 98839.600049944
        self.assertEqual(self.concrete_stud.P, P_cm)
        self.assertNotEqual(self.concrete_stud.P_sm(), P_cm)
        self.assertEqual(self.concrete_stud.P_cm(), P_cm)

    def test_s_max(self):
        self.assertEqual(self.concrete_stud.s_max, 6.0)

    def test_get_shear_load_1(self):
        self.assertEqual(self.concrete_stud.shear_load(1.0), 98839.600049944)

    def test_get_shear_load_2(self):
        self.assertEqual(self.concrete_stud.shear_load(0.4), 79071.6800399552)

    def test_slip_1(self):
        self.assertEqual(self.concrete_stud.slip(1000.0), 0.0050587011658014425)


class TestLoadSlips(TestCase):
    def test_equality(self):
        self.assertEqual(LoadSlip(1.0, 1.0), LoadSlip(1.0, 1.0))

    def test_equality_in_list(self):
        self.assertCountEqual(
            [LoadSlip(1.0, 1.0), LoadSlip(2.0, 2.0)],
            [LoadSlip(1.0, 1.0), LoadSlip(2.0, 2.0)],
        )


class TestEqualDistancedShearConnectors(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.shear_connector = HeadedStud(19.0, 100.0, 450.0, 30.0)
        self.beam_length = 500.0
        self.longitudinal_distance = 100.0

    def test_only_longitudinal_distance(self):
        shear_connectors = equal_distanced_shear_connectors(
            self.shear_connector, self.longitudinal_distance, self.beam_length
        )
        self.assertEqual(len(shear_connectors), 6)

    def test_equality(self):
        self.assertEqual(self.shear_connector, HeadedStud(19.0, 100.0, 450.0, 30.0))

    def test_shear_connector_list(self):
        shear_connectors = equal_distanced_shear_connectors(
            self.shear_connector, self.longitudinal_distance, self.beam_length
        )
        shear_connectors_list = [
            HeadedStud(19.0, 100.0, 450.0, 30.0, position=0.0),
            HeadedStud(19.0, 100.0, 450.0, 30.0, position=100.0),
            HeadedStud(19.0, 100.0, 450.0, 30.0, position=200.0),
            HeadedStud(19.0, 100.0, 450.0, 30.0, position=300.0),
            HeadedStud(19.0, 100.0, 450.0, 30.0, position=400.0),
            HeadedStud(19.0, 100.0, 450.0, 30.0, position=500.0),
        ]
        self.assertCountEqual(shear_connectors, shear_connectors_list)


if __name__ == "__main__":
    main()
