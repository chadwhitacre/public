import rdflib
import sys


store = rdflib.Graph("Sleepycat")
store.open('../')


# clean out the store
for statement in tuple(store.triples((None,)*3)):
    store.remove(statement)

# Bind a few prefix, namespace pairs.
store.bind("dc", "http://http://purl.org/dc/elements/1.1/")
store.bind("foaf", "http://xmlns.com/foaf/0.1/")
store.bind("foo", "http://foo/")

# Create a namespace object for the Friend of a friend namespace.
FOAF = rdflib.Namespace("http://xmlns.com/foaf/0.1/")

# clean out the store
for statement in tuple(store.triples((None,)*3)):
    store.remove(statement)

# Create an identifier to use as the subject for Donna.
whit537 = rdflib.URIRef("whit537")
eikeon = rdflib.URIRef("eikeon")
chimezie = rdflib.URIRef("chimezie")
michel = rdflib.URIRef("michel")

isA = rdflib.URIRef("http://foo/isA")

# Add triples using store's add method.
from random import choice
options = ('goon', 'cow', 'alligator', 'bard', 'minstrel')
for person in (whit537, eikeon, chimezie, michel):
    x = rdflib.Literal(choice(options))
    store.add((person, isA, x))

sys.stdout.write("goons: ")
for subject in store.subjects(isA, rdflib.Literal('goon')):
    sys.stdout.write(subject + ' ')
print


s = None
p = None
o = None
out = rdflib.Graph("Memory")
for statement in store.triples((s,p,o)):
    print statement
    out.add(statement)

print out.serialize()
print store.serialize()


#import code; code.interact(local=locals())

out.close()
store.close()