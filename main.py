from fastapi import FastAPI , HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pymongo , re , datetime
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
            models = db.genes.find({"model_iprscan.method_description": {"$regex": keyword}}, {"_id": 0, "transcript_id": 1, "model_iprscan": 1})
            ipr_list = []
            [ipr_list.append(model) for model in models]
            return {"interpro_results": ipr_list}
        elif type == "id":
            models = db.genes.find({"model_iprscan.interpro_accession": keyword}, {"_id": 0, "transcript_id": 1, "model_iprscan": 1})
            ipr_list = []
            [ipr_list.append ( model ) for model in models]
            return { "interpro_results" : ipr_list }
        else:
            raise TypeError
    except TypeError:
        raise HTTPException ( status_code=404 , detail="bad keyword/id" )

@app.get("/go/{keyword}-{type}")
def get_go(keyword: str, type: str):
    keyword = keyword.rstrip()
    try:
        if type == "keyword":
            models = db.genes.find({"model_go.go_name": {"$regex": keyword}}, {"_id": 0, "transcript_id": 1, "model_go": 1})
            res_dict = {}
            for item in models:
                res_dict[] = {""}
                for go in item["model_go"]:
                    if re.match(keyword, go["go_name"]):
                        print(item["transcript_id"])
                        go_list.append({"transcript_id":item["transcript_id"], "go_data": go})
                    else:
                        print("here")
            return res_dict

    except TypeError:
        raise HTTPException ( status_code=404 , detail="bad keyword/id" )