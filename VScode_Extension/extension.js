const vscode = require('vscode');
const axios = require('axios');

let currentPanel = null;

// ── Typing-speed tracker ───────────────────────────────
let lastTimestamp = Date.now();
let lastLength    = 0;

async function activate(context) {
    // Status bar indicator
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left);
    statusBarItem.text = "🔍 CodeSentinel: Ready";
    statusBarItem.show();

    // Command to manually open the analysis panel
    context.subscriptions.push(
        vscode.commands.registerCommand('codesentinel.showPanel', () => {
            if (!currentPanel) {
                createWebviewPanel(context);
            } else {
                currentPanel.reveal();
            }
        })
    );

    // Watch file changes and trigger backend analysis
    vscode.workspace.onDidChangeTextDocument(async (event) => {
        const editor = vscode.window.activeTextEditor;
        if (!editor || !editor.document) return;

        const code = editor.document.getText();
        const language = editor.document.languageId.toLowerCase();

        const supportedLanguages = ["python"]; // extend support if needed
        if (!supportedLanguages.includes(language)) {
            statusBarItem.text = `⚠️ CodeSentinel: Unsupported (${language})`;
            return;
        }

        statusBarItem.text = "🔍 CodeSentinel: Analyzing...";

        try {
            // ── compute typing speed & total length ────────────
            const now        = Date.now();
            const codeLength = code.length;
            const deltaSec   = (now - lastTimestamp) / 1000;
            const deltaChars = Math.max(0, codeLength - lastLength);
            const typingSpeed = deltaSec > 0 ? deltaChars / deltaSec : 0;
            lastTimestamp = now;
            lastLength    = codeLength;

            const lines = code.split('\n');
            const response = await axios.post('http://localhost:8000/analyze', {
                lines,
                language
            });

            console.log("✅ Backend response:", response.data);

            if (currentPanel && currentPanel.webview) {
                if (response.data.error) {
                    currentPanel.webview.postMessage({
                        command: 'showError',
                        error: response.data.error
                    });
                } else {
                    currentPanel.webview.postMessage({
                        command: 'showLineResult',
                        code,
                        lineScores:   response.data.line_scores,
                        typingSpeed,                    // chars/sec
                        codeLength                      // total chars
                    });
                }
            }

            statusBarItem.text = "✅ CodeSentinel: Done";
        } catch (error) {
            statusBarItem.text = "❌ CodeSentinel: Error";
            console.error("❌ Analysis failed:", error.message);

            if (currentPanel && currentPanel.webview) {
                currentPanel.webview.postMessage({
                    command: 'showError',
                    error: error.message || "Unknown error."
                });
            }
        }
    });
}

// 🖥️ Create Webview panel
function createWebviewPanel(context) {
    currentPanel = vscode.window.createWebviewPanel(
        'codeSentinel',
        'CodeSentinel Analysis',
        vscode.ViewColumn.One,
        {
            enableScripts: true,
            localResourceRoots: [vscode.Uri.file(context.extensionPath)]
        }
    );

    const htmlPath = vscode.Uri.file(
        context.asAbsolutePath('webview/panel.html')
    );

    (async () => {
        try {
            const bytes = await vscode.workspace.fs.readFile(htmlPath);
            let html = new TextDecoder().decode(bytes);

            const base = currentPanel.webview.asWebviewUri(
                vscode.Uri.file(context.extensionPath)
            );

            html = html
                .replace('</head>', `<base href="${base}/webview/">\n</head>`)
                .replace('</body>', `\n</body>`);

            currentPanel.webview.html = html;
        } catch (e) {
            vscode.window.showErrorMessage("Failed to load CodeSentinel panel: " + e.message);
        }
    })();

    currentPanel.onDidDispose(() => {
        currentPanel = null;
    }, null, context.subscriptions);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};