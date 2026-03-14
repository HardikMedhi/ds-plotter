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

### Command-Line Usage

#### Basic Usage

```bash
python src/plot_ds.py /path/to/PSR_B1133+16_59500.fil
```

#### Save to Directory

```bash
python src/plot_ds.py /path/to/PSR_B1133+16_59500.fil --save output_plots/
```

#### Custom Color Scaling

```bash
python src/plot_ds.py /path/to/PSR_B1133+16_59500.fil --p1 2 --p2 98
```

#### Full Example

```bash
python src/plot_ds.py data/PSR_B1133+16_59500.fil --save ./results/ --p1 5 --p2 95
```

### Programmatic Usage (Import)

You can also import `plot_filterbank()` to use this module in other projects:

```python
from filterbank_plotter.src.plot_ds import plot_filterbank

# Display plot interactively
fig, ax_main = plot_filterbank('/path/to/PSR_B1133+16_59500.fil')

# Save plot to folder
saved_path = plot_filterbank(
    '/path/to/PSR_B1133+16_59500.fil',
    save_folder='./results',
    p1=2,
    p2=98
)

# Override source name (if not following naming convention)
fig, ax_main = plot_filterbank(
    '/path/to/filterbank.fil',
    source_name='CustomSourceName'
)
```

#### Function Signature

```python
plot_filterbank(filterbank_path, save_folder=None, p1=5, p2=95, source_name=None)
```

**Parameters:**
- `filterbank_path` (str): Path to the filterbank (.fil) file
- `save_folder` (str or None, default=None): Folder to save the plot. If None, returns figure object
- `p1` (float, default=5): Lower percentile for color scaling
- `p2` (float, default=95): Upper percentile for color scaling
- `source_name` (str or None, default=None): Override source name; if None, extracts from filename

**Returns:**
- If `save_folder` is None: returns `(fig, ax_main)` tuple for further manipulation
- If `save_folder` is provided: returns the path to the saved JPEG file

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

When saving, files are organized in a source-specific subfolder: `{save_folder}/{source_name}/{source_name}_{mjd}_dyn_spec.jpeg`

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
- The module is fully importable; use `from filterbank_plotter.src.plot_ds import plot_filterbank` in other projects
- Source name is automatically extracted from the filename (part before first underscore), or can be overridden programmatically
