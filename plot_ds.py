#!/usr/bin/env python3
"""
Script to plot dynamic spectrum from filterbank files.
"""

import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from astropy.time import Time, TimezoneInfo
import astropy.units as u
from astropy.io import fits
import your

def get_file_type(file_path):
    """Determine if file is FITS or filterbank format."""
    file_ext = Path(file_path).suffix.lower()
    if file_ext in ['.fits', '.fit']:
        return 'fits'
    elif file_ext == '.fil':
        return 'filterbank'
    else:
        raise ValueError(f"Unsupported file format: {file_ext}. Expected .fits, .fit, or .fil")


def readfilbank(fb_path):
    fb_obj = your.Your(fb_path)
    header = fb_obj.your_header

    nsamp = header.nspectra
    data = fb_obj.get_data(nstart=0, nsamp=nsamp)

    return header, data


def readfits(fits_path):
    """Read a FITS file containing dynamic spectrum data.
    
    Returns a header-like object and data array compatible with the rest of the pipeline.
    """
    with fits.open(fits_path) as hdul:
        # Get the primary header and data
        header_dict = dict(hdul[0].header)
        data = hdul[0].data
        
        if data is None and len(hdul) > 1:
            # Try binary table HDU if primary is empty
            data = hdul[1].data
            header_dict = dict(hdul[1].header)
    
    # Create a simple header-like object to match your.Your interface
    class FitsHeader:
        pass
    
    header = FitsHeader()
    
    # Extract or deduce necessary parameters from FITS header
    # Common FITS keywords for dynamic spectra
    header.nchans = header_dict.get('NAXIS1', header_dict.get('NCHAN', data.shape[-1] if data is not None else 1))
    header.tsamp = header_dict.get('TSAMP', header_dict.get('CDELT2', 1.0))
    header.fch1 = header_dict.get('FCH1', header_dict.get('CRVAL1', 0.0))
    header.foff = header_dict.get('FOFF', header_dict.get('CDELT1', 1.0))
    header.tstart = header_dict.get('TSTART', header_dict.get('MJD-OBS', 0.0))
    header.basename = header_dict.get('BASENAME', Path(fits_path).stem)
    
    # Handle data shape - ensure it's 1D or 2D
    if data.ndim > 2:
        # Flatten to 1D if necessary
        data = data.flatten()
    elif data.ndim == 2:
        # Already in (time, freq) or (freq, time) format
        # Assume FITS convention: last axis is frequency
        pass
    
    return header, data


def visualizeData(source_name, mjd, reshaped_data, time_samples, freq_channels, f1, f2, x_vals=[], y_vals=[], save_folder=None, show_fig=True):
    # Calculate mean profiles
    time_profile = np.mean(reshaped_data, axis=1)  # Mean across frequency (channels)
    freq_profile = np.mean(reshaped_data, axis=0)  # Mean across time (samples)
    
    # Create figure with subplots
    # Colorbar on left, main spectrum in middle, frequency series on right
    fig = plt.figure(figsize=(16, 10))
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
        vmin=np.percentile(reshaped_data, 5),
        vmax=np.percentile(reshaped_data, 95),
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
        folder_path = '/'.join([save_folder, source_name])
        os.makedirs(folder_path, exist_ok=True)
        
        # Construct the filename
        filename = f"{source_name}_{mjd}_{f1:.2f}_{f2:.2f}_dyn_spec.jpeg"
        filepath = os.path.join(folder_path, filename)
        
        # Check if file exists and handle user input
        filepath = handle_file_existence(filepath)
        
        fig.savefig(filepath, bbox_inches='tight', dpi=150)
        plt.close(fig)
        return None
    
    return fig, ax_main

def handle_file_existence(filepath):
    """Check if file exists and prompt user for alternative action.
    
    If file exists, asks user whether to append a word to the filename.
    If user provides a word, appends it with underscore before the file extension.
    If user declines or provides empty input, returns original filepath (will overwrite).
    
    Parameters:
    - filepath: str - the intended filepath
    
    Returns:
    - str - the final filepath to use (either modified or original)
    """
    if os.path.exists(filepath):
        print(f"File already exists: {filepath}")
        user_input = input("Do you want to append a word to the filename? (yes/no): ").strip().lower()
        
        if user_input in ['yes', 'y']:
            additional_word = input("Enter the word to append: ").strip()
            if additional_word:
                # Insert the additional word before the file extension
                name_parts = filepath.rsplit('.jpeg', 1)
                filepath = f"{name_parts[0]}_{additional_word}.jpeg"
    
    return filepath


