import importlib
import os
import unittest
from unittest.mock import patch

from models.role import Role
from models.user import User


class SecurityAndConfigurationTest(unittest.TestCase):
    def test_console_user_uses_salted_bcrypt_hash(self):
        first = User(1, "first", "Secret123!", "First User", Role.OWNER)
        second = User(2, "second", "Secret123!", "Second User", Role.OWNER)

        self.assertTrue(first.check_password("Secret123!"))
        self.assertFalse(first.check_password("wrong"))
        self.assertNotEqual(first._User__password_hash, second._User__password_hash)
        self.assertTrue(first._User__password_hash.startswith(b"$2"))

    def test_weather_urls_can_be_loaded_from_environment(self):
        import external.weather as weather

        with patch.dict(
            os.environ,
            {
                "OPEN_METEO_FORECAST_URL": "https://example.test/forecast",
                "OPEN_METEO_GEOCODING_URL": "https://example.test/geocoding",
            },
        ):
            importlib.reload(weather)
            self.assertEqual(
                weather.BASE_URL,
                "https://example.test/forecast",
            )
            self.assertEqual(
                weather.GEOCODING_URL,
                "https://example.test/geocoding",
            )

        importlib.reload(weather)


if __name__ == "__main__":
    unittest.main()
