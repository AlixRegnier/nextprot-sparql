from query import Query
import networkx as nx
import matplotlib.pyplot as plt

def drawgraph(G):
	drawgraphs([G])

def drawgraphs(Gs):
	for i in range(len(Gs)):
		plt.subplot(221 + i)
		nx.draw(Gs[i], with_labels=True, font_weight='bold')
	plt.show()

def generate_gexf(queries):
	
	tags = Query.get_queries_tags(queries)
	#Graph1: 
	# Sommet { Tag, Query } 
	# Edge   {Query -> Tag}
	g1 = nx.DiGraph()
	g1.add_nodes_from([q.get_id() for q in queries])
	g1.add_nodes_from(tags)

	for q in queries:
		for tag in q.get_tags():
			g1.add_edge(q.get_id(), tag)

	print("Generating g1.gexf...")
	#drawgraph(g1)
	nx.write_gexf(g1, "g1.gexf")

	#Graph2:
	# Sommet { Tag }
	# Edge   { Tag -- Tag } (at least a query using both) [weight=the number of queries using both]
	matrix, matrixtags = Query.appearance_matrix()

	g2 = nx.Graph()
	g2.add_nodes_from(tags.keys())
	for i in range(len(matrixtags)):
		for j in range(i+1, len(matrixtags)):
			if matrix[i][j] > 0:
				g2.add_edge(matrixtags[i], matrixtags[j], weight=matrix[i][j])

	print("Generating g2.gexf...")
	#drawgraph(g2)
	nx.write_gexf(g2, "g2.gexf")
	
	#Graph3:
	# Sommet { Query }
	# Edge   { Query -- Query } (at least sharing a tag) [weight=the number of shared tags]
	g3 = nx.Graph()
	g3.add_nodes_from([q.get_id() for q in queries])
	for i in range(len(queries)):
		for j in range(i+1, len(queries)):
			len_inter = len(queries[i].get_tags() & queries[j].get_tags()) #Intersection
			if len_inter > 0:
				g3.add_edge(queries[i].get_id(), queries[j].get_id(), weight=len_inter)
	
	print("Generating g3.gexf...")
	#drawgraph(g3)
	nx.write_gexf(g3, "g3.gexf")

if __name__ == "__main__":
	queries = Query.get_queries_from_directory("./nextprot-queries")
	generate_gexf(queries)