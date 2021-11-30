import requests
import json

from ipykernel.kernelbase import Kernel


def start_session():
    start_session_data = {'RepositoryName': '', 'UserName': 'alexgo', 'Password': 'Alex-11041989'}
    start_session_data_resp = requests.post('http://localhost:80/GXquery40/rest/GXquery_StartSessionService',
                                            json=start_session_data)
    resp = json.loads(start_session_data_resp.text)

    return resp


def set_metadata(session_token, gxquerycontext):
    # Esta dando error el request

    guid = gxquerycontext["CurrentRepositoryGUID"]
    sesid = gxquerycontext["SessionId"]
    usergui = gxquerycontext["UserGUID"]
    usernam = gxquerycontext["UserName"]
    set_metadata_dict = json.dumps({
        "GXqueryContextIn": {
            "AppPath": "C:\\GXquery40\\web\\",
            "CurrentKBLocation": "",
            "CurrentVersionId": "0",
            "CurrentMetaName": "",
            "CurrentMetaId": "",
            "CurrentRepositoryGUID": guid,
            "CurrentRepositoryName": "GXquery",
            "SessionId": sesid,
            "UserGUID": usergui,
            "UserName": usernam,
            "UserType": "MetadataAdministrator",
            "MultipleRepositories": False
        },
        "MetadataName": "TravelAgencyGX16"
    })
    set_metadata_headers = {
                    'GeneXus-Agent': 'SmartDevice',
                    'Authorization': session_token,
                    'Content-Type': 'application/json'
    }

    set_metadata_resp = requests.post('http://localhost:80/GXquery40/rest/GXquery_SetMetadataService',
                                      data=set_metadata_dict, headers=set_metadata_headers)

    print(set_metadata_resp.text)
    
    
 def get_query_by_name(session_token, gxquerycontext):
    guid = gxquerycontext["CurrentRepositoryGUID"]
    sesid = gxquerycontext["SessionId"]
    usergui = gxquerycontext["UserGUID"]
    usernam = gxquerycontext["UserName"]
    metaid = gxquerycontext["CurrentMetaId"]

    get_query_name_dict = json.dumps({
        "QueryName": "QueryAttractions",
        "GXqueryContext": {
            "AppPath": "C:\\GXquery40\\web\\",
            "CurrentKBLocation": "C:\\GXquery40\\KBCatalog\\"+metaid,
            "CurrentVersionId": "0",
            "CurrentMetaName": "TravelAgencyGX16",
            "CurrentMetaId": metaid,
            "CurrentRepositoryGUID": guid,
            "CurrentRepositoryName": "GXquery",
            "SessionId": sesid,
            "UserGUID": usergui,
            "UserName": usernam,
            "UserType": "MetadataAdministrator",
            "MultipleRepositories": False
        }
    })
    get_query_name_headers = {
        'GeneXus-Agent': 'SmartDevice',
        'Authorization': session_token,
        'Content-Type': 'application/json'
    }

    get_query_name_resp = requests.post("http://localhost:80/GXquery40/rest/GXquery_GetQueryByNameService",
                                        data=get_query_name_dict, headers=get_query_name_headers)

    print(get_query_name_resp.text)




class GxQueryKernel(Kernel):
    implementation = 'TestRest'
    implementation_version = '1.0'
    language = 'no-op'
    language_version = '0.1'
    language_info = {
        'name': 'gxQuery',
        'mimetype': 'text/html',
        'file_extension': '.html',
    }
    banner = "Rest test kernel "

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        response = requests.get('http://localhost:5000/' + code)
        # stream_content = {'name': 'stdout', 'text': response.text}
        # self.send_response(self.iopub_socket,
        #                   'stream', stream_content)

        self.send_response(self.iopub_socket, 'display_data', {
            'metadata': {},
            'data': {
                'text/html': response.text}
        })

        start_session_data_resp = start_session()
        set_metadata(start_session_data_resp['GXquerySessionToken'])

        return {'status': 'ok',
                'execution_count':
                    self.execution_count,
                'payload': [],
                'user_expressions': {},
                }


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp

    IPKernelApp.launch_instance(kernel_class=GxQueryKernel)
