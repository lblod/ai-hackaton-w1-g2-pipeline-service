from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import NamespaceManager, DC, DCTERMS, FOAF, XSD, SKOS, RDFS, RDF

from actions_extractor.models import ActionFragment

# Lookup object for MeasureTypeUri
measure_type_lookup = {
  'NeedsPermit' : URIRef('http://mu.semte.ch/vocabularies/ext/maatregeltypes/1'),
  'AllowedWithoutPermit' : URIRef('http://mu.semte.ch/vocabularies/ext/maatregeltypes/2'),
  'Forbidden' : URIRef('http://mu.semte.ch/vocabularies/ext/maatregeltypes/3')
}


def convert_fragments_to_graph(fragments: list[ActionFragment], aanduidingsobjecturi: str, besluituri: str, besluitpdfuri: str) -> Graph:
    # Create an RDF graph
    graph = Graph()

    # Define the namespaces
    OA = Namespace('http://www.w3.org/ns/oa#')
    MU = Namespace('http://mu.semte.ch/vocabularies/core/')
    SRO = Namespace('https://data.vlaanderen.be/ns/slimmeraadpleegomgeving#')
    PROV = Namespace('http://www.w3.org/ns/prov#')
    ERFGOED = Namespace('https://id.erfgoed.net/vocab/ontology#')
    BESLUIT = Namespace('http://data.vlaanderen.be/ns/besluit#')
    EXT = Namespace('http://mu.semte.ch/vocabularies/ext/')
    AS = Namespace('https://www.w3.org/ns/activitystreams#')
    BIBO = Namespace('http://purl.org/ontology/bibo/')

    prefixes = NamespaceManager(Graph())
    prefixes.bind('oa', OA)
    prefixes.bind('mu', MU)
    prefixes.bind('sro', SRO)
    prefixes.bind('prov', PROV)
    prefixes.bind('erfgoed', ERFGOED)
    prefixes.bind('besluit', BESLUIT)

    # Iterate over the dataframe rows
    for index, fragment in enumerate(fragments):
        # Create URIs and literals
        aanduidings_object = URIRef(aanduidingsobjecturi)
        besluit = URIRef(besluituri)
        besluit_file = URIRef(besluitpdfuri)
        text_fragment = Literal(fragment.text_fragment)
        text_fragment_prefix = Literal("") # We don't have prefix extracted
        text_fragment_suffix = Literal("") # We don't have suffix extracted
        annotation = URIRef(f'/annotation/{index}',base=besluit_file)
        measure = URIRef(f'/measure/{index}',base=annotation)
        annotation_activity = URIRef(f'/annotation-activity/{index}',base=besluit_file)
        text_fragment_selector = URIRef(f'/text-fragment-selector/{index}',base=besluit_file)
        measure_type = measure_type_lookup.get(str(fragment.measure_type).lower(), measure_type_lookup['NeedsPermit']) # check whether this is a sensible default

        hackathon_ai_actor = URIRef('http://example/com/actor/hackathon-oe-ai')


        # Fetch decisions the data provide by OE
        oe_decision = Graph().parse(besluit, format='turtle')

        # skolemnize and replace aanduidingsobjectURI
        oe_decision = oe_decision.skolemize()
        oe_decision.update(f"""
        PREFIX erfgoed: <https://id.erfgoed.net/vocab/ontology#>
        DELETE {{
        ?s erfgoed:besluit_handeltOver ?bn.
        ?bn ?p ?o.
        }}
        INSERT {{
        ?s erfgoed:besluit_handeltOver {aanduidings_object.n3()}.
        {aanduidings_object.n3()} ?p ?o.
        }}
        WHERE {{
        ?s erfgoed:besluit_handeltOver ?bn.
        ?bn ?p ?o.
        }}
        """)

        graph += oe_decision

        # Add to the graph
        graph.add((besluit, ERFGOED.hasAnnotation, annotation))

        graph.add((annotation, RDF.type, OA.Annotation))
        graph.add((annotation, OA.hasTarget, measure))

        graph.add((measure, RDF.type, OA.SpecificResource))
        graph.add((measure, RDF.type, EXT.erfgoedProtectiveMeasure))
        graph.add((measure, OA.hasSource, besluit_file))
        graph.add((measure, OA.hasSelector, text_fragment_selector))
        graph.add((measure, EXT.erfgoedhasMeasureType, measure_type))

        graph.add((text_fragment_selector, RDF.type, OA.TextQuoteSelector))
        graph.add((text_fragment_selector, OA.prefix, text_fragment_prefix))
        graph.add((text_fragment_selector, OA.exact, text_fragment))
        graph.add((text_fragment_selector, OA.suffix, text_fragment_suffix))

        graph.add((annotation_activity, RDF.type, PROV.Activity))
        graph.add((annotation_activity, RDF.type, AS.Create))
        graph.add((annotation_activity, PROV.wasAssociatedWith, hackathon_ai_actor))
        graph.add((annotation_activity, SRO.Activiteit_genereertAnnotatie, annotation))

    prefixes = NamespaceManager(graph)
    prefixes.bind('oa', OA)
    prefixes.bind('mu', MU)
    prefixes.bind('sro', SRO)
    prefixes.bind('prov', PROV)
    prefixes.bind('erfgoed', ERFGOED)
    prefixes.bind('besluit', BESLUIT)
    prefixes.bind('ext', EXT)
    prefixes.bind('as', AS)
    prefixes.bind('bibo', BIBO)

    # Print the RDF graph
    print(graph.serialize(format='turtle'))

    # Write the RDF graph to a file
    # graph.serialize(format='turtle', destination='output.ttl')
    return graph.serialize(format='nt')
