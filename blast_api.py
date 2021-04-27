from fastapi import FastAPI , HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from Bio.Blast.Applications import NcbiblastnCommandline, NcbiblastpCommandline
from Bio.Blast import NCBIXML, NCBIWWW
from io import StringIO
from pydantic import BaseModel
app = FastAPI ( debug=True , title="Chia DB", root_path="/blast" )  # debug will need to be changed to false

app.add_middleware (
    CORSMiddleware ,
    allow_origins=['*'] ,
    # this needs to be changed when moving to prod. it will need to be the ip address of the website
    allow_methods=['*'] ,
    allow_headers=['*'] ,  # probably needs to be changed also
    max_age=1
)

class BlastData(BaseModel):
    sequence: str
    expect_threshold: float
    max_alignments: int
    word_length: int

@app.get ( "/" )
def root() :
    return { "Status" : "Operational" }

@app.post("/blastn/")
def blastn(blast_data: BlastData):
    with open("temp.fa", "w+") as temp_file:
        temp_file.write(blast_data.sequence)
    blastn_cline = NcbiblastnCommandline(query= "temp.fa", db="chia_working_models", evalue=blast_data.expect_threshold, outfmt=5, word_size = blast_data.word_length, num_alignments = blast_data.max_alignments)
    stdout, sstderr = blastn_cline()
    blast_record = NCBIXML.read(StringIO(stdout))
    results = {"blast_results": []}
    for item in blast_record.alignments:
        temp_dict = {"hit": {"accession": item.hit_id, "length": item.length, "hsps": []}}
        for hsp in item.hsps:
            temp_dict["hit"]["hsps"].append({"score": hsp.score, "bits": hsp.bits, "expected": hsp.expect, "align_length": hsp.align_length,
                                             'query_seq': hsp.query, "query_start": hsp.query_start, "query_end": hsp.query_end,
                                             "subject_seq": hsp.sbjct, "sbjct_start": hsp.sbjct_start, "sbjct_end": hsp.sbjct_end, "match": hsp.match})
        results["blast_results"].append(temp_dict)
    return results


@app.post("/blastp/")
def blastp(blast_data: BlastData):
    with open("temp2.fa", "w+") as temp_file:
        temp_file.write(blast_data.sequence)
    blastn_cline = NcbiblastpCommandline(query= "temp2.fa", db="chia_pep", evalue=blast_data.expect_threshold, outfmt=5, word_size = blast_data.word_length, num_alignments = blast_data.max_alignments)
    stdout, sstderr = blastn_cline()
    blast_record = NCBIXML.read(StringIO(stdout))
    results = {"blast_results": []}
    for item in blast_record.alignments:
        temp_dict = {"hit": {"accession": item.hit_id, "length": item.length, "hsps": []}}
        for hsp in item.hsps:
            temp_dict["hit"]["hsps"].append({"score": hsp.score, "bits": hsp.bits, "expected": hsp.expect, "align_length": hsp.align_length,
                                             'query_seq': hsp.query, "query_start": hsp.query_start, "query_end": hsp.query_end,
                                             "subject_seq": hsp.sbjct, "sbjct_start": hsp.sbjct_start, "sbjct_end": hsp.sbjct_end, "match": hsp.match})
        results["blast_results"].append(temp_dict)
    return results
