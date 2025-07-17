import logging
import azure.functions as func
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.core.rest import HttpRequest
from shared_code import azure_config
import json

environment_vars = azure_config()

# Set Azure Search endpoint and key
service_name = environment_vars["search_service_name"]
endpoint = f"https://{service_name}.search.windows.net"
key = environment_vars["search_api_key"]

# Your index name
index_name = "page-content-index"

# Create Azure SDK client
search_client = SearchClient(endpoint, index_name, AzureKeyCredential(key))

def new_shape(docs):
    old_api_shape = list(docs)
    client_side_expected_shape = []

    for item in old_api_shape:
        new_document = {}
        new_document["score"] = item["@search.score"]
        new_document["highlights"] = item.get("@search.highlights", {})

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

bp = func.Blueprint()
@bp.function_name("morelikethis")
@bp.route(route="morelikethis", methods=[func.HttpMethod.GET])
def main(req: func.HttpRequest) -> func.HttpResponse:
    
    # Get the page_id from query parameters
    page_id = req.params.get("page_id")
    
    if page_id:
        logging.info(f"/MoreLikeThis page_id = {page_id}")
        
        try:
            # Create the HTTP request for the MoreLikeThis query
            # MoreLikeThis uses GET request to /docs endpoint with moreLikeThis as query parameter
            request = HttpRequest(
                method="GET",
                url=f"{endpoint}/indexes/{index_name}/docs",
                params={
                    "api-version": "2023-11-01",
                    "moreLikeThis": page_id,
                    "top": 5,
                    "count": "true"
                },
                headers={
                    "Content-Type": "application/json",
                    "api-key": key
                }
            )
            
            # Send the request using the search client's send_request method
            response = search_client.send_request(request)
            
            # Check if the request was successful
            if response.status_code == 200:
                response_data = response.json()
                
                # Extract the documents from the response
                documents = response_data.get("value", [])
                
                # Transform the documents to match the expected shape
                returned_docs = new_shape(documents)
                
                # Format the response similar to search results
                full_response = {}
                full_response["count"] = response_data.get("@odata.count", len(documents))
                full_response["results"] = returned_docs
                
                return func.HttpResponse(
                    body=json.dumps(full_response), 
                    mimetype="application/json", 
                    status_code=200
                )
            else:
                error_message = f"Azure Search API returned status code {response.status_code}"
                logging.error(error_message)
                return func.HttpResponse(
                    body=json.dumps({"error": error_message}), 
                    mimetype="application/json", 
                    status_code=response.status_code
                )
            
        except Exception as e:
            logging.error(f"Error in MoreLikeThis: {str(e)}")
            return func.HttpResponse(
                body=json.dumps({"error": str(e)}), 
                mimetype="application/json", 
                status_code=500
            )
    else:
        return func.HttpResponse("No page_id param found.", status_code=400)