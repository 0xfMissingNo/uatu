import os

import requests


class Sourcify:

    repo_url = 'https://repo.sourcify.dev/contracts/'

    def __init__(self, address, chain_id='1'):
        self.address = address
        self.chain_id = chain_id
        self.filename = None

    def check_by_address(self):
        url = 'https://sourcify.dev/server/'
        response = requests.get(url + f'checkByAddresses?addresses={self.address}&chainIds={self.chain_id}')
        if response.status_code == 200:
            return True
        return False

    def get_metadata(self):
        return self._get_endpoint('metadata.json').json()

    def _get_endpoint(self, endpoint):
        response = requests.get(self.repo_url + f'full_match/{self.chain_id}/{self.address}/{endpoint}')
        return response

    def get_source_file(self):
        output = self.get_metadata()
        filepath = list(output['sources'].keys())[0]
        self.filename = filepath.split('/')[-1]
        return self._get_endpoint(f'sources/{filepath}')

    def __enter__(self):
        if not self.check_by_address():
            return None
        data = self.get_source_file().text
        with open(self.filename, 'w+') as file_:
            file_.write(data)
        return self

    def __exit__(self, *args):
        if not hasattr(self, 'filename'):
            return args
        if os.path.exists(self.filename):
            os.remove(self.filename)
        return args
