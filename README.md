# OpenOpys
![Coverage](https://img.shields.io/badge/coverage-96%25-yellowgreen)
![Last Commit](https://img.shields.io/github/last-commit/wcarter609/OpenOpys)

A basic Python wrapper for the [OpenOpus API project](https://openopus.org/) (with which I am unaffiliated). For a detailed description of OpenOpus, definitely check
out their site using the previous link or [their github repo](https://github.com/openopus-org/openopus_api). In short, OpenOpus is an incredibly easy-to-access repository of classical music metadata including:
  * Composers
    - e.g. date of birth/death, name, period, and a handy portrait
  * Works
    - e.g. title, genre
  * Genres
  * Performers (from famous historical performances.recordings)

The main goal of this wrapper is simply to reduce necessary boilerplate code to query and process OpenOpus data in Python applications.

## Usage
Below is the recommended way to import the openopys module. This loads the `openopys.OpenOpys` class which handles API calls/responses as well as a
helper `openopys.Genre` class which is used to search by genre.
```python
from openopys import OpenOpys, Genre
```
From there, the first step is to create an `OpenOpys` session object which will be used for all future calls. OpenOpys by default uses the API provided
by the OpenOpus project, https://api.openopus.org/, but also supports specification of a special URL with the __api_url__ argument for users
who have forked and deployed their own instance of the api.

The `OpenOpys` class extends the [requests Session class](https://requests.readthedocs.io/en/master/api/#request-sessions), and can therefore accept any 
kwargs supported by the `Session` class.

```python
from openopys import OpenOpys, Genre

opys = OpenOpys() # Initialize an OpenOpys session using default url
opys_custom = OpenOpys(api_url="https://custom.url")

```

Using the OpenOpys object, one can perform a number of queries. E.g.:
```python
opys.list_popular_composers() # List popular compsoers according to openopus database
[{'id': '87',
  'name': 'Bach',
  'complete_name': 'Johann Sebastian Bach',
  'birth': '1685-01-01',
  'death': '1750-01-01',
  'epoch': 'Baroque',
  'portrait': 'https://assets.openopus.org/portraits/12091447-1568084857.jpg'},
 {'id': '145',
  'name': 'Beethoven',
  'complete_name': 'Ludwig van Beethoven',
  'birth': '1770-01-01',
  'death': '1827-01-01',
  'epoch': 'Early Romantic',
  'portrait': 'https://assets.openopus.org/portraits/55910756-1568084860.jpg'},
 {'id': '80',
  'name': 'Brahms',
  'complete_name': 'Johannes Brahms',
  'birth': '1833-01-01',
  'death': '1897-01-01',
  'epoch': 'Romantic',
  'portrait': 'https://assets.openopus.org/portraits/46443632-1568084867.jpg'},
 ...
 
opys.search_composers_by_name('Rameau') # Get a list of composers whose name matches search string
[{'id': '178',
  'name': 'Rameau',
  'complete_name': 'Jean-Philippe Rameau',
  'birth': '1683-01-01',
  'death': '1764-01-01',
  'epoch': 'Baroque',
  'portrait': 'https://assets.openopus.org/portraits/82780595-1568084937.jpg'}]
  
opys.search_works_by_composer_id_title_and_genre('10', '', Genre.STAGE) # Get a list of stage works by Lully (composer id = 10)
[{'title': 'Acis et Galatée, LWV73',
  'subtitle': '',
  'searchterms': '',
  'popular': '0',
  'recommended': '0',
  'id': '866',
  'genre': 'Stage'},
 {'title': 'Alceste, ou le triomphe d’Alcide, LWV50',
  'subtitle': '',
  'searchterms': '',
  'popular': '0',
  'recommended': '0',
  'id': '875',
  'genre': 'Stage'},
 {'title': 'Alcidiane, LWV9',
  'subtitle': 'Ballet',
  'searchterms': '',
  'popular': '0',
  'recommended': '0',
  'id': '887',
  'genre': 'Stage'},
 {'title': 'Amadis, LWV63',
  'subtitle': '',
  'searchterms': '',
  'popular': '0',
  'recommended': '0',
  'id': '902',
  'genre': 'Stage'},
  ...

```
