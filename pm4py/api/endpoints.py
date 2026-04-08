"""
API endpoints for pm4py LLM-native process discovery.

Provides REST API for natural language → executable workflow pipeline.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DiscoverRequest:
    """Request model for process discovery from text."""
    description: str
    workflow_name: str = "GeneratedWorkflow"
    formats: List[str] = field(default_factory=lambda: ['powl', 'bpmn'])
    model: str = "groq/openai/gpt-oss-20b"
    max_refinements: int = 1


@dataclass
class DiscoverResponse:
    """Response model for process discovery from text."""
    success: bool
    workflow_name: str
    powl: Optional[str] = None
    verdict: Optional[bool] = None
    reasoning: Optional[str] = None
    feedback: Optional[str] = None
    refinements: int = 0
    generated_code: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    timestamp: str = ""


def discover_from_text(request: DiscoverRequest) -> DiscoverResponse:
    """Generate workflow from natural language description.

    Parameters
    ----------
    request : DiscoverRequest
        The discovery request containing description and options.

    Returns
    -------
    DiscoverResponse
        Response with POWL model and generated code.
    """
    try:
        from pm4py.algo.dspy.powl.natural_language import generate_powl_from_text
        from pm4py.algo.dspy.powl.codegen import generate_all_orchestrator_code

        # Validate requested formats
        valid_formats = {'powl', 'bpmn', 'n8n', 'temporal', 'yawl'}
        for fmt in request.formats:
            if fmt not in valid_formats:
                return DiscoverResponse(
                    success=False,
                    workflow_name=request.workflow_name,
                    errors=[f"Invalid format: {fmt}. Valid options: {', '.join(valid_formats)}"]
                )

        # Generate POWL from text
        powl_result = generate_powl_from_text(
            process_description=request.description,
            model=request.model,
            max_refinements=request.max_refinements
        )

        # Build response
        response = DiscoverResponse(
            success=powl_result.get('verdict', False),
            workflow_name=request.workflow_name,
            powl=powl_result.get('powl'),
            verdict=powl_result.get('verdict'),
            reasoning=powl_result.get('reasoning'),
            feedback=powl_result.get('feedback'),
            refinements=powl_result.get('refinements', 0),
            timestamp=datetime.now().isoformat()
        )

        if not response.success:
            response.errors.append(f"POWL generation failed: {response.reasoning}")
            return response

        # Generate orchestrator code if requested
        code_formats = [f for f in request.formats if f != 'powl']
        if code_formats:
            try:
                code_result = generate_all_orchestrator_code(
                    powl_string=response.powl,
                    workflow_name=request.workflow_name,
                    formats=code_formats
                )

                if code_result.n8n_json and 'n8n' in request.formats:
                    response.generated_code['n8n'] = code_result.n8n_json

                if code_result.temporal_go and 'temporal' in request.formats:
                    response.generated_code['temporal_go'] = code_result.temporal_go

                if code_result.camunda_bpmn and 'bpmn' in request.formats:
                    response.generated_code['bpmn'] = code_result.camunda_bpmn

                if code_result.yawl_xml and 'yawl' in request.formats:
                    response.generated_code['yawl'] = code_result.yawl_xml

                response.errors.extend(code_result.errors)

            except Exception as e:
                response.errors.append(f"Code generation failed: {str(e)}")

        return response

    except Exception as e:
        return DiscoverResponse(
            success=False,
            workflow_name=request.workflow_name,
            errors=[f"Discovery failed: {str(e)}"],
            timestamp=datetime.now().isoformat()
        )


def discover_from_text_json(json_body: Dict[str, Any]) -> Dict[str, Any]:
    """JSON-serializable wrapper for discover_from_text.

    Parameters
    ----------
    json_body : dict
        JSON request body with keys: description, workflow_name, formats, model, max_refinements

    Returns
    -------
    dict
        JSON-serializable response.
    """
    request = DiscoverRequest(
        description=json_body.get('description', ''),
        workflow_name=json_body.get('workflow_name', 'GeneratedWorkflow'),
        formats=json_body.get('formats', ['powl', 'bpmn']),
        model=json_body.get('model', 'groq/openai/gpt-oss-20b'),
        max_refinements=json_body.get('max_refinements', 1)
    )

    response = discover_from_text(request)

    return {
        'success': response.success,
        'workflow_name': response.workflow_name,
        'powl': response.powl,
        'verdict': response.verdict,
        'reasoning': response.reasoning,
        'feedback': response.feedback,
        'refinements': response.refinements,
        'generated_code': response.generated_code,
        'errors': response.errors,
        'timestamp': response.timestamp
    }


# FastAPI app factory
def create_app() -> Any:
    """Create and configure FastAPI application.

    Returns
    -------
    FastAPI app
        Configured FastAPI application.
    """
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel, Field

        app = FastAPI(
            title="PM4Py Process Discovery API",
            description="Generate executable workflows from natural language descriptions",
            version="1.0.0"
        )

        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Request/Response models
        class DiscoverRequestModel(BaseModel):
            description: str = Field(..., description="Process description in natural language")
            workflow_name: str = Field(default="GeneratedWorkflow", description="Name for the workflow")
            formats: List[str] = Field(default=['powl', 'bpmn'], description="Output formats")
            model: str = Field(default="groq/openai/gpt-oss-20b", description="LLM model to use")
            max_refinements: int = Field(default=1, ge=0, le=5, description="Max refinement iterations")

        class DiscoverResponseModel(BaseModel):
            success: bool
            workflow_name: str
            powl: Optional[str] = None
            verdict: Optional[bool] = None
            reasoning: Optional[str] = None
            feedback: Optional[str] = None
            refinements: int = 0
            generated_code: Dict[str, Any] = {}
            errors: List[str] = []
            timestamp: str

        @app.get("/")
        async def root():
            return {
                "service": "PM4py Process Discovery API",
                "version": "1.0.0",
                "endpoints": {
                    "POST /api/discover-from-text": "Generate workflow from text",
                    "GET /api/health": "Health check"
                }
            }

        @app.get("/api/health")
        async def health_check():
            return {"status": "healthy", "service": "pm4py-discovery"}

        @app.post("/api/discover-from-text", response_model=DiscoverResponseModel)
        async def api_discover_from_text(request_body: DiscoverRequestModel):
            """Generate workflow from natural language description."""
            json_body = {
                'description': request_body.description,
                'workflow_name': request_body.workflow_name,
                'formats': request_body.formats,
                'model': request_body.model,
                'max_refinements': request_body.max_refinements
            }

            result = discover_from_text_json(json_body)

            if not result['success']:
                raise HTTPException(status_code=400, detail=result['errors'])

            return DiscoverResponseModel(**result)

        return app

    except ImportError:
        # FastAPI not available, return None
        return None


def run_server(host: str = "0.0.0.0", port: int = 8002, log_level: str = "info"):
    """Run the FastAPI server.

    Parameters
    ----------
    host : str
        Host to bind to.
    port : int
        Port to bind to.
    log_level : str
        Logging level.
    """
    app = create_app()
    if app is None:
        raise ImportError("FastAPI is required. Install with: pip install fastapi uvicorn")

    import uvicorn
    uvicorn.run(app, host=host, port=port, log_level=log_level)
