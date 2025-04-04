from enum import Enum
from dataclasses import dataclass, asdict
from typing import Optional, List, Type, TypeVar, Dict, Any

from DataBase.database_helper import DataBaseHelper
from dao_object.conversation_prediction_object import ConversationPredictionDAO
T = TypeVar('T')


class JsonConvertible:
    @staticmethod
    def from_json_to_dict(cls: Type[T], data) -> T:
        instance_data = {}
        for key, val in data.items():
            if key in cls.__annotations__:
                instance_data[key] = val
        return cls(**instance_data)


@dataclass
class MonitoringInfo(JsonConvertible):
    country: Optional[str] = None
    countryCode: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    isp: Optional[str] = None
    org: Optional[str] = None
    device: Optional[str] = None
    ipAddress: Optional[str] = None
    browser: Optional[str] = None
    operatingSystem: Optional[str] = None
    conversationStartPage: Optional[str] = None
    conversationStartPageTitle: Optional[str] = None


@dataclass
class ConsumerParticipant(JsonConvertible):
    participantId: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    token: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatarURL: Optional[str] = None
    time: Optional[str] = None
    timeL: Optional[int] = None
    consumerName: Optional[str] = None
    dialogId: Optional[str] = None


@dataclass
class ConversationHistoryRecord(JsonConvertible):
    startTime: Optional[str]
    startTimeL: Optional[int]
    conversationId: str
    latestAgentId: Optional[str]
    fullDialogStatus: Optional[str]
    latestAgentFullName: Optional[str]
    status: Optional[str]
    last_effected_message_id: Optional[str] = None
    need_analyze: Optional[bool] = None
    basic_algorithm_result: str = None
    GSR: Optional[float] = None
    IMSR: bool = None
    max_GSR: [float] = None
    sentBy: Optional[str] = None
    language: Optional[str] = None
    endTime: Optional[str] = None
    endTimeL: Optional[int] = None
    lastUpdateTime: Optional[float] = None
    conversationEndTime: Optional[str] = None
    conversationEndTimeL: Optional[int] = None
    fullDialogEndTime: Optional[str] = None
    fullDialogEndTimeL: Optional[int] = None
    duration: Optional[int] = None
    brandId: Optional[str] = None
    latestAgentNickname: Optional[str] = None
    latestAgentLoginName: Optional[str] = None
    agentDeleted: Optional[bool] = None
    latestSkillId: Optional[int] = None
    latestSkillName: Optional[str] = None
    source: Optional[str] = None
    closeReason: Optional[str] = None
    closeReasonDescription: Optional[str] = None
    mcs: Optional[int] = None
    alertedMcs: Optional[int] = None
    firstConversation: Optional[bool] = None
    csatRate: Optional[int] = None
    device: Optional[str] = None
    browser: Optional[str] = None
    operatingSystem: Optional[str] = None
    latestAgentGroupId: Optional[int] = None
    latestAgentGroupName: Optional[str] = None
    latestQueueState: Optional[str] = None
    isPartial: Optional[bool] = None
    pendingAgentSurvey: Optional[bool] = None
    consumerParticipants: Optional[List[ConsumerParticipant]] = None
    monitoring: Optional[MonitoringInfo] = None


    def update_field(self, field_name, field_value):
        if field_value is None or field_value == 'undefined':
            return
        if field_name == "GSR":
            self.update_maxGSR(field_value)
        setattr(self, field_name, field_value)

    def update(self, other):

        # Get fields of the class
        cls_fields = self.__annotations__.keys()
        # Iterate through the fields of the class
        for field in cls_fields:
            # Get the value of the field from the other record
            other_value = getattr(other, field)
            # If the value in the other record is not None, update this record's value
            if (other_value is not None) and (other_value is not "undefined"):
                if field == "GSR":
                    self.update_maxGSR(other_value)
                setattr(self, field, other_value)

    def update_maxGSR(self, GSR_value):
        if (self.max_GSR is None) or (self.max_GSR < GSR_value):
            setattr(self, "max_GSR", GSR_value)

    def to_dict(self):
        return asdict(self)
    



class ConversationType(Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    OVERDUE = "Overdue"
