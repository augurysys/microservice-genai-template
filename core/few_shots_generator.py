from ai_logger.log_wrapper import LogWrapper
from langchain.chains.conversation.base import ConversationChain
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate


class MissingField(Exception):
    def __init__(self, message, error_code=None):
        super().__init__(message)
        self.error_code = error_code


class FewShotsGenerator:
    def __init__(self, few_shots: list, base_prompt: str, domain_data: str,
                 parser, query: str, llm, logger: LogWrapper, memory=None):
        self.few_shots = few_shots
        self.base_prompt = base_prompt
        self.domain_data = domain_data
        self.parser = parser or JsonOutputParser()
        self.query = query
        self.llm = llm
        self.memory = memory
        self.logger = logger
        self.validate_input()

    @staticmethod
    def get_final_prompt_template() -> PromptTemplate:
        return PromptTemplate(
            template="Input: {input}",
            input_variables=["input"]
        )

    def get_prompt_template(self) -> str:
        example_prompt = PromptTemplate(
            template="""
            {base_prompt}\n
            Examples:
            {few_shots}\n
            {query}
            Specific Data:
            {domain_data}\n
            Output Instructions:
            Please provide your JSON result in the following format:
            {output_instructions}\n
            """,
            input_variables=["base_prompt", "few_shots", "domain_data", "output_instructions", "query"]
        )
        return example_prompt.format(base_prompt=self.base_prompt,
                                     few_shots=self.get_few_shots_prompt().format(),
                                     domain_data=self.domain_data,
                                     output_instructions=self.parser.get_format_instructions(),
                                     query=self.query)

    def get_few_shots_prompt(self) -> FewShotPromptTemplate:
        example_prompt = PromptTemplate(
            template="Input: {input}\nOutput: {output}",
            input_variables=["input", "output"]
        )
        return FewShotPromptTemplate(
            example_prompt=example_prompt,
            examples=self.few_shots,
            suffix="",
            input_variables=["input", "output"]
        )

    def generate(self) -> dict:
        try:
            self.logger.info("starting to generate with few shots")
            prompt = self.get_prompt_template()
            final_prompt = FewShotsGenerator.get_final_prompt_template()
            self.logger.info(f"prompt: {prompt}")
            self.logger.info(f"executing chain")
            try:
                conversation = ConversationChain(
                    llm=self.llm,
                    memory=self.memory,
                    prompt=final_prompt
                )
                res = conversation.run_chain(prompt_template=final_prompt, prompt={"input": prompt})
                self.logger.info(res)
            except Exception as e:
                self.logger.info(f"failed to execute chain: {e}")
                raise e
            try:
                parsed = self.parser.parse(res)
                self.logger.info(f"parsed output {parsed}")
                return parsed
            except Exception as e:
                self.logger.info(f"failed to parse response from model response: {e}")
                raise e
        except Exception as e:
            self.logger.info(f"failed to generate with few shots: {e}")
            raise e

    def validate_input(self):
        if self.llm is None:
            raise MissingField("missing llm")
        if self.few_shots is None or len(self.few_shots) == 0:
            raise MissingField("missing few shots")
        if self.base_prompt is None or len(self.base_prompt) == 0:
            raise MissingField("missing base_prompt")
        if self.domain_data is None or len(self.domain_data) == 0:
            raise MissingField("missing domain_data")
        if self.query is None or len(self.query) == 0:
            raise MissingField("missing query")

