# MOM6 Restart Comparison Tool

A diagnostic utility designed to compare two MOM6 restart datasets.
It generates horizontal slice maps for individual layers and vertical mean/standard deviation 
profiles to identify biases between ocean model streams.

## File Overview

* **`compare_MOM_restartFields.py`**: The core Python script that processes xarray datasets and generates matplotlib visualizations for temperature and salinity.
* **`config_compare_MOM_restarts.yaml`**: A configuration file used to define input/output paths, variable metadata, and plotting scales without modifying the code.
* **`make_plots.sh`**: A wrapper shell script that sets up the required HPC environment modules and executes the diagnostic pipeline.

## Requirements

The tool requires a Python environment (e.g., `py_Feb2026`) with the following packages:
* `xarray`
* `numpy`
* `matplotlib`
* `pyyaml`

## Usage

### 1. Configure the YAML
Edit `config_compare_MOM_restarts.yaml` to point to your Control (CTL) and Experiment (EXP) restart directories. Adjust the `layer_stride` to control how many horizontal maps are generated.

### 2. Execute via Shell Script
The shell script handles the module loading and runs the comparison automatically:

```
chmod +x make_plots.sh
./make_plots.sh
```

---

Usage of `compare_MOM_restartFields.py`:

```
 ./compare_MOM_restartFields.py -h
usage: compare_MOM_restartFields.py [-h] config

MOM6 Restart Comparison Tool

positional arguments:
  config      Path to the YAML configuration file

options:
  -h, --help  show this help message and exit
```
