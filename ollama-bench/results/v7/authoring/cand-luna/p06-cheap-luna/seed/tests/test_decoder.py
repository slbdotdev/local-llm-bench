"""Visible contract test for relay window decoding."""
import importlib.util
import os


SOURCE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "relay", "decoder.py")
spec = importlib.util.spec_from_file_location("relay_decoder", SOURCE)
decoder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(decoder)


def test_window_contract():
    assert decoder.WINDOW_KIND == "half-open"
    assert decoder.decode_window("abcdefgh", 2, 5) == "cde"
    assert decoder.decode_window("abcdefgh", 0, 8) == "abcdefgh"


if __name__ == "__main__":
    test_window_contract()
    print("visible decoder contract: pass")
