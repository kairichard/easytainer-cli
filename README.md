hellowhale/cli
========
This is the CLI for <DOMAIN>.
Use this to create and remove endpoints via the commandline.

###### Synopsis
```bash
Usage: hw [OPTIONS] COMMAND [ARGS]...
```
Installing
-------------
The cli comes as python package.
```bash
> pip install <>
```
Usage
-----------
### Create an endpoint
Its possible to install a Package either locally via the files system or by specifying a remote git repo,
local git repos also work.

```bash
# create a new endpoint
> AUTH_TOKEN=a2FpOmtvZW5pZw hw create ubuntu:17.10 -c "date"
Success: Container will be available shortly
http://<NAME>.run.hw.kairichardkoenig.de

> AUTH_TOKEN=a2FpOmtvZW5pZw hw ls
http://<NAME>.run.hw.kairichardkoenig.de -> ready

> AUTH_TOKEN=a2FpOmtvZW5pZw hw remove <NAME>
<NAME> will be deleted
```

## Contributing Code

If you want to contribute code, please try to:

* Follow the same coding style as used in the project. Pay attention to the
  usage of tabs, spaces, newlines and brackets. Try to copy the aesthetics the
  best you can.
* Write [good commit messages](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html),
  explain what your patch does, and why it is needed.
* Keep it simple: Any patch that changes a lot of code or is difficult to
  understand should be discussed before you put in the effort.

Once you have tried the above, create a GitHub pull request to notify me of your
changes.

License
--------
BSD 3

Attribution
--------
Thanks to the people creating and maintaining all the packages and code this project depends and builds up on.

Logo
--------
by Mark Beltran -> https://www.instagram.com/elhoncho/
