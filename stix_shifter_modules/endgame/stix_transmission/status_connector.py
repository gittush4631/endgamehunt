import json
import time
from aiohttp.client_exceptions import ClientConnectionError
from stix_shifter_utils.modules.base.stix_transmission.\
    base_status_connector import BaseStatusConnector
from stix_shifter_utils.utils.error_response import ErrorResponder
from stix_shifter_utils.utils import logger


class InvalidResponseException(Exception):
    pass

class QueryIdNotFoundError(Exception):
    pass

class AuthenticationError(Exception):
    pass

class StatusConnector(BaseStatusConnector):
    
    #check query status class
    
    #ByPASS connector for now
    print("==========================Bypass Status connector1=================================================")
    def __init__(self, api_client):
        self.api_client = api_client
        self.logger = logger.set_logger(__name__)
        self.connector = __name__.split('.')[1]

    async def create_status_connection(self, search_id):
        
        #get query status
        #:param queryId
        #:return: data response
        try:
            print("================================inside status_connector.py---===============================")
            response = None
            response_dict = {}
            return_obj = {}
            return_obj['success'] = True
            return_obj['status'] = "COMPLETED"
            print(return_obj)
            """print("==========================Status connector call=================================================")
            response = await self.api_client.get_search_status(search_id)
            print("======got response=======")

            response_code = response.code
            response_txt = response.read()
            response_dict = json.loads(response_txt)
            print(response_dict)

            if response_code == 200:
                return_obj['success'] = True
                print("success reponse code 200")
                if response_dict["data"]["responseState"] == "FINISHED":
                    return_obj['status'] = "COMPLETED"
                    return_obj['progress'] = response_dict["data"]["progressStatus"]
                else:
                    return_obj['status'] = "RUNNING"
                    return_obj['progress'] = response_dict["data"]["progressStatus"]

            elif response_code == 404:
                return_obj['success'] = False
                response_code = response_dict.get("errors")[0].get("code")
                if response_code == 4040010:
                    raise QueryIdNotFoundError
            elif response_code == 401:
                return_obj['success'] = False
                response_code = response_dict.get("errors")[0].get("code")
                if response_code == 4010010:
                    raise AuthenticationError
            else:
                return_obj['success'] = False
                raise InvalidResponseException

        except AuthenticationError:
            response_dict['type'] = "AuthenticationError"
            response_dict['message'] = "Invalid apitoken"
            ErrorResponder.fill_error(return_obj, response_dict, ['message'],
                                      connector=self.connector)
            print("==========================Status connector10=================================================")
        except InvalidResponseException:
            response_dict['type'] = 'InvalidResponseException'
            response_dict['message'] = 'InvalidResponse'
            ErrorResponder.fill_error(return_obj, response_dict, ['message'],
                                      connector=self.connector)
        except QueryIdNotFoundError:
            response_dict['type'] = "QueryIdNotFoundError"
            response_dict['message'] = "Could not find query id: " + search_id
            ErrorResponder.fill_error(return_obj, response_dict, ['message'],
                                      connector=self.connector)
        except ConnectionError:
            response_dict['type'] = "ConnectionError"
            response_dict['message'] = "Invalid Host"
            ErrorResponder.fill_error(return_obj, response_dict, ['message'],
                                      connector=self.connector)
        except Exception as ex:
            if 'Max retries exceeded' in str(ex):
                #sleep added due to limitation of 1 call a second for each user token
                time.sleep(1)
                return_obj['status'] = "RUNNING"
                return_obj['progress'] = 50
                return return_obj
            else:
                response_dict['type'] = "unknown"
                response_dict['message'] = ex
                self.logger.error('error when checking status: %s', str(ex))
                ErrorResponder.fill_error(return_obj, response_dict, ['message'],
                                          connector=self.connector)
            """                              
        except Exception as e:
            return_obj['error']=e
            print("error in status_Connector.py " )
            print(e)
        return return_obj