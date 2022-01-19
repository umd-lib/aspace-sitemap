import json
import os
import sys
import xml.etree.ElementTree as et

import requests
from dotenv import load_dotenv
from flask import Flask, Response
from flask_compress import Compress
from asnake.aspace import ASpace
import asnake.logging as logging

# Generate and serve a sitemap.xml file for ArchivesSpace public interface
# using the the ArchivesSpace API and the ArchivesSnake Library

# Add any environment variables from .env
load_dotenv('../.env')

# Get environment variables
env = {}
for key in ('ASPACE_API_URL', 'ASPACE_API_USERNAME',
            'ASPACE_API_PASSWORD', 'ASPACE_PUBLIC_URL'):
    env[key] = os.environ.get(key)
    if env[key] is None:
        raise RuntimeError(f'Must provide environment variable: {key}')

debug = os.environ.get('FLASK_ENV') == 'development'


def generate_sitemap():
    """ Generate the sitemap. """

    # Setup the ArchivesSnake library
    config = {
        'baseurl': env['ASPACE_API_URL'],
        'username': env['ASPACE_API_USERNAME'],
        'password': env['ASPACE_API_PASSWORD'],
        'default_config': 'INFO_TO_STDERR',
    }

    logger = logging.get_logger("sitemap")
    if debug:
        logging.setup_logging(stream=sys.stderr, level="DEBUG")

    logger.debug(f'config={config}')

    logger.info("Begin generating sitemap.xml")

    aspace = ASpace(**config)

    # Authorize as the provided username
    aspace.authorize()

    # Start the xml output
    NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'

    urlset = et.Element(et.QName(NS, 'urlset'))
    urlset.tail = '\n'

    doc = et.ElementTree(urlset)

    # Add the homepage
    url = et.SubElement(urlset, et.QName(NS, 'url'))
    loc = et.SubElement(url, et.QName(NS, 'loc'))
    loc.text = f'{env["ASPACE_PUBLIC_URL"]}/'
    url.tail = '\n'

    # Iterate over published repositories
    for repo in aspace.repositories:
        if repo.publish:

            url = et.SubElement(urlset, et.QName(NS, 'url'))
            loc = et.SubElement(url, et.QName(NS, 'loc'))
            loc.text = f'{env["ASPACE_PUBLIC_URL"]}{repo.uri}'
            url.tail = '\n'

            logger.debug(f'{repo.uri} {repo.display_string}')

            # Iterate over published resources
            for resource in repo.resources:
                if resource.publish and not resource.suppressed:
                    url = et.SubElement(urlset, et.QName(NS, 'url'))
                    loc = et.SubElement(url, et.QName(NS, 'loc'))
                    loc.text = f'{env["ASPACE_PUBLIC_URL"]}{resource.uri}'
                    url.tail = '\n'

                    logger.debug(f'{resource.uri} {resource.title}')

            # Iterate over published digital objects
            for digital_object in repo.digital_objects:
                if digital_object.publish:
                    url = et.SubElement(urlset, et.QName(NS, 'url'))
                    loc = et.SubElement(url, et.QName(NS, 'loc'))
                    loc.text = \
                        f'{env["ASPACE_PUBLIC_URL"]}{digital_object.uri}'
                    url.tail = '\n'

                    logger.debug(f'{digital_object.uri}' +
                                 f'{digital_object.title}')

    logger.info("sitemap.xml generation complete")

    # Write the XML Sitemap to stdout
    return et.tostring(
            urlset,
            encoding='unicode',
            method='xml',
            xml_declaration=True,
            default_namespace=NS)


# Generate the sitemap once a startup
sitemap = generate_sitemap()

# Start the flask app, with compression enabled
app = Flask(__name__)
Compress(app)


@app.route('/')
def root():
    return {'status': 'ok'}


@app.route('/ping')
def ping():
    return {'status': 'ok'}


@app.route('/sitemap.xml')
def get_sitemap():
    return Response(sitemap, mimetype='text/xml')


if __name__ == '__main__':
    # This code is not reached when running "flask run". However the Docker
    # container runs "python app.py" and host='0.0.0.0' is set to ensure
    # that flask listents to port 5000 on all interfaces.
    app.run(host='0.0.0.0')
