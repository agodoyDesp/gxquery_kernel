import requests

from ipykernel.kernelbase import Kernel


class GxQueryKernel(Kernel):
    implementation = 'TestRest'
    implementation_version = '1.0'
    language = 'no-op'
    language_version = '0.1'
    language_info = {
        'name': 'gxQuery',
        'mimetype': 'text/plain',
        'file_extension': '.txt',
    }
    banner = "Rest test kernel "

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        response = requests.get('http://localhost:5000/' + code)
        stream_content = {'name': 'stdout', 'text': response.text}
        print(stream_content)
        self.send_response(self.iopub_socket,
                           'stream', stream_content)

        return {'status': 'ok',
                'execution_count':
                    self.execution_count,
                'payload': [],
                'user_expressions': {},
                }


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp

    IPKernelApp.launch_instance(kernel_class=GxQueryKernel)