import json

def validate(instance, schema):
    """
    Validate a JSON instance against a schema.
    Returns True if valid, False otherwise.

    Supports:
    - type checking (string, number, integer, boolean, array, object, null)
    - required fields in objects
    - minLength / maxLength for strings
    - minimum / maximum for numbers
    - items schema for array elements
    """

    # Type validation
    schema_type = schema.get("type")
    if schema_type:
        if schema_type == "string":
            if not isinstance(instance, str):
                return False
        elif schema_type == "integer":
            if not isinstance(instance, int) or isinstance(instance, bool):
                return False
        elif schema_type == "number":
            if isinstance(instance, bool) or not isinstance(instance, (int, float)):
                return False
        elif schema_type == "boolean":
            if not isinstance(instance, bool):
                return False
        elif schema_type == "array":
            if not isinstance(instance, list):
                return False
        elif schema_type == "object":
            if not isinstance(instance, dict):
                return False
        elif schema_type == "null":
            if instance is not None:
                return False

    # String validation
    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            return False
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            return False

    # Number validation
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            return False
        if "maximum" in schema and instance > schema["maximum"]:
            return False

    # Array validation
    if isinstance(instance, list):
        if "items" in schema:
            item_schema = schema["items"]
            for item in instance:
                if not validate(item, item_schema):
                    return False
        if "minItems" in schema and len(instance) < schema["minItems"]:
            return False
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            return False

    # Object validation
    if isinstance(instance, dict):
        if "required" in schema:
            for field in schema["required"]:
                if field not in instance:
                    return False

        if "properties" in schema:
            for key, prop_schema in schema["properties"].items():
                if key in instance:
                    if not validate(instance[key], prop_schema):
                        return False

    return True
