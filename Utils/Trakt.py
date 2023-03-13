

# Trakt API status codes & messages

SUCCESS = 200
BAD_REQUEST = 400
UNAUTHORIZED = 401
FORBIDDEN = 403
NOT_FOUND = 404
RATE_LIMIT_EXCEEDED = 429
SERVER_ERROR = 500

statusMessages = {
    SUCCESS : 'Success',
    BAD_REQUEST : 'Bad Request - request could not be parsed',
    UNAUTHORIZED : 'Unauthorized - OAuth must be provided',
    FORBIDDEN : 'Forbidden - invalid API key or unapproved app',
    NOT_FOUND : 'Not Found - method exists, but no record found',
    RATE_LIMIT_EXCEEDED : 'Rate Limit Exceeded',
    SERVER_ERROR : 'Server Error - please open a support ticket'
}

# Trakt Synchronization limit

SYNC_MAX_LIMIT = 1000