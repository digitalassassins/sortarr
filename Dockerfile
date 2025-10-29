FROM python:3.11-slim

ENV SERVER_PORT="8990" PUID="1000" PGID="1000" UMASK="002"

VOLUME /config

# Set working directory
WORKDIR /app

# Copy files to app
COPY app/server.py /app/server.py
COPY app/sonarr_script.py /app/sonarr_script.py
COPY app/radarr_script.py /app/radarr_script.py
COPY app/settings.env /app/blank-settings.env
COPY app/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Install requests
RUN pip install requests urllib3 python-dotenv

EXPOSE 8990

ENTRYPOINT ["python3", "server.py"]