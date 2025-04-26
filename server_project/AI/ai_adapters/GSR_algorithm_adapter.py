import logging
from typing import List

from AI.ai_adapters.aialgorithm import AIAlgorithm
from AI.algorithms.GSR import GSRAlgorithm
from AI.algorithms.basic_algorithm import BasicAlgorithm
import datetime
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from objects.message_record import MessageRecord


class GSRAlgorithmAdapter(AIAlgorithm):

    def __init__(self):
        self.model = GSRAlgorithm()
        self.logged_already = {}

    def get_name(self):
        return "GSR"

    def update_config(self, config: json) -> json:
        pass

    def reference_to_analyze(self, data: dict[str, [MessageRecord]]) -> {str, json}:
        data_to_analyze: list[tuple[list[str], list[str]]] = []
        for messages in data.values():
            data_to_analyze.append(self._extract_role_text(messages))
        #print(f"start analyze reference_to_analyze")
        response = self.model.process(data_to_analyze)
        self.log_res(data.keys(),response)
        return self.convert_to_internal_response(data.keys(), response)

    def convert_to_internal_response(self, conversations_ids, response):
        # Initialize an empty dictionary to store the results
        internal_response = {}

        # Iterate over the conversation IDs and corresponding responses
        for conv_id, resp in zip(conversations_ids, response):
            # Extract value2 from the response
            value2 = resp[1]

            # Create JSON object with "basic algorithm result" as key and value2 as value
            json_response = json.dumps({"GSR": str(value2)})

            # Assign the JSON object to the corresponding conversation ID in the dictionary
            internal_response[conv_id] = json_response

        return internal_response

    def _extract_role_text(self, messages: List[MessageRecord]) -> tuple[List[str], List[str]]:
        roles: List[str] = []
        texts: List[str] = []
        for message in messages:
            if 'msg' in message.messageData and message.messageData['msg'] is not None and message.sentBy is not None:
                texts.append(message.messageData['msg']['text'])
                if message.sentBy == "Agent":
                    roles.append("counselor")
                elif message.sentBy == "Consumer":
                    roles.append("help seeker")
                else:
                    logging.warning(f"Unrecognized message sendBy {message.sentBy}, message ID: {message.messageId}, conversation ID: {message.dialogId}")
        return roles, texts

    # for tests only
    def reference_to_analyze_test(self, data: List[str]):
        return self.model.process(data)
