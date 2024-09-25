from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from actions_extractor.base import ActionsExtractor
from actions_extractor.models import Actions


class LLMActionsExtractor(ActionsExtractor):
    def __init__(self, model: str ="mistral-nemo", temperature: float = 0.0, base_url: str = "http://ollama:11434") -> None:
        self._llm = ChatOllama(model=model, temperature=temperature, base_url=base_url)
        self._SYSTEM_PROMPT = """"
            You are now an expert in understanding heritage documents. 
            In these documents, you will find many articles and paragraphs that describe various rules and actions that a heritage site owner must comply with.
            Extract all the relevant information you can find to help the heritage site owner understand what action he can or cannot perform.
            In the end, provide all actions that can be performed without a permit, all actions for which he needs a permit, and all actions that cannot be performed at all.
            Make sure that the actions are comprehensive, well-written and include all points.
            List all the actions that an owner can or cannot perform on his heritage. You can give own interpretations.
            Important that you keep everything in dutch.
            Very important that you ALWAYS use this output structure:
            {format_instructions}
            """
        self._USER_PROMPT = """Haal op basis van de systeeminstructies de acties uit dit erfgoeddocument: {paper}. 
            Retourneer het resultaat als een JSON-object, volgens dit voorbeeld {format_instructions}."""
        self._output_parser = PydanticOutputParser(pydantic_object=Actions)

    def extract_actions(self, text: str) -> Actions:
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    self._SYSTEM_PROMPT,
                ),
                ("human", self._USER_PROMPT),
            ]
        ).partial(format_instructions=self._output_parser.get_format_instructions())
        chain = prompt_template | self._llm | self._output_parser
        actions = chain.invoke({"paper": text})

        return actions

        allowed_actions_data = []
        if actions.allowed_action_list:
            allowed_actions_data = [
                {'TextFragment': allowed_action.action, 'Forbidden': False, 'PermitNeeded': allowed_action.permit_needed}
                for allowed_action in actions.allowed_action_list
            ]

        not_allowed_actions_data = []
        if actions.not_allowed_action_list:
            not_allowed_actions_data = [
                {'TextFragment': not_allowed_action.action, 'Forbidden': True, 'PermitNeeded':  not_allowed_action.permit_needed}
                for not_allowed_action in actions.not_allowed_action_list
            ]
        # Combine both lists
        all_actions_data = allowed_actions_data + not_allowed_actions_data
        filtered_data = [item for item in all_actions_data if item['TextFragment'] is not None]

        csv_file = OUTPUT_DIR / 'actions_some_besluit.csv'
        write_output_csv(actions=filtered_data, output_path=csv_file)
        return all_actions_data
