def ErrorCheck(i, prnt=True):
    '''Checks the argument for the error code'''
    errordict = {10: {"code": "No internet connection detected"}, #No internet
                 11: {"code": "Error regarding WiFi network"},    #Internet fails to provide data
                 12: {"code": "Error regarding steam response"}}  #Steam retrieval fail
    if isinstance(i, int):
        if i in errordict:
            if prnt:
                print(errordict[i]["code"])
            return True
        else:
            return False
    else:
        return False