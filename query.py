import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform

class Query:
	def __init__(self, id=None, title="unknown", tags=set()):
		self.id = id
		self.comments = []
		self.set_title(title)
		self.tags = set(tags)

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

	def write_allmetadatas(queries, output_filename):
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

				for t in sorted(Query.get_queries_tags(queries)):
					f.write(f":{t} rdf:type :Tag .\n")
					f.write(f":{t} rdfs:label \"{t.replace('_', ' ')}\" .\n")

				for q in queries:
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
	def filter_queries(queries, include=set(), exclude=set()):
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
	
	def appearance_matrix(queries, remove=set(), applylog=True):
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
		
		#Logarithm normalize a bit datas
		if applylog:
			from math import log
			for i in range(len(matrix)):
				for j in range(i+1, len(matrix)):
					matrix[i][j] = matrix[j][i] = log(matrix[i][j]+1)

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
						if line.startswith("#id:"):
							queries[-1].set_id(line[len("#id:"):-1])
						elif line.startswith("#title:"):
							queries[-1].set_title(line[len("#title:"):-1])
						elif line.startswith("#comment:"):
							queries[-1].add_comment(line[len("#comment:"):-1])
						elif line.startswith("#tags:"):
							s = set(map(lambda s : s.strip().replace(' ', '_'), line[len("#tags:"):-1].split(',')))
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
	qcqueries = Query.filter_queries(queries, include={"QC"})

	tag_count = Query.count_queries_tags(queries)
	ttag_count = Query.count_queries_tags(tqueries)
	qctag_count = Query.count_queries_tags(qcqueries)

	################ WRITE METADATAS ################
	import os

	try:
		os.mkdir("./metadatas")
	except:
		pass

	for q in queries:
		q.write_metadatas(f"./metadatas/{q.get_id()}.ttl")
	
	Query.write_allmetadatas(queries, "./metadatas/allmetadatas.ttl")

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

	max_qctag_len = 0
	for e in qctag_count:
		if len(e) > max_qctag_len:
			max_qctag_len = len(e)
	
	#Count tags appearance
	print("\n#NUMBER OF TAGS#".ljust(max_tag_len+1),":", len(tag_count))
	for n, t in sorted(((v,k) for k,v in tag_count.items()), reverse=True):
		print(t.ljust(max_tag_len),":", n)

	#Count tags QC appearance
	print("\n#NUMBER OF QC TAGS#".ljust(max_qctag_len+1),":", len(qctag_count))
	for n, t in sorted(((v,k) for k,v in qctag_count.items()), reverse=True):
		print(t.ljust(max_qctag_len),":", n)
	
	#Count tags appearance in tutorial tags
	print("\n#NUMBER OF TUTORIAL TAGS#".ljust(max_ttag_len+1),":", len(ttag_count)-1)
	for n, t in sorted(((v,k) for k,v in ttag_count.items()), reverse=True):
		if t != "tutorial":
			print(t.ljust(max_ttag_len),":", n)

	print("\nTags that aren't in qc queries:")
	print(tag_count.keys() - qctag_count.keys(), end="\n\n")

	print("\nTags that aren't in tutorial queries:")
	print(tag_count.keys() - ttag_count.keys(), end="\n\n")

	################# HISTOGRAMS ####################

	try:
		os.mkdir("./output")
	except:
		pass

	figure = plt.figure(figsize=(15,8.5))
	grid = figure.add_gridspec(2,3)
	#Nb requete/tag
	a1 = figure.add_subplot(grid[0,0])
	a1.hist(tag_count.values())
	a1.set_title("Nombre de requêtes par tag")

	#Nb tag/requete
	a2 = figure.add_subplot(grid[1,0])
	a2.hist([q.get_tag_length() for q in queries])
	a2.set_title("Nombre de tags par requête")

	#Nb requete/tag (QC)
	a3 = figure.add_subplot(grid[0,1])
	a3.hist(qctag_count.values())
	a3.set_title("Nombre de requêtes par tag (QC)")

	#Nb tag/requete (QC)
	a4 = figure.add_subplot(grid[1,1])
	a4.hist([q.get_tag_length() for q in qcqueries])
	a4.set_title("Nombre de tags par requête (QC)")
	
	#Nb requete/tag (tutorial)
	a5 = figure.add_subplot(grid[0,2])
	a5.hist(ttag_count.values())
	a5.set_title("Nombre de requêtes par tag (tutorial)")

	#Nb tag/requete (tutorial)
	a6 = figure.add_subplot(grid[1,2])
	a6.hist([q.get_tag_length() for q in tqueries])
	a6.set_title("Nombre de tags par requête (tutorial)")
	
	plt.savefig("./output/histograms.png")
	plt.show()

	################## HEATMAP ######################

	#TODO: May normalize by dividing by self appearance in queries ? ( X /= tags["tag1"] * tags["tag2"] )
	matrix, matrixtags = Query.appearance_matrix(queries)
	m = plt.matshow(matrix)
	m.axes.set_xticklabels(matrixtags, rotation = 90)
	m.axes.set_yticklabels(matrixtags)
	m.axes.set_xticks(range(len(matrixtags)))
	m.axes.set_yticks(range(len(matrixtags)))
	plt.gcf().canvas.manager.set_window_title("Matrice d'apparition (log(x+1)")
	plt.gcf().set_size_inches(11,13)
	#plt.get_current_fig_manager().full_screen_toggle()
	plt.savefig("./output/heatmap.png")
	plt.show()
	
	def hierarchical_clustering_dendrogram(matrix, tags, title="", method="ward", save=True, output_filename="dendrogram.png"):
		dists = squareform(matrix)
		linkage_matrix = linkage(dists, method, optimal_ordering=True)
		dendrogram(linkage_matrix, labels=tags, orientation='left')
		plt.gcf().canvas.manager.set_window_title("Hierarchial clustering dendrogram from appearance matrix")
		plt.gcf().set_size_inches(15,10)
		plt.title(f"{title} ({method} linkage)")
		plt.savefig(output_filename)
		plt.show()

	#Dendrogram with no filters
	hierarchical_clustering_dendrogram(matrix, matrixtags, "All queries; all tags", output_filename="./output/dendrogram_allqueries_alltags.png")
	#Dendrogram with all queries and tags that are exclusive to qc queries
	hierarchical_clustering_dendrogram(*Query.appearance_matrix(queries, remove=(Query.get_queries_tags(queries) - Query.get_queries_tags(qcqueries)) | {"QC"}), "All queries; only tags that are exclusive to QC queries", output_filename="./output/dendrogram_allqueries_qctags.png")
	#Dendrogram with qc queries and tags that are exclusive to qc queries
	hierarchical_clustering_dendrogram(*Query.appearance_matrix(qcqueries, remove={"QC"}), "QC queries; without 'QC' tag", output_filename="./output/dendrogram_qcqueries_alltags.png")
	#Dendrogram with all queries and tags that are exclusive to tutorial queries
	hierarchical_clustering_dendrogram(*Query.appearance_matrix(queries, remove=(Query.get_queries_tags(queries) - Query.get_queries_tags(tqueries)) | {"tutorial"}), "All queries; only tags that are exclusive to tutorial queries", output_filename="./output/dendrogram_allqueries_tutotags.png")
	#Dendrogram with tutorial queries and tags that are exclusive to tutorial queries
	hierarchical_clustering_dendrogram(*Query.appearance_matrix(tqueries, remove={"tutorial"}), "Tutorial queries; without 'tutorial' tag", output_filename="./output/dendrogram_tutoqueries_alltags.png")

	################# CUSTOM CAH ####################
	
	class Node:
		def __init__(self, value=None, label="*", children=[]):
			self.value = value
			self.label = label
			self.children = children[:]
			self.calculate_value()
		
		def addChild(self, n):
			self.children.append(n)
			self.calculate_value()

		def addChildren(self, ns):
			self.children.extend(list(ns))
			self.calculate_value()

		def calculate_value(self):
			if len(self.children) > 0:
				self.value = [0]*len(self.children[0].value)
				for n in self.children:
					for i in range(len(self.value)):
						self.value[i] += n.value[i]

				for i in range(len(self.value)):
					self.value[i] /= len(self.children)

		def get_value(self):
			return self.value

		def get_children(self):
			return self.children
	
		def get_label(self):
			return self.label

		def set_label(self, label):
			self.label = label

		def toDot(self):
			g = f"\t\"{hex(id(self))}\"[label=\"{self.get_label()}\"]\n"
			if self.get_label() == "*":
				g += f"\t\"{hex(id(self))}\"[shape=point]\n"
				
			for e in self.get_children():
				g += f"\t\"{hex(id(self))}\" -- \"{hex(id(e))}\"\n" + e.toDot()
			return g

	def agglomerate1(matrix, matrixtags, output_filename):
		def distance(vect1, vect2):
			d = 0
			for i in range(len(vect1)):
				d += (vect1[i] - vect2[i]) ** 2
			return d

		acc = [Node(matrix[i][:], matrixtags[i]) for i in range(len(matrix))]

		while len(acc) > 1:
			dmin = { "dist": -1, "nodes": set() }
			for i in range(len(acc)):
				for j in range(i+1, len(acc)):
					d = distance(acc[i].get_value(), acc[j].get_value())
					if dmin["dist"] == -1 or d < dmin["dist"]:
						dmin = { "dist": d, "nodes": { acc[i], acc[j] } }
					elif d == dmin["dist"]:
						for node in dmin["nodes"]:
							if distance(acc[j].get_value(), node.get_value()) == d:
								dmin["nodes"].add(acc[j])
								break

			n = Node()
			n.addChildren(dmin["nodes"])
			for node in dmin["nodes"]:
				acc.remove(node)
			acc.append(n)

		with open(output_filename, "w", encoding="utf-8") as f:
			f.write("graph {\n" + acc[0].toDot() + "\n}")	
	
	#Create most possible couple of tags then link them with fictional nodes
	#Ref: WPGMA
	def agglomerate2(matrix, matrixtags, output_filename):
		def distance(vect1, vect2):
			d = 0
			for i in range(len(vect1)):
				d += (vect1[i] - vect2[i]) ** 2
			return d

		acc = [Node(matrix[i][:], matrixtags[i]) for i in range(len(matrix))]

		sn = []
		finalize = False
		while len(acc) > 1:
			dmin = { "dist": -1, "nodes": set() }
			for i in range(len(acc)):
				for j in range(i+1, len(acc)):
					d = distance(acc[i].get_value(), acc[j].get_value())
					if dmin["dist"] == -1 or d < dmin["dist"]:
						dmin = { "dist": d, "nodes": { acc[i], acc[j] } }
					elif d == dmin["dist"]:
						for node in dmin["nodes"]:
							if distance(acc[j].get_value(), node.get_value()) <= d and node != acc[j]:
								dmin["nodes"].add(acc[j])
								break

			n = Node()
			n.addChildren(dmin["nodes"])
			for node in dmin["nodes"]:
				acc.remove(node)	

			if len(acc) <= 1 and not finalize:
				finalize = True
				acc.extend(sn)
				sn.clear()

			if finalize:
				acc.append(n)
			else:
				sn.append(n)


		with open(output_filename, "w", encoding="utf-8") as f:
			f.write("graph {\n" + acc[0].toDot() + "\n}")	

	#TODO: Agglomerate without creating any chimeric nodes
	def agglomerate3(matrix, matrixtags, output_filename):
		pass

	#1 Chimeric nodes at each steps
	agglomerate1(matrix, matrixtags, "./output/allqueries_alltags.1.dot")
	agglomerate1(*Query.appearance_matrix(queries, remove=(Query.get_queries_tags(queries) - Query.get_queries_tags(qcqueries)) | {"QC"}), "./output/allqueries_qctags.1.dot")
	agglomerate1(*Query.appearance_matrix(qcqueries, remove={"QC"}), "./output/qcqueries_alltags.1.dot")
	agglomerate1(*Query.appearance_matrix(queries, remove=(Query.get_queries_tags(queries) - Query.get_queries_tags(tqueries)) | {"tutorial"}), "./output/allqueries_tutotags.1.dot")
	agglomerate1(*Query.appearance_matrix(tqueries, remove={"tutorial"}), "./output/tutoqueries_alltags.1.dot")

	#2 Most possible couples --> chimeric nodes
	agglomerate2(matrix, matrixtags, "./output/allqueries_alltags.2.dot")
	agglomerate2(*Query.appearance_matrix(queries, remove=(Query.get_queries_tags(queries) - Query.get_queries_tags(qcqueries)) | {"QC"}), "./output/allqueries_qctags.2.dot")
	agglomerate2(*Query.appearance_matrix(qcqueries, remove={"QC"}), "./output/qcqueries_alltags.2.dot")
	agglomerate2(*Query.appearance_matrix(queries, remove=(Query.get_queries_tags(queries) - Query.get_queries_tags(tqueries)) | {"tutorial"}), "./output/allqueries_tutotags.2.dot")
	agglomerate2(*Query.appearance_matrix(tqueries, remove={"tutorial"}), "./output/tutoqueries_alltags.2.dot")
			