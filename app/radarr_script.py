import os
import requests
import urllib3
import logging
import time
from dotenv import load_dotenv

class RadarrArchive():
    
    def __init__(self):
        ## load the environment values from the settings file
        dotenv_path = "/config/settings.env"
        #dotenv_path = "settings.env"
        load_dotenv(dotenv_path)

        # Setup logging
        LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL, logging.INFO),
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        # Disable SSL warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Configuration
        self.RADARR_BASE_URL = os.getenv("RADARR_BASE_URL")
        self.RADARR_API_URL = ""
        if self.RADARR_BASE_URL != None:
            self.RADARR_API_URL = self.RADARR_BASE_URL + "/api/v3"
        self.RADARR_API_KEY = os.getenv("RADARR_API_KEY")
        self.TEST_MOVIE_TITLE = os.getenv("TEST_MOVIE_TITLE", "")
        
        # Headers for API requests
        self.sheaders = {
            'X-Api-Key': self.RADARR_API_KEY
        }
        
        # check the connection to API on initialise
        if not self.check_connection():
            quit()

        # Gather 'tag:/folder' pairs
        self.tag_folder_map = []
        index = 1

        while True:
            pair = os.getenv(f"RADARR_TAG_FOLDER_PAIR_{index}")
            if not pair:
                break
            if ":" in pair:
                tag, folder = pair.split(":", 1)
                self.tag_folder_map.append((tag.strip(), folder.strip()))
            else:
                logging.warning(f"Invalid format in RADARR_TAG_FOLDER_PAIR_{index}, expected 'tag:/path'")
            index += 1
        
        # check the root folders exist on initialize
        self.check_root_folders()
        
        logging.info(f"-------------------------------")
        logging.info(f"")
        logging.info(f"Radarr Webhook Listening at: ")
        logging.info(f"http://localhost:8990/radarr")
        for tag_name, new_root_folder in self.tag_folder_map:
            logging.info(f"")
            logging.info(f"Mapping Tag: {tag_name} ")
            logging.info(f"-> '{new_root_folder}'")
        logging.info(f"")
        logging.info(f"-------------------------------")
    
    # try to authenticate with API Key and host, if not break
    def check_connection(self):
        # if the api key isn't set, we need to stop
        if self.RADARR_API_KEY == None:
            logging.info(f"FAIL: Radarr API Key is not set, please set the key in the 'settings.env' file and restart the container")
            return False
        
        logging.info("Checking Connection to Radarr API...")
        url = f"{self.RADARR_API_URL}/system/status"
        response = requests.get(url, headers=self.sheaders, verify=False)
        self.log_request_response(response)
        if response.status_code == 200:
            logging.info(f"SUCCESS: Radarr API connection sucessful..")
            return True
        else:
            logging.info(f"FAIL: Unable to connect to Radarr API check make sure credentials and host are correct in 'settings.env' file and restart the container!")
            return False
    
    # Get root folders from Radarr
    def get_root_folders(self):
        logging.info("Fetching root folders from Radarr...")
        url = f"{self.RADARR_API_URL}/rootfolder"
        response = requests.get(url, headers=self.sheaders, verify=False)
        self.log_request_response(response)
        return response.json()
    
    # Add root folder from Radarr
    def add_root_folder(self, folder_path):
        logging.info(f"Adding root folder {folder_path} to Radarr...")
        url = f"{self.RADARR_API_URL}/rootfolder"
        response = requests.post(
            url,
            json={'path': folder_path},
            headers=self.sheaders,
            verify=False
        )
        self.log_request_response(response)
        return response.status_code
            
    #check if the folder exists on the sonarr instance, if it doesn't then add it as a root folder
    def check_root_folders(self):
        # create the root folder
        root_folder_list = []
        root_folders = self.get_root_folders()
        for r_folder in root_folders:{
            root_folder_list.append(r_folder["path"])
        }
        
        # run through the tag map and check if the root folder exists in sonarr
        for tag_name, new_root_folder in self.tag_folder_map:
            if new_root_folder not in root_folder_list:
                logging.info(f"Root folder '{new_root_folder}' doesn't exist..")
                # the root folder doesnt exist in sonar, lets create it
                status_code = self.add_root_folder(new_root_folder)
                if status_code == 201:
                    logging.info(f"Root folder '{new_root_folder}' sucessfully created in Radarr..")
                else:
                    logging.error(f"Failed to add '{new_root_folder}' to Radarr: Status `{status_code}`")
        
        logging.info(f"Radarr Root folder checks complete..")
        
    # Log request and response details
    def log_request_response(self, response):
        logging.debug(f"Request URL: {response.request.url}")
        logging.debug(f"Request Method: {response.request.method}")
        logging.debug(f"Request Headers: {response.request.headers}")
        if response.request.body:
            logging.debug(f"Request Body: {response.request.body}")
        logging.debug(f"Response Status Code: {response.status_code}")
        logging.debug(f"Response Content: {response.text}")

    # Get the list of movies from Radarr
    def get_movies(self):
        logging.info("Fetching movies from Radarr...")
        url = f"{self.RADARR_API_URL}/movie"
        response = requests.get(url, headers=self.sheaders, verify=False)
        self.log_request_response(response)
        return response.json()

    # Get the list of tags from Radarr
    def get_tags(self):
        logging.info("Fetching tags from Radarr...")
        url = f"{self.RADARR_API_URL}/tag"
        response = requests.get(url, headers=self.sheaders, verify=False)
        self.log_request_response(response)
        return {tag['id']: tag['label'] for tag in response.json()}
    
    def get_movie_folder(self, movie):
        logging.info("Fetching movie folder from Radarr...")
        url = f"{self.RADARR_API_URL}/movie/{movie['id']}/folder"
        response = requests.get(url, headers=self.sheaders, verify=False)
        data = response.json()
        return data['folder']
    
    # Update the movie root folder and path
    def update_movie_root_folder(self, movie, new_root_folder_id, new_root_folder_path):
        logging.info(f"Updating root folder for movie: {movie['title']}")
        movie['rootFolderPath'] = new_root_folder_path
        movie['rootFolderId'] = new_root_folder_id
        movieFolderTitle = self.get_movie_folder(movie)
        newpath = f"{new_root_folder_path}/{movieFolderTitle}"
        # check if the paths are the same, otherwise don't update
        if movie['path'] != newpath:
            
            movie['path'] = newpath # Update the path because it doesnt match
            url = f"{self.RADARR_API_URL}/movie/{movie['id']}"
            response = requests.put(
                url,
                json=movie,
                headers=self.sheaders,
                params={'moveFiles': True},
                verify=False
            )
            self.log_request_response(response)
            return response.status_code
        
        else:
            ## they match so we return a custom fail code 
            return 456

    # Main script execution
    def start(self):
        
        ## run a connection check
        self.check_connection()
        
        movies_list = self.get_movies()
        tags = self.get_tags()
        root_folders = self.get_root_folders()
        
        TEST_MOVIE_TITLE=self.TEST_MOVIE_TITLE

        # Map tag names to IDs
        tag_ids = {name: id for id, name in tags.items()}
        # counters
        exist_count=0
        update_count=0
        
        for tag_name, new_root_folder in self.tag_folder_map:
            tag_id = tag_ids.get(tag_name)
            if tag_id is None:
                logging.warning(f"Tag '{tag_name}' not found in Radarr. Skipping.")
                continue

            for movie in movies_list:
                if TEST_MOVIE_TITLE and movie['title'] != TEST_MOVIE_TITLE:
                    continue
                
                logging.debug(f"Processing movie: {movie['title']}")
                if tag_id in movie.get('tags', []) and movie['rootFolderPath'] == new_root_folder:
                    exist_count+=1
                    logging.debug(f"Movie '{movie['title']}' with tag '{tag_name}' is already in the correct root folder.")
                elif tag_id in movie.get('tags', []):
                    status_code = self.update_movie_root_folder(movie, tag_id, new_root_folder)
                    if status_code == 202:
                        update_count+=1
                        logging.info(f"Updated root folder for '{movie['title']}' to '{new_root_folder}'")
                    else:
                        logging.error(f"Failed to update '{movie['title']}': Status {status_code}")
                else:
                    logging.debug(f"Movie '{movie['title']}' does not have tag '{tag_name}'")
        
        logging.info(f"-------------------------------")
        logging.info(f"Newly Updated: {update_count}")
        logging.info(f"Already Correct: {exist_count}")
        logging.info(f"-------------------------------")
        
#if __name__ == "__main__":
#   main()
