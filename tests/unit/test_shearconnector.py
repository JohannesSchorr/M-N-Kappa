from unittest import TestCase, main

from m_n_kappa.shearconnector import HeadedStud


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


if __name__ == "__main__":
    main()
