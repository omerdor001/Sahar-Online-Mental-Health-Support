from typing import List

from AI.ai_adapters.aialgorithm import AIAlgorithm
from AI.algorithms.basic_algorithm import BasicAlgorithm

import json

from objects.message_record import MessageRecord


class BasicAlgorithmAdapter(AIAlgorithm):

    def __init__(self):
        self.model = BasicAlgorithm()

    def get_name(self):
        return "Basic Algorithm Adapter"

    def update_config(self, config: json) -> json:
        pass

    def reference_to_analyze(self, data: dict[str, [MessageRecord]]) -> {str, json}:
        text_to_analyze: [str] = []
        for messages in data.values():
            messages = super().extract_hebrew_consumer_messages(messages)
            text_to_analyze.append(self._convert_to_str(messages))
        response = self.model.process(text_to_analyze)
        return self.convert_to_internal_response(data.keys(), response)

    def convert_to_internal_response(self, conversations_ids, response):
        # Initialize an empty dictionary to store the results
        internal_response = {}

        # Iterate over the conversation IDs and corresponding responses
        for conv_id, resp in zip(conversations_ids, response):
            # Extract value2 from the response
            value2 = resp[1]

            # Create JSON object with "basic algorithm result" as key and value2 as value
            json_response = json.dumps({"basic_algorithm_result": str(value2)})

            # Assign the JSON object to the corresponding conversation ID in the dictionary
            internal_response[conv_id] = json_response

        return internal_response

    # for tests only
    def reference_to_analyze_test(self, data: List[str]):
        return self.model.process(data)

    def _convert_to_str(self, messages: [MessageRecord]) -> str:
        string_parts = []
        for message in messages:
            if message.messageData["msg"] is not None:
                # Append string parts to the list
                string_parts.append(message.messageData["msg"]["text"])

                # Join the string parts to create the final string
        return ",".join(string_parts)

    def _convert_json_to_list(self, data: json) -> [str]:
        """
        Extracts all string values from a JSON object and returns them as a list.

        Args:
            data (json): The JSON object to be processed.

        Returns:
            list: A list containing all string values found in the JSON object.
        """
        strings = []

        # Helper function to recursively traverse the JSON object
        def extract_strings(obj):
            if isinstance(obj, str):
                strings.append(obj)
            elif isinstance(obj, dict):
                for value in obj.values():
                    extract_strings(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_strings(item)

        # Start the recursive traversal
        extract_strings(data)

        return strings
