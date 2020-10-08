from fastapi import FastAPI , HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pymongo , re , datetime, gridfs
from utility import get_ssr

# get the client
client = pymongo.MongoClient ( )
# connect to the genes collection in the chia database
db = client.chia

app = FastAPI ( debug=True , title="Chia DB" )  # debug will need to be changed to false

app.add_middleware (
    CORSMiddleware ,
    allow_origins=['*'] ,
    # this needs to be changed when moving to prod. it will need to be the ip address of the website
    allow_methods=['*'] ,
    allow_headers=['*'] ,  # probably needs to be changed also
    max_age=1
)


@app.get ( "/" )
def root() :
    return { "Status" : "Operational" }


@app.get ( "/id/{transcript_id}" )
def get_id(transcript_id: str) :
    try :
        item_id = transcript_id.rstrip ( )
        if re.match ( r"^Salhi[.]\d{2}G\d{6}[.]\d{1,2}$" , item_id ) : # if item_id is a transcript id
            model = db.genes.find_one ( { "transcript_id" : item_id } , { "_id" : 0 } )
            alt_splices = db.genes.find ( { "gene_id" : model ["gene_id"] ,
                                            "transcript_id" : { "$not" : { "$regex" : item_id } } } ,
                                          { "_id" : 0 , "transcript_id" : 1 } )
            model ["alt_splices"] = []
            [model ["alt_splices"].append ( splice ["transcript_id"] ) for splice in alt_splices]

        elif re.match ( r"^Salhi[.]\d{2}G\d{6}$" , item_id ) : # if item_id is a gene name and is in hc, finds the rep model
            model = db.genes.find_one ( { "gene_id" : item_id , "is_repr" : 1 } , { "_id" : 0 })
            alt_splices = db.genes.find ( { "gene_id" : model ["gene_id"] , "is_repr" : 0 ,
                                            "transcript_id" : { "$not" : { "$regex" : model["transcript_id"] } } } ,
                                          { "_id" : 0 , "transcript_id" : 1 } )
            model["alt_splices"] = []
            [model ["alt_splices"].append ( splice ["transcript_id"] ) for splice in alt_splices]

        else :
            raise HTTPException ( status_code=404 , detail="bad id" )
        get_ssr(db, model)
        return model
    except TypeError : # if item_id is a gene name and is not hc, picks the first model
        model = db.genes.find_one ( { "gene_id" : item_id } , { "_id" : 0 })
        alt_splices = db.genes.find ( { "gene_id" : model ["gene_id"] ,
                                        "transcript_id" : {
                                            "$not" : { "$regex" :  model["transcript_id"]} } } ,
                                      { "_id" : 0 , "transcript_id" : 1 } )

        model ["alt_splices"] = []
        [model ["alt_splices"].append ( splice ["transcript_id"] ) for splice in alt_splices]
        get_ssr(db, model)
        return model

@app.get("/interpro/{keyword}-{type}")
def get_interpro(keyword: str, type: str):
    keyword = keyword.rstrip()
    try:
        if type == "keyword":
            models = db.genes.aggregate ( [
                { "$match" : { "$expr" : { "regexMatch" : { "input" : "$model_iprscan.method_description" , "regex" : keyword } } } } ,
                { "$project" : { "transcript_id" : 1 , "_id" : 0 , "model_iprscan" : {
                    "$filter" : { "input" : "$model_iprscan" , "as" : "ipr" ,
                                  "cond" : { "$regexMatch" : { "input" : "$$ipr.method_description" , "regex" : keyword } } } } } } ,
                { "$match" : { "model_iprscan" : { "$elemMatch" : { "$exists" : True } } } }
            ] )
            return { "IPR scan results" : list ( models ) }
        elif type == "id":
            print(keyword)
            models = db.genes.aggregate ( [
                { "$match" : { "$expr" : { "regexMatch" : { "input" : "$model_iprscan.interpro_accession" , "regex" : keyword } } } } ,
                { "$project" : { "transcript_id" : 1 , "_id" : 0 , "model_iprscan" : {
                    "$filter" : { "input" : "$model_iprscan" , "as" : "ipr" , "cond" : {
                        "$regexMatch" : { "input" : "$$ipr.interpro_accession" , "regex" : keyword } } } } } } ,
                { "$match" : { "model_iprscan" : { "$elemMatch" : { "$exists" : True } } } }
            ] )
            return { "IPR scan results" : list(models) }
        else:
            raise TypeError
    except TypeError:
        raise HTTPException ( status_code=404 , detail="bad keyword/id" )

