def ErrorCheck(error, printError=True):
    '''Checks the argument for the error code'''
    #Dictionary of errors and their respective strings to print
    errorDict = {10: {"code": "No internet connection detected"}, #No internet
                 11: {"code": "Error regarding WiFi network"},    #Internet fails to provide data
                 12: {"code": "Error regarding steam response"}}  #Steam retrieval fail
    #If the given error is an integer and if the error is in the error dictionary, return True and,
    #print out the error string if "prnt" is True
    #If the error isn't an integer or in the error dictionary, return False
    if isinstance(error, int):
        if error in errorDict:
            if printError:
                print(errorDict[error]["code"])
            return True
        else:
            return False
    else:
        return False