import uuid
from typing import Optional, Any, Dict

from langchain_core.callbacks import CallbackManagerForChainRun
from langchain_core.outputs import LLMResult
from langchain_openai.chat_models.azure import AzureChatOpenAI
from langchain_openai.chat_models.base import ChatOpenAI

MissingProjectError = ValueError("project name is required, it will separate the traces in the tracing system")


class ChainResult:
    def __init__(self, result, run_id: uuid):
        self.result = result
        self.run_id = run_id


class BaseChain:
    def __init__(self, llm: AzureChatOpenAI, project_name: str):
        self.llm = llm
        self.project_name = project_name
        if not project_name or project_name == "":
            raise MissingProjectError

    def invoke(
            self,
            prompt: Dict[str, Any],
            memory: Optional[Any] = None,
    ) -> ChainResult:
        run_manager = CallbackManagerForChainRun.get_noop_manager()

        try:
            from langchain_core.tracers.context import tracing_v2_enabled
            with tracing_v2_enabled(project_name=self.project_name):
                response = self.llm.invoke(prompt)
                run_manager.on_chain_end(outputs={"result": response})

        except Exception as e:
            run_manager.on_chain_error(error=e)
            raise

        return ChainResult(result=response, run_id=run_manager.run_id)


class LLMConfig:
    def __init__(self, model_name: str, temperature: float, max_tokens: int, api_key: str):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key


class LLMFactory:
    @staticmethod
    def create_llm(llm_config: LLMConfig = None, **kwargs: Any) -> AzureChatOpenAI:
        return AzureChatOpenAI(
            model_name=llm_config.model_name,
            temperature=llm_config.temperature,
            max_tokens=llm_config.max_tokens,
            api_key=llm_config.api_key, **kwargs)

    @staticmethod
    def create_chain(project_name: str) -> BaseChain:
        return BaseChain(project_name=project_name, llm=LLMFactory.create_llm())


