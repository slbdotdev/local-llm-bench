from schema import validate

def test(name, instance, schema, expected):
    result = validate(instance, schema)
    if result != expected:
        print(f"FAIL: {name}")
        print(f"  instance: {instance}")
        print(f"  schema: {schema}")
        print(f"  expected: {expected}, got: {result}")
        return False
    print(f"PASS: {name}")
    return True

all_pass = True

# Type validation
all_pass &= test("string type valid", "hello", {"type": "string"}, True)
all_pass &= test("string type invalid", 123, {"type": "string"}, False)
all_pass &= test("integer type valid", 42, {"type": "integer"}, True)
all_pass &= test("integer type invalid bool", True, {"type": "integer"}, False)
all_pass &= test("integer type invalid string", "42", {"type": "integer"}, False)
all_pass &= test("number type invalid bool", True, {"type": "number"}, False)
all_pass &= test("boolean type valid", True, {"type": "boolean"}, True)
all_pass &= test("boolean type invalid", 1, {"type": "boolean"}, False)
all_pass &= test("null type valid", None, {"type": "null"}, True)
all_pass &= test("null type invalid", 0, {"type": "null"}, False)
all_pass &= test("array type valid", [1, 2], {"type": "array"}, True)
all_pass &= test("array type invalid", "not array", {"type": "array"}, False)
all_pass &= test("object type valid", {"a": 1}, {"type": "object"}, True)
all_pass &= test("object type invalid", [1, 2], {"type": "object"}, False)

# String length
all_pass &= test("minLength pass", "hello", {"type": "string", "minLength": 5}, True)
all_pass &= test("minLength fail", "hi", {"type": "string", "minLength": 5}, False)
all_pass &= test("maxLength pass", "hi", {"type": "string", "maxLength": 5}, True)
all_pass &= test("maxLength fail", "hello world", {"type": "string", "maxLength": 5}, False)

# Number bounds
all_pass &= test("minimum pass", 5, {"type": "number", "minimum": 5}, True)
all_pass &= test("minimum fail", 4, {"type": "number", "minimum": 5}, False)
all_pass &= test("maximum pass", 5, {"type": "number", "maximum": 5}, True)
all_pass &= test("maximum fail", 6, {"type": "number", "maximum": 5}, False)

# Array validation
all_pass &= test("array items", [1, 2, 3], {"type": "array", "items": {"type": "number"}}, True)
all_pass &= test("array items fail", [1, "two", 3], {"type": "array", "items": {"type": "number"}}, False)
all_pass &= test("minItems pass", [1, 2], {"type": "array", "minItems": 2}, True)
all_pass &= test("minItems fail", [1], {"type": "array", "minItems": 2}, False)
all_pass &= test("maxItems pass", [1, 2], {"type": "array", "maxItems": 2}, True)
all_pass &= test("maxItems fail", [1, 2, 3], {"type": "array", "maxItems": 2}, False)

# Object validation
all_pass &= test("required fields", {"name": "John", "age": 30},
                 {"type": "object", "required": ["name", "age"]}, True)
all_pass &= test("required missing", {"name": "John"},
                 {"type": "object", "required": ["name", "age"]}, False)
all_pass &= test("properties valid", {"name": "John"},
                 {"type": "object", "properties": {"name": {"type": "string"}}}, True)
all_pass &= test("properties invalid", {"name": 123},
                 {"type": "object", "properties": {"name": {"type": "string"}}}, False)

if all_pass:
    print("\nALL TESTS PASSED")
else:
    print("\nSOME TESTS FAILED")
    exit(1)
