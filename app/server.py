#!/usr/bin/python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
from socketserver import ThreadingMixIn
import threading
import subprocess
## setup script
subprocess.call(['sh', './entrypoint.sh'])
## import and init the classes
from sonarr_script import SonarrArchive
sonarr_archive = SonarrArchive()
from radarr_script import RadarrArchive
radarr_archive = RadarrArchive()

hostName = "0.0.0.0"
serverPort = 80

class Handler(BaseHTTPRequestHandler):
    
    def run_Script(self, arrplatform):
        ## run the main python script - Wait 5 seconds to allow auto tagging to complete before running the script
        print("Waiting for Auto Tag..")
        time.sleep(5)
        if arrplatform == "sonarr":
            print(arrplatform + " Script Executing..")
            sonarr_archive.start()
            print("Execution Complete..")
        elif arrplatform == "radarr":
            print(arrplatform + " Script Executing..")
            radarr_archive.start()
            print("Execution Complete..")
            
    def print_html(self, content):
        #self.html = self.html + content
        self.wfile.write(content.encode("utf-8"))

    def print_html_header(self, page_title=""):
        html_header = "<html><head><title>Sortaar - "+ page_title +"</title></head><body>"
        self.print_html(html_header)
            
    def print_html_footer(self):
        html_footer = "</body><html>"
        self.print_html(html_footer)
    
    def print_h1(self, content):
        self.print_html("<h1>" + content + "</h1>")
    
    def print_text(self, content):
        self.print_html("<p>" + content + "</p>")
    
    def do_POST(self):            
        if self.path == "/sonarr":
            # Respond with the file contents.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.print_html_header("Sonarr Tag Sync:")
            self.print_h1("Sonarr Tag Sync:")
            self.print_text("running...") 
            self.print_html_footer()
            self.run_Script("sonarr")
        elif self.path == "/radarr":
            # Respond with the file contents.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.print_html_header("Radarr Tag Sync:")
            self.print_h1("Radarr Tag Sync:")
            self.print_text("running...")           
            self.print_html_footer()
            self.run_Script("radarr")
        else:
            self.send_response(404)

        return
    
    def do_GET(self):
        # curl http://<ServerIP>/index.html        
        if self.path == "/":
            # Respond with the file contents.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            #content = open('index.html', 'rb').read()            
            self.print_html_header("Sortarr Active")
            self.print_h1("Webhooks Online:")
            self.print_text("Webhooks are online and available at /sonarr and /radarr")
        elif self.path == "/sonarr":
            # Respond with the file contents.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.print_html_header("Sonarr Tag Sync..")
            self.print_h1("Sonarr Tag Sync:")
            self.print_text("running...")
            self.print_html_footer()
            # for testing
            self.run_Script("sonarr")
            
        elif self.path == "/radarr":
            # Respond with the file contents.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.print_html_header("Radarr Tag Sync..")
            self.print_h1("Radarr Tag Sync:")
            self.print_text("running...")
            self.print_html_footer()
            # for testing
            self.run_Script("radarr")
        else:
            self.send_response(404)

        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
  """Handle requests in a separate thread."""

if __name__ == "__main__":
    webServer = ThreadedHTTPServer((hostName, serverPort), Handler)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")