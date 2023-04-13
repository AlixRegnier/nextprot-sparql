#Show that "PE" tag is always with "protein_existence" tag. 
#PE:                        11
#protein_existence:         18
#PE & protein_existence:    11
"""
print("PE:", tag_count["PE"])
print("protein_existence:", tag_count["protein_existence"])
hq = Query.filter_queries(queries, include={"PE", "protein_existence"})
print("PE and protein_existence:", len(hq),end="\n\n")
for q in hq:
    print(q)
"""


#Write table rows for LaTeX
#TODO: Should output in CSV format for LaTeX integration
"""
def dget(d, k):
    return d[k] if k in d else 0

with open("counts.txt", "w") as f:
    for _, t in sorted(((v,k) for k,v in tag_count.items()), reverse=True):
        f.write(f"{t.replace('_', ' ')} & {dget(tag_count, t)} & {dget(qctag_count, t)} & {dget(ttag_count, t)}\\\\\n")
"""


#Only one query tagged "Evidence" without "QC" tag
#tq = Query.filter_queries(queries, include={"evidence"}, exclude={"QC"})

#Bunch of queries that are quite interesting --> snorql-only
#tq = Query.filter_queries(queries, exclude={"QC", "tutorial"})

#Another subset of queries
#tq = Query.filter_queries(queries, exclude={"QC", "tutorial", "snorql-only", "federated_query"})
"""
print(len(tq))
for q in tq:
    print(q)
"""