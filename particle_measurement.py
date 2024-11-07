import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import matplotlib.pyplot as plt
from scipy import signal

@dataclass
class ParticleMeasurement:
    """Data class for particle measurements."""
    position: np.ndarray
    momentum: np.ndarray
    spin: np.ndarray
    interaction_strength: float
    timestamp: float

class ParticleMeasurementSystem:
    def __init__(self, sensitivity: float = 0.001, noise_level: float = 0.01):
        """
        Initialize the particle measurement system.
        
        Args:
            sensitivity (float): Detector sensitivity (0-1)
            noise_level (float): Background noise level (0-1)
        """
        self.sensitivity = sensitivity
        self.noise_level = noise_level
        self.measurements: List[ParticleMeasurement] = []
        self.calibration_factor = 1.0
        
    def calibrate_sensors(self, reference_field: np.ndarray) -> float:
        """
        Calibrate the measurement system using a reference magnetic field.
        
        Args:
            reference_field (np.ndarray): Known reference magnetic field
            
        Returns:
            float: Calibration factor
        """
        # Ensure reference_field is a numpy array
        reference_field = np.array(reference_field, dtype=float)
        
        # Simulate sensor response to reference field
        measured_response = self._simulate_sensor_response(reference_field)
        true_magnitude = np.linalg.norm(reference_field)
        measured_magnitude = np.linalg.norm(measured_response)
        
        # Calculate calibration factor (avoid division by zero)
        self.calibration_factor = true_magnitude / max(measured_magnitude, 1e-10)
        return self.calibration_factor
        
    def measure_particle_interaction(self, 
                                  magnetic_field: np.ndarray,
                                  particle_properties: Dict) -> ParticleMeasurement:
        """
        Measure particle interaction with the magnetic field.
        
        Args:
            magnetic_field (np.ndarray): Applied magnetic field vector
            particle_properties (Dict): Properties of the particle being measured
            
        Returns:
            ParticleMeasurement: Measurement results
        """
        # Ensure magnetic_field is a numpy array
        magnetic_field = np.array(magnetic_field, dtype=float)
        
        # Apply sensor sensitivity and noise
        raw_measurement = self._simulate_sensor_response(magnetic_field)
        
        # Calculate particle position with uncertainty
        position = self._calculate_position(raw_measurement, particle_properties)
        
        # Calculate particle momentum
        momentum = self._calculate_momentum(position, particle_properties)
        
        # Calculate particle spin
        spin = self._calculate_spin(magnetic_field, particle_properties)
        
        # Calculate interaction strength
        interaction_strength = self._calculate_interaction_strength(
            magnetic_field,
            position,
            particle_properties
        )
        
        # Create measurement object
        measurement = ParticleMeasurement(
            position=position,
            momentum=momentum,
            spin=spin,
            interaction_strength=interaction_strength,
            timestamp=np.datetime64('now').astype(float)
        )
        
        self.measurements.append(measurement)
        return measurement
        
    def _simulate_sensor_response(self, field: np.ndarray) -> np.ndarray:
        """
        Simulate the sensor response to a magnetic field.
        
        Args:
            field (np.ndarray): Applied magnetic field
            
        Returns:
            np.ndarray: Simulated sensor response
        """
        # Add gaussian noise
        noise = np.random.normal(0, self.noise_level, field.shape)
        
        # Apply sensitivity factor
        response = field * self.sensitivity + noise
        
        # Apply calibration
        response *= self.calibration_factor
        
        return response
        
    def _calculate_position(self,
                          measurement: np.ndarray,
                          properties: Dict) -> np.ndarray:
        """
        Calculate particle position from measurement data.
        
        Args:
            measurement (np.ndarray): Raw measurement data
            properties (Dict): Particle properties
            
        Returns:
            np.ndarray: Calculated position vector
        """
        # Extract relevant properties
        mass = float(properties.get('mass', 1.0))
        charge = float(properties.get('charge', 1.0))
        
        # Apply quantum corrections
        position = measurement * (mass / charge)
        
        # Add uncertainty based on Heisenberg principle
        uncertainty = np.random.normal(0, 1e-34/mass, measurement.shape)
        
        return position + uncertainty
        
    def _calculate_momentum(self,
                          position: np.ndarray,
                          properties: Dict) -> np.ndarray:
        """
        Calculate particle momentum.
        
        Args:
            position (np.ndarray): Particle position
            properties (Dict): Particle properties
            
        Returns:
            np.ndarray: Calculated momentum vector
        """
        # Extract mass and velocity
        mass = float(properties.get('mass', 1.0))
        velocity = np.array(properties.get('velocity', [0.0, 0.0, 0.0]), dtype=float)
        
        # Calculate classical momentum
        p_classical = mass * velocity
        
        # Add quantum corrections
        h_bar = 1.054571817e-34  # Reduced Planck constant
        wavelength = h_bar / (mass * max(np.linalg.norm(velocity), 1e-10))
        p_quantum = h_bar / wavelength
        
        return p_classical + p_quantum * np.random.normal(0, 0.1, 3)
        
    def _calculate_spin(self,
                       magnetic_field: np.ndarray,
                       properties: Dict) -> np.ndarray:
        """
        Calculate particle spin state.
        
        Args:
            magnetic_field (np.ndarray): Applied magnetic field
            properties (Dict): Particle properties
            
        Returns:
            np.ndarray: Calculated spin vector
        """
        # Gyromagnetic ratio
        g_factor = float(properties.get('g_factor', 2.0))
        
        # Calculate Zeeman splitting
        mu_B = 9.274009994e-24  # Bohr magneton
        B_magnitude = np.linalg.norm(magnetic_field)
        
        # Calculate spin vector
        spin = np.zeros(3)
        spin[2] = 0.5 * g_factor * mu_B * B_magnitude
        
        return spin
        
    def _calculate_interaction_strength(self,
                                     magnetic_field: np.ndarray,
                                     position: np.ndarray,
                                     properties: Dict) -> float:
        """
        Calculate the strength of particle-field interaction.
        
        Args:
            magnetic_field (np.ndarray): Applied magnetic field
            position (np.ndarray): Particle position
            properties (Dict): Particle properties
            
        Returns:
            float: Interaction strength
        """
        # Calculate magnetic moment
        g_factor = float(properties.get('g_factor', 2.0))
        mu_B = 9.274009994e-24  # Bohr magneton
        magnetic_moment = g_factor * mu_B
        
        # Calculate interaction energy
        B_magnitude = np.linalg.norm(magnetic_field)
        interaction_energy = -magnetic_moment * B_magnitude
        
        # Convert to interaction strength (0-1 scale)
        max_energy = magnetic_moment * max(B_magnitude, 1e-10)
        interaction_strength = abs(interaction_energy / max_energy)
        
        return float(interaction_strength)
        
    def analyze_measurement_series(self) -> Dict:
        """
        Analyze a series of measurements for patterns and statistics.
        
        Returns:
            Dict: Analysis results
        """
        if not self.measurements:
            return {}
            
        # Extract measurement components
        positions = np.array([m.position for m in self.measurements])
        momenta = np.array([m.momentum for m in self.measurements])
        spins = np.array([m.spin for m in self.measurements])
        strengths = np.array([m.interaction_strength for m in self.measurements])
        
        # Calculate statistics
        analysis = {
            'position_mean': positions.mean(axis=0).tolist(),
            'position_std': positions.std(axis=0).tolist(),
            'momentum_mean': momenta.mean(axis=0).tolist(),
            'momentum_std': momenta.std(axis=0).tolist(),
            'spin_mean': spins.mean(axis=0).tolist(),
            'interaction_strength_mean': float(strengths.mean()),
            'interaction_strength_std': float(strengths.std())
        }
        
        return analysis
        
    def plot_measurements(self) -> None:
        """Plot measurement results and statistics."""
        if not self.measurements:
            print("No measurements to plot")
            return
            
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        
        # Plot position trajectories
        positions = np.array([m.position for m in self.measurements])
        ax1.plot(positions[:, 0], positions[:, 1], 'b-', label='XY Trajectory')
        ax1.set_xlabel('X Position')
        ax1.set_ylabel('Y Position')
        ax1.set_title('Particle Trajectory')
        ax1.legend()
        
        # Plot momentum distribution
        momenta = np.array([m.momentum for m in self.measurements])
        momentum_magnitudes = np.linalg.norm(momenta, axis=1)
        ax2.hist(momentum_magnitudes, bins=30)
        ax2.set_xlabel('Momentum Magnitude')
        ax2.set_ylabel('Count')
        ax2.set_title('Momentum Distribution')
        
        # Plot spin evolution
        spins = np.array([m.spin for m in self.measurements])
        times = np.array([m.timestamp for m in self.measurements])
        ax3.plot(times, spins[:, 2], 'r-', label='Z-component')
        ax3.set_xlabel('Time')
        ax3.set_ylabel('Spin')
        ax3.set_title('Spin Evolution')
        ax3.legend()
        
        # Plot interaction strength
        strengths = np.array([m.interaction_strength for m in self.measurements])
        ax4.plot(times, strengths, 'g-')
        ax4.set_xlabel('Time')
        ax4.set_ylabel('Interaction Strength')
        ax4.set_title('Interaction Strength Evolution')
        
        plt.tight_layout()
        plt.show()
