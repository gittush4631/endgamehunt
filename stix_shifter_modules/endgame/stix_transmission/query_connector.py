import json
from stix_shifter_utils.modules.base.stix_transmission.base_query_connector \
    import BaseQueryConnector
from stix_shifter_utils.utils.error_response import ErrorResponder
from stix_shifter_utils.utils import logger
from aiohttp.client_exceptions import ClientConnectionError

class BadRequestQueryError(Exception):
    pass

class LimitOutOfRangeError(Exception):
    pass

class AuthenticationError(Exception):
    pass

class QueryConnector(BaseQueryConnector):
    """ Query connector base class """
    def __init__(self, api_client):
        self.api_client = api_client
        self.logger = logger.set_logger(__name__)
        self.connector = __name__.split('.')[1]

    async def create_query_connection(self, query):
        """
        init query
        :param query
        :return:queryId
        """
        try:
            # Construct a response object
            return_obj = {}
            response_dict = {}
            print("---------------------------------------===inside query creation in query_connector.py==============================")
            response = self.api_client.create_search_sendquery(query)
            print(type(response))
            print(response)

            print("---------------------------------------===icall success query_connector.py==============================")
            if 'oper' in response:
                response_oper=response['oper']
                print("OPERATION IS SEARCHING ALERTS")
                return_obj['success'] = True
                key=list(response)[0]
                print(key)
                if(key=='timestamp'):
                    key1=list(response)[1]
                    key2=list(response)[2]
                    searchnew=key1+"="+response[key1]+"="+key2+"="+response[key2]+'="alert"'
                    print("===================================time line search====================")
                    print(searchnew)
                    return_obj['search_id'] = searchnew              
                    print("==========return obj======================")
                    print(return_obj)
                    print("ALERT TIMELINE COMPLETED")
                else:
                    return_obj['search_id'] = key+"="+response[key]+'="alert"'               
                    print("==========return obj======================")
                    print(return_obj)
                    print("ALERT COMPLETED")
            else:
                response_code=response['code']
                print(response_code)  
                if response_code == 200:
                    print("inside 200 response code")
                    return_obj['success'] = True
                    key=list(response)[0]
                    print(key)
                    return_obj['search_id'] = key+"="+response[key]
                    print("==========return obj======================")
                    print(return_obj)
                    print("if completed")
                elif response_code == 401:
                    return_obj['success'] = False
                    response_code = response_dict.get("errors")[0].get("code")
                    if response_code == 4010010:
                        raise AuthenticationError
                elif response_code == 400:
                    return_obj['success'] = False
                    response_code = response_dict.get("errors")[0].get("code")
                    if response_code == 4000040:
                        raise BadRequestQueryError

                    if response_code == 4000010:
                        raise LimitOutOfRangeError
                else:
                    ErrorResponder.fill_error(return_obj, response_dict, ['message'],
                                            connector=self.connector)

        except AuthenticationError:
            response_dict['type'] = "AuthenticationError"
            response_dict['message'] = "Invalid apitoken"
            ErrorResponder.fill_error(return_obj, response_dict, ['message'],
                                    connector=self.connector)
        except ConnectionError:
            response_dict['type'] = "ConnectionError"
            response_dict['message'] = "Invalid Host"
            ErrorResponder.fill_error(return_obj, response_dict, ['message'],
                                    connector=self.connector)
        except LimitOutOfRangeError:
            response_dict['type'] = "LimitOutOfRangeError"
            response_dict['message'] = "Limit must be greater than or equal to 1 " \
                                    "and less than or equal to 100000"
            ErrorResponder.fill_error(return_obj, response_dict, ['message'],
                                    connector=self.connector)
        except BadRequestQueryError:
            response_dict['type'] = "BadRequestQueryError"
            response_dict['message'] = response_dict.get("errors")[0].get("detail")
            ErrorResponder.fill_error(return_obj, response_dict, ['message'],
                                    connector=self.connector)
        except Exception as ex:
            response_dict['type'] = "unknown"
            response_dict['message'] = ex
            self.logger.error('error when creating search: %s', str(ex))
            ErrorResponder.fill_error(return_obj, response_dict, ['message'],
                                    connector=self.connector)
        return return_obj
