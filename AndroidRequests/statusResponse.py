class Status:
    OK = 1
    INVALID_SESSION_TOKEN = 400
    INVALID_USER = 401
    INVALID_PARAMS = 402
    INVALID_ACCESS_TOKEN = 403
    INTERNAL_ERROR = 404
    TRIP_EVALUATION_FORMAT_ERROR = 405
    TRIP_TOKEN_DOES_NOT_EXIST = 406
    TRIP_TOKEN_COULD_NOT_BE_CREATED = 407
    TRAJECTORY_DOES_NOT_HAVE_LOCATIONS = 408
    USER_BUS_IS_FAR_AWAY_FROM_REAL_BUS = 409
    I_DO_NOT_KNOW_ANYTHING_ABOUT_REAL_BUS = 410
    REPORT_CAN_NOT_BE_SAVED = 411

    statusDict = {
        OK: {'status': 200, 'message': 'ok'},
        INVALID_SESSION_TOKEN: {'status': INVALID_SESSION_TOKEN, 'message': 'invalid session token'},
        INVALID_USER: {'status': INVALID_USER, 'message': 'invalid user'},
        INVALID_PARAMS: {'status': INVALID_PARAMS, 'message': 'invalid params'},
        # facebook or google access token
        INVALID_ACCESS_TOKEN: {'status': INVALID_ACCESS_TOKEN, 'message': 'access token is not valid'},
        INTERNAL_ERROR: {'status': INTERNAL_ERROR, 'message': 'something in the code exploded'},
        TRIP_EVALUATION_FORMAT_ERROR: {'status': TRIP_EVALUATION_FORMAT_ERROR, 'message': 'evaluation format is wrong'},
        TRIP_TOKEN_DOES_NOT_EXIST: {'status': TRIP_TOKEN_DOES_NOT_EXIST, 'message': 'trip token does not exist'},
        TRIP_TOKEN_COULD_NOT_BE_CREATED: {
            'status': TRIP_TOKEN_COULD_NOT_BE_CREATED,
            'message': 'active token could not be created'
        },
        USER_BUS_IS_FAR_AWAY_FROM_REAL_BUS: {
            'status': USER_BUS_IS_FAR_AWAY_FROM_REAL_BUS,
            'message': 'user bus is far way from real bus'
        },
        I_DO_NOT_KNOW_ANYTHING_ABOUT_REAL_BUS: {
            'status': I_DO_NOT_KNOW_ANYTHING_ABOUT_REAL_BUS,
            'message': 'i do not know anything about real bus'
        },
        TRAJECTORY_DOES_NOT_HAVE_LOCATIONS: {
            'status': TRAJECTORY_DOES_NOT_HAVE_LOCATIONS,
            'message': 'trajectory does not have locations'
        },
        REPORT_CAN_NOT_BE_SAVED: {
            'status': REPORT_CAN_NOT_BE_SAVED,
            'message': 'report can not be saved :-('
        }
    }

    @staticmethod
    def getJsonStatus(code, jsonContent):
        """ return json with status and message related to code """
        status = Status.statusDict[code]
        jsonContent.update(status)

        return jsonContent
