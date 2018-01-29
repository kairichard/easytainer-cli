import sys
import json
import click
import requests
import os

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

class EndPointError(click.ClickException):
    pass

if "HW_API" not in os.environ:
    os.environ["HW_API"] = "hallowhale.io"

class EndpointAPI(object):
    def __init__(self, client, auth):
        self.url = "http://{}/{}".format(os.environ.get("HW_API"), "endpoints")
        self.client = client
        self.default_headers = {"X-PA-AUTH-TOKEN": auth}

    def post(self, data, **kwargs):
        try:
            return self.client.post(self.url, data=data, headers=self.get_headers(**kwargs))
        except requests.exceptions.ConnectionError as exc:
            raise EndPointError("Unable to communicate with API")

    def list(self, **kwargs):
        try:
            return self.client.get(self.url, headers=self.get_headers(**kwargs))
        except requests.exceptions.ConnectionError as exc:
            raise EndPointError("Unable to communicate with API")

    def delete(self, name, **kwargs):
        try:
            return self.client.delete("{}/{}".format(self.url, name), headers=self.get_headers(**kwargs))
        except requests.exceptions.ConnectionError as exc:
            raise EndPointError("Unable to communicate with API")

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
@click.argument('image')#, help="An Image hosted on hub.docker.com")
def create(**kwargs):
    """ Create a new endpoint with <IMAGE> from hub.docker.com"""
    api = EndpointAPI(requests, kwargs.get("auth_token"))
    env = dict(e.strip().split("=") for e in kwargs.get("env", ()))
    data = dict(image=kwargs.get("image"), env=json.dumps(env, sort_keys=True))
    response = api.post(data=data)
    if response.status_code == 401:
        click.secho('Warning: Authentication Failed', fg="yellow")
        exit(1)

    if response.status_code == 429:
        click.secho('Warning: No more endpoints left - either remove or get more by contacting me', fg="yellow")
        exit(1)

    if response.status_code == 200:
        url = "http://{}.run.{}".format(response.json()["runner-name"], os.environ.get("HW_API"))
        click.secho('Success: Container will be available shortly', bold=True, fg="green")
        click.secho('{}'.format(url))

    if response.status_code != 200:
        raise EndPointError("Unable to communicate with API - {}".format(response.status_code))


@hw.command()
@auth
def ls(**kwargs):
    """ List all endpoints"""
    api = EndpointAPI(requests, kwargs.get("auth_token"))
    response = api.list()
    for e in response.json()["endpoints"]:
        click.secho(e["name"])


@hw.command()
@auth
@click.argument('name')#, help="The name of your endpoint")
def remove(**kwargs):
    """ Permanently remove an endpoint by <NAME>"""
    api = EndpointAPI(requests, kwargs.get("auth_token"))
    respone = api.delete(kwargs.get("name"))


if __name__ == '__main__':
    hw()
