from expectly import expect
import expectly
import requests_mock
import requests
import pytest
from unittest import mock

class TestMethodChaining:

    def assert_chained(self):
        assert self.obj is self.compared_obj

    def setup_method(self, test_method):
        with requests_mock.mock() as m:
            m.get('http://example.com', headers={'foo': 'bar'}, json={'bar': 'baz'})
            self.obj = expect(requests.get('http://example.com'))
        self.compared_obj = 'Not the same as obj'

    @pytest.mark.parametrize("passthrough_method", [
        'to',
        'have',
        'be',
        'that',
        'and_',
        'the',
    ])
    def test_passthrough_method(self, passthrough_method):
        self.compared_obj = getattr(self.obj, passthrough_method)
        self.assert_chained()

    @pytest.mark.parametrize('mutative_method', [
        'not_',
        'value',
    ])
    def test_mutative_method(self, mutative_method):
        self.compared_obj = getattr(self.obj, mutative_method)
        self.assert_chained()

    def test_json_method(self):
        self.compared_obj = self.obj.json
        self.assert_chained()

    def test_header_method(self):
        self.compared_obj = self.obj.header('foo')
        self.assert_chained()

class Test_Test:

    def setup_method(self, method):
        with requests_mock.mock() as m:
            m.get('http://example.com', headers={'foo': 'bar'}, json={'bar': 'baz'})
            self.obj = expect(requests.get('http://example.com'))

    @mock.patch('expectly.expect.test')
    def test_calls_test(self, mocked_test):
        self.obj._test()
        assert mocked_test.called

    def test_test_called_set(self):
        assert not self.obj.test_called
        self.obj._test()
        assert self.obj.test_called


class TestNot:

    def setup_method(self, method):
        with requests_mock.mock() as m:
            m.get('http://example.com', headers={'foo': 'bar'}, json={'bar': 'baz'})
            self.obj = expect(requests.get('http://example.com'))

    def test_test_updated(self):
        old_test = self.obj.test
        self.obj.not_
        assert self.obj.test is not old_test

    def test_test_negated_false(self):
        self.obj.not_.test(value=False)

    def test_test_negated_true(self):
        try:
            self.obj.not_.test(value=True)
        except AssertionError:
            return
        raise AssertionError('True did not raise an assertion error')

class TestGet:

    def setup_method(self, method):
        with requests_mock.mock() as m:
            m.get('http://example.com', headers={'foo': 'bar'}, json={'bar': 'baz'})
            self.obj = expect(requests.get('http://example.com'))

    def test_value(self):
        assert self.obj.get() == self.obj.response_under_test



class TestJSON:

    def setup_method(self, method):
        self.json = {'foo': 'bar'}
        with requests_mock.mock() as m:
            m.get('http://example.com', headers={'foo': 'bar'}, json=self.json)
            self.obj = expect(requests.get('http://example.com'))

    @mock.patch('expectly.expect.get')
    def test_json_sets_get(self, get):
        self.obj.json
        assert get is not self.obj.get

    def test_json_get_value(self):
        self.obj.json
        assert self.obj.get() == self.json


class TestValue:

    def setup_method(self, method):
        with requests_mock.mock() as m:
            m.get('http://example.com', headers={'foo': 'bar'}, json={'foo': 'bar'})
            self.obj = expect(requests.get('http://example.com'))

    @mock.patch('expectly.expect.get')
    def test_value_calls_get(self, get):
        self.obj.value
        assert get.called

    @mock.patch('expectly.expect.get')
    def test_value_sets_vut(self, get):
        self.obj.value
        assert self.obj.value_under_test == get.return_value


class TestHeader:

    def setup_method(self, method):
        self.headers = {'foo': 'bar', 'baz': 'foobar', 'Content-Type': 'application/json'}
        with requests_mock.mock() as m:
            m.get('http://example.com', headers=self.headers, json={'foo': 'bar'})
            self.obj = expect(requests.get('http://example.com'))

    def test_sets_vut(self):
        assert isinstance(self.obj.value_under_test, expectly._expect.NotSet)
        self.obj.header('foo')
        assert self.obj.value_under_test == self.headers['foo']

    def test_do_call_after_header(self):
        self.obj.header('foo').equal('bar')
        self.obj('is a success', lambda expect: expect.response_under_test.ok)


