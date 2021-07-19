import requests


class Sourcify:

    repo_url = 'https://repo.sourcify.dev/contracts/'

    def __init__(self, address, chain_id='1'):
        self.address = address
        self.chain_id = chain_id
        self.filename = None
        self.code = self.get_source_code()

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

    def get_source_code(self):
        if not self.check_by_address():
            return None
        output = self.get_metadata()
        filepath = list(output['sources'].keys())[0]
        self.filename = filepath.split('/')[-1]
        return self._get_endpoint(f'sources/{filepath}').text
