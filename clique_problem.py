import scipy.io as sio

y=sio.loadmat(r"D:\My Files\Documents\Vanderbilt Classes\CS 103\Twitter Project\mini_project.mat",
              struct_as_record=False,
              squeeze_me=True,
              )
flws = y['flws'].tolist()

# y=sio.loadmat(r"D:\My Files\Documents\Vanderbilt Classes\CS 103\Twitter Project\project.mat",
#               struct_as_record=False,
#               squeeze_me=True,
#               )
# flws = y['follows'].tolist()

import networkx as nx
DG= nx.DiGraph()
DG.add_edges_from(flws)
G=DG.to_undirected(reciprocal=True)
r1=nx.algorithms.clique.find_cliques(G)
r=list(r1)
# from networkx.algorithms import approximation
# r2=approximation.max_clique(G)

def makeGraph(flws):
    G={}
    for row in flws:
        a,b = row
        G.setdefault(a, set())
        G[a].add(b)
    
    for n in G:
        edges = G[n].copy()
        for e in edges:
            if e in G and n in G[e]:
                continue
            else:
                G[n].remove(e)
    return G

def isClique(G,nodes):
    return all(e in G[n] or e==n for n in nodes for e in nodes)


def prune(G,node):
    edges = G[node]
    for e in edges:
        G[e].remove(node)
    G.pop(node)



G=makeGraph(flws)
isClique(G, [2,893])
import copy
cliques = []
nodes = list(G.keys())
for node in nodes:
    stk = []
    edges = G[node].copy()
    dones = set()
    stk.append((node, edges, dones))
    while stk:
        node = stk[-1][0]
        edges = stk[-1][1]
        dones = stk[-1][2]
        if not edges:
            if not dones: #maximal
                c = [x[0] for x in stk]
                cliques.append(c)
            stk.pop()
            
        else:
            n = edges.pop()
            e = edges.intersection(G[n])
            dones.add(n)
            d = set()
            stk.append((n, e, d))

    
G=makeGraph(flws)
cliques = set(frozenset(x) for x in cliques)
r = set(frozenset(x) for x in r)
all(isClique(G,x) for x in cliques)
extras = cliques - r
for x in extras:
    supers = [s for s in cliques if x.issubset(s)]
    print(x, supers)

cliques={}
sz = 2
while len(G)>0:
    c = getClique(G,sz)
    cliques[sz]=c
    print(cliques)
    trim(G,sz)
    sz+=1
    
isClique(cliques[sz])

        

