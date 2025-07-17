import logging
import azure.functions as func
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from shared_code import azure_config
import json

environment_vars = azure_config()

# Set Azure Search endpoint and key
service_name = environment_vars["search_service_name"]
endpoint = f"https://{service_name}.search.windows.net"
key = environment_vars["search_api_key"]

# Your index name
# environment_vars["search_index_name"]
index_name = "page-content-index"

# Create Azure SDK client
search_client = SearchClient(endpoint, index_name, AzureKeyCredential(key))

# returns obj like {organizations: 'array', author:'string'}
def read_facets(facetsString):
    facets = facetsString.split(",")
    output = {}
    for x in facets:
        if x.find("*") != -1:
            newVal = x.replace("*", "")
            output[newVal] = "array"
        else:
            output[x] = "string"

    return output


# creates filters in odata syntax
def create_filter_expression(filter_list, facets):
    i = 0
    filter_expressions = []
    return_string = ""
    separator = " and "

    while i < len(filter_list):
        field = filter_list[i]["field"]
        value = filter_list[i]["value"]

        if facets[field] == "array":
            print("array")
            filter_expressions.append(f"{field}/any(t: search.in(t, '{value}', ','))")
        else:
            print("value")
            filter_expressions.append(f"{field} eq '{value}'")

        i += 1

    return_string = separator.join(filter_expressions)

    return return_string


def new_shape(docs):

    old_api_shape = list(docs)

    client_side_expected_shape = []

    for item in old_api_shape:

        new_document = {}
        new_document["score"] = item["@search.score"]
        new_document["highlights"] = item["@search.highlights"]

        new_api_shape = {}
        new_api_shape["id"] = item["page_id"]
        new_api_shape["page_id"] = item["page_id"]
        new_api_shape["journal"] = item["journal"]
        new_api_shape["published_at"] = item["published_at"]
        new_api_shape["author"] = item["author"]
        new_api_shape["persons"] = item["persons"]
        new_api_shape["companies"] = item["companies"]
        new_api_shape["industries"] = item["industries"]
        new_api_shape["tags"] = item["tags"]
        new_api_shape["categories"] = item["categories"]
        new_api_shape["primary_channels"] = item["primary_channels"]
        new_api_shape["secondary_channels"] = item["secondary_channels"]
        new_api_shape["page_content"] = item["page_content"]
        new_api_shape["people"] = item["people"]
        new_api_shape["organizations"] = item["organizations"]

        new_document["document"] = new_api_shape

        client_side_expected_shape.append(new_document)

    return list(client_side_expected_shape)

bp=func.Blueprint()
@bp.function_name("search")
@bp.route(route="search", methods=[func.HttpMethod.GET, func.HttpMethod.POST] )
def main(req: func.HttpRequest) -> func.HttpResponse:

    # variables sent in body
    req_body = req.get_json()
    q = req_body.get("q")
    top = req_body.get("top") or 8
    skip = req_body.get("skip") or 0
    filters = req_body.get("filters") or []

    facets = environment_vars["search_facets"]
    facetKeys = read_facets(facets)

    search_filter = ""
    if len(filters):
        search_filter = create_filter_expression(filters, facetKeys)

    if q:
        logging.info(f"/Search q = {q}")

        search_results = search_client.search(
            search_text=q,
            top=top,
            skip=skip,
            facets=facetKeys,
            filter=search_filter,
            include_total_count=True,
        )

        returned_docs = new_shape(search_results)

        # format the React app expects
        full_response = {}

        full_response["count"] = search_results.get_count()
        full_response["facets"] = search_results.get_facets()
        full_response["results"] = returned_docs

        return func.HttpResponse(
            body=json.dumps(full_response), mimetype="application/json", status_code=200
        )
    else:
        return func.HttpResponse("No query param found.", status_code=200)
