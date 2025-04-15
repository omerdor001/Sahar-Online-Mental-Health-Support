import unittest
from unittest.mock import patch, MagicMock
from server_project.lp_api_manager.lp_utils import LpUtils
from server_project.objects.message_record import MessageRecord


class test_LivePerson_Utils(unittest.TestCase):
    @patch('server_project.lp_api_manager.lp_executor.LpExecutor.execute')
    @patch('server_project.lp_api_manager.lp_utils.ConfigUtil')
    @patch('server_project.lp_api_manager.lp_utils.LpUtils.lp_login')
    def test_init_utils(self, mock_lp_login, mock_config_util, mock_execute):
        mock_config_util.return_value.get_config_attribute = lambda attribute: {
            "userName": "test_user",
            "password": "test_pass",
            "accountId": "test_account_id",
            "serviceLogInName": "test_service_name",
            "messageHistName": "test_message_hist_name",
            "numberOfRetriesAPICalls": "0"
        }.get(attribute)
        mock_lp_login.return_value = MagicMock(
            status_code=200,
            json=lambda: {"bearer": "test_bearer_token"},
            headers={"content-type": "application/json"}
        )
        mock_execute.return_value = MagicMock(status_code=200)
        lp_utils = LpUtils()
        self.assertIsNotNone(lp_utils.bearer_token)
        self.assertEqual(lp_utils.bearer_token, "test_bearer_token")

    @patch('server_project.lp_api_manager.lp_utils.LpExecutor.execute')
    @patch('server_project.lp_api_manager.lp_utils.LpApiConstants.login_call_uri')
    @patch('server_project.lp_api_manager.lp_utils.ConfigUtil')
    @patch('server_project.lp_api_manager.lp_utils.LpUtils.system_authenticate')
    @patch('server_project.lp_api_manager.lp_utils.LpUtils._extract_domain')
    def test_lp_login_success(self, mock_system_authenticate, mock_config_util,
                              mock_login_call_uri, mock_execute):
        mock_system_authenticate.return_value = "test_bearer_token"
        mock_login_call_uri.return_value = "https://api.liveperson.net/login"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test_token"}
        mock_execute.return_value = mock_response
        username = "test_user"
        password = "test_pass"
        account_id = "test_account_id"
        mock_config_util.return_value.get_config_attribute = lambda attribute: {
            "userName": "test_user",
            "password": "test_pass",
            "accountId": "test_account_id",
            "serviceLogInName": "test_service_name",
            "messageHistName": "test_message_hist_name",
            "numberOfRetriesAPICalls": "0"
        }.get(attribute)
        lp_utils = LpUtils()
        login_response = lp_utils.lp_login(username, password, account_id)
        self.assertEqual(login_response.json(), {"access_token": "test_token"})
        self.assertEqual(login_response.status_code, 200)
        mock_execute.assert_called_once()

    @patch('server_project.lp_api_manager.lp_utils.LpUtils._extract_domain')
    @patch('server_project.lp_api_manager.lp_utils.LpExecutor.execute')
    @patch('server_project.lp_api_manager.lp_utils.LpApiConstants.base_call_uri')
    @patch('server_project.lp_api_manager.lp_utils.ConfigUtil')
    @patch('server_project.lp_api_manager.lp_utils.LpUtils.system_authenticate')
    def test_lp_login_failure(self, mock_system_authenticate, mock_config_util, mock_base_call_uri,
                              mock_execute, mock_extract_domain):
        mock_extract_domain.return_value = "https://api.test.com"
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_execute.return_value = mock_response
        mock_config_util.return_value.get_config_attribute = lambda attribute: {
            "userName": "test_user",
            "password": "test_pass",
            "accountId": "test_account_id",
            "serviceLogInName": "test_service_name",
            "messageHistName": "test_message_hist_name",
            "numberOfRetriesAPICalls": "0"
        }.get(attribute)
        lp_utils = LpUtils()
        lp_utils.account_id = "test_account_id"
        lp_utils.user_name = "test_user"
        lp_utils.password = "test_pass"
        result = lp_utils.lp_login(lp_utils.user_name, lp_utils.password, lp_utils.account_id)
        self.assertEqual(result.status_code, 401)
        self.assertIn("error", result.json())
        self.assertEqual(result.json()["error"], "Unauthorized")
        mock_extract_domain.assert_called()
        mock_execute.assert_called_once()

    @patch('server_project.lp_api_manager.lp_utils.ConfigUtil')
    @patch('server_project.lp_api_manager.lp_utils.LpUtils.check_response')
    @patch('server_project.lp_api_manager.lp_executor.LpExecutor.execute')
    @patch('server_project.lp_api_manager.lp_utils.LpUtils.lp_login')
    def test_get_conversations_by_conv_id_success(self, mock_config_util, mock_check_response,
                                                  mock_execute, mock_lp_login):
        mock_config_util.return_value.get_config_attribute = lambda attribute: {
            "userName": "test_user",
            "password": "test_pass",
            "accountId": "test_account_id",
            "serviceLogInName": "test_service_name",
            "messageHistName": "test_message_hist_name",
            "numberOfRetriesAPICal": "0"
        }.get(attribute)
        mock_lp_login.return_value = MagicMock(
            status_code=200,
            json=lambda: {"bearer": "test_bearer_token"},
            headers={"content-type": "application/json"}
        )
        lp_utils = LpUtils()
        mock_response_data = {
            "conversationHistoryRecords": [
                {
                    "info": {
                        "startTime": "2024-12-14T12:00:00Z",
                        "startTimeL": 1702555200000,
                        "conversationId": "1234",
                        "latestAgentId": "agent_5678",
                        "fullDialogStatus": "active",
                        "latestAgentFullName": "Agent Smith",
                        "status": "CLOSE"
                    },
                    "consumerParticipants": [
                        {
                            "participantId": "consumer_001",
                            "firstName": "John",
                            "lastName": "Doe",
                            "token": "sample_token",
                            "email": "johndoe@example.com",
                            "phone": "+123456789",
                            "avatarURL": "https://example.com/avatar.jpg",
                            "time": "2024-12-14T12:01:00Z",
                            "timeL": 1702555260000,
                            "consumerName": "John Doe",
                            "dialogId": "dialog_5678"
                        }
                    ],
                    "monitoring": {"status": "active"}
                }
            ]
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_execute.return_value = mock_response_data
        mock_check_response.return_value = mock_response_data
        conversation_ids = ["1234"]
        response = lp_utils.get_conversations_by_conv_id(conversation_ids)
        self.assertIn("conversationHistoryRecords", response)
        self.assertEqual(response["conversationHistoryRecords"][0]["info"]["conversationId"], "1234")
        self.assertEqual(response["conversationHistoryRecords"][0]["info"]["status"], "CLOSE")

    @patch('server_project.lp_api_manager.lp_executor.LpExecutor.execute')
    @patch('server_project.lp_api_manager.lp_utils.LpUtils.check_response')
    @patch('server_project.lp_api_manager.lp_utils.ConfigUtil')
    @patch('server_project.lp_api_manager.lp_utils.LpUtils.lp_login')
    @patch('logging.error')
    def test_get_conversations_by_conv_id_failure(self, mock_logging_error, mock_lp_login, mock_config_util,
                                                  mock_check_response, mock_execute):
        mock_config_util.return_value.get_config_attribute = lambda attribute: {
            "userName": "test_user",
            "password": "test_pass",
            "accountId": "test_account_id",
            "serviceLogInName": "test_service_name",
            "messageHistName": "test_message_hist_name",
            "numberOfRetriesAPICal": "0"
        }.get(attribute)
        mock_lp_login.return_value = MagicMock(
            status_code=200,
            json=lambda: {"bearer": "test_bearer_token"},
            headers={"content-type": "application/json"}
        )
        lp_utils = LpUtils()
        mock_response_data = {"error": "Internal Server Error"}
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = mock_response_data
        mock_execute.return_value = mock_response
        mock_check_response.return_value = mock_response_data
        lp_utils = LpUtils()
        conversations_ids = [str(i) for i in range(1, 102)]
        lp_utils.get_conversations_by_conv_id(conversations_ids)
        mock_logging_error.assert_called_with("conversationsIds size > 100, data lost")

    @patch('server_project.lp_api_manager.lp_executor.LpExecutor.execute')
    @patch('server_project.lp_api_manager.lp_utils.LpUtils.lp_login')
    @patch('server_project.lp_api_manager.lp_utils.ConfigUtil')
    @patch.object(LpUtils, 'system_authenticate', return_value="test_bearer_token")
    def test_system_authenticate_success(self, mock_authenticate, mock_config_util, mock_lp_login, mock_execute):
        mock_config_util.return_value.get_config_attribute = lambda attribute: {
            "userName": "test_user",
            "password": "test_pass",
            "accountId": "test_account_id",
            "serviceLogInName": "test_service_name",
            "messageHistName": "test_message_hist_name",
            "numberOfRetriesAPICalls": "0"
        }.get(attribute)
        mock_lp_login.return_value = MagicMock(
            status_code=200,
            json=lambda: {"bearer": "test_bearer_token"},
            headers={"content-type": "application/json"}
        )
        mock_execute.return_value = MagicMock(status_code=200)
        lp_utils = LpUtils()
        token = lp_utils.system_authenticate()
        self.assertEqual(token, "test_bearer_token")

    @patch("server_project.lp_api_manager.lp_utils.LpUtils.lp_login")
    @patch("server_project.lp_api_manager.lp_utils.LpUtils.is_response_ok")
    @patch("server_project.lp_api_manager.lp_utils.logging.error")
    @patch("server_project.lp_api_manager.lp_utils.ConfigUtil")
    @patch("server_project.lp_api_manager.lp_executor.LpExecutor.execute")
    def test_system_authenticate_failure(self, mock_execute, mock_config_util, mock_logging_error, mock_is_response_ok,
                                         mock_lp_login):
        mock_config_util_instance = MagicMock()
        mock_config_util.return_value = mock_config_util_instance
        mock_config_util_instance.get_config_attribute = lambda attribute: {
            "userName": "test_user",
            "password": "test_pass",
            "accountId": "test_account_id",
            "serviceLogInName": "test_service_name",
            "messageHistName": "test_message_hist_name",
            "numberOfRetriesAPICalls": "0"
        }.get(attribute)
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_lp_login.return_value = mock_response
        mock_is_response_ok.return_value = False
        mock_execute.return_value = MagicMock(status_code=200)
        lp_utils = LpUtils()
        lp_utils.user_name = "test_user"
        lp_utils.password = "test_pass"
        lp_utils.account_id = "test_account_id"
        result = lp_utils.system_authenticate()
        self.assertIsNone(result)
        mock_lp_login.assert_called_with("test_user", "test_pass", "test_account_id")
        mock_is_response_ok.assert_called_with(mock_response)
        mock_logging_error.assert_called_with("system_authenticate: login failed")

    @patch('server_project.lp_api_manager.lp_utils.LpUtils.lp_login')
    @patch('server_project.lp_api_manager.lp_utils.ConfigUtil')
    @patch('server_project.lp_api_manager.lp_executor.LpExecutor.execute')
    def test_extract_conversations_success(self, mock_config_util, mock_lp_login, mock_execute):
        mock_config_util.return_value.get_config_attribute = lambda attribute: {
            "userName": "test_user",
            "password": "test_pass",
            "accountId": "test_account_id",
            "serviceLogInName": "test_service_name",
            "messageHistName": "test_message_hist_name",
            "numberOfRetriesAPICalls": "0"
        }.get(attribute)
        mock_lp_login.return_value = MagicMock(
            status_code=200,
            json=lambda: {"bearer": "test_bearer_token"},
            headers={"content-type": "application/json"}
        )
        mock_execute.return_value = MagicMock(status_code=200)
        lp_utils = LpUtils()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "conversationHistoryRecords": [
                {
                    "info": {
                        "startTime": "2024-12-14T12:00:00Z",
                        "startTimeL": 1702555200000,
                        "conversationId": "1234",
                        "latestAgentId": "agent_5678",
                        "fullDialogStatus": "active",
                        "latestAgentFullName": "Agent Smith",
                        "status": "OPEN"
                    },
                    "consumerParticipants": [
                        {
                            "participantId": "consumer_001",
                            "firstName": "John",
                            "lastName": "Doe",
                            "token": "sample_token",
                            "email": "johndoe@example.com",
                            "phone": "+123456789",
                            "avatarURL": "https://example.com/avatar.jpg",
                            "time": "2024-12-14T12:01:00Z",
                            "timeL": 1702555260000,
                            "consumerName": "John Doe",
                            "dialogId": "dialog_5678"
                        }
                    ],
                    "monitoring": {"status": "active"}
                }
            ]
        }
        mock_execute.return_value = mock_response
        response = lp_utils.extract_conversations(mock_response.json())
        self.assertEqual(len(response), 1)
        self.assertEqual(response["1234"].conversationId, "1234")
        self.assertEqual(response["1234"].consumerParticipants.firstName, "John")

    @patch('server_project.lp_api_manager.lp_utils.LpUtils.lp_login')
    @patch('server_project.lp_api_manager.lp_utils.ConfigUtil')
    @patch('server_project.lp_api_manager.lp_executor.LpExecutor.execute')
    def test_extract_base_uri_success(self,mock_config_util, mock_lp_login, mock_execute):
        mock_config_util.return_value.get_config_attribute = lambda attribute: {
            "userName": "test_user",
            "password": "test_pass",
            "accountId": "test_account_id",
            "serviceLogInName": "test_service_name",
            "messageHistName": "test_message_hist_name",
            "numberOfRetriesAPICalls": "0"
        }.get(attribute)
        mock_lp_login.return_value = MagicMock(
            status_code=200,
            json=lambda: {"bearer": "test_bearer_token"},
            headers={"content-type": "application/json"}
        )
        baseRes = {
            "baseURIs": [
                {"service": "service1", "baseURI": "https://api.service1.com"},
                {"service": "service2", "baseURI": "https://api.service2.com"}
            ]
        }
        lp_utils = LpUtils()
        serviceName = "service1"
        result = lp_utils._extract_base_uri(baseRes, serviceName)
        self.assertEqual(result, "https://api.service1.com")

    @patch('server_project.lp_api_manager.lp_utils.LpUtils.lp_login')
    @patch('server_project.lp_api_manager.lp_utils.ConfigUtil')
    @patch('server_project.lp_api_manager.lp_executor.LpExecutor.execute')
    def test_extract_base_uri_failure(self,mock_config_util, mock_lp_login, mock_execute):
        mock_config_util.return_value.get_config_attribute = lambda attribute: {
            "userName": "test_user",
            "password": "test_pass",
            "accountId": "test_account_id",
            "serviceLogInName": "test_service_name",
            "messageHistName": "test_message_hist_name",
            "numberOfRetriesAPICalls": "0"
        }.get(attribute)
        mock_lp_login.return_value = MagicMock(
            status_code=200,
            json=lambda: {"bearer": "test_bearer_token"},
            headers={"content-type": "application/json"}
        )
        lp_utils = LpUtils()
        baseRes = {
            "baseURIs": [
                {"service": "service1", "baseURI": "https://api.service1.com"},
                {"service": "service2", "baseURI": "https://api.service2.com"}
            ]
        }
        serviceName = "service3"
        result = lp_utils._extract_base_uri(baseRes, serviceName)
        self.assertIsNone(result)

    @patch('server_project.lp_api_manager.lp_utils.LpUtils.lp_login')
    @patch('server_project.lp_api_manager.lp_utils.ConfigUtil')
    @patch('server_project.lp_api_manager.lp_executor.LpExecutor.execute')
    def test_extract_base_uri_single_uri_success(self,mock_config_util, mock_lp_login, mock_execute):
        mock_config_util.return_value.get_config_attribute = lambda attribute: {
            "userName": "test_user",
            "password": "test_pass",
            "accountId": "test_account_id",
            "serviceLogInName": "test_service_name",
            "messageHistName": "test_message_hist_name",
            "numberOfRetriesAPICalls": "0"
        }.get(attribute)
        mock_lp_login.return_value = MagicMock(
            status_code=200,
            json=lambda: {"bearer": "test_bearer_token"},
            headers={"content-type": "application/json"}
        )
        lp_utils = LpUtils()
        baseRes = {
            "service": "service1",
            "baseURI": "https://api.service1.com"
        }
        serviceName = "service1"
        result = lp_utils._extract_base_uri(baseRes, serviceName)
        self.assertEqual(result, "https://api.service1.com")

    @patch('server_project.lp_api_manager.lp_utils.LpUtils.lp_login')
    @patch('server_project.lp_api_manager.lp_utils.ConfigUtil')
    @patch('server_project.lp_api_manager.lp_executor.LpExecutor.execute')
    def test_extract_base_uri_single_uri_failure(self,mock_config_util, mock_lp_login, mock_execute):
        mock_config_util.return_value.get_config_attribute = lambda attribute: {
            "userName": "test_user",
            "password": "test_pass",
            "accountId": "test_account_id",
            "serviceLogInName": "test_service_name",
            "messageHistName": "test_message_hist_name",
            "numberOfRetriesAPICalls": "0"
        }.get(attribute)
        mock_lp_login.return_value = MagicMock(
            status_code=200,
            json=lambda: {"bearer": "test_bearer_token"},
            headers={"content-type": "application/json"}
        )
        lp_utils = LpUtils()
        baseRes = {
            "service": "service2",
            "baseURI": "https://api.service2.com"
        }
        serviceName = "service1"
        result = lp_utils._extract_base_uri(baseRes, serviceName)
        self.assertIsNone(result)

    @patch('server_project.lp_api_manager.lp_utils.LpUtils.lp_login')
    @patch('server_project.lp_api_manager.lp_utils.ConfigUtil')
    @patch('server_project.lp_api_manager.lp_utils.LpExecutor.execute')
    @patch('server_project.lp_api_manager.lp_utils.LpApiConstants.base_call_uri')
    @patch('server_project.lp_api_manager.lp_utils.LpUtils.check_response')
    def test_extract_domain_success(self, mock_check_response, mock_base_call_uri, mock_execute,mock_config_util,
                                    mock_lp_login):
        mock_config_util.return_value.get_config_attribute = lambda attribute: {
            "userName": "test_user",
            "password": "test_pass",
            "accountId": "test_account_id",
            "serviceLogInName": "test_service_name",
            "messageHistName": "test_message_hist_name",
            "numberOfRetriesAPICalls": "0"
        }.get(attribute)
        mock_lp_login.return_value = MagicMock(
            status_code=200,
            json=lambda: {"bearer": "test_bearer_token"},
            headers={"content-type": "application/json"}
        )
        account_id = "test_account_id"
        service_name = "test_service_name"
        expected_base_uri = "https://api.test.com/test_account_id/test_service_name"
        mock_response_data = {"baseURIs": [{"service": "test_service_name", "baseURI": "https://api.test.com/v1"}]}
        expected_result = "https://api.test.com/v1"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_execute.return_value = mock_response
        mock_check_response.return_value = mock_response_data
        mock_base_call_uri.return_value = expected_base_uri
        lp_utils = LpUtils()
        lp_utils.account_id = account_id
        result = lp_utils._extract_domain(service_name)
        self.assertEqual(result, expected_result)
        mock_execute.assert_called()
        mock_check_response.assert_called_with(mock_response)

    @patch('server_project.lp_api_manager.lp_utils.ConfigUtil')
    @patch('server_project.lp_api_manager.lp_executor.LpExecutor.execute')
    @patch('server_project.lp_api_manager.lp_utils.LpUtils.lp_login')
    @patch('server_project.lp_api_manager.lp_utils.LpUtils.check_response')
    @patch('logging.warning')
    def test_extract_domain_failure(self, mock_logging_warning, mock_check_response,
                                    mock_lp_login, mock_execute, mock_config_util):
        mock_config_util.return_value.get_config_attribute = lambda attribute: {
            "userName": "test_user",
            "password": "test_pass",
            "accountId": "test_account_id",
            "serviceLogInName": "test_service_name",
            "messageHistName": "test_message_hist_name",
            "numberOfRetriesAPICalls": "0"
        }.get(attribute)
        account_id = "test_account_id"
        service_name = "test_service_name"
        mock_lp_login.return_value = MagicMock(
            status_code=200,
            json=lambda: {"bearer": "test_bearer_token"},
            headers={"content-type": "application/json"}
        )
        lp_utils = LpUtils()
        lp_utils.account_id = account_id
        base_call_uri = f"https://api.liveperson.net/{account_id}/{service_name}"
        with patch('server_project.lp_api_manager.lp_api_constants.LpApiConstants.base_call_uri',
                   return_value=base_call_uri):
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.headers = {"content-type": "application/json"}
            mock_response.json.return_value = {"error": "Internal Server Error"}
            mock_execute.return_value = mock_response
            mock_check_response.side_effect = Exception("Internal Server Error")
            try:
                lp_utils._extract_domain(service_name)
            except Exception as e:
                self.assertIn("Internal Server Error", str(e))
            else:
                self.fail("Exception not raised for Internal Server Error")
            mock_check_response.assert_called_with(mock_response)
            mock_logging_warning.assert_not_called()

    @patch('server_project.lp_api_manager.lp_utils.ConfigUtil')
    @patch('server_project.lp_api_manager.lp_executor.LpExecutor.execute')
    @patch('server_project.lp_api_manager.lp_utils.LpUtils.lp_login')
    def test_extract_messages(self,mock_lp_login, mock_execute, mock_config_util):
        mock_config_util.return_value.get_config_attribute = lambda attribute: {
            "userName": "test_user",
            "password": "test_pass",
            "accountId": "test_account_id",
            "serviceLogInName": "test_service_name",
            "messageHistName": "test_message_hist_name",
            "numberOfRetriesAPICalls": "0"
        }.get(attribute)
        mock_lp_login.return_value = MagicMock(
            status_code=200,
            json=lambda: {"bearer": "test_bearer_token"},
            headers={"content-type": "application/json"}
        )
        lp_utils = LpUtils()
        mock_response_data = {
            "conversationHistoryRecords": [
                {
                    "info": {
                        "conversationId": "12345",
                        "status": "OPEN",
                        "startTime": "2024-12-01T12:00:00Z",
                    },
                    "messageRecords": [
                        {
                            "messageData": {"content": "Hello"},
                            "seq": 1,
                            "time": "2024-12-01T12:01:00Z",
                            "timeL": 1700122860000,
                            "messageId": "msg_001",
                            "sentBy": "agent",
                        },
                        {
                            "messageData": {"content": "How can I help you?"},
                            "seq": 2,
                            "time": "2024-12-01T12:02:00Z",
                            "timeL": 1700122920000,
                            "messageId": "msg_002",
                            "sentBy": "agent",
                        },
                    ],
                }
            ]
        }
        expected_result = {
            "12345": {
                MessageRecord(
                    messageData={"content": "Hello"},
                    seq=1,
                    time="2024-12-01T12:01:00Z",
                    timeL=1700122860000,
                    messageId="msg_001",
                    sentBy="agent",
                ),
                MessageRecord(
                    messageData={"content": "How can I help you?"},
                    seq=2,
                    time="2024-12-01T12:02:00Z",
                    timeL=1700122920000,
                    messageId="msg_002",
                    sentBy="agent",
                ),
            }
        }
        result = lp_utils.extract_messages(mock_response_data)
        self.assertEqual(result, expected_result)

    @patch('server_project.lp_api_manager.lp_utils.ConfigUtil')
    @patch('server_project.lp_api_manager.lp_utils.LpUtils.lp_login')
    @patch('server_project.lp_api_manager.lp_utils.LpUtils.check_response')
    @patch('server_project.lp_api_manager.lp_executor.LpExecutor.execute')
    @patch('server_project.lp_api_manager.lp_utils.LpApiBuilder')
    @patch('server_project.lp_api_manager.lp_utils.LpApiConstants.message_hist_uri')
    def test_get_open_conversations_success(self, mock_message_hist_uri, mock_lp_api_builder, mock_execute,
                                            mock_check_response, mock_config_util, mock_lp_login):
        mock_config_util.return_value.get_config_attribute = lambda attribute: {
            "userName": "test_user",
            "password": "test_pass",
            "accountId": "test_account_id",
            "serviceLogInName": "test_service_name",
            "messageHistName": "test_message_hist_name",
            "numberOfRetriesAPICalls": "0"
        }.get(attribute)
        mock_lp_login.return_value = MagicMock(
            status_code=200,
            json=lambda: {"bearer": "test_bearer_token"},
            headers={"content-type": "application/json"}
        )
        lp_utils = LpUtils()
        lp_utils.bearer_token = "test_bearer_token"
        lp_utils.messageHistDomain = "test_message_hist_domain"
        lp_utils.account_id = "test_account_id"
        mock_message_hist_uri.return_value = "https://api.test.com/message_hist"
        mock_api_call = MagicMock()
        mock_lp_api_builder.return_value.add_headers.return_value = mock_lp_api_builder.return_value
        mock_lp_api_builder.return_value.add_body.return_value = mock_lp_api_builder.return_value
        mock_lp_api_builder.return_value.add_params.return_value = mock_lp_api_builder.return_value
        mock_lp_api_builder.return_value.build_call.return_value = mock_api_call
        mock_response_data = {
            "conversationHistoryRecords": [
                {
                    "info": {
                        "conversationId": "12345",
                        "status": "OPEN",
                        "startTime": "2024-12-01T12:00:00Z",
                    },
                    "consumerParticipants": [
                        {
                            "participantId": "consumer_001",
                            "consumerName": "John Doe",
                            "dialogId": "dialog_5678",
                        }
                    ],
                    "monitoring": {"status": "active"},
                }
            ]
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_execute.return_value = mock_response
        mock_check_response.return_value = mock_response_data
        start_time = "2024-12-01T00:00:00Z"
        end_time = "2024-12-13T23:59:59Z"
        offset = 0
        response = lp_utils.get_open_conversations(start_time, end_time, offset)
        self.assertEqual(response, mock_response_data)
        mock_message_hist_uri.assert_called_with("test_message_hist_domain", "test_account_id")
        mock_lp_api_builder.return_value.add_headers.assert_called_with({
            "Authorization": "Bearer test_bearer_token",
            "Content-Type": "application/json",
        })
        mock_lp_api_builder.return_value.add_body.assert_called_with({
            "start": {"from": start_time, "to": end_time},
            "contentToRetrieve": ["consumerParticipants", "messageRecords", "monitoring"],
            "status": ["OPEN", "OVERDUE"],
        })
        mock_lp_api_builder.return_value.add_params.assert_called_with({
            "offset": offset,
            "limit": 100,
            "source": "sahar_AI_openConv",
        })
        mock_execute.assert_called_with(mock_api_call)
        mock_check_response.assert_called_with(mock_response, True)

    @patch('server_project.lp_api_manager.lp_utils.LpUtils.lp_login')
    @patch('server_project.lp_api_manager.lp_utils.ConfigUtil')
    @patch('server_project.lp_api_manager.lp_utils.LpUtils.check_response')
    @patch('server_project.lp_api_manager.lp_executor.LpExecutor.execute')
    @patch('server_project.lp_api_manager.lp_utils.LpApiBuilder')
    @patch('server_project.lp_api_manager.lp_utils.LpApiConstants.message_hist_uri')
    def test_get_open_conversations_failure(self, mock_message_hist_uri, mock_lp_api_builder, mock_execute,
                                            mock_check_response, mock_config_util, mock_lp_login):
        mock_config_util.return_value.get_config_attribute = lambda attribute: {
            "userName": "test_user",
            "password": "test_pass",
            "accountId": "test_account_id",
            "serviceLogInName": "test_service_name",
            "messageHistName": "test_message_hist_name",
            "numberOfRetriesAPICalls": "0"
        }.get(attribute)
        mock_lp_login.return_value = MagicMock(
            status_code=200,
            json=lambda: {"bearer": "test_bearer_token"},
            headers={"content-type": "application/json"}
        )
        lp_utils = LpUtils()
        lp_utils.bearer_token = "test_bearer_token"
        lp_utils.messageHistDomain = "test_message_hist_domain"
        lp_utils.account_id = "test_account_id"
        mock_message_hist_uri.return_value = "https://api.test.com/message_hist"
        mock_api_call = MagicMock()
        mock_lp_api_builder.return_value.add_headers.return_value = mock_lp_api_builder.return_value
        mock_lp_api_builder.return_value.add_body.return_value = mock_lp_api_builder.return_value
        mock_lp_api_builder.return_value.add_params.return_value = mock_lp_api_builder.return_value
        mock_lp_api_builder.return_value.build_call.return_value = mock_api_call
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_execute.return_value = mock_response
        mock_check_response.side_effect = Exception("API call failed with status 401")
        start_time = "2024-12-01T00:00:00Z"
        end_time = "2024-12-13T23:59:59Z"
        offset = 0
        with self.assertRaises(Exception) as context:
            lp_utils.get_open_conversations(start_time, end_time, offset)
        mock_message_hist_uri.assert_called_with("test_message_hist_domain", "test_account_id")
        mock_lp_api_builder.return_value.add_headers.assert_called_with({
            "Authorization": "Bearer test_bearer_token",
            "Content-Type": "application/json",
        })
        mock_lp_api_builder.return_value.add_body.assert_called_with({
            "start": {"from": start_time, "to": end_time},
            "contentToRetrieve": ["consumerParticipants", "messageRecords", "monitoring"],
            "status": ["OPEN", "OVERDUE"],
        })
        mock_lp_api_builder.return_value.add_params.assert_called_with({
            "offset": offset,
            "limit": 100,
            "source": "sahar_AI_openConv",
        })
        mock_execute.assert_called_with(mock_api_call)
        mock_check_response.assert_called_with(mock_response, True)
        self.assertEqual(str(context.exception), "API call failed with status 401")

    @patch('server_project.lp_api_manager.lp_utils.LpUtils.lp_login')
    @patch('server_project.lp_api_manager.lp_utils.ConfigUtil')
    @patch('server_project.lp_api_manager.lp_executor.LpExecutor.execute')
    @patch('logging.warning')
    def test_check_response_failure(self, mock_logging_warning, mock_execute,
                                    mock_config_util, mock_lp_login):
        mock_config_util.return_value.get_config_attribute = lambda attribute: {
            "userName": "test_user",
            "password": "test_pass",
            "accountId": "test_account_id",
            "serviceLogInName": "test_service_name",
            "messageHistName": "test_message_hist_name",
            "numberOfRetriesAPICalls": "0"
        }.get(attribute)
        mock_lp_login.return_value = MagicMock(
            status_code=200,
            json=lambda: {"bearer": "test_bearer_token"},
            headers={"content-type": "application/json"}
        )
        lp_utils = LpUtils()
        lp_utils.bearer_token = "old_token"
        unauthorized_response = MagicMock()
        unauthorized_response.status_code = 401
        unauthorized_response.headers = {"content-type": "application/json"}
        unauthorized_response.json.return_value = {"error": "Unauthorized"}
        result = lp_utils.check_response(unauthorized_response, is_need_authentication=True)
        mock_logging_warning.assert_called_once_with("Unauthorized, try to authenticate")
        self.assertEqual(result, {"error": "Unauthorized"})
        non_json_response = MagicMock()
        non_json_response.status_code = 200
        non_json_response.headers = {"content-type": "text/plain"}
        non_json_response.content = "Unexpected Content"
        result = lp_utils.check_response(non_json_response)
        self.assertEqual(result, "Unexpected Content")
        no_header_response = MagicMock()
        no_header_response.status_code = 500
        no_header_response.headers = {}
        no_header_response.content = "Server Error"
        result = lp_utils.check_response(no_header_response)
        self.assertEqual(result, "Server Error")
        valid_json_response = MagicMock()
        valid_json_response.status_code = 200
        valid_json_response.headers = {"content-type": "application/json"}
        valid_json_response.json.return_value = {"success": True}
        result = lp_utils.check_response(valid_json_response)
        self.assertEqual(result, {"success": True})





if __name__ == '__main__':
    unittest.main()
