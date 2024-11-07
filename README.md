# Quantum Magnetic Field Optimization Pipeline

A quantum computing-based system for optimizing and customizing magnetic fields for precise particle measurements. This pipeline integrates quantum circuit design with real-world magnetic field data and particle measurement capabilities.

## Features

- **Quantum Circuit Optimization**: Utilizes quantum computing principles to optimize magnetic field configurations
- **Real-time Data Integration**: Fetches magnetic field data from NASA's GSFC and ESA's Swarm mission
- **Particle Measurement System**: Advanced particle detection and measurement capabilities
- **Visualization Tools**: Comprehensive plotting and analysis of measurement results
- **Modular Architecture**: Easily extensible for different use cases and requirements

## System Requirements

- Python 3.8+
- Qiskit 0.44.1+
- NumPy 1.24.3+
- Matplotlib 3.7.1+
- Requests 2.31.0+
- Pandas 2.0.3+
- SciPy 1.10.1+
- python-dotenv 1.0.0+

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd quantum-magnetic-fields
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the project root with your API keys:
```
NASA_API_KEY=your_nasa_api_key
ESA_API_KEY=your_esa_api_key
```

## Project Structure

```
quantum-magnetic-fields/
├── main.py                     # Main application entry point
├── quantum_magnetic_optimizer.py # Quantum circuit implementation
├── data_fetcher.py            # External data acquisition
├── particle_measurement.py    # Particle measurement system
├── requirements.txt          # Project dependencies
└── README.md                # Project documentation
```

## Usage

1. Basic usage with default parameters:
```python
from main import QuantumMagneticFieldPipeline

# Initialize pipeline
pipeline = QuantumMagneticFieldPipeline(num_qubits=4)

# Define parameters
target_params = {
    'target_strength': 0.5,
    'target_direction': [1.0, 0.0, 0.0],
    'precision_threshold': 0.01
}

particle_properties = {
    'mass': 1.67262192e-27,  # proton mass
    'charge': 1.60217663e-19,  # elementary charge
    'g_factor': 5.585694713,  # proton g-factor
    'velocity': [1e5, 0, 0]
}

# Run pipeline
results = pipeline.run_pipeline(
    latitude=0.0,
    longitude=0.0,
    altitude=400.0,
    target_params=target_params,
    particle_properties=particle_properties
)

# Save results
pipeline.save_results(results, 'pipeline_results.json')
```

2. Run the main script:
```bash
python main.py
```

## Components

### Quantum Magnetic Optimizer
- Implements quantum circuits for magnetic field optimization
- Uses parameterized quantum gates for field manipulation
- Provides methods for circuit creation and optimization

### Data Fetcher
- Interfaces with NASA and ESA APIs
- Fetches real-time magnetic field data
- Combines and processes data from multiple sources

### Particle Measurement System
- Simulates particle detection and measurement
- Provides comprehensive measurement analysis
- Generates visualizations of measurement results

## Output

The pipeline generates:
- Optimized magnetic field configurations
- Particle measurement analysis
- Visualization plots
- JSON results file with complete pipeline output

## Visualization

The system provides several visualization options:
- Particle trajectory plots
- Momentum distribution histograms
- Spin evolution graphs
- Interaction strength plots

## Error Handling

The pipeline includes comprehensive error handling:
- API connection failures
- Data processing errors
- Measurement system calibration issues
- File I/O errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NASA Goddard Space Flight Center for magnetic field data
- ESA Swarm Mission for magnetic field measurements
- Qiskit team for quantum computing framework
