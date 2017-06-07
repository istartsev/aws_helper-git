#!/bin/bash
if [[ ! -e ./.venv/ ]]; then
    virtualenv -p python3.6 .venv
fi

#[install]
source "$(pwd)/.venv/bin/activate"
