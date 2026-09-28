# Power Apps -> Azure Function -> Azure AI Search

Python v2 Azure Functions project exposing POST /api/search for a Power Platform custom connector.

## Local setup
1. Install Python, Azure Functions Core Tools, and the Azure Functions extension for VS Code.
2. Create a virtual environment: `py -m venv .venv`
3. Activate it on Windows: `.venv\\Scripts\\activate`
4. Install packages: `pip install -r requirements.txt`
5. Copy `local.settings.example.json` to `local.settings.json` and replace the Azure AI Search values.
6. Run: `func start`

POST body example:
`{"query":"travel policy","top":10}`

## Azure configuration
Configure AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_INDEX as Function App settings. For quick testing, set AZURE_SEARCH_API_KEY to an Azure AI Search query key. For production, omit the key, enable the Function App managed identity, and grant that identity the Azure AI Search data-plane role needed to query the index.

## Custom connector
Replace YOUR-FUNCTION-APP in `openapi.yaml`. Import the OpenAPI file into a Power Platform custom connector. The sample definition uses the Function authorization key as the `code` query parameter. For enterprise production deployments, prefer Microsoft Entra ID authentication rather than distributing a Function key to clients.

## Power Fx example
Assuming the connector is named `AzureAISearch`:

`ClearCollect(colSearchResults, AzureAISearch.SearchDocuments({query: txtSearch.Text, top: 10}).results)`

Bind a Gallery's Items property to `colSearchResults`. Common labels can use `ThisItem.title` and `ThisItem.content`; an icon can use `Launch(ThisItem.sourceUrl)`.

## Important
The fields id/title/content/sourceUrl are examples. Change `select` in function_app.py and the OpenAPI response schema to match the exact fields in your Azure AI Search index.
