# uriparser

# Python URI task

In Python, write a class or module with a bunch of functions for manipulating a URI. For this exercise, pretend that the urllib, urllib2, and urlparse modules don't exist. You can use other standard Python modules, such as re, for this. The focus of the class or module you write should be around usage on the web, so you'll want to have things that make it easier to update or append a querystring var, get the scheme for a URI, etc., and you may want to include ways to figure out the domain for a URL (british-site.co.uk, us-site.com, mailto: yourname@example.com, etc.)

# Example 

from uriparser import URI
uri_str = 'your string goes here'
uri = URI(uri_str)
print uri.summary()
