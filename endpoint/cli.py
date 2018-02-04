import sys
import json
import click
import requests
import os

from functools import wraps

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

class EndpointError(click.ClickException):
    pass

if "HW_API" not in os.environ:
    os.environ["HW_API"] = "hallowhale.io"

class EndpointAPI(object):
    def __init__(self, client, auth):
        self.url = "http://{}/{}".format(os.environ.get("HW_API"), "endpoints")
        self.client = client
        self.default_headers = {"X-PA-AUTH-TOKEN": auth}

    def common_error_handler(f):
        @wraps(f)
        def func(*a, **kw):
            try:
                response = f(*a, **kw)
                if response.status_code == 401:
                    click.secho('Warning: Authentication Failed', fg="yellow")
                    exit(1)
                if response.status_code == 404:
                    click.secho('Warning: Resource not found', fg="yellow")
                    exit(1)
                if response.status_code >= 500:
                    raise EndpointError("Error while communicating with API - {}".format(response.status_code))
                return response
            except requests.exceptions.ConnectionError as exc:
                raise EndpointError("Unable to communicate with API")
        return func


    @common_error_handler
    def post(self, data, **kwargs):
        return self.client.post(self.url, data=data, headers=self.get_headers(**kwargs))

    @common_error_handler
    def list(self, **kwargs):
        return self.client.get(self.url, headers=self.get_headers(**kwargs))

    @common_error_handler
    def get(self, name, **kwargs):
        return self.client.get("{}/{}".format(self.url, name), headers=self.get_headers(**kwargs))

    @common_error_handler
    def delete(self, name, **kwargs):
        return self.client.delete("{}/{}".format(self.url, name), headers=self.get_headers(**kwargs))

    def describe(self, name):
        url = "http://{}.run.{}/".format(name, os.environ.get("HW_API"))
        return dict(url=url)

    def get_headers(self, **kwargs):
        headers = kwargs.get("headers", self.default_headers.copy())
        defaults = self.default_headers.copy()
        defaults.update(headers)
        return defaults

auth = click.option('--auth-token', envvar="AUTH_TOKEN", default="NONE", help="Authentication token to access your account")

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='0.0.1')
def hw():
    """
    <NAME> - Run containers as a Funtion - CaaF
    """
    pass


@hw.command()
@auth
@click.option('--env', '-e', multiple=True, help="Environment variables passed to the container - multiple values possible")
@click.option('--command', '-c', help="Set the command to be run with this image")
@click.argument('image')#, help="An Image hosted on hub.docker.com")
def create(**kwargs):
    """ Create a new endpoint with <IMAGE> from hub.docker.com"""
    api = EndpointAPI(requests, kwargs.get("auth_token"))
    env = dict(e.strip().split("=") for e in kwargs.get("env", ()))
    cmd = kwargs.get("command") or ""
    data = dict(image=kwargs.get("image"), env=json.dumps(env, sort_keys=True), command=cmd.strip())
    response = api.post(data=data)
    if response.status_code == 429:
        click.secho('Warning: No more endpoints left - either remove or get more by contacting me', fg="yellow")
        exit(1)

    if response.status_code == 200:
        url = api.describe(response.json()["runner-name"])["url"]
        click.secho('Success: Container will be available shortly', bold=True, fg="green")
        click.secho('{}'.format(url))


@hw.command()
@auth
def ls(**kwargs):
    """ List all endpoints"""
    api = EndpointAPI(requests, kwargs.get("auth_token"))
    response = api.list()
    for e in response.json()["endpoints"]:
        url = api.describe(e["name"])["url"]
        click.secho("{} -> {}".format(url, api.get(e["name"]).json()["status"]))


@hw.command()
@auth
@click.argument('name')#, help="The name of your endpoint")
def remove(**kwargs):
    """ Permanently remove an endpoint by <NAME>"""
    api = EndpointAPI(requests, kwargs.get("auth_token"))
    name = kwargs.get("name")
    respone = api.delete(name)
    click.secho("{} will be deleted".format(name))


if __name__ == '__main__':
    hw()
