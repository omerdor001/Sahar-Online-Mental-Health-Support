"""
    APIConstants Class

    This class provides URI constants used in the project and functions to generate full URI strings
    based on provided arguments.
    """


class LpApiConstants:
    baseURI = (
        "https://api.liveperson.net/api/account/%s/service/%s/baseURI.json?version=1.0"
    )
    loginCall = "https://%s/api/account/%s/login?v=1.3"
    messageHistory = "https://%s/messaging_history/api/account/%s/conversations/search"
    getConvByConvId = "https://%s/messaging_history/api/account/%s/conversations/conversation/search"


    @staticmethod
    def base_call_uri(account, service):
        # account - LivePerson account ID string
        # service - Service name according to the relevant lp_api_manager string
        return LpApiConstants.baseURI % (account, service)

    @staticmethod
    def login_call_uri(domain, account_id):
        return LpApiConstants.loginCall % (domain, account_id)

    @staticmethod
    def get_conv_by_conv_id_call(domain, account_id):
        # account - LivePerson account ID string
        # service - Service name according to the relevant lp_api_manager string
        return LpApiConstants.getConvByConvId % (domain, account_id)

    @staticmethod
    def message_hist_uri(domain, account_id):
        return LpApiConstants.messageHistory % (domain, account_id)
