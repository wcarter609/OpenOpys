from enum import Enum, auto
from json.decoder import JSONDecodeError

from urllib.parse import quote
from requests import Session
from requests.models import ContentDecodingError


def _urljoin(*args):
    trailing_slash = '/' if args[-1].endswith('/') else ''
    return "/".join(map(lambda x: str(x).strip('/'), args)) + trailing_slash


class DataType(str, Enum):
    COMPOSERS = 'composers'
    WORKS = 'works'
    GENRES = 'genres'
    PERFORMERS = 'performers'


class Genre(str, Enum):
    ALL = 'all'
    POPULAR = 'Popular'
    ESSENTIAL = 'Recommended'
    CHAMBER = 'Chamber'
    KEYBOARD = 'Keyboard'
    ORCHESTRAL = 'Orchestral'
    STAGE = 'Stage'
    VOCAL = 'Vocal'


class ResponseContentTypeError(Exception):

    def __init__(self, observed, expected, *args, **kwargs):
        Exception.__init__(
            self, f"Response content is of type '{observed}'. Must be '{expected}'")


class OpenOpys(Session):

    data_base_urls = {
        DataType.COMPOSERS: 'composer',
        DataType.WORKS: 'work',
        DataType.GENRES: 'genre',
        DataType.PERFORMERS: 'performer'
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
        
        # use quote to handle converting any troublesome chars
        # don't need to be more specific since the OpenOpus API doesn't make use of params
        split_url = url.split('://')
        escaped_content = quote('://'.join(split_url[1:]))
        escaped_url = '://'.join([split_url[0], escaped_content])

        response = self.get(escaped_url, **kwargs) 

        observed_type = response.headers.get('content-type')
        if observed_type != expected_type:
            print(response.content)
            raise ResponseContentTypeError(observed_type, expected_type)

        return response.json()

    def _join_items(self, items):
        return ','.join(list(items))

    def _list_data(self, data_type, list_by='', items=[]):
        """
        """
        joined_items = self._join_items(items)
        target = _urljoin(
            self.api_url, self.data_base_urls[data_type], 'list', list_by, joined_items) + '.json'
        return self.get_json(target).get(data_type.value, [])

    def _list_composers(self, list_by='', items=[]):
        """
        """
        joined_items = self._join_items(items)
        target = _urljoin(
            self.api_url, self.data_base_urls[DataType.COMPOSERS], 'list', list_by, joined_items) + '.json'
        return self.get_json(target).get('composers', [])

    def _list_works(self, list_by='', items=[]):
        joined_items = self._join_items(items)
        target = _urljoin(
            self.api_url, self.data_base_urls[DataType.WORKS], 'list', list_by, joined_items) + '.json'
        return self.get_json(target).get('works', [])

    def _list_genres(self, list_by='', items=[]):
        joined_items = self._join_items(items)
        target = _urljoin(
            self.api_url, self.data_base_urls[DataType.GENRES], 'list', list_by, joined_items) + '.json'
        return self.get_json(target).get('genres', [])

    def list_popular_composers(self):
        items = ['pop']
        return self._list_composers(items=items)

    def list_essential_composers(self):
        items = ['rec']
        return self._list_composers(items=items)

    def list_composers_by_first_letter(self, letter):
        list_by = 'name'
        items = [letter]
        return self._list_composers(list_by=list_by, items=items)

    def list_composers_by_period(self, period):
        list_by = 'epoch'
        items = [period]
        return self._list_composers(list_by=list_by, items=items)

    def search_composers_by_name(self, name):
        list_by = 'search'
        items = [name]
        return self._list_data(DataType.COMPOSERS, list_by=list_by, items=items)
        # return self._list_composers(list_by=list_by, items=items)

    def list_composers_by_id(self, ids):
        list_by = 'ids'
        items = [ids] if type(ids) == str else ids
        return self._list_composers(list_by=list_by, items=items)

    def list_genres_by_composer_id(self, composer_id):
        list_by = 'composer'
        items = [composer_id]
        return self._list_genres(list_by=list_by, items=items)

    def list_works_by_composer_id_and_genre(self, composer_id, genre):
        list_by = _urljoin('composer', composer_id, 'genre')
        items = [genre]
        return self._list_works(list_by=list_by, items=items)

    def list_works_by_composer_id(self, composer_id):
        return self.list_works_by_composer_id_and_genre(composer_id, Genre.ALL)

    def list_popular_works_by_composer_id(self, composer_id):
        return self.list_works_by_composer_id_and_genre(composer_id, Genre.POPULAR)

    def list_essential_works_by_composer_id(self, composer_id):
        return self.list_works_by_composer_id_and_genre(composer_id, Genre.ESSENTIAL)

    def search_works_by_composer_id_title_and_genre(self, composer_id, title, genre):
        if type(genre) == Genre:
            genre = genre.value

        list_by = _urljoin('composer', composer_id, 'genre', genre, 'search')
        items = [title]
        return self._list_works(list_by=list_by, items=items)

    def search_works_by_composer_id_and_title(self, composer_id, title):
        return self.search_works_by_composer_id_title_and_genre(composer_id, title, Genre.ALL)
