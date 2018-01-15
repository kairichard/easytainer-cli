import sys
import click
import requests
import os

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class EndpointAPI(object):
    def __init__(self, client, auth):
        self.url = "http://{}/{}".format(os.environ.get("HW_API"), "endpoints")
        self.client = client
        self.default_headers = {"X-PA-AUTH-TOKEN": auth}

    def post(self, data, **kwargs):
        return self.client.post(self.url, data=data, headers=self.get_headers(**kwargs))

    def delete(self, name, **kwargs):
        return self.client.delete("{}/{}".format(self.url, name), headers=self.get_headers(**kwargs))

    def get_headers(self, **kwargs):
        headers = kwargs.get("headers", self.default_headers.copy())
        defaults = self.default_headers.copy()
        defaults.update(headers)
        return defaults


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='0.0.1')
def hw():
    pass


@hw.command()
@click.option('--env', '-e', multiple=True)
@click.option('--auth-token', envvar="AUTH_TOKEN", default="NONE")
@click.argument('image')
def create(**kwargs):
    api = EndpointAPI(requests, kwargs.get("auth_token"))
    data = dict(image=kwargs.get("image"), env="{}")
    response = api.post(data=data)
    if response.status_code == 401:
        print("Authentication Failed")
    if response.status_code == 429:
        print("No more endpoints left")
    if response.status_code == 200:
        print("Will be deployed at http://{}.run.{}".format(response.json()
                                                            ["runner-name"], os.environ.get("HW_API")))
        print("Give it some time to pull your image")
    if response.status_code != 200:
        sys.exit(1)


@hw.command()
@click.option('--auth-token', envvar="AUTH_TOKEN", default="NONE")
@click.argument('endpoint-name')
def remove(**kwargs):
    api = EndpointAPI(requests, kwargs.get("auth_token"))
    respone = api.delete(kwargs.get("endpoint_name"))


if __name__ == '__main__':
    hw()
