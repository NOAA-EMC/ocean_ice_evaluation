#!/usr/bin/env python3

import os
import glob
import yaml
import argparse

import xarray as xr
import numpy as np

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

def plot_one_layer(labels, ds_ctl, ds_diff, var_name, cfg, iLayer, output_path, fig_dpi=80):
    """Plot horizontal slices for a specific layer."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Plot 1: Control
    im1 = ds_ctl[var_name].isel(Layer=iLayer, Time=0).plot(
        ax=axes[0], 
        vmin=cfg['min'], vmax=cfg['max'], cmap=cfg['cmap'],
        cbar_kwargs={'label': ''}
    )

    # Plot 2: Difference
    im2 = ds_diff[var_name].isel(Layer=iLayer).plot(
        ax=axes[1], 
        vmin=-cfg['diff_lim'], vmax=cfg['diff_lim'], cmap='RdBu_r',
        cbar_kwargs={'label': ''}
    )

    # Formatting bold labels
    im1.colorbar.set_label(f"{var_name} ({labels[0]}) layer[{iLayer}]", fontweight='bold')
    im2.colorbar.set_label(f"{labels[1]} - {labels[0]}", fontweight='bold')

    for ax in axes.flatten():
        ax.set_title('')
        ax.set_ylabel('')
        
    fig_name = f'{output_path}/{var_name}_{labels[0]}_{labels[1]}_layer_{str(iLayer).zfill(3)}.png'
    plt.savefig(fig_name, bbox_inches='tight', dpi=fig_dpi)
    plt.close(fig)

def plot_all_Layers_summary(labels, ds_ctl, ds_exp, ds_diff, var_name, output_path, alpha_std=0.5, fig_dpi=80):
    """Plot vertical profiles for all layers."""
    num_layers = len(ds_ctl.Layer)
    layer_indices = np.arange(num_layers)

    fig, axes = plt.subplots(1, 2, figsize=(12, 7), sharey=True)

    mean_ctl = ds_ctl[var_name].mean(('lath', 'lonh')).isel(Time=0)
    std_ctl  = ds_ctl[var_name].std(('lath', 'lonh')).isel(Time=0)
    mean_exp = ds_exp[var_name].mean(('lath', 'lonh')).isel(Time=0)
    std_exp  = ds_exp[var_name].std(('lath', 'lonh')).isel(Time=0)

    # Panel 1: Means
    ax1 = axes[0]
    ax1.plot(mean_ctl, layer_indices, ls='--', lw=2, color='k', label=f'{labels[0]}')
    ax1.plot(mean_exp, layer_indices, ls=':',  lw=2, color='r', label=f'{labels[1]}')
    ax1.fill_betweenx(layer_indices, mean_ctl - alpha_std*std_ctl, mean_ctl + alpha_std*std_ctl, color='k', alpha=0.1)
    ax1.fill_betweenx(layer_indices, mean_exp - alpha_std*std_exp, mean_exp + alpha_std*std_exp, color='r', alpha=0.1)
    ax1.set_ylabel('Layer index')
    ax1.set_xlabel(f'Mean {var_name}')

    # Panel 2: Difference
    ax2 = axes[1]
    mean_diff = ds_diff[var_name].mean(('lath', 'lonh'))
    std_diff = ds_diff[var_name].std(('lath', 'lonh'))
    ax2.plot(mean_diff, layer_indices, ls='-', lw=2, color='darkgreen', label='Mean Diff')
    ax2.axvline(0, color='k', lw=1)
    ax2.fill_betweenx(layer_indices, mean_diff - std_diff, mean_diff + std_diff, color='darkgreen', alpha=0.1)
    ax2.set_xlabel(f'Diff {var_name}')

    for ax in axes:
        ax.set_ylim(num_layers - 1, 0)
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend(loc='best', fontsize='small')

    fig_name = f'{output_path}/all_Layers_summary_{var_name}_{labels[0]}_{labels[1]}.png'
    plt.savefig(fig_name, bbox_inches='tight', dpi=fig_dpi)
    plt.close(fig)

def main():
    # 1. Setup Argparse
    parser = argparse.ArgumentParser(description="MOM6 Restart Comparison Tool")
    parser.add_argument("config", help="Path to the YAML configuration file")
    args = parser.parse_args()

    # 2. Load YAML
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    # Extract settings
    paths = config['paths']
    meta = config['metadata']
    proc = config['processing']
    vars_cfg = config['variables']

    # 3. Gather Data
    try:
        restart_ctl = glob.glob(os.path.join(paths['control'], paths['file_pattern']))[0]
        restart_exp = glob.glob(os.path.join(paths['experiment'], paths['file_pattern']))[0]
    except IndexError:
        print(f"Error: Restart files not found in specified paths.")
        return

    print(f'\nReading restart files:\n\n[CTL]:{restart_ctl}\n[EXP]:{restart_exp}')
    ds_ctl = xr.open_dataset(restart_ctl, decode_times=False)
    ds_exp = xr.open_dataset(restart_exp, decode_times=False)

    # Global difference calculation (Fixing coordinate alignment)
    ds_diff = ds_exp.assign_coords(ds_ctl.coords).isel(Time=0) - ds_ctl.isel(Time=0)

    # 4. Execution Loop
    for var_name, cfg in vars_cfg.items():
        print(f'\n>>> Processing/Plotting: {var_name}')
        var_path = os.path.join(paths['output'], var_name)
        os.makedirs(var_path, exist_ok=True)
        
        # Horizontal Slices
        num_layers = len(ds_ctl.Layer)
        for l_idx in range(0, num_layers, proc['layer_stride']):
            plot_one_layer(meta['labels'], ds_ctl, ds_diff, var_name, cfg, l_idx, var_path, proc['fig_dpi'])

        # Vertical Summary
        plot_all_Layers_summary(meta['labels'], ds_ctl, ds_exp, ds_diff, var_name, paths['output'], fig_dpi=proc['fig_dpi'])

    print("\nAll tasks complete.")

if __name__ == "__main__":
    main()
