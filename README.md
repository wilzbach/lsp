Storyscript Language Server (SLS)
=================================

Install
-------

Work in a fresh virtual environment:

```sh
virtualenv venv -p /usr/bin/python3.6
. ./venv/bin/activate
```

And then install all dependencies:

```sh
pip install -r requirements.txt
```

Developing
----------

You can start the LSP server with:

```sh
./lspserver.py
```

Testing with VSCode
-------------------

1) Setup the VS client

Initially the dependencies of the VSCode extension need to be fetched:

```sh
npm install --prefix client
```

2) Start a TCP LSP server

```sh
./lspserver.py
```

3) Open up VSCode

```sh
npm run --prefix client vscode
```

VSCode will automatically try to reconnect if the socket has been lost.

### Alternative: spawn via VSCode

You can also start up a VSCode instance via VSCode. This will allow you to debug into an extension.

1) Open VSCode
2) Open Folder (-> select "<this-dir>/client")
3) View -> Debug
4) Run "Launch Client"
5) Open up a directory with Storyscript files or create a new `.story` file

If a Stdio server is used, it will automatically spawn the server and connect to it.
On changes to the server, it can be killed by e.g.:

```sh
pkill lspserver.py
```

VSCode will automatically respawn a new LSP server instance.

If you want to continuously build the client extension, do:

```sh
npm run --prefix client watch
```
