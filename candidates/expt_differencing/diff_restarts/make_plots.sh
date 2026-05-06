#!/bin/bash

# load py modules
module use /home/Santha.Akella/modulefiles
module load py_Feb2026
module list

# make plots
./compare_MOM_restartFields.py config_compare_MOM_restarts.yaml
