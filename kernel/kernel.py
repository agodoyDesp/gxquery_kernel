import requests
import json
import constants
import xmltodict
import pandas

from ipykernel.kernelbase import Kernel


def start_session():
    url = constants.BASE_URL + '/GXquery_StartSessionService'
    start_session_data = {'RepositoryName': '', 'UserName': 'andres', 'Password': 'andres'}
    start_session_data_resp = requests.post(url, json=start_session_data)

    return json.loads(start_session_data_resp.text)


def end_session(headers, gxquery_context):
    url = constants.BASE_URL + '/GXquery_EndSessionService'
    end_session_dict = json.dumps({
        'GXqueryContext': gxquery_context
    })

    resp = requests.post(url, data=end_session_dict, headers=headers)
    return resp.status_code


def set_headers(session_token):
    headers = {
        'GeneXus-Agent': 'SmartDevice',
        'Authorization': session_token,
        'Content-Type': 'application/json'
    }

    return headers


def set_metadata(headers, gxquery_context):
    url = constants.BASE_URL + '/GXquery_SetMetadataService'

    set_metadata_dict = json.dumps({
        'GXqueryContextIn': gxquery_context,
        'MetadataName': constants.METADATA
    })

    resp = requests.post(url, data=set_metadata_dict, headers=headers)
    print('metaData' + resp.text)
    return json.loads(resp.text)


def get_query_by_name(query_name, headers, gxquery_context):
    url = constants.BASE_URL + '/GXquery_GetQueryByNameService'
    get_query_by_name_dict = json.dumps({
        'QueryName': query_name,
        'GXqueryContext': gxquery_context
    })

    resp = requests.post(url, data=get_query_by_name_dict, headers=headers)

    return json.loads(resp.text)


def execute_query(query_name, headers, gxquery_context):
    url = constants.BASE_URL + '/GXquery_ExecuteQueryService'
    execute_query_dict = json.dumps({
        'QueryName': query_name,
        'QueryViewerServicesVersion': 1,
        'RuntimeParameters': [],
        'OutputFormatId': "",
        'ServiceOptions': [],
        'GXqueryContext': gxquery_context
    })

    resp = requests.post(url, data=execute_query_dict, headers=headers)

    return json.loads(resp.text)


def build_table(execute_query_resp):
    query_result = execute_query_resp['GXqueryExecuteQueryResult']
    column_names_xml = xmltodict.parse(query_result['GetMetadata'])
    col_names = []
    for name in column_names_xml['OLAPCube']['OLAPDimension']:
        col_names.append(name['@displayName'])  # insetar usando el valor dataField para el orden de las columnas
    row_data_xml = xmltodict.parse(query_result['GetData'])
    rows_xml = row_data_xml['Recordset']['Page']['Record']
    df = pandas.DataFrame(rows_xml)
    df.columns = col_names
    cell_hover = {
        'selector': 'td:hover',
        'props': [('background-color', '#ffffb3')]
    }
    index_names = {
        'selector': '.index_name',
        'props': 'font-style: italic; color: darkgrey; font-weight:normal;'
    }
    headers = {
        'selector': 'th:not(.index_name)',
        'props': 'background-color: #000066; color: white;'
    }
    df.style.set_table_styles([cell_hover, index_names, headers])
    #return df.style.to_html()
    return df.to_html(notebook=True, index=False)


class GxQueryKernel(Kernel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        start_session_data_resp = start_session()
        self.headers = set_headers(start_session_data_resp['GXquerySessionToken'])
        self.set_metadata_resp = set_metadata(self.headers, start_session_data_resp["GXqueryContext"])

    async def do_debug_request(self, msg):
        pass

    def do_apply(self, content, bufs, msg_id, reply_metadata):
        pass

    def do_clear(self):
        pass

    implementation = 'gxQuery_kernel'
    implementation_version = '1.0'
    language = 'gxQuery'
    language_version = '0.1'
    language_info = {
        'name': 'gxQuery',
        'mimetype': 'text/html',
        'file_extension': '.html',
    }
    banner = "GxQuery kernel "

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        execute_query_resp = execute_query(code, self.headers, self.set_metadata_resp["GXqueryContextOut"])
        table = build_table(execute_query_resp)

        self.send_response(self.iopub_socket, 'display_data', {
            'metadata': {},
            'data': {
                'text/html': table}
        })

        return {'status': 'ok',
                'execution_count':
                    self.execution_count,
                'payload': [],
                'user_expressions': {},
                }

    def do_shutdown(self, restart):
        end_session(self.headers, self.set_metadata_resp["GXqueryContextOut"])
        return {'restart': restart}


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp

    IPKernelApp.launch_instance(kernel_class=GxQueryKernel)
