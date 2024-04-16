from langchain.prompts.prompt import PromptTemplate

B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"

_advice_system_prompt = """

"""
_advice_instruction = """
=== JOB DESCRIPTION ===                                           
{job_description}
=== DIVERSITY ===
{context}
=======
Question: Can you suggest improvements for the above job description in regards to, {advice}.
=======
Answer:
"""


_advice_prompt = (
    B_INST + B_SYS + _advice_system_prompt + E_SYS + _advice_instruction + E_INST
)

ADVICE_PROMPT = PromptTemplate.from_template(_advice_prompt)


SUMMARISE_PROMPT = PromptTemplate.from_template(
    """
Summarise the job description after 'Job Description:' to which type of job the description matches

Job Description: {job_description}
----------------------
ANSWER:
"""
)

document_retrieval_prompt = PromptTemplate.from_template(
    """
"""
)

