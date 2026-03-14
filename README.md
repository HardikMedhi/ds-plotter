# Filterbank Plotter

A Python script to plot dynamic spectra from filterbank (.fil) files, with support for interactive visualization and batch processing.

## Features

- **Dynamic Spectrum Visualization**: Display intensity variations across time and frequency
- **Mean Profiles**: Automatically calculates and displays time and frequency profiles
- **Flexible Color Scaling**: Adjustable percentile-based color mapping for better visualization
- **Annotation Support**: Add vertical and horizontal lines to mark events of interest
- **Batch Output**: Save plots directly to disk or display interactively
- **Timezone Support**: Converts MJD timestamps to human-readable datetime with timezone adjustment

## Requirements

- Python 3.7+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Filterbank File Format

Filterbank files should follow the naming convention:
```
{source_name}_{mjd}.fil
```

**Example:** `PSR_B1133+16_59500.fil`

The source name is automatically extracted from the filename (the part before the first underscore) and used in the plot title.

## Usage

### Basic Usage

```bash
python src/plot_ds.py /path/to/PSR_B1133+16_59500.fil
```

### Save to Directory

```bash
python src/plot_ds.py /path/to/PSR_B1133+16_59500.fil --save output_plots/
```

### Custom Color Scaling

```bash
python src/plot_ds.py /path/to/PSR_B1133+16_59500.fil --p1 2 --p2 98
```

### Full Example

```bash
python src/plot_ds.py data/PSR_B1133+16_59500.fil --save ./results/ --p1 5 --p2 95
```

## Command-line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `filterbank` | str | Required | Path to the filterbank (.fil) file in format `{source_name}_{mjd}.fil` |
| `--save` | str | None | Folder to save the plot; if not provided, displays interactively |
| `--p1` | float | 5 | Lower percentile for color scale |
| `--p2` | float | 95 | Upper percentile for color scale |

## Output

The script generates a multi-panel figure including:
- **Main dynamic spectrum**: 2D intensity map with time on x-axis and frequency on y-axis
- **Time profile**: Mean intensity across all frequencies
- **Frequency profile**: Mean intensity across all time samples
- **Colorbar**: Intensity scale reference

Plots are saved as JPEG files with format: `{source_name}_{mjd}_dyn_spec.jpeg`

## Dependencies

- **numpy**: Numerical array operations
- **matplotlib**: Plotting and visualization
- **astropy**: Time/date conversions and astronomical utilities
- **your**: Filterbank file reading and data extraction

## Notes

- The script uses UTC+5:30 timezone conversion for datetime display (suitable for Indian Standard Time)
- Data is automatically reshaped to (samples × channels) format
- All frequency values are in MHz
- All time values are in seconds
