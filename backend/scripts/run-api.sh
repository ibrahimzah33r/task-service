#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

uvicorn app.main:app --reload