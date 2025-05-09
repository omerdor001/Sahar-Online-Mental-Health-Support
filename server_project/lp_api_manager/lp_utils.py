# Engagement History lp_api_manager (Chat)
import logging
import os

from DataBase.database_helper import DataBaseHelper
from utils.config_util import ConfigUtil
from lp_api_manager.lp_executor import LpExecutor
from lp_api_manager.lp_api_builder import *
from lp_api_manager.lp_api_constants import *
from objects.message_record import MessageRecord
from objects.conversation_history_record import *
from flask import Flask, request, jsonify, current_app
import requests
import base64
# import data_base_helper 

class LpUtils:
    _instance = None
    bearer_token = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            # loading modal and setting it to eval mode to avoid parameters change while predicting
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            # Construct the relative path to the model file
            relative_path = os.path.join(
                parent_dir,
                "config.json",
            )
            cls._instance.config_path = relative_path  # kwargs.get("config_path", "config.json")
            cls._instance.load_config()
            # cls._instance.bearer_token = cls._instance.system_authenticate()
            cls._instance.messageHistDomain = cls._instance._extract_domain(
                cls._instance.message_hist_name
            )
            if cls._instance.messageHistDomain:
                logging.info("Authentication to Live-Person complete successfully")
            else:
                logging.error("Authentication complete unsuccessfully")
        return cls._instance

    def load_config(self):
        config_util = ConfigUtil()
        # self.user_name = config_util.get_config_attribute("userName")
        # self.password = config_util.get_config_attribute("password")
        self.account_id = config_util.get_config_attribute("accountId")
        self.service_log_in_name = config_util.get_config_attribute("serviceLogInName")
        self.message_hist_name = config_util.get_config_attribute("messageHistName")
        self.account_config_read_only = config_util.get_config_attribute("accountConfigReadOnly")
        
    # def get_token(self,account_id, client_id, client_secret):
    #     url = f'https://va.sentinel.liveperson.net/sentinel/api/account/{account_id}/app/token?v=1.0'
    #     headers = {
    #       'Content-Type': 'application/x-www-form-urlencoded'
    #     }
    #     payload = {
    #       'client_id': client_id,
    #       'client_secret': client_secret,
    #       'grant_type': 'client_credentials'
    #     }
    #     try: 
    #        response = requests.post(url, headers=headers, data=payload)
    #        response.raise_for_status()  # Raise an error for HTTP error codes
    #        data = response.json()
    #        return data.get('access_token')
    #     except requests.RequestException as e:
    #        print(f"Error fetching token: {e}")
    #        return None

    def lp_validate_token(self, user_id, account_id, token):
        domain = self._extract_domain(self.account_config_read_only)
        headers = {
            "Authorization": f"Bearer lalalala",
            "Content-Type": "application/json",
        }
        if domain:
            validate_token_uri = LpApiConstants.validate_token_call_uri(domain, account_id, user_id)
            validate_token_res = LpExecutor.execute(
                LpApiBuilder(validate_token_uri, type=LpApiType.GET).add_headers(headers)
            .build_call())
            print("validate token uri", validate_token_uri)
            print("validate_token_res", validate_token_res)
            return validate_token_res
        else:
            logging.error(f"Extracting domain from Live-Person failed")
            return None

    def lp_login(self, username, password, account_id, number_of_retries=0):
        print(f"start login for user {username}")
        domain = self._extract_domain(self.service_log_in_name)
        if domain:
            login_call_uri = LpApiConstants.login_call_uri(domain, account_id)
            login_res = LpExecutor.execute(
                LpApiBuilder(login_call_uri)
                .add_headers(
                    {"Content-Type": "Application/JSON", "Accept": "Application/JSON"}
                )
                .add_body({"username": username, "password": password})
                .build_call(), number_of_retries
            )

            print("logged in successfully")
            return login_res
        else:
            logging.error(f"Extracting domain from Live-Person failed")
            return None



    def get_open_conversations(self, start_time, end_time, offset):
        print("getting_open_converstaions started")
        # headers = {
        #     "Authorization": f"Bearer {self.bearer_token}",
        #     "Content-Type": "application/json",
        # }

        body = {
            "start": {"from": start_time, "to": end_time},
            "contentToRetrieve": ["consumerParticipants", "messageRecords", "monitoring"],
            "status": ["OPEN", "OVERDUE"],
        }
        params = {"offset": offset, "limit": 100, "source": "sahar_AI_openConv"}

        print("get open conversation done")
        return self.check_response(LpExecutor.execute(
            LpApiBuilder(
                LpApiConstants.message_hist_uri(
                    self.messageHistDomain, self.account_id
                )
            )
            # .add_headers(headers)
            .add_body(body)
            .add_params(params)
            .build_call()
        ), True)

    # def system_authenticate(self):
    #     print("starting system authenticate")
    #     #client_secret = "t05oqsaoi36kmsspp9bh0o1arn"                         #added
    #     #client_id = "809a3744-07e3-4a8d-8198-0639d3ca23e0"
    #     #token_lp=self.get_token(40920689, client_id, client_secret)
    #     #self.bearer_token=token_lp                                           #added
    #     login_res = self.lp_login(self.user_name, self.password, self.account_id)
    #     if self.is_response_ok(login_res):
    #         if "application/json" in login_res.headers.get("content-type", ""):
    #             login_res = login_res.json()
    #         else:
    #             login_res = login_res.content
    #         bearer_token = login_res.get("bearer")
    #         print("system autheticate, token is : " ,bearer_token)
    #         return bearer_token
    #     else:
    #         logging.error(f"system_authenticate: login failed")

    def is_response_ok(self, response):
        if response is not None and response.status_code == 200 or response.status_code == 204:
            return True
        return False




    def get_conversations_by_conv_id(self, conversations_ids: [str]):
        print("get conversations by conv id started")
        # print("get_converstaions_by_conv_id token: ", self.bearer_token)
        #self.bearer_token = self.system_authenticate()
        # headers = {
        #     "Authorization": f"Bearer {self.bearer_token}",
        #     "Content-Type": "application/json",
        # }

        params = {
            "source": "sahar_AI_closeConv",
        }

        body = {
            "conversationIds": conversations_ids,
            "status": ["CLOSE"],
            "contentToRetrieve": ["consumerParticipants", "messageRecords", "monitoring"],
        }

        URI = LpApiConstants.get_conv_by_conv_id_call(
            self.messageHistDomain, self.account_id
        )

        if len(conversations_ids) > 100:
            logging.error("conversationsIds size > 100, data lost")
        response=self.check_response(LpExecutor.execute(
            LpApiBuilder(URI)
            # .add_headers(headers)
            .add_body(body)
            .add_params(params)
            .build_call()
        ), True)
        # count = response["_metadata"]["count"]
        print("successfuly get conversatins by id")
        # if 'debugMessage' in response and 'The server will not process the request' in response['debugMessage']:

        #     print("second time , try again")
        #     # headers['Authorization'] = f"Bearer {self.bearer_token}"
        #     response=self.check_response(LpExecutor.execute(
        #     LpApiBuilder(URI)
        #     # .add_headers(headers)
        #     .add_body(body)
        #     .add_params(params)
        #     .build_call()
        # ), True)
        print("response from get_conversation_by_id = ", response)
        return response
    
   
    def _extract_domain(self, service_name):
        print("starting extract domain")
        # account -	LivePerson account ID	string
        # service -	Service name according to the relevant lp_api_manager	string
        base_uri = LpApiConstants.base_call_uri(self.account_id, service_name)
        base_res = LpExecutor.execute(
            LpApiBuilder(base_uri).add_type(LpApiType.GET).build_call()
        )
        base_res = self.check_response(base_res)
        print("successfully extract domain")
        return self._extract_base_uri(base_res, service_name)

    def _extract_base_uri(self, baseRes, serviceName):
        # Check if baseRes contains a list of baseURIs or a single baseURI
        if isinstance(baseRes.get("baseURIs"), list):
            # Iterate over the baseURIs and search for the record with the specified service_name
            for record in baseRes["baseURIs"]:
                if record["service"] == serviceName:
                    return record["baseURI"]
        else:
            # Check if the single baseURI matches the service name
            if baseRes.get("service") == serviceName:
                return baseRes["baseURI"]

        # If no matching record found, return None
        return None

    @staticmethod
    def extract_messages(response) -> dict[str, set[MessageRecord]]:
        messages: dict[str, set[MessageRecord]] = {}
        for item in response["conversationHistoryRecords"]:
            conversation_info = item.get("info")
            conversation_id = conversation_info.get("conversationId")
            messagesPerConv: set[MessageRecord] = set()
            for jsonMessage in item.get("messageRecords"):
                message = MessageRecord.from_json_to_dict(jsonMessage)
                messagesPerConv.add(message)
            messages[conversation_id] = messagesPerConv

        return messages

    @staticmethod
    def extract_conversations(response) -> dict[str, ConversationHistoryRecord]:
        conversations: dict[str, ConversationHistoryRecord] = {}
        for item in response["conversationHistoryRecords"]:
            conversation_info = item.get("info")
            conversation_id = conversation_info.get("conversationId")
            record: ConversationHistoryRecord = JsonConvertible.from_json_to_dict(ConversationHistoryRecord,
                                                                                  conversation_info)

            consumerParticipants = item.get("consumerParticipants")[0]
            if consumerParticipants is not None:
                consumerParticipants_object: ConsumerParticipant = JsonConvertible.from_json_to_dict(
                    ConsumerParticipant, consumerParticipants)
                record.update_field("consumerParticipants", consumerParticipants_object)

            monitoring = item.get("monitoring")
            if monitoring is not None:
                monitoring_object: MonitoringInfo = JsonConvertible.from_json_to_dict(MonitoringInfo, monitoring)
                record.update_field("monitoring", monitoring_object)

            conversations[conversation_id] = record
            # record.to_db_record()
        return conversations

    def check_response(self, response, is_need_authentication=False):
       # print(response)
        # print("starting check_response after used token:", self.bearer_token)
        # if is_need_authentication and response.status_code == 401:
        #     print("unauthorized, try to authenticate again")
        #     logging.warning("Unauthorized, try to authenticate")
        #     self.bearer_token = self.system_authenticate()
        #     print("new token is:", self.bearer_token)
        if "application/json" in response.headers.get("content-type", ""):
            return response.json()
        else:
            return response.content
