# Sortarr - Radarr/Sonarr Archiver

This container builds upon the `alekslyse/sonarr_tag_move` project
and also the `buesche87/sonarrchiver` project

#### Changes to the project include:

- Removal of Cron to switch to a webhook system (keeping system resource usage to a minimum).
- Adding the webhook to Radarr & Sonarr means auto-archiving is only triggered on Series Add
  This makes it a really effective combination with Overseer/Jellyseer, as new movies are 
  instantly archived once added.
  For instance, this prevents Tdarr from breaking the Transcoding. Archiving is done before Tdarr 
  can grab the video file and start the encoding process.
- Added the ability to auto-archive for both Sonarr and Radarr.
- Moved environment variables to `settings.env` in a mounted volume, for portability and 
  changing settings quickly.
- Auto-add missing media folders in Radarr/Sonarr on run (must be accessible by Radarr or Sonarr)

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
| `SONARR_FOLDER_PAIR_1` | `documentaries:/mnt/media/TV Documentaries` | Tag and root folder separated by a `:` colon character |
| `SONARR_FOLDER_PAIR_2` | `kids:/mnt/media/Kids TV` | Tag and root folder separated by a `:` colon character |
| `RADARR_FOLDER_PAIR_1` | `documentaries:/mnt/media/Documentaries` | Tag and root folder separated by a `:` colon character |
| `RADARR_FOLDER_PAIR_2` | `kids:/mnt/media/Kids Movies` | Tag and root folder separated by a `:` colon character |

# How to install

### Using Docker Run: ###

```bash
docker run -p 8990:80 -v ./config:"/config" --name sortarr docker.io/mitsie/sortarr -d
```

### Using Docker Compose:
	
##### docker-compose.yaml:

```yaml
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

##### then run the command:
```bash
docker compose -f docker-compose.yaml up -d
```

### Setting up a Webhook

- Install Docker container
- Navigate to `config/settings.env`
- Enter Radarr Base URL & API Key, And/Or Sonarr Base URL & API Key
	e.g. if you have set a hostname, it can be `http://sonarr:8998`/`http://radarr:7878`
		 can be `http://localhost`
		 Or if you are on Windows on a separate bridge network from Sortarr
		 The Docker magic host `http://host.docker.internal`
- Enter `Tag:Folder` pairs 
	`Any folders not listed in Sonarr / Radarr will be added on run, must be 
	accessible by that Radarr/Sonarr container`
- Restart the container in Docker to pick up the config changes
- Go to Radarr/Sonarr -> Settings -> Connect
- Click `+` and choose `Web Hook`
- Give the Webhook a name
- Untick all trigger checkboxes and only select 
	`On Movie Added` (Radarr) / `On Series Added` (Sonarr)
- Webhook URL = `http://localhost:8990` (Or base URL provided in `settings.env` file)
- Username leave empty
- Password leave empty

### Setting up Auto Tagging

A good workflow is to use Auto Tagging. I use it to catch `children's animation` films 
and move the folder so they are auto-added to my Kids' Plex Library.
Under my `settings.env`, I have the folder pairs: 
`RADARR_TAG_FOLDER_PAIR_1="kids:/mnt/downloads/-Kids Movies"`
To set up the auto tagging, here is an example:

- Go to Radarr -> Settings -> Tags
- Under `Auto Tagging`, click the `+` Plus button
- Give it a name, I've called mine `Children Animation`
- under tag, enter your own tag you want to tag movies with
  I've chosen `kids` for simplicity
- Under `Condition`, click the `+` Plus button
- Choose `Genre` and enter a name. I've put `Children`
- In the field `Genre(s)` enter `Children`
- Tick `Required` then click save
- Under `Condition`, click the `+` Plus button again
- Choose `Genre` and enter a name. I've put `Animation`
- In the field `Genre(s)` enter `Animation`
- Tick `Required` then click save

Now, when a Movie is added, if it has both the Genres `Children` and `Animation`, it will auto-add the tag `kids`
This will fire the Sortarr webhook, which will instantly change the root folder for the movie.
	
Enjoy!
	
### Features to add in the future

- Web Interface to change settings within the web browser
- Database to store folder pairs instead of environment variables
- Simpler auto tagging web interface to add auto tagging to both Sonarr/Radarr via API
- Stored logs to keep a track of the API root folder updates
- Get Sortarr to set up webhooks automatically on first run
