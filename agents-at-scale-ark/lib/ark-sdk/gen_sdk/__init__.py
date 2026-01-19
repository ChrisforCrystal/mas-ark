#!/usr/bin/env python3
"""
SDK Generation Module

Common utilities and functions for generating SDK clients from OpenAPI schemas.
"""

import re
from typing import Dict, List, Any


def extract_api_versions(openapi_spec: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Extract API versions and their resources from OpenAPI spec"""
    versions = {}
    
    for path, methods in openapi_spec.get('paths', {}).items():
        # Extract API version from path (e.g., /apis/ark.mckinsey.com/v1alpha1/agents)
        match = re.match(r'/apis/([^/]+)/([^/]+)/([^/]+)', path)
        if match:
            group = match.group(1)
            version = match.group(2)
            resource = match.group(3)
            
            api_version = f"{group}/{version}"
            
            if api_version not in versions:
                versions[api_version] = []
            
            # Get the resource info from the schema reference
            for method, details in methods.items():
                if method in ['get', 'post'] and 'responses' in details:
                    for status, response in details['responses'].items():
                        if status.startswith('2') and 'content' in response:
                            content = response['content'].get('application/json', {})
                            schema = content.get('schema', {})
                            
                            # Extract model reference
                            if '$ref' in schema:
                                model_ref = schema['$ref']
                            elif 'properties' in schema and 'items' in schema['properties']:
                                items = schema['properties']['items']
                                if 'items' in items and '$ref' in items['items']:
                                    model_ref = items['items']['$ref']
                                else:
                                    continue
                            else:
                                continue
                            
                            # Extract model name from reference
                            model_name = model_ref.split('/')[-1]
                            
                            # Extract kind from model name (e.g., Agent_v1alpha1 -> Agent, A2AServer_v1prealpha1 -> A2AServer)
                            kind_match = re.match(r'([A-Z][a-zA-Z0-9]+)_', model_name)
                            if kind_match:
                                kind = kind_match.group(1)
                                
                                # Check if this resource already exists
                                existing = False
                                for res in versions[api_version]:
                                    if res['plural'] == resource:
                                        existing = True
                                        break
                                
                                if not existing:
                                    versions[api_version].append({
                                        'kind': kind,
                                        'plural': resource,
                                        'model_class': model_name,
                                        'api_version': api_version
                                    })
                            break
                    break
    
    return versions