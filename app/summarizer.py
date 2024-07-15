import json

from llm import LLMModel


SYS_PROMPT = """As a Competitor Analyst, your task is to analyze the homepage content of our competitor. 
    The text below is the contents extracted from their homepage. 
    Summarize the content without adding any comments or remakrs 
    and produce following JSON output: 
    {{"summary": <results - range: 150-{num_words} words>}}"""


class Summarizer:
    def __init__(self, llm_model: LLMModel, nwords=400) -> None:
        self.sys_prompt = SYS_PROMPT.format(num_words=nwords)
        self.llm_model = llm_model

    def summarize(self, content, max_tokens=1200):
        response = self.llm_model.chat(content, self.sys_prompt, 
                                       max_tokens, 0.)

        res = response.choices[0].message.content
        # Remove the newline character and the end-of-text identifier
        res = res.strip().replace("<|eot_id|>", "").lower()
        res = res.replace('\n', '')

        idx_start = res.find('{')
        idx_end = res.rfind('}')
        res = res[idx_start:idx_end+1]

        # Parse the JSON string
        res = json.loads(res)
        return res['summary']