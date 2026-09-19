import re
from time import perf_counter
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.providers import CodingProvider, ProviderError


class AgentState(TypedDict):
    message: str
    requested_agent: str
    agent: str
    answer: str
    activity: list[dict]


def select_agent(message: str, requested_agent: str) -> tuple[str, str]:
    if requested_agent != 'auto':
        return requested_agent, 'Selected explicitly in the request.'
    # Deterministic first milestone router. Visible in the trace; no claim of LLM classification.
    routes = [
        ('document', r'\b(pdf|document|uploaded|attachment)\b'),
        ('research', r'\b(research|compare|investigate)\b'),
        ('search', r'\b(search|latest|news|today|web)\b'),
        ('coding', r'\b(code|coding|python|javascript|typescript|react|function|debug|bug|sql)\b'),
    ]
    for agent, pattern in routes:
        if re.search(pattern, message, re.IGNORECASE):
            return agent, f'Keyword router matched {agent} intent.'
    return 'coding', 'First milestone fallback to Coding; ask a programming question.'


def build_graph(provider: CodingProvider):
    def route(state: AgentState):
        started = perf_counter()
        agent, reason = select_agent(state['message'], state['requested_agent'])
        return {'agent': agent, 'activity': [{
            'step': 'Router', 'status': 'completed', 'detail': reason,
            'duration_ms': round((perf_counter() - started) * 1000),
        }]}

    def coding(state: AgentState):
        started = perf_counter()
        answer = provider.generate(state['message'])
        mode = 'Offline fixed fixture returned; no AI call.' if provider.settings.nexus_provider == 'demo' else 'Bedrock Converse returned an answer; code was not executed.'
        return {'answer': answer, 'activity': state['activity'] + [{
            'step': 'Coding agent', 'status': 'completed', 'detail': mode,
            'duration_ms': round((perf_counter() - started) * 1000),
        }]}

    def unavailable(state: AgentState):
        raise ProviderError(
            f"The {state['agent']} agent is planned for the next milestone. Try a Coding task.",
            'agent_not_implemented', 501,
        )

    graph = StateGraph(AgentState)
    graph.add_node('route', route)
    graph.add_node('coding', coding)
    graph.add_node('unavailable', unavailable)
    graph.add_edge(START, 'route')
    graph.add_conditional_edges('route', lambda s: 'coding' if s['agent'] == 'coding' else 'unavailable')
    graph.add_edge('coding', END)
    graph.add_edge('unavailable', END)
    return graph.compile()
