# set up - tested under es 7.2
from elasticsearch import Elasticsearch
from tika import parser
import json
es = Elasticsearch("localhost:9200")

es.indices.create(
    index='bookshelf',
    body={
        "settings": {
            "index": {
                "analysis": {
                    "analyzer": {
                        "my_analyzer": {
                            "type": "custom",
                            "tokenizer": "nori_tokenizer"
                        }
                    }
                }
            }
        }
    }
)

#bulk insert
parsed = parser.from_file('test.pdf', xmlContent=True)
paged = parsed["content"].split('<div class="page">')
body = ""
iPage = 1
for i in paged[1:-2]:
    body = body + json.dumps({"index": {"_index": "bookshelf", "_type": "bookshelf_datas"}}) + '\n'
    body = body + json.dumps({"title":"test.pdf", "page":iPage, "content":paged[iPage]}) + '\n'
    iPage = iPage + 1
es.bulk(body)

#delete all docs
es.delete_by_query(index='bookshelf', body={"query":{"match_all":{}}})
#search docs
docs = es.search(index='bookshelf', body={"query":{"multi_match":{"query": "Spam Filter", "fields":["content"]}}})