class TestHeaders:

    def setup_method(self, method):
        self.headers = {'foo': 'bar', 'baz': 'foobar'}
        with requests_mock.mock() as m:
            m.get('http://example.com', headers=self.headers, json={'foo': 'bar'})
            self.obj = expect(requests.get('http://example.com'))

    def test_sets_vut(self):
        assert isinstance(self.obj.value_under_test, expectly._expect.NotSet)
        self.obj.headers(['foo', 'baz'])
        self.obj.value_under_test == self.headers

    def test_fails_for_missing_headers(self):
        assert isinstance(self.obj.value_under_test, expectly._expect.NotSet)
        try:
            self.obj.headers(['foo', 'bar'])
        except AssertionError as e:
            pass


class TestAddJoinWord:

    def teardown_method(self, method):
        del expect.foo

    def test_add_foo_no_predicate_str(self):
        expect.add_join_word('foo')
        obj = expect('bar')
        assert not obj.predicate
        assert obj.foo is obj
        assert obj.predicate == ['foo']

    def test_add_foo_with_predicate_str(self):
        expect.add_join_word('foo', 'bar')
        obj = expect('baz')
        assert not obj.predicate
        assert obj.foo is obj
        assert obj.predicate == ['bar']


class TestAddAssertion:

    def get_assertion(self):
        def assert_bar(self):
            assert self.response_under_test == 'bar'
            return self

        return assert_bar

    def test_add_bar_property(self):
        expect.add_assertion('bar', self.get_assertion(), is_property=True)
        obj = expect('bar').bar
        assert obj.predicate == ['assert_bar']
        try:
            expect('foo').bar
        except AssertionError:
            pass
        del expect.bar

    def test_add_bar_property_with_predicate_str(self):
        expect.add_assertion('bar', self.get_assertion(), is_property=True, predicate_str='foobaz')
        obj = expect('bar').bar
        assert obj.predicate == ['foobaz']
        del expect.bar

    def test_add_bar_not_prop(self):
        def is_value(self, value):
            return self.response_under_test == value

        expect.add_assertion('is_value', is_value, is_property=False)
        obj = expect('bar')
        obj.is_value('bar')
        try:
            obj.is_value('foo')
        except AssertionError:
            pass


class TestPath:

    def setup_method(self, method):
        self.json = {'foo': 'bar'}
        with requests_mock.mock() as m:
            m.get('http://example.com', headers={'foo': 'bar'}, json=self.json)
            self.obj = expect(requests.get('http://example.com'))

    def test_path_success(self):
        self.obj.json.path('foo')
        assert self.obj.value_under_test == 'bar'

    def test_path_failure(self):
        self.obj.json.path('bar')
        assert self.obj.value_under_test is None

class TestSchema:

    def setup_method(self, method):
        self.json = {'foo': 'bar'}
        with requests_mock.mock() as m:
            m.get('http://example.com', headers={'foo': 'bar'}, json=self.json)
            self.obj = expect(requests.get('http://example.com'))

    def test_schema_valid(self):
        self.obj.json.schema({
            'type': 'object',
            'properties': {
                'foo': {'type': 'string'},
            },
        })

    def test_invalid_schema(self):
        import jsonschema
        try:
            self.obj.json.schema({
                'type': 'object',
                'required': ['bar'],
                'properties': {
                    'bar': {'type': 'number'},
                },
            })
        except jsonschema.ValidationError:
            pass


class TestCall:

    def setup_method(self, method):
        self.json = {'foo': 'bar'}
        with requests_mock.mock() as m:
            m.get('http://example.com', headers={'foo': 'bar'}, json=self.json)
            self.obj = expect(requests.get('http://example.com'))

    def test_call(self):
        self.obj.json('to have key foo', lambda expect: 'foo' in expect.get())
        assert 'to have key foo' in self.obj.assertion


