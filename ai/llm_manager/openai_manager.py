from openai import OpenAI
import os

class OpenAIManager:
    def __init__(self, api_key,model_name="gpt-4o-mini",base_url=None):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        if base_url:
            self.client = OpenAI(api_key=api_key,base_url=base_url)

        self.model_name = model_name

    def ask_question(self,context,question):
        prompt = f"""
            
            You are a knowledgeable assistant with deep understanding of a large codebase. The codebase is represented as a graph of nodes, where each node includes the following information:
            - **ID:** A unique identifier for the code component.
            - **Name:** The name of the function, class, or file.
            - **Text:** A code snippet or detailed description of the component.
            - **Relationships:** A list of related nodes (e.g., function calls, dependencies) and their types.
    
            Below are some context documents retrieved from the codebase that are relevant to the current question:
    
            {context}
    
            Using this context, please answer the following question. Provide a detailed explanation, including references to the specific code components if applicable.
        """
        response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                stream=False
            )
        return response.choices[0].message.content

    def embededding(self,text):
        response = self.client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
        return response.data[0].embedding["data"][0]["embedding"]
