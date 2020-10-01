def get_ssr(db, model):
    ssr = db.chia_ssr.find ( { "end5" : { "$gt" : model["start"]} , "end3" : { "$lt" : model["stop"] }, "scaffold" : model["scaffold"] }, {"_id": 0} )
    if ssr :
        model ["ssr"] = [ssr_data for ssr_data in ssr]
    else :
        model ["ssr"] = None
    return model