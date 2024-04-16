import requests
import time

from config.settings import MODEL
# from config.settings import SUMMARISE_API
# from config.settings import SUMMARISE_URL
# from config.settings import FACTCHECK_API
# from config.settings import FACTCHECK_URL
# from config.settings import GLOSSERY_API
# from config.settings import GLOSSERY_URL

class API:

    def __init__(self, api_key, url):
        self.api_key = api_key 
        self.url = url
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": f"{self.api_key}",
        }

    def invoke_post(self, message):
        post_data = {
            "content": [
                {
                    "contentType": "text",
                    "mediaType": "string",
                    "body": message
                }
            ],
            "model": MODEL
        }
        response = requests.post(self.url+ "/conversation", json=post_data, headers=self.headers)
        json_respn =  response.json()
        return json_respn
    
    def invoke_get(self, conversation_id, message_id = None ):
        uri_path = "/conversation/ "+conversation_id
        if message_id: 
            uri_path = uri_path + "/" + message_id
        response = requests.get(
            self.url + uri_path,
            headers=self.headers,
        )

        return response