import httpx
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.request = httpx.Request('POST', 'https://api.tavily.com/search')

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                'error', request=self.request,
                response=httpx.Response(self.status_code, request=self.request),
            )

    def json(self):
        return self._payload


def _app(monkeypatch, payload=None, status_code=200, error=None, key='test-search-key'):
    captured = {}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            captured['timeout'] = kwargs.get('timeout')

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def post(self, url, headers=None, json=None):
            captured['url'] = url
            captured['headers'] = headers or {}
            captured['json'] = json or {}
            if error:
                raise error
            return FakeResponse(status_code, payload)

    monkeypatch.setattr('app.agents.search.httpx.Client', FakeClient)
    client = TestClient(create_app(Settings(
        _env_file=None, nexus_provider='demo', demo_access_token='', tavily_api_key=key,
    )))
    return client, captured


def test_search_returns_tavily_citations(monkeypatch):
    payload = {
        'answer': 'Agent frameworks keep expanding tool use.',
        'results': [
            {'title': 'AI agent news', 'url': 'https://example.com/agents', 'content': 'New agent runtimes shipped.'},
            {'title': 'Also agents', 'url': 'https://example.org/ai', 'content': 'Orchestrators gained memory.'},
        ],
    }
    client, captured = _app(monkeypatch, payload)
    result = client.post('/api/chat', json={'message': 'What are the latest developments in AI agents?'})
    assert result.status_code == 200
    body = result.json()
    assert body['agent'] == 'search'
    assert [a['step'] for a in body['activity']] == ['Router', 'Search agent']
    assert body['citations'] == [
        {'id': 's1', 'title': 'AI agent news', 'url': 'https://example.com/agents', 'page': None, 'document_id': None, 'excerpt': 'New agent runtimes shipped.'},
        {'id': 's2', 'title': 'Also agents', 'url': 'https://example.org/ai', 'page': None, 'document_id': None, 'excerpt': 'Orchestrators gained memory.'},
    ]
    assert 'AI agent news' in body['answer']
    assert 'Agent frameworks keep expanding tool use.' in body['answer']
    assert body['provider'] == 'tavily'
    assert 'https://not-from-tavily.example' not in body['answer']
    assert 'test-search-key' not in result.text
    assert captured['json']['query'] == 'What are the latest developments in AI agents?'
    assert captured['json']['include_answer'] is True
    assert captured['json']['max_results'] == 5
    assert 'api_key' not in captured['json']


def test_explicit_search_bedrock_updates(monkeypatch):
    payload = {
        'answer': 'Bedrock added new inference profiles.',
        'results': [{'title': 'Bedrock update', 'url': 'https://aws.example/bedrock', 'content': 'Nova models expanded.'}],
    }
    client, _captured = _app(monkeypatch, payload)
    result = client.post('/api/chat', json={
        'message': 'Search the web for recent AWS Bedrock updates.', 'agent': 'search',
    })
    assert result.status_code == 200
    body = result.json()
    assert body['agent'] == 'search'
    assert body['citations'][0]['url'] == 'https://aws.example/bedrock'


def test_search_drops_non_http_urls(monkeypatch):
    payload = {'results': [
        {'title': 'Bad', 'url': 'javascript:alert(1)'},
        {'title': 'Good', 'url': 'https://example.com/ok', 'content': 'Usable source.'},
    ]}
    client, _captured = _app(monkeypatch, payload)
    body = client.post('/api/chat', json={'message': 'latest news'}).json()
    assert [item['url'] for item in body['citations']] == ['https://example.com/ok']


def test_empty_tavily_results_are_honest(monkeypatch):
    client, _captured = _app(monkeypatch, {'answer': 'Invented summary with no sources.', 'results': []})
    result = client.post('/api/chat', json={'message': 'latest news'})
    assert result.status_code == 200
    body = result.json()
    assert body['citations'] == []
    assert 'No web sources were returned' in body['answer']
    assert 'Invented summary' not in body['answer']
    assert 'no usable source URLs' in body['activity'][-1]['detail']


def test_search_provider_failure_does_not_leak_key(monkeypatch):
    client, _captured = _app(monkeypatch, status_code=500)
    result = client.post('/api/chat', json={'message': 'latest news'})
    assert result.status_code == 502
    assert result.json()['detail']['code'] == 'search_unavailable'
    assert 'test-search-key' not in result.text
    assert 'answer' not in result.json()


def test_health_reports_search_when_configured():
    client = TestClient(create_app(Settings(
        _env_file=None, nexus_provider='demo', tavily_api_key='test-search-key', demo_access_token='',
    )))
    health = client.get('/health').json()
    assert health['capabilities']['search'] is True
    assert health['capabilities']['coding'] is True
    assert health['capabilities']['document'] is True


def test_coding_fixture_still_works_when_search_is_configured(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Coding must not call Tavily')
    monkeypatch.setattr('app.agents.search.httpx.Client', forbidden)
    client = TestClient(create_app(Settings(
        _env_file=None, nexus_provider='demo', tavily_api_key='test-search-key', demo_access_token='',
    )))
    result = client.post('/api/chat', json={'message': 'Write a Python function to reverse a string.'})
    assert result.status_code == 200
    assert result.json()['agent'] == 'coding'
    assert 'not an AI-generated answer' in result.json()['answer']
    assert result.json()['citations'] == []
