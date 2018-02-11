import os
import unittest

import click
import requests
import requests_mock
from click.testing import CliRunner
try:
    from mock import patch
except ImportError:
    from unittest.mock import patch


from endpoint import cli


@requests_mock.Mocker()
class CliTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["API"] = "mock.mock"
        super(CliTestCase, self).setUp()
        self.runner = CliRunner()

    def invoke(self, *args):
        return self.runner.invoke(
            cli.cli, args, catch_exceptions=False)

    def test_unauthenticated(self, m):
        m.post("http://mock.mock/endpoints", status_code=401)
        result = self.invoke("create", "ubuntu")
        self.assertIn("Authentication Failed", result.output)
        self.assertEqual(result.exit_code, 1)
        self.assertTrue(m.called)

    def test_no_more_resources(self, m):
        m.post("http://mock.mock/endpoints", status_code=429)
        result = self.invoke("create", "ubuntu")
        self.assertIn("No more endpoints left", result.output)
        self.assertEqual(result.exit_code, 1)
        self.assertTrue(m.called)

    def test_create(self, m):
        m.post("http://mock.mock/endpoints", status_code=200, text='{"runner-name": "something"}')
        result = self.invoke("create", "ubuntu")
        self.assertEqual(result.exit_code, 0)
        self.assertIn("http://something.run.mock.mock", result.output)
        self.assertTrue(m.called)

    def test_delete(self, m):
        m.delete("http://mock.mock/endpoints/ice-cream", status_code=200)
        result = self.invoke("remove", "ice-cream")
        self.assertEqual(result.exit_code, 0)
        self.assertIn("ice-cream will be deleted", result.output)
        self.assertTrue(m.called)

    def test_delete_non_existant_endpoint(self, m):
        m.delete("http://mock.mock/endpoints/ice-cream", status_code=404)
        result = self.invoke("remove", "ice-cream")
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Warning: Resource not found", result.output)
        self.assertTrue(m.called)

    def test_list_ready(self, m):
        m.get("http://mock.mock/endpoints", status_code=200, text='{"endpoints": [{"image": "ubuntu", "name": "cake"}]}')
        m.get("http://mock.mock/endpoints/cake", status_code=200, text='{"status": "ready"}')
        result = self.invoke("ls")
        self.assertEqual(result.exit_code, 0)
        self.assertIn("http://cake.run.mock.mock/ -> ready", result.output)
        self.assertTrue(m.called)

    def test_list_unauthenticated(self, m):
        m.get("http://mock.mock/endpoints", status_code=401, text='Unauthenticated')
        result = self.invoke("ls")
        self.assertEqual(result.exit_code, 1)

    def test_list_absent(self, m):
        m.get("http://mock.mock/endpoints", status_code=200, text='{"endpoints": [{"image": "ubuntu", "name": "cake"}]}')
        m.get("http://mock.mock/endpoints/cake", status_code=200, text='{"status": "absent"}')
        result = self.invoke("ls")
        self.assertEqual(result.exit_code, 0)
        self.assertIn("http://cake.run.mock.mock/ -> absent", result.output)
        self.assertTrue(m.called)

    @patch("endpoint.cli.requests.post", wraps=cli.requests.post)
    def test_create_with_env(self, m, r):
        m.post("http://mock.mock/endpoints", status_code=200, text='{"runner-name": "something"}')
        result = self.invoke("create", "ubuntu", "-e TEST=True", "-e DEBUG=False")
        r.assert_called_with('http://mock.mock/endpoints', data={'image': 'ubuntu', 'env': '{"DEBUG": "False", "TEST": "True"}'}, headers={'X-PA-AUTH-TOKEN': '123'})
        self.assertIn("http://something.run.mock.mock", result.output)

    @patch("endpoint.cli.requests.post", wraps=cli.requests.post)
    def test_create_with_env(self, m, r):
        m.post("http://mock.mock/endpoints", status_code=200, text='{"runner-name": "something"}')
        result = self.invoke("create", "ubuntu", "-c bash")
        r.assert_called_with('http://mock.mock/endpoints', data={'image': 'ubuntu', 'env': '{}', 'command': 'bash'}, headers={'X-PA-AUTH-TOKEN': '123'})
        self.assertIn("http://something.run.mock.mock", result.output)

    @patch("endpoint.cli.EndpointAPI", wraps=cli.EndpointAPI)
    def test_create_uses_auth_token(self, m, e):
        m.post("http://mock.mock/endpoints", status_code=200, text='{"runner-name": "something"}')
        result = self.invoke("create", "ubuntu", "--auth-token=123")
        e.assert_called_with(requests, "123")

    @patch("endpoint.cli.EndpointAPI", wraps=cli.EndpointAPI)
    def test_delete_uses_auth_token(self, m, e):
        m.delete("http://mock.mock/endpoints/ubuntu", status_code=200)
        result = self.invoke("remove", "ubuntu", "--auth-token=123")
        e.assert_called_with(requests, "123")

    @patch("endpoint.cli.EndpointAPI", wraps=cli.EndpointAPI)
    def test_create_uses_auth_token__env(self, m, e):
        m.post("http://mock.mock/endpoints", status_code=200, text='{"runner-name": "something"}')
        os.environ["AUTH_TOKEN"] = "123"
        result = self.invoke("create", "ubuntu")
        e.assert_called_with(requests, "123")

    @patch("endpoint.cli.EndpointAPI", wraps=cli.EndpointAPI)
    def test_delete_uses_auth_token__env(self, m, e):
        m.delete("http://mock.mock/endpoints/ubuntu", status_code=200)
        os.environ["AUTH_TOKEN"] = "123"
        result = self.invoke("remove", "ubuntu")
        e.assert_called_with(requests, "123")


if __name__ == "__main__":
    unittest.main()
