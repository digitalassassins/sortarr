#!/bin/sh
if [ ! -f /config/settings.env ]; then
    cp -R /app/blank-settings.env /config/settings.env
fi