import os
import re
import types
from functools import wraps

import jmespath
import jsonschema


def predicate(fn_or_string):
    """

    :param fn_or_string:
    :return:
    """
    if callable(fn_or_string):
        fn = fn_or_string

        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            self.predicate.append(fn.__name__)
            result = fn(self, *args, **kwargs)
            if result is self:
                return self
            else:
                self._test(value=result)

        return wrapper

    else:
        predicate_str = fn_or_string

        def predicate_wrapper(fn):

            @wraps(fn)
            def wrapper(self, *args, **kwargs):
                self.predicate.append(predicate_str.format(*args, **kwargs))
                result = fn(self, *args, **kwargs)
                if result is self:
                    return result
                else:
                    self._test(value=result)

            return wrapper

        return predicate_wrapper


class NotSet:
    """A sentinel class indicating a value that is not None/null"""
    pass


class expect:
    """The main class in this library. Provides the test methods."""
    def __init__(self, response_under_test):

        self.response_under_test = response_under_test
        """The response under test"""

        self.value_under_test = NotSet()
        """The value that is being tested"""

        self.predicate = []
        """A :class:`list` of :class:`str`s that will be joined to make a human readable assertion"""

        self.test_called = False
        """A flag indicating whether any tests have been made"""

        self.verbose = os.environ.get('EXPECTLY_VERBOSE_MODE', True)
        """A flag indicating whether to print output while testing"""

    @classmethod
    def add_assertion(cls, name, assertion_callable, is_property=False, predicate_str=None):
        """Helper function to add an assertion to the expect class

        :param name:
        :param assertion_callable:
        :param is_property:
        :param predicate_str:
        :return:
        """
        if predicate_str is not None:
            assertion_callable = predicate(predicate_str)(assertion_callable)
        else:
            assertion_callable = predicate(assertion_callable)

        if is_property:
            assertion_callable = property(assertion_callable)

        setattr(cls, name, assertion_callable)

    @classmethod
    def add_join_word(cls, word, predicate_str=None):
        """Adds a non sementically meaningful join word, e.g. "to", "and", etc

        :param word:
        :param predicate_str:
        :return:
        """
        predicate_str = predicate_str or word

        def joiner(expect):
            return expect

        cls.add_assertion(word, joiner, is_property=True, predicate_str=predicate_str)

    #
    # HELPERS
    #

    def update_test_method(self, fn):
        """Given a function calls that function when :func:`expectly.expect.test` is called.

        :param fn:
        :return:
        """
        self.test = types.MethodType(fn, self)

    def _test(self, *args, **kwargs):
        """The actual test method that gets called. Calls the :func:`expectly.expect.test` method
        as well as sets some variables and prints some output if it is in debug mode.
        """
        self.test_called = True
        self.test(*args, **kwargs)
        if self.verbose:
            print(self.assertion)

    def test(self, value=True):
        """The default test method. It asserts the passed value is true with the assertion clause"""
        assert value, self.assertion

    def get(self):
        """A lazy getter for the value under test"""
        return self.response_under_test

    @property
    def assertion(self):
        """Composes the current human readable assertion

        :return: a :class:`str`
        """
        if not self.predicate:
            return f'Expected {self.response_under_test.__class__.__name__} to exist.'
        return f'Expected {self.response_under_test.__class__.__name__} ' + ' '.join(
            [part for part in self.predicate if part]) + '.'

    #
    # Semantically irrelevant join words
    #

    @property
    @predicate
    def to(self):
        """

        :return:
        """
        return self

    @property
    @predicate
    def have(self):
        """

        :return:
        """
        return self

    @property
    @predicate
    def be(self):
        """

        :return:
        """
        return self

    @property
    @predicate
    def that(self):
        """

        :return:
        """
        return self

    @property
    @predicate('and')
    def and_(self):
        """

        :return:
        """
        return self

    @property
    @predicate
    def the(self):
        """

        :return:
        """
        return self

    #
    # Semantically Relevant Modifers
    #

    @property
    @predicate('not')
    def not_(self):
        """Changes the test method to be a negative assertion

        :return:
        """
        def test(self, value=False):
            assert not value, self.assertion

        self.update_test_method(test)
        return self

    #
    # Data Preparation/Parsing
    #

    @predicate('a "{0}" header')
    def header(self, header):
        """Tests that the header exists. Sets the header to the value_under_test"""
        self._test(value=(header in self.response_under_test.headers))
        self.value_under_test = self.response_under_test.headers[header]
        return self

    @predicate('headers {0}')
    def headers(self, headers):
        self.value_under_test = {header: self.response_under_test.headers[header]
                                 for header in [h for h in headers if h in self.response_under_test.headers]}
        self._test(value=(len(headers) == len(self.value_under_test)))
        return self

    @property
    @predicate('body decoded as json')
    def json(self):
        def get(self):
            return self.response_under_test.json()

        self.get = types.MethodType(get, self)
        return self

    #
    # Assertions
    #

    @predicate('equal to "{0}"')
    def equal(self, value):
        return self.value_under_test == value

    @predicate('equals "{0}"')
    def equals(self, value):
        return self.value_under_test == value

    @predicate('like "{0}"')
    def like(self, regex):
        return bool(re.compile(regex).search(self.value_under_test))

    @predicate('exactly like "{0}"')
    def exactly_like(self, regex):
        return bool(re.compile(regex).fullmatch(self.value_under_test))

    @predicate('contains "{0}"')
    def contains(self, value):
        return value in self.value_under_test

    @predicate('a status code of "{0}"')
    def status_code(self, code):
        return code == self.response_under_test.status_code

    @property
    @predicate
    def ok(self):
        return self.response_under_test.ok

    @predicate('an encoding of "{0}"')
    def encoding(self, encoding):
        return self.response_under_test.encoding == encoding

    @property
    @predicate
    def null(self):
        return self.value_under_test is None

    @property
    @predicate
    def valid(self):
        try:
            self.value_under_test = self.get()  # Is essentially an "assert self.get does not raise"
            return True
        except Exception as e:
            return False

    @predicate('correct schema')
    def schema(self, schema):
        jsonschema.validate(self.get(), schema)
        return True

    @predicate('at the path "{0}"')
    def path(self, path):
        self.value_under_test = jmespath.search(path, self.get())
        return self

    @property
    @predicate('')
    def value(self):
        self.value_under_test = self.get()
        return self

    def __call__(self, predicate_str, fn):
        return predicate(predicate_str)(fn)(self)

    def __repr__(self):
        return 'expect({0})'.format(self.response_under_test)
