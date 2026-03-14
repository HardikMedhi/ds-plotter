#!/usr/bin/env python3
"""
Script to plot dynamic spectrum from filterbank files.
"""

import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from astropy.time import Time, TimezoneInfo
import astropy.units as u
import your

def readfilbank(fb_path):
    fb_obj = your.Your(fb_path)
    header = fb_obj.your_header

    nsamp = header.nspectra
    data = fb_obj.get_data(nstart=0, nsamp=nsamp)

    return header, data


def visualizeData(source_name, mjd, reshaped_data, time_samples, freq_channels, x_vals=[], y_vals=[], save_folder=None, show_fig=True, p1=5, p2=95):
    # Calculate mean profiles
    time_profile = np.mean(reshaped_data, axis=1)  # Mean across frequency (channels)
    freq_profile = np.mean(reshaped_data, axis=0)  # Mean across time (samples)
    
    # Create figure with subplots
    # Colorbar on left, main spectrum in middle, frequency series on right
    fig = plt.figure(figsize=(13, 10))
    gs = fig.add_gridspec(2, 3, height_ratios=[3, 1], width_ratios=[0.15, 3, 1],
                          hspace=0.05, wspace=0.25)
    
    # Colorbar (left of main plot)
    ax_cbar = fig.add_subplot(gs[0, 0])
    
    # Main dynamic spectrum
    ax_main = fig.add_subplot(gs[0, 1])
    im = ax_main.imshow(
        reshaped_data.T,
        aspect='auto',
        origin='lower',
        cmap='inferno',
        vmin=np.percentile(reshaped_data, p1),
        vmax=np.percentile(reshaped_data, p2),
        extent=[time_samples[0], time_samples[-1], freq_channels[0], freq_channels[-1]]
    )
    ax_main.set_ylabel("Frequency (MHz)", fontsize=11)
    ax_main.set_title(f"{source_name}\n{mjdToDateTime(mjd).strftime('%Y-%m-%d %H:%M:%S')}", 
                      fontsize=12, fontweight='bold')
    ax_main.tick_params(labelbottom=False)
    
    # Add vertical and horizontal lines
    for x in x_vals:
        ax_main.axvline(x=x, color='white', linestyle='--', linewidth=2)
    for y in y_vals:
        ax_main.axhline(y=y, color='white', linestyle='--', linewidth=2)
    
    # Colorbar with tick labels on the left
    cbar = plt.colorbar(im, cax=ax_cbar, label="Intensity")
    ax_cbar.yaxis.set_ticks_position('left')
    ax_cbar.yaxis.set_label_position('left')
    
    # Time series (below main plot)
    ax_time = fig.add_subplot(gs[1, 1], sharex=ax_main)
    ax_time.plot(time_samples, time_profile, color='black', linewidth=1)
    ax_time.set_xlabel("Time (s)", fontsize=11)
    ax_time.set_ylabel("Mean Intensity", fontsize=10)
    ax_time.grid(True, alpha=0.3)
    
    # Frequency series (right of main plot)
    ax_freq = fig.add_subplot(gs[0, 2])
    ax_freq.plot(freq_profile, freq_channels, color='black', linewidth=1)
    ax_freq.set_xlabel("Mean Intensity", fontsize=10)
    #ax_freq.set_ylabel("Frequency (MHz)", fontsize=11)
    ax_freq.set_ylim(freq_channels[0], freq_channels[-1])  # Match direction with main plot
    ax_freq.grid(True, alpha=0.3)

    if save_folder is not None:
        os.makedirs(save_folder, exist_ok=True)
        fig.savefig(f"{save_folder}/{source_name}_{mjd}_dyn_spec.jpeg", bbox_inches='tight', dpi=150)
        plt.close(fig)
        return None
    
    return fig, ax_main

def mjdToDateTime(mjd):
    """Converts MJD to a datetime object."""
    t = Time(mjd, format='mjd', scale='utc')
    return t.to_datetime(timezone=TimezoneInfo(utc_offset=5.5*u.hour))


def main():
    """Main function to plot dynamic spectrum from a filterbank file."""
    parser = argparse.ArgumentParser(
        description='Plot dynamic spectrum from a filterbank file.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python plot_ds.py /path/to/data.fil
  python plot_ds.py /path/to/data.fil --source "PSR B1133+16"
  python plot_ds.py /path/to/data.fil --save output_plots/
        """
    )
    
    parser.add_argument('filterbank', type=str,
                       help='Path to the filterbank (.fil) file')
    parser.add_argument('--source', type=str, default='Unknown Source',
                       help='Source name (default: Unknown Source)')
    parser.add_argument('--save', type=str, default=None,
                       help='Folder to save the plot (if not provided, plot will be displayed)')
    parser.add_argument('--p1', type=float, default=5,
                       help='Lower percentile for color scale (default: 5)')
    parser.add_argument('--p2', type=float, default=95,
                       help='Upper percentile for color scale (default: 95)')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.filterbank):
        parser.error(f"Filterbank file not found: {args.filterbank}")
    
    print(f"Reading filterbank file: {args.filterbank}")
    
    # Read filterbank file
    header, data = readfilbank(args.filterbank)
    
    # Extract header parameters
    nchan = header.nchans
    tsampl = header.tsamp # s
    freq_start = header.fch1
    channel_bw = header.foff
    epoch = header.tstart
    
    print(f"  Number of channels: {nchan}")
    print(f"  Sample time: {tsampl} s")
    print(f"  Start frequency: {freq_start} MHz")
    print(f"  Channel bandwidth: {channel_bw} MHz")
    print(f"  Epoch (MJD): {epoch}")
    
    # Reshape data (nsamp × nchan)
    print("Loading and reshaping data...")
    reshaped_data = data.reshape(-1, nchan)
    
    nsamples = reshaped_data.shape[0]
    print(f"  Data shape: {reshaped_data.shape} (samples × channels)")
    
    # Create time and frequency arrays
    time_samples = np.arange(nsamples) * tsampl
    freq_channels = freq_start + np.arange(nchan) * channel_bw
    
    # Visualize the data
    print("Plotting dynamic spectrum...")
    show_fig = args.save is None
    
    result = visualizeData(
        source_name=args.source,
        mjd=epoch,
        reshaped_data=reshaped_data,
        time_samples=time_samples,
        freq_channels=freq_channels,
        save_folder=args.save,
        show_fig=show_fig,
        p1=args.p1,
        p2=args.p2
    )
    
    if show_fig:
        plt.show()
        print("Plot displayed.")
    else:
        print(f"Plot saved to {args.save}/")


if __name__ == "__main__":
    main()





