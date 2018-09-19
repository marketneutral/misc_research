#!/bin/bash
conda env create -f zipline_conda.yml
source activate env_zipline
python -m ipykernel install --user --name env_zipline --display-name "Python 3.5 (env_zipline)"
