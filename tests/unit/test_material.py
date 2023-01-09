from m_n_kappa.material import Material, Concrete, ConcreteCompressionNonlinear, Steel

from unittest import TestCase, main


class TestMaterial(TestCase):

    def setUp(self):
        self.stress_strain_list = [
            [-100.0, -1.0],
            [-50.0, -0.6],
            [0.0, 0.0],
            [50, 0.5],
            [150.0, 2.0],
        ]
        self.section_type = "slab"
        self.material = Material(
            section_type=self.section_type,
            stress_strain=self.stress_strain_list)

    def test_stress_strain(self):
        self.assertListEqual(self.material.stress_strain, self.stress_strain_list)

    def test_section_type(self):
        self.assertEqual(self.material.section_type, self.section_type)

    def test_maximum_strain(self):
        self.assertEqual(self.material.maximum_strain, 2.0)

    def test_minimum_strain(self):
        self.assertEqual(self.material.minimum_strain, -1.0)

    def test_strains(self):
        self.assertEqual(self.material.strains, [-1.0, -0.6, 0.0, 0.5, 2.0])

    def test_stresses(self):
        self.assertEqual(self.material.stresses, [-100.0, -50.0, 0.0, 50.0, 150.0])

    def test_get_material_index_positive_strain(self):
        self.assertEqual(self.material._get_material_index(strain=1.0), 3)

    def test_get_material_index_zero(self):
        self.assertEqual(self.material._get_material_index(strain=0.0), 2)

    def test_get_material_index_negative_strain(self):
        self.assertEqual(self.material._get_material_index(strain=-0.5), 1)

    def test_get_intermediate_strains_positive(self):
        self.assertEqual(
            self.material.get_intermediate_strains(strain_1=1.0, strain_2=0.0), [0.5]
        )

    def test_get_intermediate_strain_positive_small(self):
        self.assertEqual(
            self.material.get_intermediate_strains(strain_1=0.1, strain_2=0.0), []
        )

    def test_get_intermediate_strain_negative(self):
        self.assertEqual(
            self.material.get_intermediate_strains(strain_1=-1.0, strain_2=0.0),
            [-0.6],
        )

    def test_get_intermediate_strain_with_two_strains(self):
        self.assertEqual(
            self.material.get_intermediate_strains(strain_1=-1.0, strain_2=1.0),
            [-0.6, 0.5],
        )

    def test_get_material_stress_1(self):
        self.assertEqual(self.material.get_material_stress(-1.0), -100.0)

    def test_get_material_stress_2(self):
        self.assertEqual(self.material.get_material_stress(0.25), 25)

    def test_get_material_stress_3(self):
        self.assertEqual(self.material.get_material_stress(2.0), 150.0)

    def test_sort_strains_ascending(self):
        self.material.sort_strains_ascending()
        self.assertListEqual(self.material.stress_strain, self.stress_strain_list)

    def test_sort_strains_descending(self):
        self.material.sort_strains_descending()
        self.assertListEqual(
            self.material.stress_strain,
            [[150.0, 2.0], [50, 0.5], [0.0, 0.0], [-50.0, -0.6], [-100.0, -1.0]],
        )
        self.material.sort_strains_ascending()


class TestConcrete(TestCase):
    """Test general-functions of material-module"""

    def setUp(self):
        self.f_cm = 35.0
        self.concrete = Concrete(f_cm=self.f_cm)

    def test_f_cm(self):
        self.assertEqual(self.concrete.f_cm, self.f_cm)

    def test_compression_stress_strain_type(self):
        self.assertEqual(self.concrete.compression_stress_strain_type, "Nonlinear")


class TestConcreteCompressionNonlinear(TestCase):

    """Test Concrete-class of material-module with non-linear stress-strain_value relationship"""

    def setUp(self):
        self.f_cm = 35.0
        self.concrete = Concrete(f_cm=self.f_cm)
        self.compression = ConcreteCompressionNonlinear(
            self.f_cm, self.concrete.epsilon_y, self.concrete.E_cm
        )

    def test_f_cm(self):
        self.assertEqual(self.compression.f_cm, self.f_cm)

    def test_compression_stress_strain_type(self):
        self.assertEqual(self.concrete.compression_stress_strain_type, "Nonlinear")

    def test_stress_strains(self):
        self.assertEqual(
            self.compression.stress_strain(),
            [
                [-0.0, -0.0],
                [-13.125764641863459, -0.0004370035264271907],
                [-22.461118693025618, -0.0008396726328503419],
                [-33.58438351512978, -0.0016793452657006837],
                [-35.0, -0.002107458997361724],
                [-31.304785402824145, -0.002803729498680862],
                [-20.338424138047706, -0.0035],
            ],
        )


class TestSteel(TestCase):
    def setUp(self):
        self.f_y = 355.0
        self.f_u = 500.0
        self.steel = Steel(f_y=self.f_y, f_u=self.f_u)

    def test_f_y(self):
        self.assertEqual(self.steel.f_y, self.f_y)

    def test_f_u(self):
        self.assertEqual(self.steel.f_u, None)

    def test_e_a(self):
        self.assertGreater(self.steel.E_a, 0.0)

    def test_stress_strain(self):
        self.assertListEqual(
            self.steel.stress_strain, [[-210000.0, -1.0], [0.0, 0.0], [210000, 1.0]]
        )


class TestSteelBilinear(TestCase):
    def setUp(self):
        self.f_y = 355.0
        self.f_u = 500.0
        self.epsilon_u = 0.15
        self.steel = Steel(f_y=self.f_y, f_u=self.f_u, failure_strain=self.epsilon_u)

    def test_f_y(self):
        self.assertEqual(self.steel.f_y, self.f_y)

    def test_f_u(self):
        self.assertEqual(self.steel.f_u, self.f_u)

    def test_epsilon_u(self):
        self.assertEqual(self.steel.failure_strain, self.epsilon_u)

    def test_epsilon_y(self):
        epsilon_y = self.f_y / 210000.0
        self.assertEqual(self.steel.epsilon_y, epsilon_y)

    def test_stress_strain(self):
        self.assertEqual(
            self.steel.stress_strain,
            [
                [-500.0, -0.15],
                [-355.0, -0.0016904761904761904],
                [-0.0, -0.0],
                [355.0, 0.0016904761904761904],
                [500.0, 0.15],
            ],
        )


if __name__ == "__main__":
    main()