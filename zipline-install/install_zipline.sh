#!/bin/bash

# Create and install necessary packages
conda env create -f zipline_conda.yml

# Export the environment so it can be used in Jupyter
source activate env_zipline
python -m ipykernel install --user --name env_zipline --display-name "Python 3.5 (env_zipline)"

# We want all users to hit the same S3 directory for data
#export ZIPLINE_ROOT=/mnt/s3/exos-sim/zipline_root
