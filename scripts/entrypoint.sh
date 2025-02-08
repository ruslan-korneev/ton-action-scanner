#!/bin/bash

alembic upgrade head

# execute command
exec "$@"
