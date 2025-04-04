from dataclasses import dataclass
from typing import Dict
from typing import Optional


@dataclass
class MessageRecord:
    messageData: Optional[Dict]
    seq: Optional[int]
    time: Optional[str]
    timeL: Optional[int]
    messageId: Optional[str]
    sentBy: Optional[str]
    dialogId: Optional[str] = None
    participantId: Optional[str] = None
    source: Optional[str] = None
    device: Optional[str] = None
    audience: Optional[str] = None
    contextData: Optional[Dict] = None
    type: Optional[str] = None

    @classmethod
    def from_json_to_dict(cls, data):
        fields = cls.__annotations__.keys()
        instance_data = {}
        for key, value in data.items():
            if key in fields:
                instance_data[key] = value
        return cls(**instance_data)

    def __eq__(self, other):
        if isinstance(other, MessageRecord):
            return self.messageId == other.messageId
        return False

    def __hash__(self):
        return hash(self.messageId)
