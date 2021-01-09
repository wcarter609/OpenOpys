from json.decoder import JSONDecodeError
from requests import Session
from requests.models import ContentDecodingError

def _urljoin(*args):
    trailing_slash = '/' if args[-1].endswith('/') else ''
    return "/".join(map(lambda x: str(x).strip('/'), args)) + trailing_slash


class ResponseContentTypeError(Exception):

    def __init__(self, observed, expected, *args, **kwargs):
        Exception.__init__(self, f"Response content is of type '{observed}'. Must be '{expected}'")


class OpenOpys(Session):

    section_urls = {
        'composer': 'composer',
        'work': 'work',
        'genre': 'genre',
        'performer': 'performer'
    }

    def __init__(self, api_url='https://api.openopus.org', **kwargs):
        Session.__init__(self, **kwargs)
        self.api_url = api_url

    def get_json(self, url, **kwargs):
        """
        Wrap standard get method with steps to retrieve and return parsed json content from response.

        Raises ResponseContentTypeError if content is not of type JSON
        Raises JSONDecodeError if content cannot be parsed as JSON

        """
        expected_type = 'application/json'
        response = self.get(url, **kwargs)

        observed_type = response.headers.get('content-type')
        if observed_type != expected_type:
            print(response.content)
            raise ResponseContentTypeError(observed_type, expected_type)

        return response.json()

    def _join_items(self, items):
        return ','.join(list(items))

    def _list_composers(self, list_type='', items=[]):
        joined_items = self._join_items(items)
        target = _urljoin(self.api_url, self.section_urls['composer'], 'list', list_type, joined_items) + '.json'
        return self.get_json(target).get('composers', [])


    def _list_works(self, list_type='', items=[]):
        joined_items = self._join_items(items)
        target = _urljoin(self.api_url, self.section_urls['work'], 'list', list_type, joined_items) + '.json'
        return self.get_json(target).get('works', [])

    def list_popular_composers(self):
        items = 'pop'
        return self._list_composers(items=items)

    def list_essential_composers(self):
        items = 'rec'
        return self._list_composers(items=items)

    def list_composers_by_first_letter(self, letter):
        list_type = 'name'
        items = [letter]
        return self._list_composers(list_type=list_type, items=items)

    def list_composers_by_period(self, period):
        list_type = 'epoch'
        items = [period]
        return self._list_composers(list_type=list_type, items=items)

    def search_composers_by_name(self, name):
        list_type = 'search'
        items = [name]
        return self._list_composers(list_type=list_type, items=items)

    def list_composers_by_id(self, ids):
        list_type = 'ids'
        items = [ids] if type(ids)==str else ids
        return self._list_composers(list_type=list_type, items=items)
