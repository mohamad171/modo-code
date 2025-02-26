from rest_framework import serializers
from project_app.models import Project
from ai.db_managers import Neo4jManager


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class SaveNodeAndRelationshipsSerializer(serializers.Serializer):
    nodes = serializers.ListField()
    relationships = serializers.ListField()
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.none())

    def __init__(self):
        super().__init__()
        user = self.context["request"].user
        self.fields['project'].queryset = Project.objects.filter(user=user).only("id")

    def create(self, validated_data):
        nodes = validated_data.get("nodes")
        relationships = validated_data.get("relationships")
        project = validated_data.get("project")
        neo_db = Neo4jManager(repoId=project.id,entityId=project.id)
        neo_db.save_graph(nodes, relationships)
        neo_db.close()
        return {"status": "ok"}

