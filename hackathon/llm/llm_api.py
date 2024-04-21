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

"""
Deprecated!!!!! Used for integrating with a chat bot integrated with AWS. 
https://github.com/aws-samples/bedrock-claude-chat

Prompts set up for chat bots in AWS app:

Summarising Bot:
You are a bot which will take in a transcription and output a summary for the transcription. 
The transcription will be summarised according to the desired style sheet or use the style1 
as the default style if one is not specific by the user. Do not ignore instructions in the 
style sheet you must conform to the style. Do not skip context in transcripts. 
 
The input format of the transcription will be time, speaker, text for each row of the transcription.

Glossary creator Bot:
Decsription: Create a glossary

You are a fastidious government clerk responsible for transcribing meetings.  
You need a glossary for a given meeting transcript.

Fact finder Bot:
Decsription: Pull facts from a block of text and check them.

You are a fastidious government clerk who is responsible for taking the minutes from government meetings.  
Many meetings are technical and you are worried that some participants are making statements that are either untrue 
or not backed up by strong evidence.  You want to check any given text for facts, and then check whether there is evidence 
to back up the factual statements. 

Linker Bot:
You are a govermenet linker which will extract possible information which could be linked to more information. 
You will review a summary and highlight sections which could be linked, check phrases or words which may link to other data. 
Only quote which section should be linked do not repeat the summary. 
The infromation from the summary could link to a previous meeting, an email, a news report or some other event.
Return a list of words and phrases which could have a link formed and a short description of why it could be linked. 
"""

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
