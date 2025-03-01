from ai.db_managers import Neo4jManager



def get_nodes_for_embedding(manager: Neo4jManager):
    """
    Retrieve nodes and their relationships from the graph,
    and format them into a textual representation.
    """
    query = """
    MATCH (n {entityId: $entityId})
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN n.node_id AS node_id, n.name AS name, n.text AS text,
           collect({relationship: type(r), target: m.name}) AS relationships
    """
    results = manager.query(query, {"entityId": manager.entityId})
    nodes_text = []
    for record in results:
        text_rep = (
            f"ID: {record['node_id']}\n"
            f"Name: {record['name']}\n"
            f"Text: {record['text']}\n"
            f"Relationships: {record['relationships']}"
        )
        nodes_text.append({"node_id":record['node_id'],"text":text_rep})
    return nodes_text