import time

import requests

from config.settings import (
    CONVERSATION_API,
    CONVERSATION_URL,
    FACTCHECK_API,
    FACTCHECK_URL,
    GLOSSERY_API,
    GLOSSERY_URL,
    MODEL,
    SUMMARISE_API,
    SUMMARISE_URL,
)


class API:

    def __init__(self, api_key, url):
        self.api_key = api_key
        self.url = url
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": f"{self.api_key}",
        }

    def invoke_post(self, message, conversation_id=None):
        post_data = {
            "message": {
                "content": [
                    {"contentType": "text", "mediaType": "string", "body": message}
                ],
                "model": MODEL,
            }
        }
        if conversation_id is not None:
            post_data["conversationId"] = conversation_id
        response = requests.post(
            self.url + "/conversation", json=post_data, headers=self.headers
        )
        json_respn = response.json()
        return json_respn

    def invoke_get(self, conversation_id):
        uri_path = "/conversation/" + conversation_id
        response = requests.get(
            self.url + uri_path,
            headers=self.headers,
        )
        json_response = response.json()

        last_msg_id = json_response["lastMessageId"]
        return json_response["messageMap"][last_msg_id]["content"][0]["body"]


summary_api = API(SUMMARISE_API, SUMMARISE_URL)
fact_check_api = API(FACTCHECK_API, FACTCHECK_URL)
glossery_api = API(GLOSSERY_API, GLOSSERY_URL)
conversation_api = API(CONVERSATION_API, CONVERSATION_URL)
