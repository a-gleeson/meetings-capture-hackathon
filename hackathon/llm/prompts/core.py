from langchain.prompts.prompt import PromptTemplate

B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"

_advice_system_prompt = """

"""
_advice_instruction = """
===  ===                                           
{}
===  ===
{context}
=======
Question: , {}.
=======
Answer:
"""


_advice_prompt = (
    B_INST + B_SYS + _advice_system_prompt + E_SYS + _advice_instruction + E_INST
)

ADVICE_PROMPT = PromptTemplate.from_template(_advice_prompt)


SUMMARISE_PROMPT = PromptTemplate.from_template(
    """
Summarise the 

: {}
----------------------
ANSWER:
"""
)

document_retrieval_prompt = PromptTemplate.from_template(
    """
"""
)
