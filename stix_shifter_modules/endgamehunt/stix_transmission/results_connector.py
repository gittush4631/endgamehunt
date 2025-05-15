import json
from stix_shifter_utils.modules.base.stix_transmission.base_json_results_connector\
    import BaseJsonResultsConnector
from stix_shifter_utils.utils.error_response import ErrorResponder
from stix_shifter_utils.utils import logger
from aiohttp.client_exceptions import ClientConnectionError


class LimitOutOfRangeError(Exception):
    pass

class QueryIdNotFoundError(Exception):
    pass

class AuthenticationError(Exception):
    pass

class ResultsConnector(BaseJsonResultsConnector):
    """ResultsConnector class"""
    def __init__(self, api_client):
        self.api_client = api_client
        self.logger = logger.set_logger(__name__)
        self.connector = __name__.split('.')[1]

    async def create_results_connection(self, search_id, offset, length):
        """
        Fetching the results using query, offset and length
        :param search_id: str, Data Source queryID
        :param offset: str, Offset value
        :param length: str, Length value
        :return: dict
        """
        try:
            print("Inside create_result connector")
            min_range = int(offset)
            max_range = int(offset) + int(length)
            
            return_obj = {}
            response_dict = dict()

            response = await self.api_client.get_search_results(
                search_id, min_range, max_range)
            print("====================back to results_connector.py----==========================")
            response_code = response.code
            print("====================max range and min range--==========================")
            print(min_range)
            print(max_range)
            print("====================max range and min range end--==========================")
            response_txt = response.read().decode('utf-8')
            response_dict = json.loads(response_txt)
            print("====================================INITIAL RESPONSE IN RESULT CONNECTOR==============================")
            print(response_dict)
            print("====================================INITIAL RESPONSE IN RESULT CONNECTOR END==============================")
            total_data = []

            #Construct a response object
            if response_code == 200:
                return_obj['success'] = True
                if("results" in response_dict['data']):
                    print("CHAT API RESULTS LOADED")
                    print(response_dict['data']['results'][0])
                    for item in response_dict['data']['results']:
                        total_data.append(item)
                    return_obj['data']=total_data
                    print("++++++++++final return obj for the chat api investigation++++++++++++++++++++++++++++++++++")
                    print(return_obj)
                    print("++++++++++final return obj++++++++++++++++++++++++++++++++++")    
                else:
                    print("=====================status code 200 calling check_empty_data=======")
                    response_dict = ResultsConnector.check_empty_data(response_dict)
                    for item in response_dict['data']:
                        total_data.append(item)
                    return_obj['data'] =total_data
                    print("++++++++++final return obj++++++++++++++++++++++++++++++++++")
                    print(return_obj)
                    print("++++++++++final return obj++++++++++++++++++++++++++++++++++")
            elif response_code == 400:
                return_obj['success'] = False
                response_code = response_dict.get("errors")[0].get("code")
                if response_code == 4000010:
                    raise LimitOutOfRangeError
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
                ErrorResponder.fill_error(return_obj, response_dict, ['message'],
                                          connector=self.connector)

            """
            if response_dict.get("pagination"):
                pagination_dict = response_dict.get("pagination")
                if pagination_dict.get("nextCursor"):
                    cursor = pagination_dict.get("nextCursor")
                else:
                    cursor = None

                while cursor is not None:
                    response = await self.api_client.get_search_results(
                        search_id, min_range, max_range, nextcursor=cursor)
                    response_code = response.code
                    response_txt = response.read().decode('utf-8')
                    response_dict = json.loads(response_txt)
                    response_dict = self.check_empty_data(response_dict)

                    for item in response_dict['data']:
                        total_data.append(item)

                    if response_dict.get("pagination"):
                        pagination_dict = response_dict.get("pagination")
                        if pagination_dict.get("nextCursor"):
                            cursor = pagination_dict.get("nextCursor")
                        else:
                            cursor = None

            if response_code == 200:
                return_obj['success'] = True
                return_obj['data'] = total_data[min_range:max_range] if total_data else []
            elif response_code == 400:
                return_obj['success'] = False
                response_code = response_dict.get("errors")[0].get("code")
                if response_code == 4000010:
                    raise LimitOutOfRangeError
            else:
                ErrorResponder.fill_error(return_obj, response_dict, ['message'],
                                          connector=self.connector)
            """
        except AuthenticationError:
            response_dict['type'] = "AuthenticationError"
            response_dict['message'] = "Invalid apitoken"
            ErrorResponder.fill_error(return_obj, response_dict, ['message'],
                                      connector=self.connector)
        except ClientConnectionError:
            response_dict['type'] = "ConnectionError"
            response_dict['message'] = "Invalid Host"
            ErrorResponder.fill_error(return_obj, response_dict, ['message'],
                                      connector=self.connector)
        except LimitOutOfRangeError:
            response_dict['type'] = "LimitOutOfRangeError"
            response_dict['message'] = "Limit must be greater than or equals to 1 " \
                                       "and less than equals to 1000"
            ErrorResponder.fill_error(return_obj, response_dict, ['message'],
                                      connector=self.connector)
        except QueryIdNotFoundError:
            response_dict['type'] = "QueryIdNotFoundError"
            response_dict['message'] = "Could not find query id: " + search_id
            ErrorResponder.fill_error(return_obj, response_dict, ['message'],
                                      connector=self.connector)
        except Exception as ex:
            self.logger.error('error in query result: %s', str(ex))
            ErrorResponder.fill_error(return_obj, response_dict, ['message'],
                                      connector=self.connector)
        return return_obj

    @staticmethod
    def check_empty_data(res_dict):
        """
        Format the results in json format
        :param item: list of dictionary items
        :return: list
        """
        #flatten the sensor object
        count=0
        for item in res_dict['data']:
            print("check empty list started")
            if item.get("sensors"):
                print("sensor present")
                sensor=item.get("sensors")[0]
                sensorkeys=sensor.keys()
                for key in sensorkeys:
                    item["sensor_"+key]=sensor[key]
                item.pop("sensors")
                item.pop("tags")
                item.pop("groups")
            if item.get("indexed_at"):
                print("ALERT OBJECT as INDEXED at is present =====================================================")
                alert_id=item.get('id')
                alert_type=item.get('type')
                item['alert_id']=alert_id
                item['alert_type']=alert_type
                
                
            
            #ResultsConnector.replace_escape_character(item)
            #print(res_dict)
            print("------------------final flatted object above from change method===============================")
        return res_dict

    @staticmethod
    def replace_escape_character(item):
        """
        replace escape character from results in json format
        :param item: list of dictionary items
        """
        if item is not None:
            fields = ['processCmd', 'srcProcCmdLine', 'tgtProcCmdLine',
                      'processImagePath', 'signatureSignedInvalidReason',
                      'srcProcImageSha1', 'srcProcParentActiveContentPath',
                      'srcProcParentImagePath', 'tgtFilePath', 'srcProcParentImagePath',
                      'srcProcParentImageSha1', 'fileFullName', 'srcProcActiveContentPath',
                      'storyline', 'tgtFileDescription', 'tgtFileOldPath',
                      'srcProcImageSha256', 'srcProcParentCmdLine', 'srcProcParentImageSha256']

            for fieldname in fields:
                if item.get(fieldname) is not None:
                    val = item.get(fieldname)
                    # Escaping the double quote in certain fields value like srcProcCmdLine
                    if val.find("\"") != -1:
                        val = val.replace('\"', '\\"')
                    elif val.find('"') != -1:
                        val = val.replace('"', '\\"')
                    item[fieldname] = val
