import unittest
from unittest.mock import patch, MagicMock
from requests import RequestException
from server_project.lp_api_manager.lp_api_call import LpApiCall
from server_project.lp_api_manager.lp_executor import LpExecutor

class test_LivePerson_Executor(unittest.TestCase):
    @patch("logging.error")
    @patch("logging.warning")
    def test_log_success(self, mock_warning, mock_error):
        prepared_request = MagicMock()
        prepared_request.headers = {'Content-Type': 'application/json'}
        prepared_request.body = '{"key": "value"}'
        prepared_request.url = "https://test.api.com"
        prepared_request.method = "GET"
        executor = LpExecutor()
        executor._log(current_try=1, number_of_retries=3, message="Request failed", prepared_request=prepared_request)
        mock_warning.assert_called_once_with("Number of retries: 1, Message: Request failed")
        mock_error.assert_not_called()

    @patch("logging.error")
    @patch("logging.warning")
    def test_log_last_attempt_failure(self, mock_warning, mock_error):
        prepared_request = MagicMock()
        prepared_request.headers = {'Content-Type': 'application/json'}
        prepared_request.body = '{"key": "value"}'
        prepared_request.url = "https://test.api.com"
        prepared_request.method = "GET"
        executor = LpExecutor()
        executor._log(current_try=2, number_of_retries=3, message="Request failed", prepared_request=prepared_request)
        mock_error.assert_any_call("Error message: Request failed")
        self.assertEqual(len(mock_error.call_args_list), 2)
        mock_warning.assert_not_called()

    @patch("logging.error")
    @patch("logging.warning")
    def test_log_non_last_attempt_failure(self, mock_warning, mock_error):
        prepared_request = MagicMock()
        prepared_request.headers = {'Content-Type': 'application/json'}
        prepared_request.body = '{"key": "value"}'
        prepared_request.url = "https://test.api.com"
        prepared_request.method = "GET"
        executor = LpExecutor()
        executor._log(current_try=1, number_of_retries=3, message="Request failed", prepared_request=prepared_request)
        mock_warning.assert_called_once_with("Number of retries: 1, Message: Request failed")
        mock_error.assert_not_called()

    @patch("logging.error")
    @patch("logging.warning")
    def test_log_last_attempt_failure_no_prepared_request(self, mock_warning, mock_error):
        executor = LpExecutor()
        executor._log(current_try=2, number_of_retries=3, message="Request failed", prepared_request=None)
        mock_warning.assert_not_called()
        mock_error.assert_called_once_with(
            "Error message: Request failed"
        )

    @patch("logging.error")
    @patch("logging.warning")
    def test_log_non_last_attempt_failure_no_prepared_request(self, mock_warning, mock_error):
        executor = LpExecutor()
        executor._log(current_try=1, number_of_retries=3, message="Request failed", prepared_request=None)
        mock_warning.assert_called_once_with("Number of retries: 1, Message: Request failed")
        mock_error.assert_not_called()

    @patch("requests.Session.send")
    def test_execute_success(self, mock_send):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_send.return_value = mock_response
        api_call = LpApiCall(
            type=MagicMock(value="POST"),
            url="https://test.api.com",
            headers={"Authorization": "Bearer test_token"},
            json={"key": "value"},
        )
        executor = LpExecutor()
        response = executor.execute(api_call, number_of_retries=1, verbose=True)
        self.assertEqual(response, mock_response)

    @patch("requests.Session.send")
    def test_execute_failure_404(self, mock_send):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_send.return_value = mock_response
        api_call = LpApiCall(
            type=MagicMock(value="GET"),
            url="https://test.api.com/missing",
        )
        executor = LpExecutor()
        with self.assertLogs(level="ERROR") as log:
            executor.execute(api_call, number_of_retries=2)
            self.assertTrue(any("404 Not Found" in entry for entry in log.output))

    @patch("requests.Session.send")
    def test_execute_failure_401(self, mock_send):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_send.return_value = mock_response
        api_call = LpApiCall(
            type=MagicMock(value="GET"),
            url="https://test.api.com/unauthorized",
        )
        executor = LpExecutor()
        with self.assertLogs(level="ERROR") as log:
            executor.execute(api_call, number_of_retries=2)
            self.assertTrue(any("Unauthorized — Bad Authentication" in entry for entry in log.output))

    @patch("requests.Session.send")
    def test_execute_failure_403(self, mock_send):
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_send.return_value = mock_response
        api_call = LpApiCall(
            type=MagicMock(value="GET"),
            url="https://test.api.com/forbidden",
        )
        executor = LpExecutor()
        with self.assertLogs(level="ERROR") as log:
            executor.execute(api_call, number_of_retries=2)
            self.assertTrue(any("Unauthorized — Forbidden request" in entry for entry in log.output))

    @patch("requests.Session.send")
    @patch("time.sleep", return_value=None)
    def test_execute_retry_on_429(self, mock_sleep, mock_send):
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "2"}
        mock_send.return_value = mock_response
        api_call = LpApiCall(
            type=MagicMock(value="GET"),
            url="https://test.api.com/too-many-requests",
        )
        executor = LpExecutor()
        with self.assertLogs(level="WARNING") as log:
            executor.execute(api_call, number_of_retries=2)
            self.assertEqual(
                log.output[0],
                "WARNING:root:Number of retries: 0, Message: Too Many Requests — Retry after 2 seconds"
            )
            mock_sleep.assert_called_with(2)

    @patch("requests.Session.send")
    @patch("time.sleep", return_value=None)
    def test_execute_retry_on_500(self, mock_sleep, mock_send):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_send.return_value = mock_response
        api_call = LpApiCall(
            type=MagicMock(value="GET"),
            url="https://test.api.com/server-error",
        )
        executor = LpExecutor()
        with self.assertLogs(level="ERROR") as log:
            executor.execute(api_call, number_of_retries=3)
            self.assertTrue(any("Internal server error" in entry for entry in log.output))
            mock_sleep.assert_called_with(15)

    @patch("requests.Session.send")
    def test_execute_unhandled_status_code(self, mock_send):
        mock_response = MagicMock()
        mock_response.status_code = 418
        mock_send.return_value = mock_response
        api_call = LpApiCall(
            type=MagicMock(value="GET"),
            url="https://test.api.com/teapot",
        )
        executor = LpExecutor()
        with self.assertLogs(level="ERROR") as log:
            executor.execute(api_call, number_of_retries=2)
            self.assertTrue(any("Unhandled status code: 418" in entry for entry in log.output))

    @patch("requests.Session.send")
    def test_execute_request_exception(self, mock_send):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_send.return_value = mock_response
        mock_send.side_effect = [mock_response, RequestException("Request failed")]
        api_call = LpApiCall(
            type=MagicMock(value="GET"),
            url="https://test.api.com/exception",
        )
        executor = LpExecutor()
        with self.assertLogs(level="ERROR") as log:
            try:
                executor.execute(api_call, number_of_retries=2)
            except RequestException:
                self.assertTrue(any("Error executing lp_api_manager call" in entry for entry in log.output))


if __name__ == "__main__":
    unittest.main()
