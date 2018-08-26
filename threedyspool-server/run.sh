#!/bin/sh

export FLASK_ENV=development
export FLASK_APP=threedyspool.py
export THREEDYSPOOL_CONFIG=~+/config.py

flask run
