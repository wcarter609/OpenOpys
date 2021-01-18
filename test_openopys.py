import re

import pytest
from delayed_assert import expect, assert_expectations

from src.openopys import OpenOpys, Genre, _urljoin


"""
Some testcases have been temporarily disabled/changed to match current (Rather than desired) behavior.
These are namely around 
    (1) searching composers by name which seems to work something like 'startswith',
    (2) searching works by title which returns unexpected hits
"""

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


def _result_size_in_range(size, min=None, max=None):
    if min is None and max is None:
        return True

    elif min is None and max is not None:
        return size <= max

    elif min is not None and max is None:
        return size >= min

    elif min is not None and max is not None:
        return size >= min and size <= max

    else:
        return False


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


@pytest.mark.parametrize('openopys_constructor, setting, response_schema, min_num_results, max_num_results', [
    (default_openopys, 'defualt', composer_list_schema, 1, None),
    (custom_url_openopys, 'custom', composer_list_schema, 1, None)
])
def test_list_popular_composers(openopys_constructor, setting, response_schema, min_num_results, max_num_results):
    openopys = openopys_constructor()
    result = openopys.list_popular_composers()
    expect(
        _result_size_in_range(len(result), min_num_results, max_num_results),
        f"Did not return expected number of results (min={min_num_results}, max={max_num_results})."
        + f"Got {len(result)} results.")

    _validate_result_with_schema(result, response_schema)

    assert_expectations()


@pytest.mark.parametrize('openopys_constructor, setting, response_schema, min_num_results, max_num_results', [
    (default_openopys, 'defualt', composer_list_schema, 1, None),
    (custom_url_openopys, 'custom', composer_list_schema, 1, None)
])
def test_list_essential_composers(openopys_constructor, setting, response_schema, min_num_results, max_num_results):
    openopys = openopys_constructor()
    result = openopys.list_essential_composers()
    expect(
        _result_size_in_range(len(result), min_num_results, max_num_results),
        f"Did not return expected number of results (min={min_num_results}, max={max_num_results})."
        + f"Got {len(result)} results.")

    _validate_result_with_schema(result, response_schema)
    assert_expectations()


@pytest.mark.parametrize('openopys_constructor, letter, response_schema, min_num_results, max_num_results', [
    (default_openopys, 'a', composer_list_schema, 1, None),
    (custom_url_openopys, 'a', composer_list_schema, 1, None),
    (default_openopys, 'R', composer_list_schema, 1, None),
    (default_openopys, 'b', composer_list_schema, 1, None),
    (default_openopys, 'X', composer_list_schema, 1, None),
    (default_openopys, '!', composer_list_schema, 0, 0),
])
def test_list_composers_by_first_letter(openopys_constructor, letter, response_schema, min_num_results, max_num_results):
    openopys = openopys_constructor()
    result = openopys.list_composers_by_first_letter(letter)
    expect(
        _result_size_in_range(len(result), min_num_results, max_num_results),
        f"Did not return expected number of results (min={min_num_results}, max={max_num_results})."
        + f"Got {len(result)} results.")

    _validate_result_with_schema(result, response_schema)

    # Also check that every result starts with expected letter
    for item in result:
        expect(
            item['name'][0] in [letter.upper(), letter.lower()],
            f"Name='{item['name']}' | StartsWith='{item['name'][0]}', Expected='{letter}'"
        )

    assert_expectations()


@pytest.mark.parametrize('openopys_constructor, period, response_schema, min_num_results, max_num_results', [
    (default_openopys, 'Baroque', composer_list_schema, 1, None),
    (custom_url_openopys, 'Baroque', composer_list_schema, 1, None),
    (default_openopys, 'Medieval', composer_list_schema, 1, None),
    (default_openopys, 'Renaissance', composer_list_schema, 1, None),
    (default_openopys, 'Classical', composer_list_schema, 1, None),
    (default_openopys, 'Romantic', composer_list_schema, 1, None),
    (default_openopys, 'Punk', composer_list_schema, 0, 0)
])
def test_list_composers_by_period(openopys_constructor, period, response_schema, min_num_results, max_num_results):
    openopys = openopys_constructor()
    result = openopys.list_composers_by_period(period)

    expect(
        _result_size_in_range(len(result), min_num_results, max_num_results),
        f"Did not return expected number of results (min={min_num_results}, max={max_num_results})."
        + f"Got {len(result)} results.")

    _validate_result_with_schema(result, response_schema)

    # Also check that every composer belongs to the specified period
    for item in result:
        expect(
            item['epoch'] == period,
            f"Name='{item['name']}' | Observed Epoch='{item['epoch']}', Expected Epoch='{period}'"
        )

    assert_expectations()


