import importlib.util
import pathlib
import unittest
from unittest import mock


MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "epic_downloader.py"
spec = importlib.util.spec_from_file_location("epic_downloader", MODULE_PATH)
assert spec is not None
assert spec.loader is not None
epic_downloader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(epic_downloader)


class EpicClientAuthTests(unittest.TestCase):
    def test_token_auth_sets_authorization_header_and_skips_password_hashing(self):
        client = epic_downloader.EpicClient(token="test-" + "token")

        with mock.patch.object(epic_downloader, "compute_pass_hash", side_effect=AssertionError("should not hash password")):
            self.assertTrue(client.login())

        self.assertEqual(client.session.headers["authorization"], "Bearer test-token")

    def test_login_requires_credentials_without_token(self):
        client = epic_downloader.EpicClient()

        self.assertFalse(client.login())
        self.assertNotIn("authorization", client.session.headers)


if __name__ == "__main__":
    unittest.main()
