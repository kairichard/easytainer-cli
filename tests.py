import os
import unittest

import click
import requests
import requests_mock
from click.testing import CliRunner
from mock import patch


@requests_mock.Mocker()
class CliTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["HW_API"] = "mock.mock"
        super().setUp()
        self.runner = CliRunner()

    def test_unauthenticated(self, m):
        m.post("http://mock.mock/endpoints", status_code=401)
        result = self.runner.invoke(
            cli.hw, ["create", "ubuntu"], catch_exceptions=False)
        self.assertIn("Authentication Failed", result.output)
        self.assertEqual(result.exit_code, 1)
        self.assertTrue(m.called)

    def test_no_more_resources(self, m):
        m.post("http://mock.mock/endpoints", status_code=429)
        result = self.runner.invoke(cli.hw, ["create", "ubuntu"])
        self.assertIn("No more endpoints left", result.output)
        self.assertEqual(result.exit_code, 1)
        self.assertTrue(m.called)

    def test_create(self, m):
        m.post("http://mock.mock/endpoints", status_code=200)
        result = self.runner.invoke(
            cli.hw, ["create", "ubuntu"], catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Will be deployed at http://", result.output)
        self.assertIn("Give it some time to pull your image", result.output)
        self.assertTrue(m.called)

    def test_delete(self, m):
        m.delete("http://mock.mock/endpoints/ice-cream", status_code=200)
        result = self.runner.invoke(
            cli.hw, ["remove", "ice-cream"], catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(m.called)

    def test_create_with_env(self, m):
        m.post("http://mock.mock/endpoints", status_code=200)
        result = self.runner.invoke(
            cli.hw, ["create", "ubuntu", "-e TEST=True", "-e DEBUG=False"])
        self.assertIn("Will be deployed at http://", result.output)

    @patch("endpoint.cli.EndpointAPI.__init__")
    def test_create_uses_auth_token(self, m, e):
        result = self.runner.invoke(
            cli.hw, ["create", "ubuntu", "--auth-token=123"])
        e.assert_called_with(requests, "123")

    @patch("endpoint.cli.EndpointAPI.__init__")
    def test_delete_uses_auth_token(self, m, e):
        result = self.runner.invoke(
            cli.hw, ["remove", "ubuntu", "--auth-token=123"])
        e.assert_called_with(requests, "123")

    @patch("endpoint.cli.EndpointAPI.__init__")
    def test_create_uses_auth_token__env(self, m, e):
        os.environ["AUTH_TOKEN"] = "123"
        result = self.runner.invoke(cli.hw, ["create", "ubuntu"])
        e.assert_called_with(requests, "123")

    @patch("endpoint.cli.EndpointAPI.__init__")
    def test_delete_uses_auth_token__env(self, m, e):
        os.environ["AUTH_TOKEN"] = "123"
        result = self.runner.invoke(cli.hw, ["remove", "ubuntu"])
        e.assert_called_with(requests, "123")


if __name__ == "__main__":
    unittest.main()
