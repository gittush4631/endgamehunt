import json
import time
from stix_shifter_utils.stix_transmission.utils.RestApiClientAsync import RestApiClientAsync

class APIClient():

    QUERY_ENDPOINT = 'api/v1/endpoints'
    ALERT_ENDPOINT = 'api/v1/alerts'
    RESULT_ENDPOINT = 'api/v1/endpoints'
    CHAT_ENDPOINT = 'api/v1/chat'
    QUERY_SUMMARY = 'api/v1/collections/query-summary'
    QUERY_ROWS = 'api/v1/collections/query-rows'
    PING_STATUS = 'api/v1/license/status'
    query={}

    def __init__(self, connection, configuration):

        headers = dict()
        self.auth = configuration.get('auth')
        self.api_key = "JWT " + self.auth.get('apitoken')
        print("==================================start withing the api-client.py code section ==================================")
        print(self.api_key)
        print("==================================end withing the api-client.py code section ==================================")
        headers['Authorization'] = self.api_key
        headers['Content-type'] = 'application/json'
        self.timeout = connection['options']['timeout']
        self.client = RestApiClientAsync(connection.get('host'),
                                     connection.get('port', None),
                                     headers,
                                     url_modifier_function=None
                                     )
        print(self.client)
        print(headers)

    async def ping_datasource(self):
        """
        ping or check the system status
        """
        endpoint = self.PING_STATUS
        print(" ==================================withing the ping datasource code section ==================================")
        print(endpoint)
        print("==================================withing the ping datasource code section ==================================")
        return await self.client.call_api(endpoint, 'GET', headers=self.client.headers, timeout=self.timeout)

    def create_search_sendquery(self, query_expression):
        """
        init query
        :param data source query
        :return:queryId
        """
        
        endpoint = self.QUERY_ENDPOINT
        print("within the create_search================")
        data = query_expression
        responseObj={}
        print("Printing the query expressions================================")
        print(data)
        #GETTING new splitting of query logic for parameter and value
        data=json.loads(data)
        querystr=data['query']
        newquery=""
        if('raw_text' in querystr):
            print("RAW TEXT PRESENT----------creating chat query")
            newquery=querystr[12:]
            qend=newquery.index('"')
            newquery=newquery[:qend]
            print("=======================================NEW QUERY FOR CHAT====================")
            print(newquery)
        splited=querystr.split()
        print("========================splitted string=========================")
        print(splited)
        
        params=dict()
        params[splited[0]]=splited[2]

        if(splited[0]=='alert_ip_address'):
            print("ALERT BY IP ADDRESS")
            params['ip_address']=splited[2]
            params.pop('alert_ip_address')
            print(params)
            responseObj=params
            responseObj['code']=200
            responseObj['oper']='alerts'
            print("========response obj alerts query dict=======")
            print(responseObj)
            return responseObj
        elif(splited[0]=='alert_id'):
            print("ALERT BY ALERT_ID")
            params['id']=splited[2]
            params.pop('alert_id')
            print(params)
            responseObj=params
            responseObj['code']=200
            responseObj['oper']='alerts'
            print("========response obj alerts query dict for alert id=======")
            print(responseObj)
            return responseObj
        elif(splited[0]=='timestamp'):
            print("ALERT BY TIMELIME")
            
            params['indexed_from']=splited[6]
            params['indexed_to']=splited[8]
            #params.pop('alert_id')
            print(params)
            responseObj=params
            responseObj['code']=200
            responseObj['oper']='alerts'
            print("========response obj alerts query dict for alert id=======")
            print(responseObj)
            return responseObj
        elif(splited[0]=='raw_text'):
            print("================================Creating investigation using CHATAPI=====================================")
            
            params['raw_text']=newquery
            #params['indexed_to']=splited[8]
            #params.pop('chat_text')
            print("==================================CHAT API PARAMS DICT===============================")
            print(params)
            responseObj=params
            responseObj['code']=200
            responseObj['oper']='chat'
            print("========response obj CHAT API query dict for raw_text===============")
            print(responseObj)
            return responseObj    
        else:
            print("========final params dict=======")
            print(params)
            print("========final params dict=======")
            print("Printed the  query expressions calling the GET call================================")
            responseObj=params
            responseObj['code']=200
            print("========response obj params dict=======")
            print(responseObj)
            return responseObj
        
    async def create_search_for_alerts(self, params):
        
        #get query status
        #:param queryId:
        #:return:
        
        print("Inside create search for ================================")
        print(params)
        responseObj={}
        responseObj=params
        responseObj['code']=200
        reponseObj['oper']='alerts'
        print("========response obj params dict=======")
        print(responseObj)
        return responseObj
    

    async def get_search_status(self, search_id):
        
        #get query status
        #:param queryId:
        #:return:
        
        print("Inside get_search_status================================")
        print("search id")
        print(search_id)
        
        endpoint = self.QUERY_STATUS + "?queryId=" + search_id
        #endpoint = self.QUERY_STATUS + "?ipaddress=10.2.19.187"
        print(endpoint)
        params = {}
        params['output'] = 'json'
        return await self.client.call_api(endpoint, 'GET', headers=self.client.headers, urldata=params, timeout=self.timeout)


    async def get_search_results(self, search_id, offset, length, nextcursor=None):
        """
        Get results from Data Source
        :param query: Data Source QueryId,nextcursor,limit
        :return: Response Object
        """
        print("inside get_search_results api_client.py")
        print(search_id)
        print(type(search_id))
        endpoint = self.QUERY_ENDPOINT
        #Max limit of getting result in a api call is 1000
        limit = 1000
        print("default endpoint=======output")
        print(endpoint)
        params=dict()
        checkoper=search_id.split('="')
        splitedsid=search_id.split('="')
        splitedsid[1]=splitedsid[1].replace('"','')
        if 'alert"' in checkoper:
            print("alert OPERATION IN get_results")
            
            params[splitedsid[0]]=splitedsid[1]
            print("API CALL for IP")
            if(splitedsid[0]=='id' or splitedsid[0]=='indexed_from' or splitedsid[0]=='indexed_to'):
                print("API CALL TO CALL SINGLE ALERT BASED ON ID and TIMELINE")
                if(splitedsid[0]=='indexed_from'):
                    splitedsid[3]=splitedsid[3].replace('"','')
                    params[splitedsid[0]]=splitedsid[1]
                    params[splitedsid[2]]=splitedsid[3]

                    print("---------------------------------------change in indexed from completed to form params--------------------")
                print(params)
                endpoint=self.ALERT_ENDPOINT
                print("new endpoint")
                print(endpoint)
                return await self.client.call_api(endpoint, 'GET', headers=self.client.headers, urldata=params, timeout=self.timeout)
            else:    
                print(params)
                res=await self.client.call_api(endpoint, 'GET', headers=self.client.headers, urldata=params, timeout=self.timeout)
                response_txt = res.read().decode('utf-8')
                response_dict = json.loads(response_txt)  
                print(response_dict)  
                endpointid=response_dict['data'][0]['id'] 
                print("endpoint id")
                print(endpointid)
                endpoint=self.ALERT_ENDPOINT
                print("new endpoint")
                print(endpoint)
                #endpoint=self.QUERY_ENDPOINT
                paramsnew={}
                paramsnew['endpoint_id']=endpointid
                print(paramsnew)
                return await self.client.call_api(endpoint, 'GET', headers=self.client.headers, urldata=paramsnew, timeout=self.timeout)
        elif('chat"' in checkoper):
            print("============================CHAT API in api_client.py get_search results ====================")
            endpoint=self.CHAT_ENDPOINT
            print("chat endpoint is")
            print(endpoint)
            rawdata=checkoper[0][9:]
            print("raw_text final query")
            print(rawdata)
            data=json.dumps({'raw_text':rawdata})
            print(data)
            

            res = await self.client.call_api(endpoint, 'POST', headers=self.client.headers, data=data, timeout=self.timeout)
            data=json.dumps({'raw_text':'yes'})
            
            print(data)
            print("Calling yes in chat API")
            res= await self.client.call_api(endpoint, 'POST', headers=self.client.headers, data=data, timeout=self.timeout)
            response_txt=res.read().decode('utf-8')
            response_dict=json.loads(response_txt)

            conlen=len(response_dict['conversation'])
            print(conlen)
            inv_id=response_dict['conversation'][conlen-2]['investigation_id']
            print("GOT INVESTIGATION ID")
            print(inv_id)
            paramsnew={}
            paramsnew['query']='events_all'
            paramsnew['investigation_id']=inv_id
            paramsnew['per_page']='50'
            print(paramsnew)
            endpoint=self.QUERY_ROWS
            print("rows endpoint")
            print(endpoint)
            count=0
            res_count=0
            while(count<18):
                count +=1
                res= await self.client.call_api(endpoint, 'GET', headers=self.client.headers, urldata=paramsnew, timeout=self.timeout)
                response_txt=res.read().decode('utf-8')
                response_dict=json.loads(response_txt)
                print("inside while loop")
                #print(response_dict)
                res_count=response_dict['metadata']['count']
                print(res_count)
                if(res_count>0):
                    print("found results")
                    break
                time.sleep(10)
            print("OUTSIDE WHILE LOOP") 
            return await self.client.call_api(endpoint, 'GET', headers=self.client.headers, urldata=paramsnew, timeout=self.timeout)

        else:
            params[splitedsid[0]]=splitedsid[1]
            print(params)       
            return await self.client.call_api(endpoint, 'GET', headers=self.client.headers, urldata=params, timeout=self.timeout)
        
        
    def delete_search(self, search_id):
        """
        delete api is not supported
        :param queryId:
        :return:dict
        """
        return {"code": 200, "success": True}
