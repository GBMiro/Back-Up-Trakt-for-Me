#### Trakt API status codes ####

TRAKT_SUCCESS = 200
TRAKT_SUCCESS_RESOURCE = 201
TRAKT_SUCCESS_DELETE = 204
TRAKT_PENDING_OR_BAD_REQUEST = 400
TRAKT_UNAUTHORIZED = 401
TRAKT_FORBIDDEN = 403
TRAKT_NOT_FOUND_OR_INVALID_CODE = 404
TRAKT_METHOD_NOT_FOUND = 405
TRAKT_CODE_USED = 409
TRAKT_CODE_EXPIRED = 410
TRAKT_PRECONDITION_FAILED = 412
TRAKT_CODE_DENIED = 418
TRAKT_ACCOUNT_LIMIT_EXCEEDED = 420
TRAKT_UNPROCESSABLE = 422
TRAKT_LOCKED_USER = 423
TRAKT_VIP = 426
TRAKT_RATE_LIMIT_EXCEEDED = 429
TRAKT_SERVER_ERROR = 500
TRAKT_SERVICE_UNAVAILABLE_1 = 502
TRAKT_SERVICE_UNAVAILABLE_2 = 503
TRAKT_SERVICE_UNAVAILABLE_3 = 504
TRAKT_SERVICE_UNAVAILABLE_4 = 520
TRAKT_SERVICE_UNAVAILABLE_5 = 521
TRAKT_SERVICE_UNAVAILABLE_6 = 522

#### REQUESTS ####

REQUESTS_ERROR =  -10

#### CONTROLLER ####

CONTROLLER_OK = 20

#### DATABASE ####

DATABASE_OK = 30
DATABASE_ERROR = -30

#### EXPORTER ####

EXPORTER_OK = 40
EXPORTER_ERROR = -40

statusMessages = {

    #### TRAKT ####

    TRAKT_SUCCESS : 'Success',
    TRAKT_SUCCESS_RESOURCE:'Success - new resource created (POST)',
    TRAKT_SUCCESS_DELETE:'Success - no content to return (DELETE)',
    TRAKT_PENDING_OR_BAD_REQUEST : 'Waiting user tho authorize app / Bad Request - request could not be parsed',
    TRAKT_UNAUTHORIZED : 'Unauthorized - OAuth must be provided',
    TRAKT_FORBIDDEN : 'Forbidden - invalid API key or unapproved app',
    TRAKT_NOT_FOUND_OR_INVALID_CODE : 'Not Found - method exists, but no record found / Invalid device code to authorize user',
    TRAKT_METHOD_NOT_FOUND : 'Method not found - method does not exist',
    TRAKT_CODE_USED : 'Already Used - user already approved this code',
    TRAKT_CODE_EXPIRED : 'Expired - the tokens have expired, restart the process',
    TRAKT_PRECONDITION_FAILED:'Precondition Failed - use application/json content type',
    TRAKT_CODE_DENIED : 'Denied - user explicitly denied this code',
    TRAKT_ACCOUNT_LIMIT_EXCEEDED:'Account Limit Exceeded - list count, item count, etc',
    TRAKT_UNPROCESSABLE:'Unprocessable Entity - validation errors',
    TRAKT_LOCKED_USER:'Locked User Account - have the user contact support',
    TRAKT_VIP:'VIP Only - user must upgrade to VIP',
    TRAKT_RATE_LIMIT_EXCEEDED : 'Rate Limit Exceeded',
    TRAKT_SERVER_ERROR : 'Server Error - please open a support ticket',
    TRAKT_SERVICE_UNAVAILABLE_1:'Service Unavailable - server overloaded (try again in 30s) (1)',
    TRAKT_SERVICE_UNAVAILABLE_2:'Service Unavailable - server overloaded (try again in 30s) (2)',
    TRAKT_SERVICE_UNAVAILABLE_3:'Service Unavailable - server overloaded (try again in 30s) (3)',
    TRAKT_SERVICE_UNAVAILABLE_4:'Service Unavailable - Cloudflare error (1)',
    TRAKT_SERVICE_UNAVAILABLE_5:'Service Unavailable - Cloudflare error (2)',
    TRAKT_SERVICE_UNAVAILABLE_6:'Service Unavailable - Cloudflare error (3)',

    #### REQUESTS ####
    REQUESTS_ERROR: 'Error in requests. Check previous logs',

    #### DATABASE ####
    DATABASE_ERROR: 'Error in database. Check previous logs'
}