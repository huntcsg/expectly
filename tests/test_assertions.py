import requests_mock
from expectly import expect
import requests


class TestStandardResponse:

    def get_response(self):
        with requests_mock.mock() as m:
            m.get(
                'http://example.com',
                headers={'Content-Type': 'application/json'},
                text='{"foo":"bar", "baz": [{"1": "one", "2": 2}]}',
                status_code=200,
            )
            response = requests.get('http://example.com')
        return response

    def test_pass(self):
        resp = self.get_response()
        expect(resp).to.have.status_code(200)
        expect(resp).json.to.be.valid
        expect(resp).json.path('baz[0]."1"').to.be.equal('one')

    def test_schema(self):
        resp = self.get_response()
        expect(resp).to.be.ok
        expect(resp).to.have.encoding('utf-8')
        expect(resp).json.to.have.the.schema({
            'type': 'object',
            'required': ['foo', 'baz'],
            'properties': {
                'foo': {'type': 'string'},
                'baz': {
                    'type': 'array',
                    'items': [
                        {
                            'type': 'object',
                            'required': ['1', '2'],
                            'properties': {
                                '1': {'type': 'string'},
                                '2': {'type': 'number'},
                            }
                        }
                    ]
                }
            }
        })


class TestErrorResponse:

    def get_response(self):
        with requests_mock.mock() as m:
            m.get(
                'http://example.com',
                headers={'Content-Type': 'application/json'},
                text='{"status":"ERROR"}',
                status_code=404,
            )
            response = requests.get('http://example.com')
        return response

    def test_pass(self):
        resp = self.get_response()
        expect(resp).to.not_.be.ok
        expect(resp).json.path('status').to.not_.be.like('SUCCESS')
        expect(resp).json.path('status').to.be.equal('ERROR')
        expect(resp).to.have.header('Content-Type').like('json')
        expect(resp).to.not_.have.headers(['Content-Encoding', 'Date'])