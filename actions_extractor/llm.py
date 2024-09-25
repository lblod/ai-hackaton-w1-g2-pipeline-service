from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from actions_extractor.base import ActionsExtractor
from actions_extractor.models import Actions, ActionFragment, MeasureType, ActionCategory


class LLMActionsExtractor(ActionsExtractor):
    def __init__(self, model: str ="mistral-nemo", temperature: float = 0.0, base_url: str = "http://ollama:11434") -> None:
        self._llm = ChatOllama(model=model, temperature=temperature, base_url=base_url)
        self._SYSTEM_PROMPT = """"
            You are now an expert in understanding heritage documents and classification of actions. 
            In these documents, you will find many articles and paragraphs that describe various rules and actions that a heritage site owner must comply with.
            Extract all the relevant information you can find to help the heritage site owner understand what action he can or cannot perform.
            In the end, provide all actions that can be performed without a permit, all actions for which he needs a permit, and all actions that cannot be performed at all.
            Make sure that the actions are comprehensive, well-written and include all points.
            List all the actions that an owner can or cannot perform on his heritage. You can give own interpretations.
            Important that you keep everything in dutch.
            Very important that you ALWAYS use this output structure:
            {format_instructions}
            """
        self._USER_PROMPT = """Based on your system prompt retrieve all relevant information from this heritage paper: {paper}.
            For every action also provide what category it belongs to: {action_categories}.
            Return the output as a JSON-object, following this example {format_instructions}."""
        self._output_parser = PydanticOutputParser(pydantic_object=Actions)

    def extract_actions(self, text: str) -> list[ActionFragment]:
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
        actions: Actions = chain.invoke({"paper": text, "action_categories": [e.value for e in ActionCategory]})

        print(actions)

        allowed_action_fragments = [ActionFragment(text_fragment=action.action, measure_type=MeasureType.NEEDS_PERMIT if action.permit_needed else MeasureType.ALLOWED_WITHOUT_PERMIT, category=action.category) for action in actions.allowed_action_list if action.action is not None]
        not_allowed_action_fragments = [ActionFragment(text_fragment=action.action, measure_type=MeasureType.NEEDS_PERMIT if action.permit_needed else MeasureType.FORBIDDEN, category=action.category) for action in actions.not_allowed_action_list if action.action is not None]

        return allowed_action_fragments + not_allowed_action_fragments

        all_actions_data = [
            {'TextFragment': action_item.action, 'Forbidden': action_item.forbidden,
             'PermitNeeded': action_item.permit_needed, 'Category': action_item.category}
            for action_item in actions.action_list
        ]

        return actions

        filtered_data = [item for item in all_actions_data if item['TextFragment'] is not None]

        csv_file = OUTPUT_DIR / 'actions_some_besluit.csv'
        write_output_csv(actions=filtered_data, output_path=csv_file)
        return all_actions_data
