import matplotlib.pyplot as plt
import networkx as nx

class Query:
	allqueries = []
	alltags = set()

	def __init__(self, id=None, title=None, tags=set()):
		self.id = id
		self.comments = []
		self.title = title
		self.tags = set(tags)
		Query.alltags |= tags
		Query.allqueries.append(self)

	def add_comment(self, comment):
		self.comments.append(comment.replace('"', "'"))
		
	def add_tags(self, tags):
		self.tags |= set(tags)

	def get_id(self):
		return self.id

	def get_tag_length(self):
		return len(self.tags)
	
	def get_tags(self):
		return self.tags
	
	def set_id(self, id):
		self.id = id
	
	def set_title(self, title):
		self.title = title
	
	def write_metadatas(self, output_filename):
		try:
			with open(output_filename, "w", encoding="utf-8") as f:
				f.write("""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX owl: <http://www.w3.org/2002/07/owl#> 
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 
PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 
PREFIX dct: <http://purl.org/dc/terms/> 

PREFIX nextprot: <http://nextprot.org/rdf#>
PREFIX : <http://nextprot.org/query/>\n\n""")
				f.write(f":{self.id} rdf:type :Query .\n")
				f.write(f":{self.id} rdfs:label \"{self.id}\" .\n")
				f.write(f":{self.id} dct:creator <https://www.nextprot.org> .\n")
				f.write(f":{self.id} rdfs:identifier \"{self.id}\" .\n")
				f.write(f":{self.id} dct:title \"{self.title}\" .\n")
				for c in self.comments:
					f.write(f":{self.id} rdfs:comment \"{c}\" .\n")
				for t in self.tags:
					f.write(f":{t} rdf:type :Tag .\n")
					f.write(f":{t} rdfs:label \"{t.replace('_', ' ')}\" .\n")
					f.write(f":{self.id} dct:subject :{t} .\n")
		except IOError:
			print("ERROR: Failed to write '{output_filename}'")

	def write_allmetadatas(output_filename):
		try:
			with open(output_filename, "w", encoding="utf-8") as f:
				f.write("""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX owl: <http://www.w3.org/2002/07/owl#> 
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 
PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 
PREFIX dct: <http://purl.org/dc/terms/> 

PREFIX nextprot: <http://nextprot.org/rdf#>
PREFIX : <http://nextprot.org/query/>\n\n""")

				for t in Query.alltags:
					f.write(f":{t} rdf:type :Tag .\n")
					f.write(f":{t} rdfs:label \"{t.replace('_', ' ')}\" .\n")

				for q in Query.allqueries:
					f.write(f":{q.id} rdf:type :Query .\n")
					f.write(f":{q.id} rdfs:label \"{q.id}\" .\n")
					f.write(f":{q.id} dct:creator <https://www.nextprot.org> .\n")
					f.write(f":{q.id} rdfs:identifier \"{q.id}\" .\n")
					f.write(f":{q.id} dct:title \"{q.title}\" .\n")
					for c in q.comments:
						f.write(f":{q.id} rdfs:comment \"{c}\" .\n")
					for t in q.tags:
						f.write(f":{q.id} dct:subject :{t} .\n")
		except IOError:
			print(f"ERROR: Failed to write '{output_filename}'")


	def __str__(self):
		return f"Id:\t{self.id}\nTitle:\t{self.title}\nTags:\t{self.tags}\n"


	#Static method
	def appearance_matrix(queries=allqueries, qinclude=set(), remove=set()):
		"""
		Parameters
		----------
		queries : default = allqueries
			<allqueries> are all Query that has been initialized
			Calculate appearance using a list of queries

		qinclude : default = set()
			Select only queries which their tags is a superset of those in qinclude

		remove : default = set()
			Remove from result a set of tags

		Return
		------

		[0] Matrix of appearance
		[1] List, tag order
		[2] Dict, tag index in [1]
		"""
		all_tags = set()
		qs = [q for q in queries if qinclude.issubset(q.tags)]

		for q in qs:
			all_tags |= q.get_tags()

		#Remove unwanted tags
		all_tags -= remove

		#Sort set to always get the same result (see: hash function)
		l = sorted(list(all_tags))

		#Zero square matrix of size n, n = set cardinality
		matrix = [[0]*len(all_tags) for _ in range(len(all_tags))]

		for i in range(len(l)):
			for j in range(i+1, len(l)): #Triangle
				for q in qs:
					if l[i] in q.get_tags() and l[j] in q.get_tags():
						matrix[i][j] += 1
				matrix[j][i] = matrix[i][j] #Complete matrix

		return matrix, l
	
