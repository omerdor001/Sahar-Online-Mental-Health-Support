from datetime import datetime, timedelta
from objects.conversation_cache import ConversationCache
from lp_api_manager.lp_utils import *


class LpConversationGrabber:
    last_grab_time = 0

    def __init__(
            self,
            last_grab_time=int((datetime.now() - timedelta(hours=24)).timestamp() * 1000),
    ):
        self.live_person_util = LpUtils()
        self.bearer_token = self.live_person_util.bearer_token
        self.message_hist_domain = self.live_person_util.messageHistDomain
        self.account_id = self.live_person_util.account_id
        self.last_grab_time = last_grab_time

    def grab(self):  # remove conv that not with language = he - IL
        logging.info("Start grabber")
        current_time_ms = int(datetime.now().timestamp() * 1000)

        start_time = int((datetime.now() - timedelta(hours=24)).timestamp() * 1000)
        offset = 0

        # Initialize an empty dictionary to store conversation records
        conversations: dict[str, ConversationHistoryRecord] = {}
        messages: dict[str, set[MessageRecord]] = {}

        while True:
            print("going to grab and get open conversations")
            response = self.live_person_util.get_open_conversations(start_time, current_time_ms, offset)
            count = response["_metadata"]["count"]
            # Extract conversation records from the response
            conversation_records = LpUtils.extract_conversations(response)
            messages_records = LpUtils.extract_messages(response)
            # Update the conversations dictionary with the new records
            conversations.update(conversation_records)
            messages.update(messages_records)

            if count > offset + 100:
                offset += 100
            else:
                break

        catch = ConversationCache()
        catch.update_conversations(current_time_ms, conversations, messages)

        self.last_grab_time = current_time_ms
        print("Finish grabbing successfully")
        logging.info("Finish grabbing successfully")
        return conversations
