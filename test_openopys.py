import pytest
from delayed_assert import expect, assert_expectations

from src.openopys import OpenOpys, _urljoin

default_api_url = 'https://api.openopus.org'
custom_api_url = 'https://api.openopus.org'


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


