"""Behavioral contract for this route adapter."""
import importlib.util
import os

CASES = (('  raw-birch  ', 'birchlantern'), ('passthrough_birch_lantern', 'passthrough_birch_lantern'))

def _load(index):
    name = "repair_%02d" % index
    path = os.path.join(os.path.dirname(__file__), "..", "src", "opaltelemetry", name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def _assert_registry():
    modules = [_load(index) for index in range(32)]
    assert [module.ROUTE_INDEX for module in modules] == list(range(32))
    assert {module.PROTOCOL for module in modules} == {"opal-v7"}

def test_birch_lantern_contract():
    _assert_registry()
    fn = _load(1).translate_birch_lantern
    for incoming, expected in CASES:
        assert fn(incoming) == expected
    assert fn("unrelated") == "unrelated"
