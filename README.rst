Expectly - An HTTP API centric BDD style test framework
-------------------------------------------------------

|travis| |pypi| |docs|

Use Cases:

    - Making assertions about api responses more readable
    - Extending expectly with new assertions to reduce boilerplate


    .. DANGER::

       This library is in alpha. I will try my utmost to not make backwards incompatible changes
       but it is possible that

Installing
==========

   .. code-block:: shell

      $ pip install expectly

API Examples
============

Built In Assertion methods
**************************

    .. code-block:: python

        # status_code (with status code number)
        expect(response).to.have.status_code(200)

        # header (asserts the header exists). Sets the header value to be further tested against
        expect(response).to.have.header('Content-Type')

        # equals
        expect(response).to.have.header('Content-Type').equal('application/json')

        # like (does a regex match against the value)
        expect(response).to.have.header('Content-Type').like('application')

        # exactly_like (does a regex match against the whole value
        expect(response).to.have.header('Content-Type').exactly_like('^application/[\w]*$')

        # encoding
        expect(response).to.have.encoding('utf-8')

        # ok (uses requests.response.ok attribute)
        expect(response).to.be.ok


Extending expectly.expect with additional assertions
****************************************************

TODO

JSON handling in expectly
*************************


jsonschema is used for evaluating whether json responses match the relevant schema
jmespath is used for navigating/selecting information to test inside of the json response


Development
===========

   .. code-block:: shell

      $ git clone https://github.com/huntcsg/expectly.git
      $ cd expectly
      $ ./utils/manage clean
      $ ./utils/manage test
      $ ./utils/manage docs


1. All pull requests must pass the travis-ci builds
2. All pull requests should include inline (docstring) documentation, updates to built documentation if applicable,
   and test coverage. This project aspires to be a 100% test coverage library.


.. |travis| image:: https://travis-ci.org/huntcsg/expectly.svg?branch=master
   :target: https://travis-ci.org/huntcsg/expectly
.. |pypi| image:: https://img.shields.io/pypi/v/expectly.svg
   :target: https://pypi.python.org/pypi/expectly
.. |docs| image:: https://readthedocs.org/projects/expectly/badge/?version=latest
   :target: http://expectly.readthedocs.io/en/latest/?badge=latest