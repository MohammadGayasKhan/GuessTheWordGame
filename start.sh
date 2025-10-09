#!/usr/bin/env bash
cd WordGuesser
gunicorn --bind 0.0.0.0:$PORT WordGuesser.wsgi:application