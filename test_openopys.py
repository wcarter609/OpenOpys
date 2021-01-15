import re

import pytest
from delayed_assert import expect, assert_expectations

from src.openopys import OpenOpys, Genre, _urljoin

# API URLs
default_api_url = 'https://api.openopus.org'
custom_api_url = 'https://api.openopus.org'

# Response Schemas
composer_list_schema = {
    'id': [str],
    'name': [str],
    'complete_name': [str],
    'birth': [str],
    'death': [str, type(None)],
    'epoch': [str],
    'portrait': [str],
}

work_list_schema = {
    'title': [str],
    'subtitle': [str],
    'searchterms': [str],
    'popular': [str],
    'recommended': [str],
    'id': [str],
    'genre': [str]
}

genre_list_schema = str


def _validate_result_with_schema(result, response_schema):
    for item in result:
        if type(response_schema) == dict:
            for key, expected_types in response_schema.items():
                expect(
                    key in item and type(item.get(key)) in expected_types,
                    f"expected_type={expected_types}, observed_type={type(item.get(key))}"
                )
        else:
            expect(
                type(item) == response_schema,
                f"expected_type={response_schema}, observed_type={type(item)}"
            )


def default_openopys():
    return OpenOpys()


def custom_url_openopys():
    return OpenOpys(api_url=custom_api_url)


@pytest.mark.parametrize('openopys_constructor, setting, expected_attr_dict', [
    (default_openopys, 'defualt', {'api_url': default_api_url}),
    (custom_url_openopys, 'custom', {'api_url': custom_api_url})
])
def test_create_openopys(openopys_constructor, setting, expected_attr_dict):
    openopys = openopys_constructor()
    expect(isinstance(openopys, OpenOpys),
           f"Could not construct a {setting} OpenOpys obj. Object is type {type(openopys)}")
    for attr, val in expected_attr_dict.items():
        observed_val = getattr(openopys, attr, 'DNE')
        if val is None:
            expectation = observed_val is val
        else:
            expectation = observed_val == val

        expect(
            expectation, f"{setting} OpenOpys obj | attr='{attr}', expected={val}, observed={observed_val}")

    assert_expectations()


@pytest.mark.parametrize('path_snippets, expected', [
    (
        [
            'http://website.net'
        ],
        'http://website.net'
    ),
    (
        [
            'http://website.net/'
        ],
        'http://website.net/'
    ),
    (
        [
            'http://website.net',
            'app'
        ],
        'http://website.net/app'
    ),
    (
        [
            'http://website.net/',
            'app'
        ],
        'http://website.net/app'
    ),
    (
        [
            'http://website.net',
            '/app'
        ],
        'http://website.net/app'
    ),
    (
        [
            'http://website.net/',
            '/app'
        ],
        'http://website.net/app'
    ),
    (
        [
            'http://website.net',
            'app/'
        ],
        'http://website.net/app/'
    ),
    (
        [
            'http://website.net',
            'app',
            'sub'
        ],
        'http://website.net/app/sub'
    ),
])
def test_url_join(path_snippets, expected):
    joined = _urljoin(*path_snippets)
    assert joined == expected, f"Expected='{expected}', Observed='{joined}'"


@pytest.mark.parametrize('openopys_constructor, setting, response_schema', [
    (default_openopys, 'defualt', composer_list_schema),
    (custom_url_openopys, 'custom', composer_list_schema)
])
def test_list_popular_composers(openopys_constructor, setting, response_schema):
    openopys = openopys_constructor()
    result = openopys.list_popular_composers()
    _validate_result_with_schema(result, response_schema)
    assert_expectations()


@pytest.mark.parametrize('openopys_constructor, setting, response_schema', [
    (default_openopys, 'defualt', composer_list_schema),
    (custom_url_openopys, 'custom', composer_list_schema)
])
def test_list_essential_composers(openopys_constructor, setting, response_schema):
    openopys = openopys_constructor()
    result = openopys.list_essential_composers()
    _validate_result_with_schema(result, response_schema)
    assert_expectations()


@pytest.mark.parametrize('openopys_constructor, letter, response_schema', [
    (default_openopys, 'a', composer_list_schema),
    (custom_url_openopys, 'a', composer_list_schema),
    (default_openopys, 'R', composer_list_schema),
    (default_openopys, 'b', composer_list_schema),
    (default_openopys, 'X', composer_list_schema),
    (default_openopys, '!', composer_list_schema),
])
def test_list_composers_by_first_letter(openopys_constructor, letter, response_schema):
    openopys = openopys_constructor()
    result = openopys.list_composers_by_first_letter(letter)
    _validate_result_with_schema(result, response_schema)

    # Also check that every result starts with expected letter
    for item in result:
        expect(
            item['name'][0] in [letter.upper(), letter.lower()],
            f"Name='{item['name']}' | StartsWith='{item['name'][0]}', Expected='{letter}'"
        )

    assert_expectations()