@pytest.mark.parametrize('openopys_constructor, search_str, response_schema, min_num_results, max_num_results', [
    (default_openopys, 'Rameau', composer_list_schema, 1, 1),
    (custom_url_openopys, 'Rameau', composer_list_schema, 1, 1),
    (default_openopys, 'rameau', composer_list_schema, 1, 1),
    # (default_openopys, 'ach', composer_list_schema, 1, None), # Disable until openopus allows searching with patterns
    (default_openopys, '', composer_list_schema, 1, None),
    (default_openopys, 'dasdasdvasv', composer_list_schema, 0, 0),
])
def test_search_composers_by_name(openopys_constructor, search_str, response_schema, min_num_results, max_num_results):
    openopys = openopys_constructor()
    result = openopys.search_composers_by_name(search_str)

    expect(
        _result_size_in_range(len(result), min_num_results, max_num_results),
        f"Did not return expected number of results (min={min_num_results}, max={max_num_results})."
        + f"Got {len(result)} results.")

    _validate_result_with_schema(result, response_schema)
    # Also check that every result contains the search string
    for item in result:
        expect(
            re.search(search_str, item['name'], re.IGNORECASE) is not None,
            f"Name='{item['name']}' | Could not find search_str='{search_str}'"
        )

    assert_expectations()


@pytest.mark.parametrize('openopys_constructor, ids, response_schema, min_num_results, max_num_results', [
    (default_openopys, ['178'], composer_list_schema, 1, 1),
    (custom_url_openopys, ['178'], composer_list_schema, 1, 1),
    (default_openopys, ['10'], composer_list_schema, 1, 1),
    (default_openopys, ['178', '10'], composer_list_schema, 2, 2),
    (default_openopys, ['178', '10', '204'], composer_list_schema, 3, 3),
    (default_openopys, ['-1'], composer_list_schema, 0, 0),
    (default_openopys, ['178', '10', '204', '-1'], composer_list_schema, 3, 3),
])
def test_list_composers_by_id(openopys_constructor, ids, response_schema, min_num_results, max_num_results):
    openopys = openopys_constructor()
    result = openopys.list_composers_by_id(ids)

    expect(
        _result_size_in_range(len(result), min_num_results, max_num_results),
        f"Did not return expected number of results (min={min_num_results}, max={max_num_results})."
        + f"Got {len(result)} results.")

    _validate_result_with_schema(result, response_schema)
    # Also check that every result is a composer in provided ids
    for item in result:
        expect(
            item['id'] in ids,
            f"Composer '{item['name']}' has id='{item['id']}' not in provided ids {ids}"
        )

    assert_expectations()


@pytest.mark.parametrize('openopys_constructor, composer_id, response_schema, min_num_results, max_num_results', [
    (default_openopys, '178', genre_list_schema, 1, None),
    (custom_url_openopys, '178', genre_list_schema, 1, None),
    (default_openopys, '10', genre_list_schema, 1, None),
    (default_openopys, '204', genre_list_schema, 1, None),
    (default_openopys, '-1', genre_list_schema, 0, 0),
])
def test_list_genres_by_composer_id(openopys_constructor, composer_id, response_schema, min_num_results, max_num_results):
    openopys = openopys_constructor()
    result = openopys.list_genres_by_composer_id(composer_id)

    expect(
        _result_size_in_range(len(result), min_num_results, max_num_results),
        f"Did not return expected number of results (min={min_num_results}, max={max_num_results})."
        + f"Got {len(result)} results.")

    _validate_result_with_schema(result, response_schema)
    assert_expectations()


@pytest.mark.parametrize('openopys_constructor, composer_id, genre, response_schema, min_num_results, max_num_results', [
    (default_openopys, '178', 'Stage', work_list_schema, 1, None),
    (custom_url_openopys, '178', 'Stage', work_list_schema, 1, None),
    (default_openopys, '178', Genre.STAGE, work_list_schema, 1, None),
    (default_openopys, '204', Genre.POPULAR, work_list_schema, None, None),
    (default_openopys, '-1', Genre.STAGE, work_list_schema, 0, 0),
])
def test_list_works_by_composer_id_and_genre(openopys_constructor, composer_id, genre, response_schema, min_num_results, max_num_results):
    openopys = openopys_constructor()
    result = openopys.list_works_by_composer_id_and_genre(composer_id, genre)

    expect(
        _result_size_in_range(len(result), min_num_results, max_num_results),
        f"Did not return expected number of results (min={min_num_results}, max={max_num_results})."
        + f"Got {len(result)} results.")

    _validate_result_with_schema(result, response_schema)

    # Also check that every result belongs to specified genre
    for item in result:
        expect(
            item['genre'] == genre,
            f"'{item['title']}' has genre='{item['genre']}' not expected_genre={genre}"
        )
    assert_expectations()


@pytest.mark.parametrize('openopys_constructor, composer_id, response_schema, min_num_results, max_num_results', [
    (default_openopys, '178', work_list_schema, 1, None),
    (custom_url_openopys, '178', work_list_schema, 1, None),
    (default_openopys, '10', work_list_schema, 1, None),
    (default_openopys, '204', work_list_schema, 1, None),
    (default_openopys, '-1', work_list_schema, 0, 0),
])
def test_list_works_by_composer_id(openopys_constructor, composer_id, response_schema, min_num_results, max_num_results):
    openopys = openopys_constructor()
    result = openopys.list_works_by_composer_id(composer_id)

    expect(
        _result_size_in_range(len(result), min_num_results, max_num_results),
        f"Did not return expected number of results (min={min_num_results}, max={max_num_results})."
        + f"Got {len(result)} results.")

    _validate_result_with_schema(result, response_schema)
    assert_expectations()