def drawgraph(G):
	drawgraphs([G])

def drawgraphs(Gs):
	for i in range(len(Gs)):
		plt.subplot(221 + i)
		nx.draw(Gs[i], with_labels=True, font_weight='bold')
	plt.show()

def generate_gexf(queries):
	#Graph1: 
	# Sommet { Tag, Query } 
	# Edge   {Query -- Tag}
	g1 = nx.Graph()
	g1.add_nodes_from([q.get_id() for q in queries])
	g1.add_nodes_from(tags.keys())

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

	#For all queries
	queries = []
	tags = dict()
	#For queries tagged "tutorial"
	ttags = dict()
	tqueries = []
	
	for i in range(1,9702+1):
		filename = f"./nextprot-queries/NXQ_{i:05}.rq"

		try:
			with open(filename, "r", encoding="utf-8") as f:
				queries.append(Query())
				for line in f:
					if line[:4] == "#id:":
						queries[-1].set_id(line[4:-1])
					elif line[:7] == "#title:":
						queries[-1].set_title(line[7:-1])
					elif line[:9] == "#comment:":
						queries[-1].add_comment(line[9:-1])
					elif line[:6] == "#tags:":
						s = set(map(lambda s : s.strip().replace(' ', '_'), line[6:-1].split(',')))
						s.discard("")
						
						for e in s:
							if e in tags:
								tags[e] += 1
							else:
								tags[e] = 1
								
						if "tutorial" in s:
							tqueries.append(queries[-1])
							for e in s:
								if e in ttags:
									ttags[e] += 1
								else:
									ttags[e] = 1
							
						queries[-1].add_tags(s)
						break
					elif line == '\n':
						break
		except IOError:
			pass
			#print(f"ERROR: Couldn't process {filename} successfully")
			
	for q in queries:
		q.write_metadatas(f"./metadatas/{q.get_id()}.ttl")
	
	Query.write_allmetadatas("./allmetadatas.ttl")
	print(len(queries), "requêtes analysées")
	max_tag_len = 0
	for e in tags:
		if len(e) > max_tag_len:
			max_tag_len = len(e)
	
	max_ttag_len = 0
	for e in ttags:
		if len(e) > max_ttag_len:
			max_ttag_len = len(e)
	
	#Count tags appearance
	print("\n#NUMBER OF TAGS#".ljust(max_tag_len+1),":", len(tags))
	for n, t in sorted(((v,k) for k,v in tags.items()), reverse=True):
		print(t.ljust(max_tag_len),":", n)
	
	#Count tags appearance in tutorial tags
	print("\n#NUMBER OF TUTORIAL TAGS#".ljust(max_ttag_len+1),":", len(ttags)-1)
	for n, t in sorted(((v,k) for k,v in ttags.items()), reverse=True):
		if t != "tutorial":
			print(t.ljust(max_ttag_len),":", n)

	print("\nTags that aren't in tutorial queries:")
	print(tags.keys() - ttags.keys(),end="\n\n")


	figure = plt.figure()
	#Nb requete/tag
	a1 = figure.add_subplot(221)
	a1.hist(tags.values())
	a1.set_title("Nombre de requêtes par tag")

	#Nb tag/requete
	a2 = figure.add_subplot(222)
	a2.hist([q.get_tag_length() for q in queries])
	a2.set_title("Nombre de tags par requête")

	#Nb requete/tag (tutorial)
	a3 = figure.add_subplot(223)
	a3.hist(ttags.values())
	a3.set_title("Nombre de requêtes par tag (tutorial)")

	#Nb tag/requete (tutorial)
	a4 = figure.add_subplot(224)
	a4.hist([q.get_tag_length() for q in tqueries])
	a4.set_title("Nombre de tags par requête (tutorial)")

	plt.show()

	#TODO: CAH ? Group closer tags match
	matrix, matrixtags = Query.appearance_matrix(qinclude={"tutorial"}, remove={"QC", "evidence", "tutorial"})
	m = plt.matshow(matrix)
	m.axes.set_xticklabels(matrixtags)
	m.axes.set_yticklabels(matrixtags)
	m.axes.set_xticks(range(len(matrixtags)))
	m.axes.set_yticks(range(len(matrixtags)))
	
	plt.gcf().canvas.manager.set_window_title("Matrice d'apparition")
	plt.show()

	generate_gexf(queries)

