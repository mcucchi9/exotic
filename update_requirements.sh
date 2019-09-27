#!/bin/bash
conda list -e > requirements.txt
conda env export > l96.yml
