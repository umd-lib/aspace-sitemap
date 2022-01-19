# aspace-sitemap

Python 3 Flask application to generate and serve a sitemap.xml file for ArchivesSpace public interface using the the ArchivesSpace API and the ArchivesSnake Library.

## Requires

* Python 3

## Installation

```bash
# clone this repository
git clone git@github.com:umd-lib/aspace-sitemap.git

# install requirements
cd aspace-sitemap
pip install -r requirements.txt
```

## Running the Webapp

```bash
# create a .env file (then manually update environment variables)
cp .env-template .env

# run the app with Flask
flask run
```

This will start the webapp listening on the default port 5000 on localhost
(127.0.0.1), and running in [Flask's debug mode].

Root endpoint (just returns `{status: ok}` to all requests):
<http://localhost:5000/>

/ping endpoint (just returns `{status: ok}` to all requests):
<http://localhost:5000/ping>

/sitemap.py endpoint: <http://localhost:5000/sitemap.py>

[Flask's debug mode]: https://flask.palletsprojects.com/en/2.0.x/quickstart/#debug-mode

## License

See the [LICENSE](LICENSE.txt) file for license rights and limitations.
