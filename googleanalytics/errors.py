# encoding: utf-8

class GoogleAnalyticsError(Exception):
    pass


class InvalidRequestError(GoogleAnalyticsError):
    # invalid parameter, bad request
    pass


class NotPermittedError(GoogleAnalyticsError):
    # invalid credentials, no permission
    pass


class LimitExceededError(GoogleAnalyticsError):
    # quota, rate limit, ...
    pass


class ServerError(GoogleAnalyticsError):
    # internal server error / backend error
    pass