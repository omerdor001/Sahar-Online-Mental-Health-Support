import datetime
from abc import ABC, abstractmethod
import json
from typing import List
import logging
from objects.message_record import MessageRecord


class AIAlgorithm(ABC):
    logged_already: dict[str, list[float]]
    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def update_config(self, config: json):
        pass

    @abstractmethod
    def reference_to_analyze(
        self, data: dict[str, [MessageRecord]]
    ) -> {str, json}:  # {field name, value}
        pass

    def extract_hebrew_consumer_messages(
        cls, messages: List[MessageRecord]
    ) -> List[MessageRecord]:
        sorted_messages: List[MessageRecord] = []
        for message in messages:
            if getattr(message, "sentBy", None) == "Consumer":
                if message.messageData["msg"] is not None:
                    sorted_messages.append(message)
        # todo - filter by hebrew
        return sorted_messages
    
    def log_res(self, conv_ids, predictions):
        try:
            for conv_id, pred in zip(conv_ids,predictions):
                if self.needLogging(conv_id,pred):
                    logging.info(f"algorithm:{self.get_name()} made a prodiction:{pred} with regards to conversation ID:{conv_id}")
                    self.logged_already[conv_id] = pred
            for key in list(self.logged_already.keys()):  # Create a list of keys to iterate over
                if key not in conv_ids:
                    del self.logged_already[key]  # Safe to delete from the dictionary
        except Exception as e:
            print(e)

    def needLogging(self, id, pred):
        return not (id in self.logged_already and (self.logged_already[id] == pred).all())