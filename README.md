# PyIGT-Shimmer: Iowa Gambling Task v3.0

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18071106.svg)](https://doi.org/10.5281/zenodo.18071106)

A modern Python implementation of the Iowa Gambling Task (IGT) with real-time physiological data synchronization via Shimmer3 GSR+ sensors.

## Key Features

- **Bechara Protocol** – Full implementation of the classic 100-trial IGT paradigm
- **Shimmer3 GSR+ Integration** – Real-time electrodermal activity recording with automatic timestamp synchronization
- **PyQt6 Interface** – Modern, responsive GUI with configurable trial parameters

## Installation

```bash
pip install -r requirements.txt
python src/main.py
```

## Validation

The `validation/` folder contains a Monte Carlo simulation (`simulation.py`) that statistically validates the deck payoff structure, confirming Decks A/B as disadvantageous and Decks C/D as advantageous per the original Bechara et al. paradigm.

```bash
python validation/simulation.py
```

## Citation

If you use this software in your research, please cite it using the metadata in [`CITATION.cff`](CITATION.cff):

> Ozel, H. F. (2025). *PyIGT-Shimmer: A Modern Iowa Gambling Task Implementation with Physiological Synchronization* (Version 3.0.0). https://github.com/diferansiyel1/igt_tr

## License

[CC BY-NC 4.0](LICENSE) © 2025 Dr. H. Fehmi Ozel

*Free for academic and research use. Commercial use prohibited.*
