import json
import os
import time

from rest_framework import serializers
from sentence_transformers import SentenceTransformer

from ai.db_managers.chroma_manager import ChromaManager
from ai.llm_manager.openai_manager import OpenAIManager
from ai.llm_manager.langchain_manager import Embedding
from ai.utils import get_nodes_for_embedding
from project_app.models import Project, Task
from ai.db_managers import Neo4jManager
from .tasks import run_task

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
        run_task.delay(task_type=0,
                       project_id=validated_data["project"].id,
                       nodes=nodes,
                       relationships=relationships
                       )



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
