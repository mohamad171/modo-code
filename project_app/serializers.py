import json
import os

from rest_framework import serializers
from sentence_transformers import SentenceTransformer

from ai.db_managers.chroma_manager import ChromaManager
from ai.llm_manager.openai_manager import OpenAIManager
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
        neo_db = Neo4jManager(repoId=project.id,entityId=project.id)
        neo_db.save_graph(nodes, relationships)
        neo_db.close()

        #TODO this task should run on celery | add status to project model
        result = get_nodes_for_embedding(neo_db)
        text_data = []
        for i in result:
            text_data.append(i["text"])
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        embeddings = model.encode(text_data)
        ids = [item["node_id"] for item in result]
        chroma = ChromaManager(project.id)
        chroma.save_graph(text_data,embeddings,ids)



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
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        query_embedding = model.encode([question]).tolist()
        results = ChromaManager(project.id).query(query_embedding)
        context_data = ""
        for doc in results['documents'][0]:
            context_data += f"{doc}\n"
        llm = OpenAIManager(api_key=os.getenv("OPENAI_API_KEY"), model_name="gpt-4o-mini")
        result = llm.ask_question(context=context_data, question=question)

        return result