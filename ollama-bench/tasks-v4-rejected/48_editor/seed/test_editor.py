"""Visible examples for 48_editor.  Run with:  python test_editor.py"""
from editor import Editor, EditorError


def example_1_insert_replace_undo():
    e = Editor()
    e.insert("hello")
    e.insert(" you")                 # coalesces: 5 + 4 <= 12
    assert e.undo_depth() == 1
    e.set_selection(6, 9)
    assert e.selected_text() == "you"
    e.insert("me")                   # kind "replace"
    assert (e.text, e.cursor, e.anchor) == ("hello me", 8, 8)
    assert e.undo_depth() == 2
    assert e.undo() is True
    assert (e.text, e.cursor, e.anchor) == ("hello you", 9, 6)


def example_2_word_motion_and_cut():
    e = Editor()
    e.insert("one two three")
    e.move_doc(-1)
    e.move_word(+1)
    assert e.cursor == 3
    e.move_word(+1, extend=True)
    assert e.selection() == (3, 7) and e.selected_text() == " two"
    e.cut()
    assert (e.text, e.clipboard, e.cursor, e.anchor) == ("one three", " two", 3, 3)


def example_3_delete_back_undo():
    e = Editor()
    e.insert("abcdef")
    e.move_char(-1)
    assert e.cursor == 5
    e.delete_back(2)
    assert (e.text, e.cursor) == ("abcf", 3)
    assert e.undo() is True
    assert (e.text, e.cursor, e.anchor) == ("abcdef", 5, 5)
    assert e.redo_depth() == 1


def example_4_edit_clears_redo():
    e = Editor()
    e.insert("ab")
    e.undo()
    e.insert("z")
    assert e.redo_depth() == 0 and e.text == "z"


def example_5_errors():
    e = Editor()
    e.insert("abc")
    for fn, args in ((e.set_selection, (0, 9)), (e.delete_forward, (-1,)),
                     (e.move_char, (2,))):
        try:
            fn(*args)
        except EditorError:
            pass
        else:
            raise AssertionError("expected EditorError from %r" % (fn,))
    assert (e.text, e.cursor, e.anchor) == ("abc", 3, 3)
    assert issubclass(EditorError, ValueError)


for _name, _fn in sorted(list(globals().items())):
    if _name.startswith("example_"):
        _fn()
print("visible examples OK")
