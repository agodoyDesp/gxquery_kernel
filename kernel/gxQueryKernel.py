import requests
import json
import constants

from ipykernel.kernelbase import Kernel


def start_session():
    url = constants.BASE_URL+'/GXquery_StartSessionService'
    start_session_data = {'RepositoryName': '', 'UserName': 'andres', 'Password': 'andres'}
    start_session_data_resp = requests.post(url, json=start_session_data)
    resp = json.loads(start_session_data_resp.text)

    return resp


def set_headers(session_token):
    headers = {
        'GeneXus-Agent': 'SmartDevice',
        'Authorization': session_token,
        'Content-Type': 'application/json'
    }

    return headers


def set_metadata(headers, gxquery_context):
    guid = gxquery_context["CurrentRepositoryGUID"]
    sesid = gxquery_context["SessionId"]
    usergui = gxquery_context["UserGUID"]
    usernam = gxquery_context["UserName"]
    url = constants.BASE_URL+'/GXquery_SetMetadataService'

    set_metadata_dict = json.dumps({
        'GXqueryContextIn': gxquery_context,
        'MetadataName': constants.METADATA
    })

    resp = requests.post(url, data=set_metadata_dict, headers=headers)
    print(resp.text)
    return json.loads(resp.text)


def get_query_by_name(headers, gxquery_context):
    url = constants.BASE_URL+'/GXquery_GetQueryByNameService'
    get_query_by_name_dict = json.dumps({
        'QueryName': constants.QUERY_NAME,
        'GXqueryContext': gxquery_context
    })

    resp = requests.post(url, data=get_query_by_name_dict, headers=headers)

    return json.loads(resp.text)


def execute_query(headers, gxquery_context):
    url = constants.BASE_URL + '/GXquery_ExecuteQueryService'
    execute_query_dict = json.dumps({
        'QueryName': constants.QUERY_NAME,
        'QueryViewerServicesVersion': 1,
        'RuntimeParameters': [],
        'OutputFormatId': "",
        'ServiceOptions': [],
        'GXqueryContext': gxquery_context
    })

    resp = requests.post(url, data=execute_query_dict, headers=headers)

    return json.loads(resp.text)


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
        headers = set_headers(start_session_data_resp['GXquerySessionToken'])
        set_metadata_resp = set_metadata(headers, start_session_data_resp["GXqueryContext"])
        get_query_by_name_resp = get_query_by_name(headers, set_metadata_resp["GXqueryContextOut"])
        execute_query_resp = execute_query(headers, set_metadata_resp["GXqueryContextOut"])

        return {'status': 'ok',
                'execution_count':
                    self.execution_count,
                'payload': [],
                'user_expressions': {},
                }


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp

    IPKernelApp.launch_instance(kernel_class=GxQueryKernel)
