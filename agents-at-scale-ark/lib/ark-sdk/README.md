# ARK SDK

## Build Process
The build converts Kubernetes CRDs to OpenAPI schema using `crd_to_openapi.py`, generates Python SDK with OpenAPI Generator, adds custom Kubernetes client classes via `generate_ark_clients.py`, and packages as wheel files. Run `make build` to execute the full pipeline: CRD YAML → OpenAPI → Python SDK → Custom Clients → Tests → Package.

## Client Generation
The `generate_ark_clients.py` script parses the OpenAPI schema to extract API versions and resources, creates a generic `ARKResourceClient` base class with CRUD operations, generates version-specific clients (e.g., `ARKClientV1alpha1`) with typed resource attributes, and provides both sync and async methods. It outputs `versions.py` containing all client classes and generates corresponding unit tests.

## Usage Examples

### Basic CRUD Operations
```python
from ark_sdk.versions import ARKClientV1alpha1
from ark_sdk.models.agent_v1alpha1 import AgentV1alpha1, AgentV1alpha1Spec

# Initialize client
client = ARKClientV1alpha1(namespace="default")

# Create agent
agent = AgentV1alpha1(
    metadata={"name": "my-agent"},
    spec=AgentV1alpha1Spec(prompt="Hello", modelRef={"name": "gpt-4"})
)
created = client.agents.create(agent)

# Get, update, delete
agent = client.agents.get("my-agent")
agent.spec.prompt = "Updated"
client.agents.update(agent)
client.agents.delete("my-agent")
```

### Async Operations
```python
# List agents asynchronously
agents = await client.agents.a_list()

# Create query asynchronously
query = await client.queries.a_create(QueryV1alpha1(...))
```

### Working with Multiple Resources
```python
client = ARKClientV1alpha1()

# Access different resource types
models = client.models.list()
queries = client.queries.list(label_selector="status=completed")
teams = client.teams.get("research-team")
tools = client.tools.list()
```
