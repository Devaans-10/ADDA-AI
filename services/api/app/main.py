import secrets
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum

from app.config import Settings
from app.graph import build_graph
from app.providers import CodingProvider, ProviderError
from app.schemas import ChatRequest, ChatResponse


def create_app(settings: Settings | None = None, provider: CodingProvider | None = None) -> FastAPI:
    settings = settings or Settings()
    graph = build_graph(provider or CodingProvider(settings))
    app = FastAPI(title='NexusAI API', version='0.1.0')
    app.add_middleware(
        CORSMiddleware, allow_origins=settings.origins,
        allow_methods=['GET', 'POST'], allow_headers=['Content-Type', 'X-Demo-Token'],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request: Request, _exc: RequestValidationError):
        return JSONResponse(status_code=422, content={'detail': {
            'code': 'invalid_request',
            'message': 'Send a nonblank message of at most 12,000 characters and a supported agent.',
        }})

    def authorize(x_demo_token: str | None = Header(default=None)):
        if settings.demo_access_token and not secrets.compare_digest(
            (x_demo_token or '').encode(), settings.demo_access_token.encode()
        ):
            raise HTTPException(401, detail={'code': 'unauthorized', 'message': 'Enter the demo access token.'})

    @app.get('/health')
    def health():
        return {'status': 'ok', 'provider': settings.nexus_provider,
                'capabilities': {'coding': True, 'document': False, 'search': False, 'research': False}}

    @app.post('/api/chat', response_model=ChatResponse, dependencies=[Depends(authorize)])
    def chat(body: ChatRequest):
        request_id = str(uuid4())
        try:
            state = graph.invoke({'message': body.message, 'requested_agent': body.agent,
                                  'agent': '', 'answer': '', 'activity': []})
        except ProviderError as exc:
            raise HTTPException(exc.status, detail={
                'code': exc.code, 'message': exc.message, 'request_id': request_id,
            }) from exc
        return ChatResponse(request_id=request_id, agent=state['agent'], answer=state['answer'],
                            provider=settings.nexus_provider, activity=state['activity'])

    return app


app = create_app()
handler = Mangum(app, lifespan='off')