@pytest.mark.parametrize('openopys_constructor, composer_id, response_schema, min_num_results, max_num_results', [
    (default_openopys, '178', work_list_schema, None, None),
    (custom_url_openopys, '178', work_list_schema, None, None),
    (default_openopys, '10', work_list_schema, None, None),
    (default_openopys, '204', work_list_schema, None, None),
    (default_openopys, '-1', work_list_schema, 0, 0),
])
def test_list_popular_works_by_composer_id(openopys_constructor, composer_id, response_schema, min_num_results, max_num_results):
    openopys = openopys_constructor()
    result = openopys.list_popular_works_by_composer_id(composer_id)

    expect(
        _result_size_in_range(len(result), min_num_results, max_num_results),
        f"Did not return expected number of results (min={min_num_results}, max={max_num_results})."
        + f"Got {len(result)} results.")

    _validate_result_with_schema(result, response_schema)
    # Also check that every result is popular
    for item in result:
        expect(
            item['genre'] == Genre.POPULAR,
            f"'{item['title']}' has genre='{item['genre']}' not expected_genre={Genre.POPULAR}"
        )
    assert_expectations()


@pytest.mark.parametrize('openopys_constructor, composer_id, response_schema, min_num_results, max_num_results', [
    (default_openopys, '178', work_list_schema, None, None),
    (custom_url_openopys, '178', work_list_schema, None, None),
    (default_openopys, '10', work_list_schema, None, None),
    (default_openopys, '204', work_list_schema, None, None),
    (default_openopys, '-1', work_list_schema, 0, 0),
])
def test_list_essential_works_by_composer_id(openopys_constructor, composer_id, response_schema, min_num_results, max_num_results):
    openopys = openopys_constructor()
    result = openopys.list_popular_works_by_composer_id(composer_id)

    expect(
        _result_size_in_range(len(result), min_num_results, max_num_results),
        f"Did not return expected number of results (min={min_num_results}, max={max_num_results})."
        + f"Got {len(result)} results.")

    _validate_result_with_schema(result, response_schema)
    # Also check that every result is popular
    for item in result:
        expect(
            item['genre'] == Genre.ESSENTIAL,
            f"'{item['title']}' has genre='{item['genre']}' not expected_genre={Genre.POPULAR}"
        )
    assert_expectations()


@pytest.mark.parametrize('openopys_constructor, composer_id, title_search, genre, response_schema, min_num_results, max_num_results', [
    (default_openopys, '178', 'Dard', Genre.STAGE, work_list_schema, 1, 1),
    # (custom_url_openopys, '178', 'Hip', Genre.STAGE, work_list_schema, 1, 1), # Disable until search issues resolved by openopus api
    (default_openopys, '10', 'De', Genre.VOCAL, work_list_schema, 1, None),
    (default_openopys, '204', 'Viol', Genre.CHAMBER, work_list_schema, 1, None),
    (default_openopys, '-1', '', Genre.POPULAR, work_list_schema, 0, 0),
])
def test_search_works_by_composer_id_title_and_genre(openopys_constructor, composer_id, title_search, genre, response_schema, min_num_results, max_num_results):
    openopys = openopys_constructor()
    result = openopys.search_works_by_composer_id_title_and_genre(
        composer_id, title_search, genre)

    expect(
        _result_size_in_range(len(result), min_num_results, max_num_results),
        f"Did not return expected number of results (min={min_num_results}, max={max_num_results})."
        + f"Got {len(result)} results.")

    _validate_result_with_schema(result, response_schema)
    # Also check that every result is popular
    for item in result:
        expect(
            item['genre'] == genre.value,
            f"'{item['title']}' has genre='{item['genre']}' not expected_genre={genre.value}"
        )
    assert_expectations()


@pytest.mark.parametrize('openopys_constructor, composer_id, title_search, response_schema, min_num_results, max_num_results', [
    # (default_openopys, '178', 'Dard', work_list_schema, 1, 1), # Disable until search issues resolved by openopus api
    # (custom_url_openopys, '178', 'Hip', work_list_schema, 1, 1), # Disable until search issues resolved by openopus api
    (custom_url_openopys, '178', 'Hip', work_list_schema, 1, 1),
    (default_openopys, '10', 'De', work_list_schema, 1, None),
    (default_openopys, '204', 'Viol', work_list_schema, 1, None),
    (default_openopys, '-1', '', work_list_schema, 0, 0),
])
def test_search_works_by_composer_id_and_title(openopys_constructor, composer_id, title_search, response_schema, min_num_results, max_num_results):
    openopys = openopys_constructor()
    result = openopys.search_works_by_composer_id_and_title(
        composer_id, title_search)

    expect(
        _result_size_in_range(len(result), min_num_results, max_num_results),
        f"Did not return expected number of results (min={min_num_results}, max={max_num_results})."
        + f"Got {len(result)} results.")

    _validate_result_with_schema(result, response_schema)
    
    assert_expectations()