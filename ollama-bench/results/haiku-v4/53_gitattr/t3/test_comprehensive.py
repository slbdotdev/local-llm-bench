#!/usr/bin/env python3
'''Comprehensive test suite for gitattr.py'''

from gitattr import AttrError, compile_attrs, check_attrs

def test_errors():
    print('Testing error conditions...')
    
    try:
        compile_attrs([' text'])
        assert False
    except AttrError as e:
        assert e.kind == 'empty_pattern'
        print('OK: empty_pattern error')
    
    try:
        compile_attrs(['x/ -text'])
        assert False
    except AttrError as e:
        assert e.kind == 'trailing_slash'
        print('OK: trailing_slash error')
    
    try:
        compile_attrs(['[ text'])
        assert False
    except AttrError as e:
        assert e.kind == 'unterminated_class'
        print('OK: unterminated_class error')

    try:
        compile_attrs(['[[:invalid:] text'])
        assert False
    except AttrError as e:
        assert e.kind == 'bad_posix_class'
        print('OK: bad_posix_class error')

    try:
        compile_attrs(['*.txt'])
        assert False
    except AttrError as e:
        assert e.kind == 'no_attrs'
        print('OK: no_attrs error on rule')

    try:
        compile_attrs(['*.txt 9bad'])
        assert False
    except AttrError as e:
        assert e.kind == 'bad_attr_name'
        print('OK: bad_attr_name error')

    try:
        compile_attrs(['[attr]9m text'])
        assert False
    except AttrError as e:
        assert e.kind == 'bad_macro_name'
        print('OK: bad_macro_name error')

    try:
        compile_attrs(['[attr]m a', '[attr]m b'])
        assert False
    except AttrError as e:
        assert e.kind == 'duplicate_macro'
        print('OK: duplicate_macro error')

    try:
        compile_attrs(['[attr]a b', '[attr]b a'])
        assert False
    except AttrError as e:
        assert e.kind == 'macro_cycle'
        print('OK: macro_cycle error')

def test_basic():
    print()
    print('Testing basic functionality...')
    
    c = compile_attrs(['*.txt text'])
    assert check_attrs('file.txt', c) == {'text': True}
    print('OK: basic matching')
    
    c = compile_attrs(['/doc/*.txt -text diff=plain'])
    result = check_attrs('doc/b.txt', c)
    assert result == {'text': False, 'diff': 'plain'}
    print('OK: anchored pattern with attributes')
    
    c = compile_attrs(['[attr]binary -diff -text', '*.png binary', '*.png diff=hex'])
    result = check_attrs('x.png', c)
    assert result == {'binary': True, 'diff': 'hex', 'text': False}
    print('OK: macro expansion')

if __name__ == '__main__':
    test_errors()
    test_basic()
    print()
    print('All tests passed!')
