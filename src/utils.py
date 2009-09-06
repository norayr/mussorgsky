import gobject

def escape_html (text, max_length=40):
    if (len (text) > max_length):
        cutpoint = text.find (' ', max_length-10)
        if (cutpoint == -1 or cutpoint > max_length):
            cutpoint = max_length
        text = text [0:cutpoint] + "..."
    return gobject.markup_escape_text (text)


# Set socket timeout
import socket
import urllib2

timeout = 5
socket.setdefaulttimeout(timeout)

class UrllibWrapper ():

    def save_content_into_file (self, content, filename):
        output = open (filename, 'w')
        output.write (content)
        output.close ()
        
    def get_url (self, url):
        request = urllib2.Request (url)
        request.add_header ('User-Agent', 'Mussorgsky/0.1 Test')
        opener = urllib2.build_opener ()
        try:
            return opener.open (request).read ()
        except:
            return None



class Set:

    def __init__ (self):
        self.d = {}
        self.k = None
        
    def insert (self, element):
        if (not self.d.has_key (element)):
            print "insert", element
            self.d[element] = 1
            self.k = None

    def as_list (self):
        if (self.k):
            return self.k
        
        self.k = self.d.keys ()
        self.k.sort ()
        return self.k
        


