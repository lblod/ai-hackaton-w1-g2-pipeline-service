from string import Template
from helpers import query, update, generate_uuid
from escape_helpers import sparql_escape_uri, sparql_escape_datetime, sparql_escape_string
from datetime import datetime
from flask import request, jsonify

from download_besluiten import process_aanduidingsobject_url
from text_extractor import PlainTextExtractor
from actions_extractor import LLMActionsExtractor

import os

LLM_ENDPOINT = "http://ollama:11434"

if os.getenv('LLM_ENDPOINT'):
   LLM_ENDPOINT = os.getenv('LLM_ENDPOINT')

@app.route("/hello")
def hello():
    return "Hello from the mu-python-template!"


@app.route("/extract", methods=["POST"])
def extract():
    data = request.get_json()
    aanduidingsobject = data.get("aanduidingsobject")
    # INSERT MAIN PIPELINE HERE
    data = process_aanduidingsobject_url(aanduidingsobject)
    pdf_bytes_buffers = data["buffers"]
    besluit = data["meta"]["besluiten"][0]  #that's hard coded demo shit
    print("Extracted pdfs")
    text = PlainTextExtractor().extract_text(buffer=pdf_bytes_buffers[0])
    actions = LLMActionsExtractor(base_url = LLM_ENDPOINT).extract_actions(text=text)

    # SAVE OUT IN DATABASE
    save_data(aanduidingsobject, besluit)

    return jsonify({}), 201


def save_data(aanduidingsobject, besluit):
    job_uuid = generate_uuid()
    job_uri = "http://data.lblod.info/hackton/g2/jobs/" + job_uuid
    created = datetime.now()

    besluit_uuid = generate_uuid()
    aanduidingsobject_uuid = generate_uuid()

    query_template = Template("""
        PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX cogs: <http://vocab.deri.ie/cogs#>
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX adms: <http://www.w3.org/ns/adms#>
        PREFIX task: <http://redpencil.data.gift/vocabularies/tasks/>

        INSERT DATA {
          GRAPH <http://mu.semte.ch/graphs/public> {
               $job a cogs:Job;
                 mu:uuid $uuid;
                 dct:created $created;
                 dct:source $aanduidingsobject;
                 adms:status "Finished";
                 task:operation <http://data.lblod.info/extract/toelatingsplichtigeHandelingen>.


  $aanduidingsobject a <https://inventaris.onroerenderfgoed.be/Aanduidingsobject>;
    mu:uuid $aanduidingsobject_uuid;
    <https://inventaris.onroerenderfgoed.be/heeftBesluit>  $besluit.

  $besluit a <http://data.vlaanderen.be/ns/besluit#Besluit>;
    dcterms:title $besluit_titel ;
    mu:uuid $besluit_uuid;
    <https://id.erfgoed.net/vocab/ontology#dateBetekend> $besluit_date.

          }
        }
        """)
    query_string = query_template.substitute(job=sparql_escape_uri(job_uri),
                                             created=sparql_escape_datetime(created),
                                             aanduidingsobject=sparql_escape_uri(aanduidingsobject),
                                             uuid=sparql_escape_string(job_uuid),
                                             besluit=sparql_escape_uri(besluit["besluit_url"]),
                                             aanduidingsobject_uuid=sparql_escape_string(aanduidingsobject_uuid),
                                             besluit_uuid=sparql_escape_string(besluit_uuid),
                                             besluit_date=sparql_escape_datetime(besluit["besluit_date"]),
                                             besluit_titel=sparql_escape_string(besluit["besluit_titel"])
                                             )

    print(query_string)
    query_result = update(query_string)
