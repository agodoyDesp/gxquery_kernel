import requests
import json

from ipykernel.kernelbase import Kernel


def start_session():
    start_session_data = {'RepositoryName': '', 'UserName': 'andres', 'Password': 'andres'}
    start_session_data_resp = requests.post('http://localhost:80/GXquery40/rest/GXquery_StartSessionService',
                                            json=start_session_data)
    resp = json.loads(start_session_data_resp.text)

    return resp


def set_metadata(session_token):
    # Esta dando error el request
    set_metadata_dict = {'CurrentMetaName': 'TravelAgencyGX16'}
    set_metadata_headers = {'GeneXus-Agent': 'SmartDevice',
                            'Authorization': 'OAuth' + session_token}
    set_metadata_resp = requests.post('http://localhost:80/GXquery40/rest/GXquery_SetMetadataService',
                                      json=set_metadata_dict, headers=set_metadata_headers)


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