@pytest.mark.parametrize('openopys_constructor, period, response_schema', [
    (default_openopys, 'Baroque', composer_list_schema),
    (custom_url_openopys, 'Baroque', composer_list_schema),
    (default_openopys, 'Medieval', composer_list_schema),
    (default_openopys, 'Renaissance', composer_list_schema),
    (default_openopys, 'Classical', composer_list_schema),
    (default_openopys, 'Romantic', composer_list_schema),
    (default_openopys, 'Punk', composer_list_schema)
])
def test_list_composers_by_period(openopys_constructor, period, response_schema):
    openopys = openopys_constructor()
    result = openopys.list_composers_by_period(period)
    _validate_result_with_schema(result, response_schema)

    # Also check that every composer belongs to the specified period
    for item in result:
        expect(
            item['epoch'] == period,
            f"Name='{item['name']}' | Observed Epoch='{item['epoch']}', Expected Epoch='{period}'"
        )

    assert_expectations()


@pytest.mark.parametrize('openopys_constructor, search_str, response_schema', [
    (default_openopys, 'Rameau', composer_list_schema),
    (custom_url_openopys, 'Rameau', composer_list_schema),
    (default_openopys, 'rameau', composer_list_schema),
    (default_openopys, 'ach', composer_list_schema),
    (default_openopys, '', composer_list_schema),
    # (default_openopys, '#!@#$', composer_list_schema),
])
def test_search_composers_by_name(openopys_constructor, search_str, response_schema):
    openopys = openopys_constructor()
    result = openopys.search_composers_by_name(search_str)
    _validate_result_with_schema(result, response_schema)
    # Also check that every result contains the search string
    for item in result:
        expect(
            re.search(search_str, item['name'], re.IGNORECASE) is not None,
            f"Name='{item['name']}' | Could not find search_str='{search_str}'"
        )

    assert_expectations()


@pytest.mark.parametrize('openopys_constructor, ids, response_schema', [
    (default_openopys, ['178'], composer_list_schema),
    (custom_url_openopys, ['178'], composer_list_schema),
    (default_openopys, ['10'], composer_list_schema),
    (default_openopys, ['178', '10'], composer_list_schema),
    (default_openopys, ['178', '10', '204'], composer_list_schema),
    (default_openopys, ['-1'], composer_list_schema),
    (default_openopys, ['178', '10', '204', '-1'], composer_list_schema),
])
def test_list_composers_by_id(openopys_constructor, ids, response_schema):
    openopys = openopys_constructor()
    result = openopys.list_composers_by_id(ids)
    _validate_result_with_schema(result, response_schema)
    # Also check that every result is a composer in provided ids
    for item in result:
        expect(
            item['id'] in ids,
            f"Composer '{item['name']}' has id='{item['id']}' not in provided ids {ids}"
        )

    assert_expectations()


@pytest.mark.parametrize('openopys_constructor, composer_id, response_schema', [
    (default_openopys, '178', genre_list_schema),
    (custom_url_openopys, '178', genre_list_schema),
    (default_openopys, '10', genre_list_schema),
    (default_openopys, '204', genre_list_schema),
    (default_openopys, '-1', genre_list_schema),
])
def test_list_genres_by_composer_id(openopys_constructor, composer_id, response_schema):
    openopys = openopys_constructor()
    result = openopys.list_genres_by_composer_id(composer_id)
    _validate_result_with_schema(result, response_schema)
    assert_expectations()

@pytest.mark.parametrize('openopys_constructor, composer_id, genre, response_schema', [
    (default_openopys, '178', 'Stage', work_list_schema),
    (custom_url_openopys, '178', 'Stage', work_list_schema),
    (default_openopys, '178', Genre.STAGE, work_list_schema),
    (default_openopys, '204', Genre.POPULAR, work_list_schema),
    (default_openopys, '-1', Genre.STAGE, work_list_schema),
])    
def test_list_works_by_composer_id_and_genre(openopys_constructor, composer_id, genre, response_schema):
    openopys = openopys_constructor()
    result = openopys.list_works_by_composer_id_and_genre(composer_id, genre)
    _validate_result_with_schema(result, response_schema)
    # Also check that every result belongs to specified genre
    for item in result:
        expect(
            item['genre'] == genre,
            f"'{item['title']}' has genre='{item['genre']}' not expected_genre={genre}"
        )
    assert_expectations()

@pytest.mark.parametrize('openopys_constructor, composer_id, response_schema', [
    (default_openopys, '178', work_list_schema),
    (custom_url_openopys, '178', work_list_schema),
    (default_openopys, '10', work_list_schema),
    (default_openopys, '204', work_list_schema),
    (default_openopys, '-1', work_list_schema),
])
def test_list_works_by_composer_id(openopys_constructor, composer_id, response_schema):
    openopys = openopys_constructor()
    result = openopys.list_works_by_composer_id(composer_id)
    _validate_result_with_schema(result, response_schema)
    assert_expectations()