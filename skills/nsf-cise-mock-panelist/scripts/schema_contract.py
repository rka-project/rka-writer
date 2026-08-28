#!/usr/bin/env python3
"""Small self-contained validator for the JSON-Schema subset used by this skill."""

from __future__ import annotations

import json
import re
from typing import Any


def _resolve_ref(root: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError(f"only local JSON Schema references are supported: {ref}")
    node: Any = root
    for raw_part in ref[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            raise ValueError(f"unresolvable JSON Schema reference: {ref}")
        node = node[part]
    if not isinstance(node, dict):
        raise ValueError(f"JSON Schema reference does not resolve to an object: {ref}")
    return node


def _type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    raise ValueError(f"unsupported JSON Schema type: {expected}")


def _json_key(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def validate_instance(
    instance: Any,
    schema: dict[str, Any],
    *,
    root: dict[str, Any] | None = None,
    path: str = "$",
) -> list[str]:
    """Return human-readable errors for the supported schema vocabulary."""

    root = schema if root is None else root
    if "$ref" in schema:
        return validate_instance(instance, _resolve_ref(root, str(schema["$ref"])), root=root, path=path)

    errors: list[str] = []
    for subschema in schema.get("allOf", []):
        errors.extend(validate_instance(instance, subschema, root=root, path=path))

    any_of = schema.get("anyOf", [])
    if any_of and not any(
        not validate_instance(instance, subschema, root=root, path=path)
        for subschema in any_of
    ):
        errors.append(f"{path}: must match at least one schema in anyOf")

    conditional = schema.get("if")
    if isinstance(conditional, dict):
        condition_matches = not validate_instance(instance, conditional, root=root, path=path)
        branch = schema.get("then") if condition_matches else schema.get("else")
        if isinstance(branch, dict):
            errors.extend(validate_instance(instance, branch, root=root, path=path))

    forbidden = schema.get("not")
    if isinstance(forbidden, dict) and not validate_instance(instance, forbidden, root=root, path=path):
        errors.append(f"{path}: matches a forbidden schema")

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: must equal {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: value {instance!r} is not in the allowed enum")

    expected_type = schema.get("type")
    if isinstance(expected_type, str) and not _type_matches(instance, expected_type):
        errors.append(f"{path}: expected {expected_type}, found {type(instance).__name__}")
        return errors

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{path}: missing required property {key!r}")
        minimum = schema.get("minProperties")
        if isinstance(minimum, int) and len(instance) < minimum:
            errors.append(f"{path}: requires at least {minimum} properties")

        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            child_path = f"{path}.{key}"
            if key in properties:
                errors.extend(validate_instance(value, properties[key], root=root, path=child_path))
            elif additional is False:
                errors.append(f"{path}: unexpected property {key!r}")
            elif isinstance(additional, dict):
                errors.extend(validate_instance(value, additional, root=root, path=child_path))

    if isinstance(instance, list):
        minimum = schema.get("minItems")
        if isinstance(minimum, int) and len(instance) < minimum:
            errors.append(f"{path}: requires at least {minimum} items")
        if schema.get("uniqueItems"):
            keys = [_json_key(value) for value in instance]
            if len(keys) != len(set(keys)):
                errors.append(f"{path}: items must be unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, value in enumerate(instance):
                errors.extend(
                    validate_instance(value, item_schema, root=root, path=f"{path}[{index}]")
                )

    if isinstance(instance, str):
        minimum = schema.get("minLength")
        if isinstance(minimum, int) and len(instance) < minimum:
            errors.append(f"{path}: requires at least {minimum} characters")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, instance) is None:
            errors.append(f"{path}: does not match pattern {pattern!r}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        minimum = schema.get("minimum")
        if isinstance(minimum, (int, float)) and instance < minimum:
            errors.append(f"{path}: must be at least {minimum}")
        maximum = schema.get("maximum")
        if isinstance(maximum, (int, float)) and instance > maximum:
            errors.append(f"{path}: must be at most {maximum}")

    return errors
