from __future__ import annotations

import logging
from collections.abc import Awaitable, Sequence
from typing import Any, Literal, overload

import agent_framework

logger = logging.getLogger(__name__)


class OrchestratorAgent(agent_framework.Agent):
    def __init__(
        self,
        chat_client: agent_framework.BaseChatClient,
        context_providers: Sequence[agent_framework.BaseContextProvider] | None = None,
    ) -> None:
        super().__init__(
            client=chat_client,
            name="OrchestratorAgent",
            description="Orchestrator agent that delegates tasks to worker agents.",
            instructions=(
                "You are an orchestrator agent that delegates tasks to skills. "
                "You have access to live Financial Data APIs that provide stock quotes, portfolio holdings, "
                "and market indices. When the user asks about 'our holdings', 'our portfolio', or any "
                "financial data, retrieve it using the available skills — NEVER ask the user to provide "
                "this data. All portfolio, stock, and index data is available through the APIs."
            ),
            context_providers=context_providers,
        )
        logger.info("OrchestratorAgent initialized.")

    @overload
    def run(
        self,
        messages: agent_framework.AgentRunInputs | None = ...,
        *,
        stream: Literal[False] = ...,
        session: agent_framework.AgentSession | None = ...,
        **kwargs: Any,
    ) -> Awaitable[agent_framework.AgentResponse[Any]]: ...

    @overload
    def run(
        self,
        messages: agent_framework.AgentRunInputs | None = ...,
        *,
        stream: Literal[True],
        session: agent_framework.AgentSession | None = ...,
        **kwargs: Any,
    ) -> agent_framework.ResponseStream[
        agent_framework.AgentResponseUpdate, agent_framework.AgentResponse[Any]
    ]: ...

    def run(  # type: ignore[override]
        self,
        messages: agent_framework.AgentRunInputs | None = None,
        *,
        stream: bool = False,
        session: agent_framework.AgentSession | None = None,
        **kwargs: Any,
    ) -> (
        Awaitable[agent_framework.AgentResponse[Any]]
        | agent_framework.ResponseStream[
            agent_framework.AgentResponseUpdate, agent_framework.AgentResponse[Any]
        ]
    ):

        if not stream:
            return super().run(messages, stream=False, session=session, **kwargs)

        response_stream = super().run(messages, stream=True, session=session, **kwargs)

        return response_stream
