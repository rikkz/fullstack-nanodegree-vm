from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Restaurant , MenuItem

engine = create_engine("sqlite:///restaurantmenu.db")
Base.metadata.bind = engine
DBSession = sessionmaker( bind = engine )
session = DBSession()


from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi


class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Hello!</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>&#161 Hola !</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type' , 'text/html')
                self.end_headers()
                quer = session.query(Restaurant).all()
                output = ''
                output += '<html><head><title>Restauarnt Menu</title></head><body>'

                for q in quer:
                    output += '<h1>%s</h1>' % q.name
                    output +='<a href = "/restaurants/%s/edit"> Edit </a><br><a href = "/restaurants/%s/delete"> Delete</a>' % (q.id , q.id)
                output +='<br><a href = "/restaurants/new"> Create a new Restaurant </a>'
                output += '</body></html>'
                self.wfile.write(output)
                return

            if self.path.endswith('/edit'):
                restaurant_id = self.path.split("/")[2]
                quer = session.query(Restaurant).filter_by(id = restaurant_id).one()
                if quer:
                    self.send_response(200)
                    self.send_header('Content-type' , 'text/html')
                    self.end_headers()
                    output = ''
                    output += '<html><head><title>Restauarnt Name Edit</title></head><body>'
                    output += '<h2>%s</h2>' % quer.name
                    output += '<form method = "post" enctype="multipart/form-data">'
                    output += '<input type="text" name = "edit_restaurant" placeholder = "%s">' % quer.name
                    output += '<input type="submit" value = "Rename">'
                    output += '</form></body></html>'
                    self.wfile.write(output)
                return

            if self.path.endswith('/delete'):
                restaurant_id = self.path.split("/")[2]
                quer = session.query(Restaurant).filter_by(id = restaurant_id).one()
                if quer:
                    self.send_response(200)
                    self.send_header('Content-type' , 'text/html')
                    self.end_headers()
                    output = ''
                    output += '<html><head><title>Restauarnt Delete</title></head><body>'
                    output += '<h2> Are you Sure you want to delete %s</h2>' % quer.name
                    output += '<form method = "post" enctype="multipart/form-data">'
                    output += '<input type="submit" value = "Delete">'
                    output += '</form></body></html>'
                    self.wfile.write(output)
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type' , 'text/html')
                self.end_headers()
                output = ''
                output += '<html><head><title>Restauarnt Menu</title></head><body>'
                output += '<h2>Make a New Restaurant</h2>'
                output += '<form method = "post" enctype="multipart/form-data">'
                output += '<input type="text" name = "new_restaurant">'
                output += '<input type="submit" value = "Submit">'
                output += '</form></body></html>'
                self.wfile.write(output)
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith('/restaurants/new'):
                ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('new_restaurant')
                new_restaurant = Restaurant( name = messagecontent[0] )
                session.add( new_restaurant )
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location','/restaurants')
                self.end_headers()
                return
            if self.path.endswith('/edit'):

                restaurant_id = self.path.split("/")[2]
                quer = session.query(Restaurant).filter_by(id = restaurant_id).one()

                ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('edit_restaurant')
                if quer:
                    quer.name = messagecontent[0]
                    session.add( quer )
                    session.commit()
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location','/restaurants')
                self.end_headers()
                return

            if self.path.endswith('/delete'):

                restaurant_id = self.path.split("/")[2]
                quer = session.query(Restaurant).filter_by(id = restaurant_id).one()

                ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                if quer:
                    session.delete( quer )
                    session.commit()
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location','/restaurants')
                self.end_headers()
                return

                # self.wfile.write( messagecontent[0] )

            """self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message')
            output = ""
            output += "<html><body>"
            output += " <h2> Okay, how about this: </h2>"
            output += "<h1> %s </h1>" % messagecontent[0]
            output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
            output += "</body></html>"
            self.wfile.write(output)
            print output"""
        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()
