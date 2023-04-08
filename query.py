import matplotlib.pyplot as plt
import networkx as nx

class Query:
	allqueries = []
	alltags = set()

	def __init__(self, id=None, title="unknown", tags=set()):
		self.id = id
		self.comments = []
		self.set_title(title)
		self.tags = set(tags)
		Query.alltags |= set(tags)
		Query.allqueries.append(self)

	def add_comment(self, comment):
		self.comments.append(comment.replace('"', "'"))
		
	def add_tags(self, tags):
		self.tags |= set(tags)
		Query.alltags |= set(tags)

	def get_id(self):
		return self.id

	def get_tag_length(self):
		return len(self.tags)
	
	def get_tags(self):
		return self.tags
	
	def set_id(self, id):
		self.id = id
	
	def set_title(self, title):
		self.title = title.replace('"', "'")
	
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
			print(f"ERROR: Failed to write '{output_filename}'")

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

				for t in sorted(Query.alltags):
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

	#Static methods
	def filter_queries(queries=allqueries, include=set(), exclude=set()):
		"""
		Parameters
		----------
		include : default = set()
			Select only queries which their tags is a superset of those in <include> set

		exclude : default = set()
			Select only queries which their tags aren't in <exclude> set

		Return
		------
			Filtered list of queries (must include all tags of <include> and none of tags from <exclude>)
		"""
		return [q for q in queries if include.issubset(q.tags) and len(exclude & q.tags) == 0]
	
	def get_queries_tags(queries):
		r = set()
		for q in queries:
			r |= q.tags
		return r

	def count_queries_tags(queries):
		r = dict()
		for q in queries:
			for t in q.tags:
				if t in r.keys():
					r[t] += 1
				else:
					r[t] = 1
		return r
	
	def appearance_matrix(queries=allqueries, remove=set()):
		"""
		Parameters
		----------
		queries : default = allqueries
			<allqueries> are all Query that has been initialized
			Calculate appearance using a list of queries

		remove : default = set()
			Remove from result a set of tags

		Return
		------
		[0] Matrix of appearance
		[1] List, tag order
		"""
		all_tags = set()
		
		for q in queries:
			all_tags |= q.tags

		#Remove unwanted tags
		all_tags -= remove

		#Sort set to always get the same result (see: hash function)
		l = sorted(list(all_tags))

		#Zero square matrix of size n, n = set cardinality
		matrix = [[0]*len(all_tags) for _ in range(len(all_tags))]

		indices = {l[i]:i for i in range(len(l))}
		for q in queries:
			lt = list(q.tags)
			for i in range(len(lt)):
				for j in range(i+1, len(lt)):
					if lt[i] in indices and lt[j] in indices:
						matrix[indices[lt[i]]][indices[lt[j]]] += 1
						matrix[indices[lt[j]]][indices[lt[i]]] += 1

		return matrix, l
	

	def get_queries_from_directory(path=".", prefix="NXQ_", suffix=".rq", start=1, end=9702):
		path = path.rstrip('/')
		queries = []

		for i in range(start,end+1):
			filename = f"{path}/{prefix}{i:05}{suffix}"

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
							queries[-1].add_tags(s)
							break
						elif line == '\n':
							break
			except IOError:
				pass
				#print(f"ERROR: Couldn't process {filename} successfully")
		return queries

if __name__ == "__main__":
	queries = Query.get_queries_from_directory("./nextprot-queries")
	tqueries = Query.filter_queries(queries, include={"tutorial"})

	tag_count = Query.count_queries_tags(queries)
	ttag_count = Query.count_queries_tags(tqueries)
	################ WRITE METADATAS ################
	
	import os

	os.mkdir("./metadatas")
	for q in queries:
		q.write_metadatas(f"./metadatas/{q.get_id()}.ttl")
	
	Query.write_allmetadatas("./allmetadatas.ttl")

	##################### RECAP #####################

	print(len(queries), "requêtes analysées")
	max_tag_len = 0
	for e in tag_count:
		if len(e) > max_tag_len:
			max_tag_len = len(e)
	
	max_ttag_len = 0
	for e in ttag_count:
		if len(e) > max_ttag_len:
			max_ttag_len = len(e)
	
	#Count tags appearance
	print("\n#NUMBER OF TAGS#".ljust(max_tag_len+1),":", len(tag_count))
	for n, t in sorted(((v,k) for k,v in tag_count.items()), reverse=True):
		print(t.ljust(max_tag_len),":", n)
	
	#Count tags appearance in tutorial tags
	print("\n#NUMBER OF TUTORIAL TAGS#".ljust(max_ttag_len+1),":", len(ttag_count)-1)
	for n, t in sorted(((v,k) for k,v in ttag_count.items()), reverse=True):
		if t != "tutorial":
			print(t.ljust(max_ttag_len),":", n)

	print("\nTags that aren't in tutorial queries:")
	print(tag_count.keys() - ttag_count.keys(), end="\n\n")

	################# HISTOGRAMS ####################

	figure = plt.figure()
	#Nb requete/tag
	a1 = figure.add_subplot(221)
	a1.hist(tag_count.values())
	a1.set_title("Nombre de requêtes par tag")

	#Nb tag/requete
	a2 = figure.add_subplot(222)
	a2.hist([q.get_tag_length() for q in queries])
	a2.set_title("Nombre de tags par requête")

	#Nb requete/tag (tutorial)
	a3 = figure.add_subplot(223)
	a3.hist(ttag_count.values())
	a3.set_title("Nombre de requêtes par tag (tutorial)")

	#Nb tag/requete (tutorial)
	a4 = figure.add_subplot(224)
	a4.hist([q.get_tag_length() for q in tqueries])
	a4.set_title("Nombre de tags par requête (tutorial)")

	plt.show()

	################## HEATMAP ######################

	#TODO: Hierarchical clustering from appearance 
	#TODO: Could normalize by dividing by self appearance in queries ( X /= tags["tag1"] * tags["tag2"] )

	#TODO: Check Tutorial, QC, ...
	matrix, matrixtags = Query.appearance_matrix()

	m = plt.matshow(matrix)
	m.axes.set_xticklabels(matrixtags, rotation = 90)
	m.axes.set_yticklabels(matrixtags)
	m.axes.set_xticks(range(len(matrixtags)))
	m.axes.set_yticks(range(len(matrixtags)))
	plt.gcf().canvas.manager.set_window_title("Matrice d'apparition")
	plt.show()
	
	from math import log
	#Logarithm approach to minimize high values (+1 for avoiding domain errors)
	logmatrix = [list(map(lambda i: log(i + 1), l)) for l in matrix]

	logm = plt.matshow(logmatrix)
	logm.axes.set_xticklabels(matrixtags, rotation = 90)
	logm.axes.set_yticklabels(matrixtags)
	logm.axes.set_xticks(range(len(matrixtags)))
	logm.axes.set_yticks(range(len(matrixtags)))

	plt.gcf().canvas.manager.set_window_title("Matrice d'apparition (log(x+1))")
	plt.show()

