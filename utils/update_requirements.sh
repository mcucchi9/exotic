#!/bin/bash
conda list -e > ../requirements.txt
conda env export > ../exotic.yml
