import json
import re

def urlencode(string):
    """ Percent-encodes a string """
    return ''.join(c if re.match(URI.UNRESERVED_CHAR, c) else '%' + c.encode('hex').upper() for c in string)


class URI(object):
    """ Utility class to handle URIs """

    SCHEME_REGEX = "[a-z][a-z0-9+.-]"
    UNRESERVED_CHAR = "[a-zA-Z0-9\-._~]"
    HOSTNAME_CHAR =  "[a-z0-9\.\-]"

    @staticmethod
    def unreserved(string):
        """ Checks that the given string is only made of "unreserved" characters """
        return all(re.match(URI.UNRESERVED_CHAR, c) for c in string)

    @staticmethod
    def valid_hostname(hostname):
        """ Checks if the given hostname is valid """
        return all(re.match(URI.HOSTNAME_CHAR, c) for c in hostname)
    
    def __init__(self, uri, strict=False):
        """ Parses the given URI """
        uri = uri.strip()

        # URI scheme is case-insensitive
        self.scheme = uri.split(':')[0].lower()

        if not re.match(URI.SCHEME_REGEX, self.scheme):
            raise ValueError("Invalid URI scheme: '{}'".format(self.scheme))

        self.path = uri[len(self.scheme) + 1:]

        # URI fragments
        self.fragment = None
        if '#' in self.path:
            self.path, self.fragment = self.path.split('#')

        # Query parameters (for instance: http://mysite.com/page?key=value&other_key=value2)
        self.parameters = dict()
        if '?' in self.path:
            separator = '&' if '&' in self.path else ';'
            query = '?'.join(self.path.split('?')[1:])
            query_params = query.split(separator)
            query_params = map(lambda p : p.split('='), query_params)

            if not URI.unreserved(query.replace('=', '').replace(separator, '')):     
                if strict:
                    raise ValueError('Invalid query: {}'.format(query))
                else:
                    query_params = [map(urlencode, couple) for couple in query_params]

            self.parameters = {key : value for key, value in query_params}
            self.path = self.path.split('?')[0]


        # For URIs that have a path starting with '//', we try to fetch additional info:
        self.authority = None
        if self.path.startswith('//'):
            self.path = self.path.lstrip('//')
            uri_tokens = self.path.split('/')

            self.authority = uri_tokens[0]
            self.hostname = self.authority
            self.path = self.path[len(self.authority):]

            # Fetching authentication data. For instance: "http://login:password@site.com"
            self.authenticated = '@' in self.authority
            if self.authenticated:
                self.user_information, self.hostname = self.authority.split('@')
                
                # Validating userinfo
                if not URI.unreserved(self.user_information.replace(':', '')):
                    if strict:
                        raise ValueError("Invalid user information: '{}'".format(self.user_information))
                    else:
                        userinfo_tokens = self.user_information.split(':')
                        self.user_information = ':'.join(map(urlencode, userinfo_tokens))

            # Fetching port
            self.port = None
            if ':' in self.hostname:
                self.hostname, self.port = self.hostname.split(':')
                try:
                    self.port = int(self.port)
                    if not 0 <= self.port <= 65535:
                        raise ValueError
                except ValueError:
                    raise ValueError("Invalid port: '{}'".format(self.port))

            # Hostnames are case-insensitive
            self.hostname = self.hostname.lower()

            # Validating the hostname and path
            if not URI.valid_hostname(self.hostname):
                raise ValueError("Invalid hostname: '{}'".format(self.hostname))
            
            if self.path and not URI.unreserved(self.path.replace('/', '')):
                if strict:
                    raise ValueError("Invalid path: '{}'".format(self.path))
                else:
                    path_tokens = self.path.split('/')
                    self.path = '/'.join(map(urlencode, path_tokens))

        elif len(self.path.split('@')) > 2 or not URI.unreserved(self.path.split('@')[-1]):
            raise ValueError("Invalid path: '{}'".format(self.path))

    def remove_fragment(self):
        self.fragment = None

    def remove_query(self):
        self.parameters = dict()

    def remove_port(self):
        self.port = None

    def query(self):
        """ Returns a serialized representation of the query parameters. """
        return '&'.join('{}={}'.format(key, value) for key, value in sorted(self.parameters.iteritems()))

    def summary(self):
        """ Summary of the URI object. Useful for debugging. """
        uri_repr = '{}\n'.format(self)
        uri_repr += '\n'
        uri_repr += "* Scheme name: '{}'\n".format(self.scheme)

        if self.authority:
            uri_repr += "* Authority path: '{}'\n".format(self.authority)

            uri_repr += "  . Hostname: '{}'\n".format(self.hostname)
            if self.authenticated:
                uri_repr += "  . User information = '{}'\n".format(self.user_information)
            if self.port:
                uri_repr += "  . Port = '{}'\n".format(self.port)

        uri_repr += "* Path: '{}'\n".format(self.path)
        if self.parameters:
            uri_repr += "* Query parameters: '{}'\n".format(self.parameters)
        if self.fragment:
            uri_repr += "* Fragment: '{}'\n".format(self.fragment)
        return uri_repr

    def json(self):
        """ JSON serialization of the URI object """
        return json.dumps(self.__dict__, sort_keys=True, indent=2)

    def __str__(self):
        """ Outputs the URI as a normalized string """
        uri = '{}:'.format(self.scheme)
        
        if self.authority:
            uri += '//'
            if self.authenticated:
                uri += self.user_information + '@'
            uri += self.hostname
            if self.port:
                uri += ':{}'.format(self.port)

        uri += self.path
        if self.parameters:
            uri += '?' + self.query()
        if self.fragment:
            uri += '#' + urlencode(self.fragment)
        return uri

    def __eq__(self, uri):
        """ Equivalence between two URIs: the equivalence of their respective normalized string representation """
        return str(self) == str(uri)

