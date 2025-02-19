from graph_construction.core.graph_builder import GraphConstructor
import uuid
import os
from db_managers import Neo4jManager

os.environ["NEO4J_URI"] = "neo4j+s://172.187.208.104:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "Fax159159"
# os.environ["OPENAI_API_KEY"] = "sk-..."

repoId = str(uuid.uuid4())
entityId = str(uuid.uuid4())
graph_manager = Neo4jManager(repoId, entityId)

graph_manager = Neo4jManager(repoId, entityId)

try:
    graph_constructor = GraphConstructor(entityId,"example/blar-example-repos")
    nodes, relationships = graph_constructor.build_graph()
    graph_manager.save_graph(nodes, relationships)
    graph_manager.close()
except Exception as e:
    print(e)
    graph_manager.close()

