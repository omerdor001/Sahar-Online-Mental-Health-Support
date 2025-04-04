import requests
import logging
import time

from lp_api_manager.lp_api_call import LpApiCall
from utils.config_util import ConfigUtil


"""
    LpExecutor Class

    This class wraps lp_api_manager calls, implements retry mechanism, handles lp_api_manager responses, and logging.

    Methods:
        _log(self, currentTry, numberOfRetries, message, prepared_request):
            Internal method to log messages and lp_api_manager call details based on retry attempts.

        execute(api_call: APICall, numberOfRetries=3):
            Executes the provided lp_api_manager call with optional retry mechanism.

    """


class LpExecutor:
    def _log(self, current_try, number_of_retries, message, prepared_request):
        if current_try == number_of_retries - 1:
            logging.error(f"Error message: {message}")
            if prepared_request:
                logging.error(
                    f"lp_api_manager Call: Headers - {prepared_request.headers}, Body - {prepared_request.body},"
                    f" Url - {prepared_request.url}, Type - {prepared_request.method}"
                )
        else:
            logging.warning(f"Number of retries: {current_try}, Message: {message}")

    @staticmethod
    def execute(api_call: LpApiCall, number_of_retries: int = 0, verbose=False):
        if number_of_retries == 0:
            config_util = ConfigUtil()
            number_of_retries = config_util.get_config_attribute(
                "numberOfRetriesAPICalls"
            )
        for i in range(number_of_retries):
            try:
                # Make the lp_api_manager call
                prepared_request = requests.Request(
                    method=api_call.type.value,
                    url=api_call.url,
                    headers=api_call.headers if api_call.headers else None,
                    json=api_call.body if api_call.body else None,
                    params=api_call.params if api_call.params else None,
                ).prepare()
                if verbose:
                    logging.debug(
                        f"lp_api_manager call - "
                        f"Method - {prepared_request.method}, "
                        f"URL - {prepared_request.url}, "
                        f"Body - {prepared_request.body}, "
                        f"Headers - {prepared_request.headers}"
                    )
                session = requests.Session()
                response = session.send(prepared_request)

                # Check if the request was successful
                if response.status_code in range(200, 300):
                    logging.debug(
                        f"lp_api_manager Call: Headers - {prepared_request.headers}, Body - {prepared_request.body},"
                        f" Url - {prepared_request.url}, Type - {prepared_request.method}"
                    )
                    break
                # Handle specific error scenarios
                if response.status_code == 400:
                    LpExecutor()._log(
                        i,
                        number_of_retries,
                        "Bad request — Problem with body or query parameters",
                        prepared_request,
                    )
                elif response.status_code == 401:
                    LpExecutor()._log(
                        i,
                        number_of_retries,
                        "Unauthorized — Bad Authentication (invalid site, agent, or credentials)",
                        prepared_request,
                    )
                elif response.status_code == 403:
                    LpExecutor()._log(
                        i,
                        number_of_retries,
                        "Unauthorized — Forbidden request",
                        prepared_request,
                    )
                elif response.status_code == 404:
                    LpExecutor()._log(
                        i, number_of_retries, "404 Not Found", prepared_request
                    )
                elif response.status_code == 429:
                    retry_after = int(
                        response.headers.get("Retry-After", "5")
                    )  # Default to 5 seconds if no Retry-After header
                    LpExecutor()._log(
                        i,
                        number_of_retries,
                        f"Too Many Requests — Retry after {retry_after} seconds",
                        prepared_request,
                    )
                    time.sleep(retry_after)
                elif response.status_code in range(500, 600):
                    LpExecutor()._log(
                        i, number_of_retries, "Internal server error", prepared_request
                    )
                    if i == 0:
                        time.sleep(5)
                    elif i == 1:
                        time.sleep(10)
                    elif i == 2:
                        time.sleep(15)
                else:
                    LpExecutor()._log(
                        i,
                        number_of_retries,
                        f"Unhandled status code: {response.status_code}",
                        prepared_request,
                    )
            except requests.exceptions.RequestException as e:
                LpExecutor()._log(
                    i,
                    number_of_retries,
                    f"Error executing lp_api_manager call: {e}, response.status_codef: {response.status_code}",
                    prepared_request,
                )
        return response
