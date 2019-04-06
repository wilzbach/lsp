import * as path from 'path';
import * as net from 'net';
import * as cp from 'child_process';
import {
    commands,
    Disposable,
    ExtensionContext,
    OutputChannel,
    window as Window,
    workspace,
} from 'vscode';

import {
    CloseAction,
    ErrorHandler,
    ErrorAction,
    Executable,
    LanguageClient,
    LanguageClientOptions,
    Message,
    ServerOptions,
    StreamInfo,
    SocketTransport,
    TransportKind,
} from 'vscode-languageclient';

let client: LanguageClient;
let socket: net.Socket;

let out:OutputChannel;
let restartHandler;

/*
 * Check e.g. https://github.com/Microsoft/vscode-languageserver-node/blob/master/client/src/main.ts
 * for the interface
 */

export function activate(context: ExtensionContext) {
    out = Window.createOutputChannel("SLS");
    // Options to control the language client
    let clientOptions: LanguageClientOptions = {
        // Register the server for storyscript documents
        documentSelector: [
            { scheme: 'file', language: 'storyscript' },
        ],
        synchronize: {
            // Notify the server about file changes to '.story' files contained in the workspace
            fileEvents: [
                workspace.createFileSystemWatcher('**/.story'),
            ],
            configurationSection: 'sls',
        },
        errorHandler: new CustomErrorHandler("sls"),
    };

    // Create the language client and start the client.
    const port = 2042;
    client = startLangServerTCP(port, clientOptions);
    //client = startLangServerStdio(context.asAbsolutePath('..'), clientOptions);
    out.appendLine(`Starting (port: ${port})`)
    // debugging
    out.show(); // reveal the SLS channel in the UI

    // Handy restart of the socket connection
    restartHandler = () => {
        socket.destroy();
        client.stop();
        client = startLangServerTCP(port, clientOptions);
        context.subscriptions.push(client.start());
    };

    context.subscriptions.push(commands.registerCommand('sls.restart', restartHandler));

    // Start the client
    context.subscriptions.push(client.start());
}

// TODO
function startLangServerStdio(rootDir: string, clientOptions: LanguageClientOptions): LanguageClient {
    const lspPath = path.join(rootDir, 'lspserver.py');

    let server:Executable = {
        command: lspPath,
        args: ['stdio'],
        options: {
            shell: true,
            cwd: rootDir,
        }
    };

    let serverOptions: ServerOptions = server;
    return new LanguageClient(
        'storyscript',
        'Storyscript LSP (Stdio)',
        serverOptions,
        clientOptions
    );
}

function startLangServerTCP(port: number, clientOptions: LanguageClientOptions): LanguageClient {
    const serverOptions: ServerOptions = function() {
        return new Promise((resolve, reject) => {
            if (socket !== undefined) {
                socket.destroy();
            }
            socket = new net.Socket();
            socket.connect(port, "127.0.0.1");
            socket.on('connect', function(err) {
                resolve({
                    reader: socket,
                    writer: socket,
                });
            });
            socket.on('error', function(err) {
                out.appendLine('socket.error: ' + err)
                // try to connect to a newly started server automatically
                setTimeout(restartHandler, 500);
            });
            socket.on('close', function() {
                out.appendLine('socket.close')
            });
        });
    }

    return new LanguageClient(`SLS (port ${port})`, serverOptions, clientOptions);
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}

// from https://github.com/Microsoft/vscode-languageserver-node/blob/04c4f6549d97487375aeb4ad0a43f060fb714c0c/client/src/client.ts
class CustomErrorHandler implements ErrorHandler {

    private restarts: number[];

    constructor(private name: string) {
        this.restarts = [];
    }

    public error(_error: Error, _message: Message, count: number): ErrorAction {
        out.appendLine("error" + _error.toString());
        if (count && count <= 3) {
            return ErrorAction.Continue;
        }
        return ErrorAction.Shutdown;
    }
    public closed(): CloseAction {
        this.restarts.push(Date.now());
        if (this.restarts.length < 20) {
            return CloseAction.Restart;
        } else {
            let diff = this.restarts[this.restarts.length - 1] - this.restarts[0];
            if (diff <= 60 * 1000) {
                Window.showErrorMessage(`The ${this.name} server crashed 20 times in the last minute. The server will not be restarted.`);
                return CloseAction.DoNotRestart;
            } else {
                this.restarts = [];
                return CloseAction.Restart;
            }
        }
    }
}
