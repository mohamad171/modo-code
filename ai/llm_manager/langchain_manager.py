from langchain.chains import LLMChain
from langchain_community.llms.cloudflare_workersai import CloudflareWorkersAI
from langchain_core.prompts import PromptTemplate
from langchain_community.embeddings.cloudflare_workersai import (
    CloudflareWorkersAIEmbeddings,
)


class ChatLLMManager:
    def __init__(self, account_id, api_token, prompt, model):
        self.prompt = PromptTemplate.from_template(prompt)
        self.llm = CloudflareWorkersAI(account_id=account_id, api_token=api_token, model=model)
        self.model = model


class EmbeddingManager:
    def __init__(self, account_id, api_token, model):
        self.embeddings = CloudflareWorkersAIEmbeddings(
            account_id=account_id,
            api_token=api_token,
            model_name=model,
        )
        self.model = model


class ChatLLM(ChatLLMManager):
    def __init__(self, account_id, api_token):
        prompt = f"""
            
            You are a knowledgeable assistant with deep understanding of a large codebase. The codebase is represented as a graph of nodes, where each node includes the following information:
            - **ID:** A unique identifier for the code component.
            - **Name:** The name of the function, class, or file.
            - **Text:** A code snippet or detailed description of the component.
            - **Relationships:** A list of related nodes (e.g., function calls, dependencies) and their types.
    
        """
        model = "@hf/google/gemma-7b-it"
        super().__init__(account_id, api_token, prompt, model)

    def ask(self, question, context):
        prompt_question = f"""Below are some context documents retrieved from the codebase that are relevant to the current question:
    
            {context}
    
            Using this context, please answer the following question. Provide a detailed explanation, including references to the specific code components if applicable.
            {question}
            """
        llm_chain = LLMChain(prompt=self.prompt, llm=self.llm)
        return llm_chain.run(prompt_question)


class Embedding(EmbeddingManager):
    def __init__(self, account_id, api_token):
        model = "@cf/baai/bge-large-en-v1.5"
        super().__init__(account_id, api_token, model)

    def embedded(self, query_text):
        print(query_text)
        return self.embeddings.embed_query(query_text)