def mjdToDateTime(mjd):
    """Converts MJD to a datetime object."""
    t = Time(mjd, format='mjd', scale='utc')
    return t.to_datetime(timezone=TimezoneInfo(utc_offset=5.5*u.hour))


def plot_dynspec(file_path, save_folder=None, f1=None, f2=None, source_name=None):
    """Read a filterbank or FITS file and produce (or save) the dynamic spectrum plot.

    Parameters:
    - file_path: str - path to the .fil or .fits file
    - save_folder: str or None - if provided, save the plot to this folder
    - f1: float or None - start frequency in MHz; if None, uses file start frequency
    - f2: float or None - end frequency in MHz; if None, uses file end frequency
    - source_name: optional override for the source name used in the plot title

    Returns:
    - If `save_folder` is None: returns (fig, ax_main)
    - If `save_folder` is provided: returns the output filepath string
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Detect file type and read accordingly
    file_type = get_file_type(file_path)
    print(f"Reading {file_type} file: {file_path}")
    
    if file_type == 'fits':
        header, data = readfits(file_path)
    else:
        header, data = readfilbank(file_path)

    # Determine source name
    if source_name is None:
        try:
            source_name = header.basename.split('_')[0]
        except Exception:
            source_name = Path(file_path).stem.split('_')[0]

    nchan = header.nchans
    tsampl = header.tsamp  # seconds
    freq_start = header.fch1
    channel_bw = header.foff
    epoch = str(round(header.tstart, 6))

    if len(epoch) < 12:
        epoch += '0' * (12 - len(epoch))

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

    # Get file's frequency range
    file_f_start = freq_channels[0]
    file_f_end = freq_channels[-1]

    # Filter by frequency range if specified, with clamping to file bandwidth
    if f1 is None:
        f1 = file_f_start
    else:
        # Clamp to file's frequency range
        f1 = min(f1, file_f_start)
    
    if f2 is None:
        f2 = file_f_end
    else:
        # Clamp to file's frequency range
        f2 = max(f2, file_f_end)

    # Filter channels by frequency range
    freq_mask = (freq_channels <= f1) & (freq_channels >= f2)
    reshaped_data = reshaped_data[:, freq_mask]
    freq_channels = freq_channels[freq_mask]
    
    print(f"  Frequency range: {f1:.2f} - {f2:.2f} MHz")
    print(f"  Filtered data shape: {reshaped_data.shape} (samples × channels)")

    # Visualize the data
    print("Plotting dynamic spectrum...")
    show_fig = save_folder is None

    result = visualizeData(
        source_name=source_name,
        mjd=epoch,
        reshaped_data=reshaped_data,
        time_samples=time_samples,
        freq_channels=freq_channels,
        f1=f1,
        f2=f2,
        save_folder=save_folder,
        show_fig=show_fig,
    )

    if save_folder is None:
        return result

    # If saved, return the expected filepath
    folder_path = os.path.join(save_folder, source_name)
    out_path = os.path.join(folder_path, f"{source_name}_{epoch}_{f1:.2f}_{f2:.2f}_dyn_spec.jpeg")
    return out_path


def main():
    """Main function to plot dynamic spectrum from a filterbank or FITS file."""
    parser = argparse.ArgumentParser(
        description='Plot dynamic spectrum from a filterbank (.fil) or FITS file.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python plot_ds.py /path/to/data.fil
  python plot_ds.py /path/to/data.fits
  python plot_ds.py /path/to/data.fil --save output_plots/
        """
    )
    
    parser.add_argument('filterbank', type=str,
                       help='Path to the filterbank (.fil) or FITS (.fits) file')
    parser.add_argument('--save', type=str, default=None,
                       help='Folder to save the plot (if not provided, plot will be displayed)')
    parser.add_argument('--f1', type=float, default=None,
                       help='Start frequency in MHz (default: filterbank start frequency)')
    parser.add_argument('--f2', type=float, default=None,
                       help='End frequency in MHz (default: filterbank end frequency)')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.filterbank):
        parser.error(f"Filterbank file not found: {args.filterbank}")

    # Use reusable function so this module can be imported
    result = plot_dynspec(
        file_path=args.filterbank,
        save_folder=args.save,
        f1=args.f1,
        f2=args.f2,
    )

    # If the plot was displayed (result contains figure), show it
    if args.save is None and result is not None:
        plt.show()
        print("Plot displayed.")
    elif args.save is not None:
        print(f"Plot saved to {args.save}/")


if __name__ == "__main__":
    main()