@app.get("/go/{keyword}-{type}")
def get_go(keyword: str, type: str):
    keyword = keyword.rstrip()
    try:
        if type == "keyword":
            models = db.genes.aggregate ( [
                { "$match" : { "$expr" : { "regexMatch" : { "input" : "$model_go.go_name" , "regex" : keyword } } } } ,
                { "$project" : { "transcript_id" : 1 , "_id" : 0 , "model_go" : {
                    "$filter" : { "input" : "$model_go" , "as" : "go" ,
                                  "cond" : { "$regexMatch" : { "input" : "$$go.go_name" , "regex" : keyword } } } } } } ,
                { "$match" : { "model_go" : { "$elemMatch" : { "$exists" : True } } } }
            ] )
            return { "GO_results" : list ( models ) }
        elif type == "id":
            models = db.genes.aggregate ( [
                { "$match" : { "$expr" : { "regexMatch" : { "input" : "$model_go.go_accession" , "regex" : keyword } } } } ,
                { "$project" : { "transcript_id" : 1 , "_id" : 0 , "model_go" : {
                    "$filter" : { "input" : "$model_go" , "as" : "go" , "cond" : {
                        "$regexMatch" : { "input" : "$$go.go_accession" , "regex" : keyword } } } } } } ,
                { "$match" : { "model_go" : { "$elemMatch" : { "$exists" : True } } } }
            ] )
            return { "GO_results" : list(models) }
        else:
            raise TypeError
    except TypeError:
        raise HTTPException ( status_code=404 , detail="bad keyword/id" )

@app.get("/func_anno/{keyword}")
def get_func_anno(keyword: str):
    keyword = keyword.rstrip()
    models = db.genes.find({"func_anno": {"$regex": keyword}}, {"_id": 0, "transcript_id": 1, "func_anno": 1})
    return list(models)

@app.get("/seq/{transcript_id}-{type}")
def get_seq(transcript_id: str, type: str):
    try:
        if type == "cds" or type == "cdna" or type == "protein":
            if re.match ( r"^Salhi[.]\d{2}G\d{6}[.]\d{1,2}$" , transcript_id ):
                model = db.genes.find_one({"transcript_id": transcript_id}, {"_id": 0, "transcript_id": 1, type : 1})
                return model
            elif re.match ( r"^Salhi[.]\d{2}G\d{6}$" , transcript_id ):
                rep_model = db.genes.find_one({"gene_id": transcript_id, "is_repr": 1}, {"_id": 0, "transcript_id": 1, type: 1})
                if not rep_model:
                    rep_model = db.genes.find_one({"gene_id": transcript_id}, {"_id": 0, "transcript_id": 1, type: 1})
                return rep_model
            else:
                raise TypeError
        else:
            raise TypeError
    except TypeError:
        raise HTTPException ( status_code=404 , detail="bad keyword/id" )

@app.get("/seq_chr/{chr}-{start}-{stop}")
def get_seq_chr(chr: str, start: int, stop: int):
    try:
        fs = gridfs.GridFS(db)
        header = ">" + chr + " " + str(start) + "-" + str(stop)
        file = db.fs.files.find_one({"filename": chr})
        with fs.get(file["_id"]) as fp_read:
            result = fp_read.read()
            result = result.decode()
            if stop > (len(result)) or start > stop:
                raise TypeError
            else:
                return {"header":header, "sequence": result[start - 1: stop-1]}
    except TypeError:
        raise HTTPException ( status_code=404 , detail="bad keyword/id" )

@app.get("/seq_stream/{bp}-{type}-{transcript_id}")
def seq_stream(bp: int, type: str, transcript_id: str):
    try:
        if re.match ( r"^Salhi[.]\d{2}G\d{6}[.]\d{1,2}$" , transcript_id ) :
            model = db.genes.find_one ( { "transcript_id" : transcript_id } ,
                                        { "_id" : 0 , "transcript_id" : 1 , "start": 1, "stop": 1, "scaffold": 1} )
        elif re.match ( r"^Salhi[.]\d{2}G\d{6}$" , transcript_id ) :
            model = db.genes.find_one ( { "gene_id" : transcript_id , "is_repr" : 1 } ,
                                            { "_id" : 0 , "transcript_id" : 1, "start":1, "stop":1 , "scaffold": 1} )
            if not model :
                model = db.genes.find_one ( { "gene_id" : transcript_id } ,
                                                { "_id" : 0 , "transcript_id" : 1, "start":1, "stop":2, "scaffold": 1} )
        if type == "up":
            fs = gridfs.GridFS(db)
            file = db.fs.files.find_one({"filename": model["scaffold"]})
            with fs.get(file["_id"]) as fp_read:
                result = fp_read.read()
                result = result.decode()
                header = ">" + model["scaffold"] + " " + str(bp) + " upstream of " + model["transcript_id"]
                result = result[(model["stop"] - 1): (model["stop"] -1 + bp)]
                return {"header": header, "sequence": result}
        elif type == "down":
            fs = gridfs.GridFS(db)
            file = db.fs.files.find_one({"filename": model["scaffold"]})
            with fs.get(file["_id"]) as fp_read:
                result = fp_read.read()
                result = result.decode()
                header = ">" + model["scaffold"] + " " + str(bp) + " downstream of " + model["transcript_id"]
                result = result[(model["start"] - 1 - bp): (model["start"] - 1)]
                return {"header":header, "sequence": result}
        else:
            raise IndexError

    except TypeError:
        raise HTTPException ( status_code=404 , detail="bad keyword/id" )
    except IndexError:
        raise HTTPException ( status_code=404 , detail="bad start/stop" )