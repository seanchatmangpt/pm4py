"""
Self-serve demo interface for NL → executable workflow pipeline.

Provides a simple web interface where users can describe a workflow
and get executable BPMN + orchestrator code.
"""

import os
from typing import Optional

# Try to create FastAPI app, fall back to Flask
try:
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

try:
    from flask import Flask, render_template_string, request, jsonify
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


# HTML template for the demo interface
DEMO_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PM4Py Workflow Discovery Demo</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .header p {
            color: #7f8c8d;
            margin: 0;
        }
        .demo-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        @media (max-width: 768px) {
            .demo-container {
                grid-template-columns: 1fr;
            }
        }
        .panel {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .panel h2 {
            margin-top: 0;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #34495e;
        }
        input[type="text"],
        textarea,
        select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            font-family: inherit;
        }
        textarea {
            min-height: 150px;
            resize: vertical;
        }
        .checkbox-group {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 5px;
        }
        .checkbox-group label {
            font-weight: normal;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        button {
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.2s;
        }
        button:hover {
            background: #2980b9a;
        }
        button:disabled {
            background: #95a5a6;
            cursor: not-allowed;
        }
        .result-section {
            margin-top: 20px;
        }
        .result-panel {
            background: #f8f9fa;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #3498db;
        }
        .result-panel h3 {
            margin-top: 0;
            color: #2c3e50;
            font-size: 16px;
        }
        .result-content {
            font-family: 'Courier New', monospace;
            font-size: 13px;
            white-space: pre-wrap;
            word-break: break-all;
            max-height: 300px;
            overflow-y: auto;
            background: white;
            padding: 10px;
            border-radius: 4px;
        }
        .status {
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 15px;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .examples {
            margin-top: 20px;
        }
        .example-btn {
            background: #ecf0f1;
            color: #2c3e50;
            border: 1px solid #bdc3c7;
            padding: 8px 16px;
            margin: 5px;
            font-size: 14px;
            border-radius: 4px;
            cursor: pointer;
        }
        .example-btn:hover {
            background: #d5dbdb;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .loading.active {
            display: block;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔄 Process Discovery Demo</h1>
        <p>Describe your workflow in plain English, get executable code</p>
    </div>

    <div class="demo-container">
        <div class="panel">
            <h2>Describe Your Workflow</h2>

            <form id="discoverForm">
                <div style="margin-bottom: 15px;">
                    <label for="description">Process Description *</label>
                    <textarea
                        id="description"
                        name="description"
                        placeholder="Describe your process step by step...&#10;&#10;Example: A customer places an order. We check inventory. If in stock, we pick and ship. If out of stock, we notify the customer and place a backorder."
                        required
                    ></textarea>
                </div>

                <div style="margin-bottom: 15px;">
                    <label for="workflowName">Workflow Name</label>
                    <input
                        type="text"
                        id="workflowName"
                        name="workflowName"
                        value="My Workflow"
                        placeholder="My Workflow"
                    >
                </div>

                <div style="margin-bottom: 15px;">
                    <label>Output Formats</label>
                    <div class="checkbox-group">
                        <label>
                            <input type="checkbox" name="formats" value="powl" checked disabled>
                            POWL Model
                        </label>
                        <label>
                            <input type="checkbox" name="formats" value="bpmn" checked>
                            BPMN XML
                        </label>
                        <label>
                            <input type="checkbox" name="formats" value="n8n">
                            n8n JSON
                        </label>
                        <label>
                            <input type="checkbox" name="formats" value="temporal">
                            Temporal Go
                        </label>
                        <label>
                            <input type="checkbox" name="formats" value="yawl">
                            YAWL XML
                        </label>
                    </div>
                </div>

                <div style="margin-bottom: 15px;">
                    <label for="model">LLM Model</label>
                    <select id="model" name="model">
                        <option value="groq/openai/gpt-oss-20b" selected>Groq GPT-OSS 20B (Fast)</option>
                        <option value="groq/openai/gpt-oss-120b">Groq GPT-OSS 120B (High Quality)</option>
                    </select>
                </div>

                <button type="submit" id="generateBtn">
                    ⚡ Generate Workflow
                </button>
            </form>

            <div class="examples">
                <p style="color: #7f8c8d; font-size: 14px;">Try an example:</p>
                <button class="example-btn" onclick="loadExample('loan')">Loan Approval</button>
                <button class="example-btn" onclick="loadExample('onboarding')">Employee Onboarding</button>
                <button class="example-btn" onclick="loadExample('support')">Customer Support</button>
            </div>
        </div>

        <div class="panel">
            <h2>Results</h2>

            <div id="loading" class="loading">
                <div class="spinner"></div>
                <p>Generating workflow...</p>
            </div>

            <div id="results" style="display: none;">
                <!-- Results will be populated here -->
            </div>
        </div>
    </div>

    <script>
        const examples = {
            loan: `A bank processes loan applications. The customer submits an application. A clerk reviews the documents. If the documents are incomplete, the clerk requests additional documents and the customer resubmits. Once documents are complete, the clerk forwards to an underwriter. The underwriter either approves or rejects the loan. If approved, the funds are disbursed and the case is closed. If rejected, a rejection letter is sent and the case is closed.`,
            onboarding: `New employee onboarding process: Employee accepts offer. HR prepares paperwork while IT sets up accounts in parallel. Employee completes I-9 and tax forms. IT conducts security training. Manager conducts role training. After all training complete, employee signs handbook. Employee gets badge access. Onboarding complete and archived.`,
            support: `Customer support ticket process: Customer submits ticket. Support system categorizes ticket as billing, technical, or general. Routes to appropriate specialist. Specialist attempts first contact resolution. If resolved, close ticket and survey customer. If not resolved, escalate to tier 2. Tier 2 investigates. If tier 2 resolves, close and survey. If tier 2 cannot resolve, escalate to engineering. After fix, verify with customer. Close ticket if satisfied.`
        };

        function loadExample(name) {
            document.getElementById('description').value = examples[name];
        }

        document.getElementById('discoverForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            const btn = document.getElementById('generateBtn');

            // Show loading
            loading.classList.add('active');
            results.style.display = 'none';
            btn.disabled = true;

            // Gather form data
            const formData = new FormData(e.target);
            const formats = Array.from(formData.getAll('formats'));

            const requestBody = {
                description: formData.get('description'),
                workflow_name: formData.get('workflowName'),
                formats: formats.length > 0 ? formats : ['powl', 'bpmn'],
                model: formData.get('model'),
                max_refinements: 1
            };

            try {
                const response = await fetch('/api/discover-from-text', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestBody)
                });

                const result = await response.json();

                // Display results
                loading.classList.remove('active');
                results.style.display = 'block';

                if (result.success) {
                    let html = `<div class="status success">✓ Workflow generated successfully!</div>`;

                    // POWL Model
                    html += `<div class="result-panel">
                        <h3>POWL Model</h3>
                        <div class="result-content">${escapeHtml(result.powl || '')}</div>
                    </div>`;

                    // Generated Code
                    if (result.generated_code) {
                        if (result.generated_code.n8n) {
                            html += `<div class="result-panel">
                                <h3>n8n Workflow JSON</h3>
                                <div class="result-content">${escapeHtml(JSON.stringify(result.generated_code.n8n, null, 2))}</div>
                            </div>`;
                        }
                        if (result.generated_code.temporal_go) {
                            html += `<div class="result-panel">
                                <h3>Temporal Go Code</h3>
                                <div class="result-content">${escapeHtml(result.generated_code.temporal_go)}</div>
                            </div>`;
                        }
                        if (result.generated_code.bpmn) {
                            html += `<div class="result-panel">
                                <h3>BPMN XML</h3>
                                <div class="result-content">${escapeHtml(result.generated_code.bpmn)}</div>
                            </div>`;
                        }
                        if (result.generated_code.yawl) {
                            html += `<div class="result-panel">
                                <h3>YAWL XML</h3>
                                <div class="result-content">${escapeHtml(result.generated_code.yawl)}</div>
                            </div>`;
                        }
                    }

                    if (result.feedback) {
                        html += `<div class="result-panel">
                            <h3>💡 Feedback</h3>
                            <p>${escapeHtml(result.feedback)}</p>
                        </div>`;
                    }

                    results.innerHTML = html;
                } else {
                    results.innerHTML = `<div class="status error">✗ Generation failed</div>
                        <div class="result-panel"><h3>Errors:</h3><ul>${result.errors.map(e => `<li>${escapeHtml(e)}</li>`).join('')}</ul></div>`;
                }

            } catch (error) {
                loading.classList.remove('active');
                results.style.display = 'block';
                results.innerHTML = `<div class="status error">✗ Request failed: ${escapeHtml(error.message)}</div>`;
            } finally {
                btn.disabled = false;
            }
        });

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
"""


def create_flask_app():
    """Create Flask app for demo interface."""
    if not HAS_FLASK:
        raise ImportError("Flask is required. Install with: pip install flask")

    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template_string(DEMO_HTML)

    @app.route("/api/discover-from-text", methods=["POST"])
    def api_discover():
        """API endpoint for workflow discovery."""
        try:
            from pm4py.api.endpoints import discover_from_text_json
            from pm4py.algo.dspy.powl import DiscoverRequest

            json_body = request.get_json()

            result = discover_from_text_json(json_body)
            return jsonify(result)

        except Exception as e:
            return jsonify({
                'success': False,
                'errors': [str(e)],
                'timestamp': ''
            }), 500

    return app


def create_fastapi_app():
    """Create FastAPI app for demo interface."""
    if not HAS_FASTAPI:
        raise ImportError("FastAPI is required. Install with: pip install fastapi uvicorn")

    from pm4py.api.endpoints import create_app

    app = create_app()

    @app.get("/", response_class=HTMLResponse)
    async def index():
        return DEMO_HTML

    return app


def run_demo(host: str = "127.0.0.1", port: int = 8080, framework: str = "auto"):
    """Run the demo server.

    Parameters
    ----------
    host : str
        Host to bind to.
    port : int
        Port to bind to.
    framework : str
        Framework to use ('auto', 'flask', 'fastapi').
    """
    if framework == "auto":
        if HAS_FASTAPI:
            framework = "fastapi"
        elif HAS_FLASK:
            framework = "flask"
        else:
            raise ImportError("Neither FastAPI nor Flask is available. "
                                "Install with: pip install fastapi uvicorn OR pip install flask")

    print(f"Starting PM4Py Discovery Demo on http://{host}:{port}")
    print(f"Framework: {framework}")

    if framework == "fastapi":
        app = create_fastapi_app()
        import uvicorn
        uvicorn.run(app, host=host, port=port)
    else:
        app = create_flask_app()
        app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    import sys
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    framework = sys.argv[3] if len(sys.argv) > 3 else "auto"
    run_demo(host, port, framework)
