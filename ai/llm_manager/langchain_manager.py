from langchain.chains import LLMChain
from langchain_community.llms.cloudflare_workersai import CloudflareWorkersAI
from langchain_core.prompts import PromptTemplate

class LLMManager:
    def __init__(self, account_id,api_token,prompt):
        self.prompt = PromptTemplate.from_template(prompt)
        self.llm = CloudflareWorkersAI(account_id=account_id, api_token=api_token)



class ChatLLM(LLMManager):
    def __init__(self, account_id,api_token,prompt):
        super().__init__(account_id,api_token,prompt)


    def ask(self,question):
        llm_chain = LLMChain(prompt=self.prompt, llm=self.llm)
        return llm_chain.run(question)

