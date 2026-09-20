import secrets
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Request, UploadFile, File
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum

from app.config import Settings
from app.graph import build_graph
from app.providers import CodingProvider, ProviderError
from app.schemas import ChatRequest, ChatResponse
from app.agents.document import DocumentStore, MAX_BYTES
from app.agents.s3_document import S3DocumentStore
from app.body_limit import BodyLimit


def create_app(settings: Settings | None = None, provider: CodingProvider | None = None) -> FastAPI:
    settings = settings or Settings()
    documents = S3DocumentStore(settings.document_bucket) if settings.document_bucket else DocumentStore()
    graph = build_graph(provider or CodingProvider(settings), documents)
    app = FastAPI(title='ADDA AI API', version='0.1.0')
    app.add_middleware(BodyLimit)
    app.add_middleware(
        CORSMiddleware, allow_origins=settings.origins,
        allow_methods=['GET', 'POST', 'DELETE'], allow_headers=['Content-Type', 'X-Demo-Token', 'X-Document-Token'],
    )

    @app.exception_handler(ProviderError)
    async def provider_error(_request: Request, exc: ProviderError):
        return JSONResponse(status_code=exc.status, content={'detail': {
            'code': exc.code, 'message': exc.message,
        }})

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
                'capabilities': {'coding': True, 'document': settings.document_enabled,
                                 'search': settings.search_enabled, 'research': settings.document_enabled or settings.search_enabled},
                'limits': {'upload_bytes': MAX_BYTES, 'document_pages': 30, 'document_ttl_seconds': 3600},
                'research_mode': 'attached document, or Tavily when configured'}

    @app.post('/api/documents', dependencies=[Depends(authorize)])
    def upload_document(file: UploadFile = File(...)):
        try:
            if not settings.document_enabled:
                raise ProviderError('Document storage is unavailable in this deployment.', 'documents_disabled', 503)
            data = file.file.read(MAX_BYTES + 1)
            return documents.ingest(data, file.filename or 'upload')
        finally:
            file.file.close()

    @app.post('/api/documents/demo', dependencies=[Depends(authorize)])
    def demo_document():
        if not settings.document_enabled:
            raise ProviderError('Document storage is unavailable in this deployment.', 'documents_disabled', 503)
        source = Path(__file__).parent / 'samples' / 'atlas-project.pdf'
        return documents.ingest(source.read_bytes(), source.name)

    @app.delete('/api/documents/{document_id}', dependencies=[Depends(authorize)])
    def delete_document(document_id: str, x_document_token: str = Header(default='')):
        documents.delete(document_id, x_document_token)
        return {'deleted': True}

    @app.post('/api/chat', response_model=ChatResponse, dependencies=[Depends(authorize)])
    def chat(body: ChatRequest, x_document_token: str = Header(default='')):
        request_id = str(uuid4())
        try:
            if body.document_id and not settings.document_enabled:
                raise ProviderError('Document storage is unavailable in this deployment.', 'documents_disabled', 503)
            state = graph.invoke({'message': body.message, 'requested_agent': body.agent,
                                  'agent': '', 'answer': '', 'activity': [], 'citations': [],
                                  'document_id': body.document_id, 'document_token': x_document_token,
                                  'provider': settings.nexus_provider, 'plan': [], 'collection': {}})
        except ProviderError as exc:
            raise HTTPException(exc.status, detail={
                'code': exc.code, 'message': exc.message, 'request_id': request_id,
            }) from exc
        return ChatResponse(request_id=request_id, agent=state['agent'], answer=state['answer'],
                            provider=state['provider'], activity=state['activity'],
                            citations=state.get('citations') or [])

    return app


app = create_app()
handler = Mangum(app, lifespan='off')
