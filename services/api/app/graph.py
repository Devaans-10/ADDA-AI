import re
from time import perf_counter
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.search import MAX_RESULTS, SearchProvider
from app.agents.document import DocumentStore
from app.agents.research import plan_research, collect_research, render_research
from app.providers import CodingProvider, ProviderError


class AgentState(TypedDict):
    message: str
    requested_agent: str
    agent: str
    answer: str
    activity: list[dict]
    citations: list[dict]
    document_id: str | None
    document_token: str
    provider: str
    plan: list[str]
    collection: dict


def select_agent(message: str, requested_agent: str, document_id: str | None = None) -> tuple[str, str]:
    if requested_agent != 'auto':
        return requested_agent, 'Selected explicitly in the request.'
    # Intent rules are visible, deterministic and testable; no claim of model classification.
    if re.search(r'\b(write|implement|debug|fix|explain|refactor|generate|build|review|optimize|compare)\b', message, re.I) and re.search(r'\b(code|coding|function|python|javascript|typescript|react|sql|component|bug)\b', message, re.I):
        return 'coding', 'Programming action and code context detected.'
    if re.search(r'\b(research|investigate|compare)\b', message, re.I):
        return 'research', 'Evidence brief requested; plan, retrieve, and assemble sources.'
    if document_id and not re.search(r'\b(search|latest|news|web)\b', message, re.I):
        return 'document', 'Using the attached document as the evidence source.'
    routes = [
        ('document', r'\b(pdf|document|uploaded|attachment)\b'),
        ('research', r'\b(research|compare|investigate)\b'),
        ('search', r'\b(search|latest|news|today|web|current|recent)\b'),
        ('coding', r'\b(code|coding|python|javascript|typescript|react|function|debug|bug|sql)\b'),
    ]
    for agent, pattern in routes:
        if re.search(pattern, message, re.IGNORECASE):
            return agent, f'Keyword router matched {agent} intent.'
    return 'coding', 'First milestone fallback to Coding; ask a programming question.'


def _next_node(state: AgentState) -> str:
    if state['agent'] == 'coding':
        return 'coding'
    if state['agent'] == 'search':
        return 'search'
    if state['agent'] == 'document':
        return 'document'
    if state['agent'] == 'research':
        return 'research_plan'
    return 'unavailable'


def build_graph(provider: CodingProvider, documents: DocumentStore | None = None):
    search_provider = SearchProvider(provider.settings)
    documents = documents or DocumentStore()

    def route(state: AgentState):
        started = perf_counter()
        agent, reason = select_agent(state['message'], state['requested_agent'], state.get('document_id'))
        return {'agent': agent, 'activity': [{
            'step': 'Router', 'status': 'completed', 'detail': reason,
            'duration_ms': round((perf_counter() - started) * 1000),
        }]}

    def coding(state: AgentState):
        started = perf_counter()
        answer = provider.generate(state['message'])
        mode = 'Offline fixed fixture returned; no AI call.' if provider.settings.nexus_provider == 'demo' else 'Bedrock Converse returned an answer; code was not executed.'
        return {'answer': answer, 'provider': provider.settings.nexus_provider, 'activity': state['activity'] + [{
            'step': 'Coding agent', 'status': 'completed', 'detail': mode,
            'duration_ms': round((perf_counter() - started) * 1000),
        }]}

    def search(state: AgentState):
        started = perf_counter()
        result = search_provider.search(state['message'])
        return {
            'answer': result['answer'],
            'citations': result['citations'],
            'provider': 'tavily',
            'activity': state['activity'] + [{
                'step': 'Search agent', 'status': 'completed',
                'detail': (
                    f"Queried Tavily (basic, max {MAX_RESULTS}). "
                    f"Returned {result['source_count']} source URL(s); no extra citations added."
                    if result['source_count']
                    else 'Queried Tavily; no usable source URLs were returned.'
                ),
                'duration_ms': round((perf_counter() - started) * 1000),
            }],
        }

    def document(state: AgentState):
        started = perf_counter()
        if not state.get('document_id'):
            raise ProviderError('Attach a PDF or text document first.', 'document_required', 422)
        result = documents.answer(state['document_id'], state.get('document_token', ''), state['message'])
        return {'answer': result['answer'], 'citations': result['citations'], 'provider': 'extractive',
                'activity': state['activity'] + [{'step': 'Document retrieval', 'status': 'completed',
                'detail': f"Retrieved {result['source_count']} page passages using local keyword matching.",
                'duration_ms': round((perf_counter() - started) * 1000)}]}

    def research_plan(state: AgentState):
        started = perf_counter()
        plan = plan_research(state['message'])
        return {'plan': plan, 'activity': state['activity'] + [{
            'step': 'Research plan', 'status': 'completed', 'detail': ' | '.join(plan),
            'duration_ms': round((perf_counter() - started) * 1000)}]}

    def research_collect(state: AgentState):
        started = perf_counter()
        collection = collect_research(state['message'], state['plan'], documents,
                                      state.get('document_id'), state.get('document_token', ''), search_provider)
        return {'collection': collection, 'activity': state['activity'] + [{
            'step': 'Collect evidence', 'status': 'completed',
            'detail': f"Completed {len(collection['checks'])} retrieval checks; {len(collection['citations'])} distinct sources/passages.",
            'duration_ms': round((perf_counter() - started) * 1000)}]}

    def research_report(state: AgentState):
        started = perf_counter()
        result = render_research(state['message'], state['collection'])
        return {'answer': result['answer'], 'citations': result['citations'], 'provider': result['provider'],
                'activity': state['activity'] + [{'step': 'Evidence brief', 'status': 'completed',
                'detail': 'Assembled cited excerpts; no unsupported conclusions or model synthesis.',
                'duration_ms': round((perf_counter() - started) * 1000)}]}

    def unavailable(state: AgentState):
        raise ProviderError(
            f"The {state['agent']} agent is planned for the next milestone. Try a Coding task.",
            'agent_not_implemented', 501,
        )

    graph = StateGraph(AgentState)
    graph.add_node('route', route)
    graph.add_node('coding', coding)
    graph.add_node('search', search)
    graph.add_node('document', document)
    graph.add_node('research_plan', research_plan)
    graph.add_node('research_collect', research_collect)
    graph.add_node('research_report', research_report)
    graph.add_node('unavailable', unavailable)
    graph.add_edge(START, 'route')
    graph.add_conditional_edges('route', _next_node)
    graph.add_edge('coding', END)
    graph.add_edge('search', END)
    graph.add_edge('document', END)
    graph.add_edge('research_plan', 'research_collect')
    graph.add_edge('research_collect', 'research_report')
    graph.add_edge('research_report', END)
    graph.add_edge('unavailable', END)
    return graph.compile()
