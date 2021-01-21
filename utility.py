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

def get_regex(species):
    regex_dict = dict()
    if species == "salvia_hispanica":
        regex_dict["transcript_regex"] = "^Salhi[.]\d{2}G\d{6}[.]\d{1,2}$"
        regex_dict["gene_regex"] = "^Salhi[.]\d{2}G\d{6}$"
        return regex_dict
    elif species == "tectona_grandis":
        regex_dict["transcript_regex"] = "^Tg\d{2}g\d{5}[.]t\d{1,2}$"
        regex_dict["gene_regex"] = "^Tg\d{2}g\d{5}$"
        return regex_dict
    elif species == "callicarpa_americana":
        regex_dict["transcript_regex"] = "^Calam[.]\d{2}G\d{6}[.]\d{1,2}$"
        regex_dict["gene_regex"] = "^Calam[.]\d{2}G\d{6}$"
        return regex_dict
    elif species == "nepeta_cataria" or species == "nepeta_mussinii" or species == "hyssopus_officinalis":
        regex_dict["transcript_regex"] = "^g\d{1,5}.t\d{1,2}"
        regex_dict["gene_regex"] = "^g\d{1,5}"
        return regex_dict
    else:
        raise FileNotFoundError
