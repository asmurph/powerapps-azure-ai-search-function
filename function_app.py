import json
import logging
import os

import azure.functions as func
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


# Creates an Azure AI Search client using an API key or managed identity.
def get_search_client(index_name: str) -> SearchClient:
    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
    api_key = os.getenv("AZURE_SEARCH_API_KEY")
    credential = AzureKeyCredential(api_key) if api_key else DefaultAzureCredential()
    return SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)


@app.route(route="search", methods=["POST"])
# Receives a search request, queries Azure AI Search, and returns matching documents.
def search(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        query = str(body.get("query", "")).strip()
        if not query:
            return func.HttpResponse(json.dumps({"error": "query is required"}), status_code=400, mimetype="application/json")

        index_name = os.getenv("AZURE_SEARCH_INDEX", "documents-index")
        top = min(max(int(body.get("top", 10)), 1), 50)
        filter_expression = body.get("filter") or None
        select = body.get("select") or ["id", "title", "content", "sourceUrl"]

        client = get_search_client(index_name)
        results = client.search(
            search_text=query,
            top=top,
            filter=filter_expression,
            select=select,
            query_type=QueryType.SIMPLE,
        )

        items = []
        for result in results:
            doc = {field: result.get(field) for field in select}
            doc["score"] = result.get("@search.score")
            items.append(doc)

        return func.HttpResponse(
            json.dumps({"query": query, "count": len(items), "results": items}, default=str),
            status_code=200,
            mimetype="application/json",
        )
    except ValueError as ex:
        return func.HttpResponse(json.dumps({"error": str(ex)}), status_code=400, mimetype="application/json")
    except Exception:
        logging.exception("Azure AI Search request failed")
        return func.HttpResponse(json.dumps({"error": "Search request failed"}), status_code=500, mimetype="application/json")