class TestAssertionBase:

    def setup_method(self, method):
        self.json = {'foo': 'bar'}
        self.headers = {'foo': 'bar'}
        with requests_mock.mock() as m:
            m.get('http://example.com', headers=self.headers, json=self.json)
            self.obj = expect(requests.get('http://example.com'))


class TestEqual(TestAssertionBase):

    def test_pass(self):
        self.obj.json.path('foo').equal('bar')
        assert 'equal to' in self.obj.assertion

    def test_fail(self):
        with pytest.raises(AssertionError):
            self.obj.json.path('foo').equal('foo')
        assert 'equal to' in self.obj.assertion


class TestEquals(TestAssertionBase):

    def test_pass(self):
        self.obj.json.path('foo').equals('bar')
        assert 'equals' in self.obj.assertion

    def test_fail(self):
        with pytest.raises(AssertionError):
            self.obj.json.path('foo').equals('foo')
        assert 'equals' in self.obj.assertion


class TestLike(TestAssertionBase):
    def test_pass(self):
        self.obj.json.path('foo').like('ba')

    def test_fail(self):
        with pytest.raises(AssertionError):
            self.obj.json.path('foo').like('NOTMATCHED')

class TestExactlyLike(TestAssertionBase):

    def test_pass(self):
        self.obj.json.path('foo').exactly_like('[rab]{3}')

    def test_fail(self):
        with pytest.raises(AssertionError):
            self.obj.json.path('foo').exactly_like('ba')


class TestContains(TestAssertionBase):

    def test_pass(self):
        self.obj.json.path('foo').contains('b')

    def test_fail(self):
        with pytest.raises(AssertionError):
            self.obj.json.path('foo').contains('z')


class TestStatusCode(TestAssertionBase):

    def test_pass(self):
        self.obj.status_code(200)

    def test_fail(self):
        with pytest.raises(AssertionError):
            self.obj.status_code(500)

class TestOK(TestAssertionBase):

    def test_pass(self):
        self.obj.ok

    def test_fail(self):
        self.json = {'foo': 'bar'}
        self.headers = {'foo': 'bar'}
        with requests_mock.mock() as m:
            m.get('http://example.com', headers=self.headers, json=self.json, status_code=500)
            self.obj = expect(requests.get('http://example.com'))

        with pytest.raises(AssertionError):
            self.obj.ok


class TestEncoding(TestAssertionBase):

    def test_pass(self):
        self.obj.encoding('utf-8')

    def test_fail(self):
        with pytest.raises(AssertionError):
            self.obj.encoding('ascii')

class TestNull(TestAssertionBase):

    def test_pass(self):
        self.obj.json.path('bar').null

    def test_fail(self):
        with pytest.raises(AssertionError):
            self.obj.json.path('foo').null

class TestValid:

    def test_pass(self):
        self.text = '{"foo": "bar"}'
        self.headers = {'Content-Type': 'application/json'}
        with requests_mock.mock() as m:
            m.get('http://example.com', headers=self.headers, text=self.text, status_code=200)
            self.obj = expect(requests.get('http://example.com'))

        self.obj.json.valid

    def test_fail(self):
        self.text = '{"foo": "bar",}'  # Invalid JSON
        self.headers = {'Content-Type': 'application/json'}
        with requests_mock.mock() as m:
            m.get('http://example.com', headers=self.headers, text=self.text, status_code=200)
            self.obj = expect(requests.get('http://example.com'))

        with pytest.raises(AssertionError):
            self.obj.json.valid

class TestVerbose(TestAssertionBase):

    def test_not_verbose(self, capsys):
        self.obj.verbose = False
        self.obj._test()
        out,err = capsys.readouterr()
        assert not out

    def test_verbose(self, capsys):
        self.obj.verbose = True
        self.obj._test()
        out,err = capsys.readouterr()
        assert out
