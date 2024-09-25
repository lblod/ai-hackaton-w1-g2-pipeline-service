from string import Template
from helpers import query, update, generate_uuid
from escape_helpers import sparql_escape_uri, sparql_escape_datetime
from datetime import datetime
from flask import request, jsonify

from download_besluiten import process_aanduidingsobject_url
from extract_text import extract_text

@app.route("/hello")
def hello():
    return "Hello from the mu-python-template!"


@app.route("/extract", methods=["POST"])
def extract():
    data = request.get_json()
    aanduidingsobject = data.get("aanduidingsobject")
    # INSERT MAIN PIPELINE HERE
    pdf_bytes_buffers = process_aanduidingsobject_url(aanduidingsobject)
    for pdf_bytes in pdf_bytes_buffers:
        text = extract_text(pdf_bytes)

    # SAVE OUT IN DATABASE
    save_data(aanduidingsobject)

    return jsonify({}), 201


def save_data(aanduidingsobject):
    job_uuid = generate_uuid()
    job_uri = "http://data.lblod.info/hackton/g2/jobs/" + job_uuid
    created = datetime.now()

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
                 dct:created $created;
                 dct:source $aanduidingsobject;
                 adms:status "Finished";
                 task:operation <http://data.lblod.info/extract/toelatingsplichtigeHandelingen>.
          }
        }
        """)
    query_string = query_template.substitute(job=sparql_escape_uri(job_uri),
                                             created=sparql_escape_datetime(created),
                                             aanduidingsobject=sparql_escape_uri(aanduidingsobject)
                                             )

    print(query_string)
    query_result = update(query_string)
