# Filterbank Plotter

A Python script to plot dynamic spectra from filterbank (.fil) files, with support for interactive visualization and batch processing.

## Features

- **Dynamic Spectrum Visualization**: Display intensity variations across time and frequency
- **Mean Profiles**: Automatically calculates and displays time and frequency profiles
- **Frequency Range Selection**: Specify custom frequency range (f1, f2) or use the entire filterbank bandwidth
- **Batch Output**: Save plots directly to disk or display interactively
- **Timezone Support**: Converts MJD timestamps to human-readable datetime with timezone adjustment
- **Importable Module**: Use as a library in other Python projects

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

#### Basic Usage (Full Frequency Range)

```bash
python plot_ds.py /path/to/PSR_B1133+16_59500.fil
```

#### Specify Frequency Range

```bash
python plot_ds.py /path/to/PSR_B1133+16_59500.fil --f1 100 --f2 80
```

**Note:** Due to negative channel bandwidth in the ORT data format, `f1` (start frequency) will always be **higher** than `f2` (end frequency). For example, `--f1 326.2 --f2 325.8` selects frequencies between 325.8 and 326.2 MHz.

#### Save to Directory

```bash
python plot_ds.py /path/to/PSR_B1133+16_59500.fil --save output_plots/
```

#### Full Example with Frequency Range

```bash
python plot_ds.py data/PSR_B1133+16_59500.fil --f1 250 --f2 150 --save ./results/
```

### Programmatic Usage (Import)

You can also import `plot_filterbank()` to use this module in other projects:

```python
from filterbank_plotter.plot_ds import plot_filterbank

# Display plot interactively (full frequency range)
fig, ax_main = plot_filterbank('/path/to/PSR_B1133+16_59500.fil')

# Specify frequency range and save plot
saved_path = plot_filterbank(
    '/path/to/PSR_B1133+16_59500.fil',
    save_folder='./results',
    f1=100,
    f2=80
)

# Override source name (if not following naming convention)
fig, ax_main = plot_filterbank(
    '/path/to/filterbank.fil',
    source_name='CustomSourceName'
)
```

#### Function Signature

```python
plot_filterbank(filterbank_path, save_folder=None, f1=None, f2=None, source_name=None)
```

**Parameters:**
- `filterbank_path` (str): Path to the filterbank (.fil) file
- `save_folder` (str or None, default=None): Folder to save the plot. If None, returns figure object
- `f1` (float or None, default=None): Start frequency in MHz (typically higher than f2 due to negative channel bandwidth). If None, uses filterbank start frequency. If outside file's bandwidth, clamped to nearest available frequency
- `f2` (float or None, default=None): End frequency in MHz (typically lower than f1 due to negative channel bandwidth). If None, uses filterbank end frequency. If outside file's bandwidth, clamped to nearest available frequency
- `source_name` (str or None, default=None): Override source name; if None, extracts from filename

**Returns:**
- If `save_folder` is None: returns `(fig, ax_main)` tuple for further manipulation
- If `save_folder` is provided: returns the path to the saved JPEG file

## Command-line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `filterbank` | str | Required | Path to the filterbank (.fil) file in format `{source_name}_{mjd}.fil` |
| `--save` | str | None | Folder to save the plot; if not provided, displays interactively |
| `--f1` | float | None | Start frequency in MHz; if not provided, uses filterbank start frequency |
| `--f2` | float | None | End frequency in MHz; if not provided, uses filterbank end frequency |

## Output

The script generates a multi-panel figure including:
- **Main dynamic spectrum**: 2D intensity map with time on x-axis and frequency on y-axis
- **Time profile**: Mean intensity across all frequencies
- **Frequency profile**: Mean intensity across all time samples
- **Colorbar**: Intensity scale reference

Plots are saved as JPEG files with format: `{source_name}_{mjd}_{f1}_{f2}_dyn_spec.jpeg` where f1 and f2 are the frequency range boundaries in MHz.

**Example:** `PSR_B1133+16_60000.50_150.25_250.75_dyn_spec.jpeg`

When saving, files are organized in a source-specific subfolder: `{save_folder}/{source_name}/{source_name}_{mjd}_{f1}_{f2}_dyn_spec.jpeg`

## Dependencies

- **numpy**: Numerical array operations
- **matplotlib**: Plotting and visualization
- **astropy**: Time/date conversions and astronomical utilities
- **your**: Filterbank file reading and data extraction

## Notes

- **ORT Data Origin**: This code was built specifically for data from the Ooty Radio Telescope (ORT), which handles frequency inversions via negative channel bandwidth. The frequency parameter ordering (f1 > f2) reflects this characteristic
- The script uses UTC+5:30 timezone conversion for datetime display (suitable for Indian Standard Time)
- Data is automatically reshaped to (samples × channels) format
- All frequency values are in MHz; all time values are in seconds
- The module is fully importable for use in other Python projects
- Source name is automatically extracted from the filename (part before first underscore), or can be overridden programmatically
- If frequency range is not specified, the entire filterbank bandwidth is used
- If specified frequency values fall outside the filterbank's bandwidth, they are automatically clamped to the nearest available frequencies
- Color scaling uses fixed percentiles (5th and 95th) for consistent visualization
- Actual frequency boundaries used are always included in the output filename for traceability

## Author

Hardik Medhi (with the help of Gemini 3 & Claude Haiku 4.5)