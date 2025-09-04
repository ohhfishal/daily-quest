#!/usr/bin/env bash
uvicorn app.main:app --reload --log-config scripts/logging.json
