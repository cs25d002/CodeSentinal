const vscode = acquireVsCodeApi();
const resultsDiv = document.getElementById("results");

window.addEventListener("message", (event) => {
    console.log("Received message in webview:", event.data);

    const message = event.data;

    if (message.command === "showResult") {
        const isAI = message.isAI;
        const explanation = message.explanation || "No details available.";

        const resultBox = document.createElement("div");
        resultBox.className = `alert ${isAI ? "ai" : "human"}`;
        resultBox.innerHTML = `
            <strong>${isAI ? "⚠️ AI-generated code detected!" : "✅ Human-written code"}:</strong><br>
            ${explanation}
        `;
        resultsDiv.appendChild(resultBox);
    }

    // ✅ NEW: Handle backend errors
    if (message.command === "showError") {
        const errorBox = document.createElement("div");
        errorBox.className = "alert error";
        errorBox.innerHTML = `
            <strong>❌ Analysis Error:</strong><br>
            ${message.error || "Unknown error occurred."}
        `;
        resultsDiv.appendChild(errorBox);
    }
});
