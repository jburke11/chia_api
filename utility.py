import pymongo
def get_ssr(db, model):
    ssr = db.chia_ssr.find ( { "end5" : { "$gt" : model["start"]} , "end3" : { "$lt" : model["stop"] }, "scaffold" : model["scaffold"] }, {"_id": 0} )
    if ssr :
        model ["ssr"] = [ssr_data for ssr_data in ssr]
    else :
        model ["ssr"] = None
    return model

def open_db(species):
    if species == "salvia_hispanica":
        client = pymongo.MongoClient ( )
        db = client.chia
        return db
    elif species == "tectona_grandis":
        client = pymongo.MongoClient ( )
        db = client.teak
        return db
    elif species == "callicarpa_americana":
        client = pymongo.MongoClient ( )
        db = client.callicarpa
        return db
    elif species == "nepeta_cataria":
        client = pymongo.MongoClient ( )
        db = client.cataria
        return db
    elif species == "nepeta_mussinii":
        client = pymongo.MongoClient ( )
        db = client.mussinii
        return db
    elif species == "hyssopus_officinalis":
        client = pymongo.MongoClient ( )
        db = client.officinalis
        return db
    else:
        raise FileNotFoundError