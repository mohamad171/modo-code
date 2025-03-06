import json
import os

from rest_framework import serializers
from sentence_transformers import SentenceTransformer

from ai.db_managers.chroma_manager import ChromaManager
from ai.llm_manager.openai_manager import OpenAIManager
from ai.llm_manager.langchain_manager import Embedding
from ai.utils import get_nodes_for_embedding
from project_app.models import Project
from ai.db_managers import Neo4jManager


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ["user"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        validated_data["ignores"] = ".env,.git,.idea,__pycache__,.vscode,venv"
        return Project.objects.create(**validated_data)


class SaveNodeAndRelationshipsSerializer(serializers.Serializer):
    nodes = serializers.CharField()
    relationships = serializers.CharField()
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = kwargs["context"]["request"].user
        self.fields['project'].queryset = Project.objects.filter(user=user).only("id")

    def create(self, validated_data):
        nodes = validated_data.get("nodes")
        relationships = validated_data.get("relationships")

        nodes = json.loads(nodes)
        relationships = json.loads(relationships)
        project = validated_data.get("project")
        neo_db = Neo4jManager(repoId=project.id, entityId=project.id)
        neo_db.save_graph(nodes, relationships)
        neo_db.close()

        # TODO this task should run on celery | add status to project model
        result = get_nodes_for_embedding(neo_db)
        text_data = []
        chunk_size = 10
        chunked_embeddings = []
        for i in result:
            text_data.append(i["text"])

        # Process texts in chunks
        for j in range(0, len(text_data), chunk_size):
            chunk = text_data[j:j + chunk_size]
            for text in chunk:
                embedding = Embedding(account_id=os.getenv("CLOUDFLARE_ACCOUNT_ID"),
                                      api_token=os.getenv("CLOUDFLARE_API_TOKEN")).embedded(text)
                chunked_embeddings.append(embedding)

        ids = [item["node_id"] for item in result]
        chroma = ChromaManager(project.id)

        for j in range(0, len(text_data), chunk_size):
            chunk_text = text_data[j:j + chunk_size]
            chunk_ids = ids[j:j + chunk_size]
            chunk_embeddings = chunked_embeddings[j:j + chunk_size]

            chroma.save_graph(chunk_text, chunk_embeddings, chunk_ids)

        return {"status": "ok"}


class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField()
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = kwargs["context"]["request"].user
        self.fields['project'].queryset = Project.objects.filter(user=user).only("id")

    def create(self, validated_data):
        question = validated_data.get("question")
        project = validated_data.get("project")
        query_embedding = Embedding(account_id=os.getenv("CLOUDFLARE_ACCOUNT_ID"),
                                    api_token=os.getenv("CLOUDFLARE_API_TOKEN")).embedded(question)
        results = ChromaManager(project.id).query(query_embedding)
        context_data = ""
        for doc in results['documents'][0]:
            context_data += f"{doc}\n"
        llm = OpenAIManager(api_key=os.getenv("OPENAI_API_KEY"), model_name="gpt-4o-mini")
        result = llm.ask_question(context=context_data, question=question)

        return result
