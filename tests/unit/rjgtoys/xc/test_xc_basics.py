
import json

from pytest import raises


from rjgtoys.xc import Bug, Error

class ExampleError(Error):

    name: str

    code: int

    detail = "Example error: name={name} code={code}"


def test_example_ok():

    with raises(ExampleError) as e:
        raise ExampleError(name='ok', code=1)

    assert e.value.name == 'ok'
    assert e.value.code == 1

def test_example_to_dict():

    e = ExampleError(name='json', code=2)

    rebuilt = e.to_dict()

    assert rebuilt['content'] == dict(
        name='json',
        code=2
        )

    # Test that we can reconstruct the exception

    f = Error.from_obj(rebuilt)

    assert f == e



def test_example_from_json():

    data = """
        {
            "type": "test_xc_basics.ExampleError",
            "content": {
            "name": "from_json",
            "code": 3
            }
        }
    """

    e = Error.from_json(data)

    assert isinstance(e, ExampleError)


def test_example_from_json_fails():

    data = """
        {
            "type": "NoSuchError"
        }
    """

    with raises(TypeError) as e:
        Error.from_json(data)

    assert str(e.value) == "No Error type NoSuchError"


def test_example_parse_json():


    data = """
        {
            "name": "from_json",
            "code": 3
        }
    """

    e = ExampleError.parse_json(data)

    assert isinstance(e, ExampleError)

    assert e.name == "from_json"
    assert e.code == 3

def test_example_str():

    e = ExampleError(name="string", code=42)

    assert str(e) == "Example error: name=string code=42"


class DefaultedError(Error):

    label: str = "missing"


def test_defaulted_ok():

    e = DefaultedError()

    assert e.label == "missing"


