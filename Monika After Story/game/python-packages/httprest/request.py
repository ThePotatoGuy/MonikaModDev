import httplib
import json

# connection results

IDLE = 0
# request not sent
# data is None

BAD_REDIRECT = 1
# redirect status given but response did not give new url
# data is the response

HTTP_ERROR = 2
# some httpException was raised
# data is the exception

NOT_OK = 3
# a status other than 200 was returned (except 301)
# data is the response

BAD_JSON = 3
REDIRECT = 4


class Request(object):
    """
    Generates a request. Currently only supports endpoints that return JSONs.

    NOTE: it is recommended to use threading in some way to avoid hangs.

    PROPERTIES:
        status - the status of the request
        data - any data associated with the status. Varies depending on status.
    """

    def __init__(self, h_conn, req, redirect_limit=2):
        """
        Constructor

        IN:
            h_conn - the HTTPConnection to use. Assumes newly created.
            req - the request string
            redirect_limit - max number of redirects to follow.
                Set to 0 to not redirect at all.
                (Default: 2)
        """
        self.h_conn = h_conn
        self.request = req
        self.redirect_limit = redirect_limit

        self.status = IDLE
        self.data = None

    @staticmethod
    def create_simple(url, req, timeout=10, ssl=True, redirect_limit=2):
        """
        Creates a simple request object.

        IN:
            url -the url to connect to
            req - the actual request string
            timeout - timeout in seconds.
                (Default: 10)
            ssl - pass False to NOT use ssl
                (Default: True)
            redirect_limit - max number of redirects to follow. Set to 0
                to not redirect at all.
                (Default: 2)

        RETURNS: request object
        """
        if ssl:
            h_conn = httplib.HTTPSConnection(url, timeout=timeout)
        else:
            h_conn = httplib.HTTPConnection(url, timeout=timeout)

        return Request(h_conn, req, redirect_limit=redirect_limit)

    def send_request(self):
        """
        Sends the request and stores the results in the results prop.
        """
        read_json = None

        try:
            self.h_conn.connect()

            # do request
            self.h_conn.request(self.request)
            response = h_conn.getresponse()

            if response.status == 301: # redirect
                new_url = response.getheader("location", None)

                if new_url is None:
                    self.results.append(BAD_REDIRECT)
                    return

                # otherwise, say redirect, and save response data
                # TODO handle redirects?
                self.results.append(REDIRECT)
                self.results.append(response)
                return

            if response.status != 200:
                # not OK is bad
                self.results.append(NOT_OK)
                self.results.append(response)
                return

            # otherwise, 200
            read_json = server_response.read()

        except httplib.HTTPException as e:
            # assumed timeout or maybe some other error
            self.results.append(HTTP_ERROR)
            self.results.append(e)

        finally:
            self.h_conn.close()

        # TODO; parse the JSON
