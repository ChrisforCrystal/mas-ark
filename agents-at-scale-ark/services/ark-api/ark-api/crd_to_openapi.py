#!/usr/bin/env python3
"""
Convert Kubernetes CRDs to OpenAPI v3 spec

Usage: python crd_to_openapi.py <input_crd1.yaml> [<input_crd2.yaml> ...]

Outputs unified OpenAPI spec to stdout. Diagnostic messages go to stderr.
"""

import yaml
import json
import sys
from typing import Dict, Any, List


def convert_k8s_type_to_openapi(k8s_type: str) -> str:
    """Convert Kubernetes type to OpenAPI type"""
    type_mapping = {
        "string": "string",
        "integer": "integer",
        "number": "number",
        "boolean": "boolean",
        "object": "object",
        "array": "array"
    }
    return type_mapping.get(k8s_type, "string")


def process_properties(properties: Dict[str, Any], required: List[str] = None) -> Dict[str, Any]:
    """Process CRD properties into OpenAPI schema"""
    openapi_properties = {}
    
    for prop_name, prop_def in properties.items():
        openapi_prop = {}
        
        if "type" in prop_def:
            openapi_prop["type"] = convert_k8s_type_to_openapi(prop_def["type"])
        
        if "description" in prop_def:
            openapi_prop["description"] = prop_def["description"]
        
        if "default" in prop_def:
            openapi_prop["default"] = prop_def["default"]
        
        if "enum" in prop_def:
            openapi_prop["enum"] = prop_def["enum"]
        
        if "minimum" in prop_def:
            openapi_prop["minimum"] = prop_def["minimum"]
        
        if "maximum" in prop_def:
            openapi_prop["maximum"] = prop_def["maximum"]
        
        if "pattern" in prop_def:
            openapi_prop["pattern"] = prop_def["pattern"]
        
        if prop_def.get("type") == "array" and "items" in prop_def:
            openapi_prop["items"] = process_schema(prop_def["items"])
        
        if prop_def.get("type") == "object" and "properties" in prop_def:
            nested_required = prop_def.get("required", [])
            openapi_prop["properties"] = process_properties(prop_def["properties"], nested_required)
            if nested_required:
                openapi_prop["required"] = nested_required
        
        openapi_properties[prop_name] = openapi_prop
    
    return openapi_properties


def process_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Process CRD schema into OpenAPI schema"""
    openapi_schema = {}
    
    if "type" in schema:
        openapi_schema["type"] = convert_k8s_type_to_openapi(schema["type"])
    
    if "description" in schema:
        openapi_schema["description"] = schema["description"]
    
    if "properties" in schema:
        required = schema.get("required", [])
        openapi_schema["properties"] = process_properties(schema["properties"], required)
        if required:
            openapi_schema["required"] = required
    
    if schema.get("type") == "array" and "items" in schema:
        openapi_schema["items"] = process_schema(schema["items"])
    
    return openapi_schema


def crd_to_openapi(crds: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Convert multiple CRDs to a single OpenAPI specification"""
    
    # Create base OpenAPI spec
    openapi = {
        "openapi": "3.0.0",
        "info": {
            "title": "Kubernetes CRDs API",
            "version": "1.0.0",
            "description": "OpenAPI spec for Kubernetes custom resources"
        },
        "paths": {},
        "components": {
            "schemas": {}
        }
    }
    
    # Process each CRD
    for crd in crds:
        # Extract metadata
        group = crd["spec"]["group"]
        versions = crd["spec"]["versions"]
        kind = crd["spec"]["names"]["kind"]
        plural = crd["spec"]["names"]["plural"]
        
        # Process each version
        for version in versions:
            version_name = version["name"]
            schema = version.get("schema", {}).get("openAPIV3Schema", {})
            
            # Create schema component
            schema_name = f"{kind}_{version_name}"
            openapi["components"]["schemas"][schema_name] = process_schema(schema)
            
            # Create paths
            base_path = f"/apis/{group}/{version_name}/{plural}"
            
            # List endpoint
            openapi["paths"][base_path] = {
                    "get": {
                "summary": f"List {plural}",
                "operationId": f"list_{plural}_{version_name}",
                "responses": {
                    "200": {
                        "description": f"List of {plural}",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "items": {
                                            "type": "array",
                                            "items": {
                                                "$ref": f"#/components/schemas/{schema_name}"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
                "post": {
                "summary": f"Create {kind}",
                "operationId": f"create_{kind.lower()}_{version_name}",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{schema_name}"
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": f"{kind} created",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": f"#/components/schemas/{schema_name}"
                                }
                            }
                        }
                    }
                }
                }
            }
            
            # Instance endpoints
            instance_path = f"{base_path}/{{name}}"
            openapi["paths"][instance_path] = {
                "get": {
                "summary": f"Get {kind}",
                "operationId": f"get_{kind.lower()}_{version_name}",
                "parameters": [
                    {
                        "name": "name",
                        "in": "path",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": f"{kind} details",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": f"#/components/schemas/{schema_name}"
                                }
                            }
                        }
                    }
                }
            },
                "put": {
                "summary": f"Update {kind}",
                "operationId": f"update_{kind.lower()}_{version_name}",
                "parameters": [
                    {
                        "name": "name",
                        "in": "path",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{schema_name}"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": f"{kind} updated",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": f"#/components/schemas/{schema_name}"
                                }
                            }
                        }
                    }
                }
            },
                "delete": {
                "summary": f"Delete {kind}",
                "operationId": f"delete_{kind.lower()}_{version_name}",
                "parameters": [
                    {
                        "name": "name",
                        "in": "path",
                        "required": True,
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "responses": {
                    "204": {
                        "description": f"{kind} deleted"
                    }
                    }
                }
            }
    
    return openapi


def main():
    if len(sys.argv) < 2:
        print("Usage: python crd_to_openapi.py <input_crd1.yaml> [<input_crd2.yaml> ...]", file=sys.stderr)
        sys.exit(1)
    
    input_files = sys.argv[1:]
    
    # Read all CRDs
    crds = []
    for input_file in input_files:
        with open(input_file, 'r') as f:
            crd = yaml.safe_load(f)
            crds.append(crd)
        print(f"Loaded CRD from {input_file}", file=sys.stderr)
    
    # Convert to OpenAPI
    openapi_spec = crd_to_openapi(crds)
    
    # Output OpenAPI spec to stdout
    json.dump(openapi_spec, sys.stdout, indent=2)
    sys.stdout.write('\n')  # Add final newline


if __name__ == "__main__":
    main()