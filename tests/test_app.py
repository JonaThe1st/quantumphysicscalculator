import unittest

from scipy import constants as const

from app import create_app


class AppTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app("testing")
        self.client = app.test_client()

    def test_homepage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Quantum Physics Calculator", response.data)

    def test_health_endpoint(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)

    def test_convert_ev_to_j(self):
        payload = {"value": 1, "source_unit": "eV", "target_unit": "J"}
        response = self.client.post("/api/v1/convert", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(data["result"], 1.602176634e-19, places=30)

    def test_convert_validation_error(self):
        payload = {"value": 1, "source_unit": "abc", "target_unit": "J"}
        response = self.client.post("/api/v1/convert", json=payload)

        self.assertEqual(response.status_code, 400)

    def test_convert_scientific_notation_string(self):
        payload = {"value": "2*10^5", "source_unit": "Hz", "target_unit": "J"}
        response = self.client.post("/api/v1/convert", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(data["result"], const.h * 2e5, places=40)

    def test_convert_prefixed_value_input(self):
        payload = {"value": "1G", "source_unit": "Hz", "target_unit": "J"}
        response = self.client.post("/api/v1/convert", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(data["result"], const.h * 1e9, places=30)

    def test_convert_prefixed_source_unit(self):
        payload = {"value": 2, "source_unit": "keV", "target_unit": "J"}
        response = self.client.post("/api/v1/convert", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(data["result"], 2e3 * const.e, places=30)

    def test_convert_prefixed_target_unit(self):
        payload = {"value": 1, "source_unit": "J", "target_unit": "mJ"}
        response = self.client.post("/api/v1/convert", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(data["result"], 1000.0, places=10)

    def test_convert_ev_to_kelvin(self):
        payload = {"value": 1, "source_unit": "eV", "target_unit": "K"}
        response = self.client.post("/api/v1/convert", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(data["result"], const.e / const.Boltzmann, places=7)

    def test_convert_ev_to_tesla(self):
        payload = {"value": 1, "source_unit": "eV", "target_unit": "T"}
        response = self.client.post("/api/v1/convert", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        bohr_magneton = const.physical_constants["Bohr magneton"][0]
        self.assertAlmostEqual(data["result"], const.e / bohr_magneton, places=7)

    def test_homepage_form_submission(self):
        response = self.client.post(
            "/",
            data={
                "value": "5*10^2",
                "source_unit": "ev",
                "target_unit": "hz",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Result", response.data)

    def test_homepage_has_no_prefix_dropdowns(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'name="source_prefix"', response.data)
        self.assertNotIn(b'name="target_prefix"', response.data)

    def test_homepage_contains_swap_button(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Swap From/To", response.data)


if __name__ == "__main__":
    unittest.main()
