# Sortarr - Radarr/Sonarr Archiver

This container builds upon the `alekslyse/sonarr_tag_move` project
and also the `buesche87/sonarrchiver` project

####Changes to the project include:

	- Removal or Cron to switch to a webhook system (keeping system resources to a minimum)
	- Adding the webhook to Radarr & Sonarr means auto archiving is only triggered on Series Add
	  This makes it a really effective combination with Overseer/Jellyseer as new movies are instantly archived once added.
	  Which prevents the breaking of Transcoding with Tdarr, Archiving is done before Tdarr can grab the video file.
	- Added the ability to auto archive for both Sonarr and Radarr
	- Moved environment variables to `settings.env` in a mounted volume, for portability and changing settings quickly
	- Auto Add missing folders in Radarr/Sonarr on run

The script has been extended to support **multiple tag/root-folder pairs**.  
To use this feature, define one or more `SONARR_FOLDER_PAIR_X` / `RADARR_FOLDER_PAIR_X` environment variables, e.g.:

	SONARR_FOLDER_PAIR_1=documentaries:/mnt/media/TV Documentaries
    SONARR_FOLDER_PAIR_2=kids:/mnt/media/Kids TV
	
	RADARR_FOLDER_PAIR_1=documentaries:/mnt/media/Documentaries
    RADARR_FOLDER_PAIR_2=kids:/mnt/media/Kids Movies

There is no fixed limit to the number of pairs, as long as the variables are named one after the other within the `settings.env`.

> 🐳 Pull the image from: `docker.io/mitsie/sortarr`

## Environment variables saved in `settings.env`

| variable | value | explanation |
| ----------- | ----------- | ----------- |
| `SONARR_BASE_URL` | `http://sonarr:8989/` | Sonarr API endpoint |
| `SONARR_API_KEY` | `d5198e8de5259712b6361a56de515a51` | Sonarr API key |
| `RADARR_BASE_URL` | `http://radarr:7878/` | Radarr API endpoint |
| `RADARR_API_KEY` | `d5198e8de5259712b6361a56de515a51` | Radarr API key |
| `LOG_LEVEL` | `INFO` | Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `TEST_SERIES_TITLE` | `Andor` | Keep empty to process all series |
| `TEST_SERIES_TITLE` | `Andor` | Keep empty to process all movies |
| `SONARR_FOLDER_PAIR_1` | `documentaries:/mnt/media/TV Documentaries` | Tag and root folder seperated by a `:` colon character |
| `SONARR_FOLDER_PAIR_2` | `kids:/mnt/media/Kids TV` | Tag and root folder seperated by a `:` colon character |
| `RADARR_FOLDER_PAIR_1` | `documentaries:/mnt/media/Documentaries` | Tag and root folder seperated by a `:` colon character |
| `RADARR_FOLDER_PAIR_2` | `kids:/mnt/media/Kids Movies` | Tag and root folder seperated by a `:` colon character |

# How to install

###Using Docker Run:###

	```
	docker run -p 8990:80 -v ./config:"/config" --name sortarr docker.io/mitsie/sortarr -d
	```

###Using Docker Compose:###
	
	#####docker-compose.yaml:
	```
	services:
	  sortarr:
		image: docker.io/mitsie/sortarr:latest
		container_name: sortarr
		hostname: sortarr
		ports: 
		  - 8990:80
		volumes:
		  - ./config:/config
	```
	
	```
	docker compose -f docker-compose.yaml up -d
	```

### Setting up a Webhook

	- Install docker container
	- Navigate to `config/settings.env`
	- Enter Radarr Base URL & API Key And/Or Sonarr Base URL & API Key
	- Enter `Tag:Folder` pairs (Any folders not listed in Sonarr / Radarr will be added on run)	
	- Go to Radarr/Sonarr -> Settings -> Connect
	- Click `+` and choose `Web Hook`
	- Give the Webhook a name
	- Untick all triggers checkboxes and only select 
		`On Movie Added` (Radarr) `On Series Added` (Sonarr)
	- Webhook URL = `http://localhost:8990`
	- Username leave empty
	- Password leave empty
