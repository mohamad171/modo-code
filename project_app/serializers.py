import json

from rest_framework import serializers
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
        print(nodes,relationships)

        print(len(nodes),len(relationships))
        print(type(nodes),type(relationships))
        neo_db = Neo4jManager(repoId=project.id,entityId=project.id)
        neo_db.save_graph(nodes, relationships)
        neo_db.close()
        return {"status": "ok"}

