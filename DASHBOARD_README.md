# Morty Express Analytics Dashboard

Interactive web-based dashboard for analyzing Morty Express experiment results.

## Features

- **Multi-Run Support**: Load and analyze any JSON result file
- **Interactive Visualizations**:
  - Success rate trends over time
  - Planet usage patterns
  - Performance heatmaps
  - Planet-by-planet breakdown
- **Run Comparison**: Compare multiple experiment runs side-by-side
- **Detailed Metrics**:
  - Success/failure streaks
  - Per-planet statistics
  - Trip-level data
- **Real-time Filtering**: Toggle between different runs instantly

## Installation

```bash
pip install -r requirements.txt
```

## Running the Dashboard

```bash
streamlit run morty_dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Supported Data Formats

The dashboard automatically detects and loads:

- **Baseline runs** (`morty_data_*.json`) - Single planet isolation tests
- **Pattern runs** (`morty_pattern_*.json`) - Repeating pattern experiments
- **Detector runs** (`morty_pattern_detector_*.json`) - Adaptive strategy runs

## Usage

1. **Select a Run**: Use the sidebar dropdown to choose which experiment to analyze
2. **Explore Tabs**: Navigate through different visualizations
3. **Compare Runs**: Use the comparison section to analyze multiple runs
4. **View Raw Data**: Expand the raw data viewer to see the underlying JSON

## Tips

- Run multiple experiments to enable comparison mode
- Look for patterns in the heatmap to identify timing-based strategies
- Check the "Best Streak" and "Worst Streak" for insights into consistency
- Compare trip success rates vs. overall morty success rates for strategy effectiveness
