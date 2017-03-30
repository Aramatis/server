
class Status():
    OK = 1
    INVALID_SESSION_TOKEN = 2
    INVALID_USER = 3
    INVALID_PARAMS = 4
    INVALID_ACCESS_TOKEN = 5

    statusDict = {
            OK: {'status':200, 'message': 'ok'},
            INVALID_SESSION_TOKEN: {'status':400, 'message': 'invalid session token'},
            INVALID_USER: {'status':401, 'message': 'invalid user'},
            INVALID_PARAMS: {'status':402, 'message': 'invalid params'},
            # facebook or google access token
            INVALID_ACCESS_TOKEN: {'status':403, 'message': 'access token is not valid'},
            }

    @staticmethod
    def getJsonStatus(code, jsonContent):
        """ return json with status and message related to code """
        status = Status.statusDict[code]
        
        return jsonContent.update(status)
