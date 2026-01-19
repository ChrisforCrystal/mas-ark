#!/usr/bin/env python3
"""
Generate ARK Client Classes from OpenAPI Schema

This script generates typed ARK client classes for each API version found in the OpenAPI schema.
Each generated client extends a generic base client and includes all resources for that version.
"""

import json
import sys
import argparse
from pathlib import Path

# Import from the new gen_sdk module
from gen_sdk import extract_api_versions
from gen_sdk.python_sdk import (
    generate_base_client,
    generate_versioned_client,
    generate_yaml_routing
)
from gen_sdk.python_sdk_tests import (
    generate_test_base,
    generate_resource_client_tests,
    generate_versioned_client_tests,
    generate_test_footer
)


def main():
    """Main function to generate ARK clients from OpenAPI schema"""
    parser = argparse.ArgumentParser(description='Generate ARK Client Classes from OpenAPI Schema')
    parser.add_argument('schema_path', help='Path to OpenAPI schema JSON file')
    parser.add_argument('-v', '--version', action='store_true', help='Generate version info to stdout')
    parser.add_argument('-t', '--test', action='store_true', help='Generate unittest tests for the generated clients')
    
    args = parser.parse_args()
    # Load OpenAPI schema
    print(f"Loading OpenAPI schema from {args.schema_path}...", file=sys.stderr)
    with open(args.schema_path, 'r') as f:
        openapi_spec = json.load(f)

    # Extract API versions and resources
    print("Extracting API versions and resources...", file=sys.stderr)
    versions = extract_api_versions(openapi_spec)

    if args.test: # Handle -t flag - generate tests
        print("Generating unittest tests...", file=sys.stderr)
        
        # Collect all versioned client imports
        versioned_imports = []
        for api_version, resources in sorted(versions.items()):
            if resources:
                version_part = api_version.split('/')[-1]
                class_name = f"ARKClient{version_part.capitalize()}"
                versioned_imports.append(class_name)
        
        # Generate test base with fixtures and all imports
        base_test = generate_test_base()
        if versioned_imports:
            # Insert the versioned client imports after ARKResourceClient import
            import_line = "from ark_sdk.versions import " + ", ".join(versioned_imports)
            base_test = base_test.replace(
                "from ark_sdk.versions import ARKResourceClient",
                f"from ark_sdk.versions import ARKResourceClient, {', '.join(versioned_imports)}"
            )
        print(base_test, end='')
        
        # Generate ARKResourceClient tests
        print(generate_resource_client_tests(), end='')
        
        # Generate tests for each versioned client
        for api_version, resources in sorted(versions.items()):
            if resources:  # Only generate if there are resources
                print(generate_versioned_client_tests(api_version, resources), end='')
        
        print(generate_test_footer(), end='')
        print("\nTest generation complete!", file=sys.stderr)
        return
    elif args.version: # Handle -v flag

        # Default behavior - generate clients
        print(generate_base_client(), end='')

        # Write versioned clients
        for api_version, resources in sorted(versions.items()):
            if resources:  # Only generate if there are resources
               print(generate_versioned_client(api_version, resources), end='')

        print("\nGeneration complete!", file=sys.stderr)
        return
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()