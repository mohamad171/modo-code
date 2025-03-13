from modo_code.celery import app as celery_app
from project_app.models import Task, Project
import json
from ai.db_managers import Neo4jManager
from ai.utils import get_nodes_for_embedding
from ai.db_managers.chroma_manager import ChromaManager
from ai.llm_manager.openai_manager import OpenAIManager
from ai.llm_manager.langchain_manager import Embedding
import os
import time

@celery_app.task(bind=True)
def run_task(self,**kwargs):
    task_type = kwargs["task_type"]
    project_id = kwargs["project_id"]
    project = Project.objects.filter(id=project_id).first()
    task = Task.objects.create(task_type=task_type,project=project)
    if task_type == Task.TaskTypeChoices.BUILD_GRAPH:
        task.task_status = Task.TaskStatusChoices.DOING
        task.save()

        # try:
        nodes = kwargs["nodes"]
        relationships = kwargs["relationships"]

        nodes = json.loads(nodes)
        relationships = json.loads(relationships)
        neo_db = Neo4jManager(repoId=str(project.id), entityId=str(project.id))
        neo_db.save_graph(nodes, relationships)
        neo_db.close()

        result = get_nodes_for_embedding(neo_db)
        text_data = []
        chunk_size = 100
        chunked_embeddings = []
        for i in result:
            text_data.append(i["text"])

        for j in range(0, len(text_data), chunk_size):
            chunk = text_data[j:j + chunk_size]
            for text in chunk:
                embedding = Embedding(account_id=os.getenv("CLOUDFLARE_ACCOUNT_ID"),
                                      api_token=os.getenv("CLOUDFLARE_API_TOKEN")).embedded(text)
                chunked_embeddings.append(embedding)
                time.sleep(0.3)

        ids = [item["node_id"] for item in result]
        chroma = ChromaManager(project.id)

        for j in range(0, len(text_data), chunk_size):
            chunk_text = text_data[j:j + chunk_size]
            chunk_ids = ids[j:j + chunk_size]
            chunk_embeddings = chunked_embeddings[j:j + chunk_size]

            chroma.save_graph(chunk_text, chunk_embeddings, chunk_ids)
        task.task_status = Task.TaskStatusChoices.DONE
        task.save()
        # except Exception as ex:
        #     print(e)
        #     task.task_status = Task.TaskStatusChoices.ERROR
        #     task.error_text = str(ex)
        #     task.save()


