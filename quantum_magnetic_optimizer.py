from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import Aer
from qiskit.compiler import transpile
from qiskit.circuit import Parameter
import numpy as np
from typing import List, Dict, Optional
import matplotlib.pyplot as plt

class QuantumMagneticOptimizer:
    def __init__(self, num_qubits: int = 4):
        """
        Initialize the quantum magnetic field optimizer.
        
        Args:
            num_qubits (int): Number of qubits to use in the circuit
        """
        self.num_qubits = num_qubits
        self.qr = QuantumRegister(num_qubits, 'q')
        self.cr = ClassicalRegister(num_qubits, 'c')
        self.circuit = QuantumCircuit(self.qr, self.cr)
        self.theta = Parameter('θ')
        self.phi = Parameter('φ')
        
    def create_base_circuit(self) -> None:
        """Create the base quantum circuit for magnetic field optimization."""
        # Initialize superposition
        self.circuit.h(self.qr)
        
        # Add parameterized rotation gates for magnetic field simulation
        for i in range(self.num_qubits):
            self.circuit.rz(self.theta, self.qr[i])
            self.circuit.rx(self.phi, self.qr[i])
            
        # Add entanglement layer
        for i in range(self.num_qubits - 1):
            self.circuit.cx(self.qr[i], self.qr[i + 1])
            
    def apply_magnetic_field_data(self, field_strength: float, direction: List[float]) -> None:
        """
        Apply magnetic field data to the quantum circuit.
        
        Args:
            field_strength (float): Magnitude of the magnetic field
            direction (List[float]): Vector representing field direction [x, y, z]
        """
        try:
            direction_array = np.array(direction, dtype=float)
            norm = np.linalg.norm(direction_array)
            if norm == 0:
                normalized_direction = np.array([1.0, 0.0, 0.0])  # Default direction if zero vector
            else:
                normalized_direction = direction_array / norm
            
            # Map field parameters to quantum gates
            theta_val = field_strength * np.pi
            phi_val = np.arctan2(normalized_direction[1], normalized_direction[0])
            
            # Create new circuit with assigned parameters
            self.circuit = self.circuit.assign_parameters({
                self.theta: theta_val,
                self.phi: phi_val
            })
        except Exception as e:
            print(f"Error in apply_magnetic_field_data: {str(e)}")
            # Use default values if there's an error
            self.circuit = self.circuit.assign_parameters({
                self.theta: np.pi/4,
                self.phi: np.pi/4
            })
        
    def optimize_field_configuration(self, target_params: Dict) -> Dict:
        """
        Optimize the magnetic field configuration using quantum algorithms.
        
        Args:
            target_params (Dict): Target parameters for optimization
            
        Returns:
            Dict: Optimized field configuration
        """
        try:
            # Initialize simulator
            simulator = Aer.get_backend('qasm_simulator')
            
            # Add measurement to all qubits
            self.circuit.measure(self.qr, self.cr)
            
            # Transpile circuit for the simulator
            transpiled_circuit = transpile(self.circuit, simulator)
            
            # Execute circuit
            job = simulator.run(transpiled_circuit, shots=1000)
            result = job.result()
            counts = result.get_counts(transpiled_circuit)
            
            # Process results
            optimized_config = self._process_measurement_results(counts)
            return optimized_config
        except Exception as e:
            print(f"Error in optimize_field_configuration: {str(e)}")
            return {
                'optimal_state': '0' * self.num_qubits,
                'probability': 0.0,
                'field_parameters': {
                    'field_strength': 0.0,
                    'normalized_parameters': 0.0
                }
            }
    
    def _process_measurement_results(self, counts: Dict) -> Dict:
        """
        Process the measurement results to determine optimal field configuration.
        
        Args:
            counts (Dict): Raw measurement counts
            
        Returns:
            Dict: Processed results with optimal configuration
        """
        try:
            # Convert counts to probabilities
            total_shots = sum(counts.values())
            probabilities = {state: count/total_shots for state, count in counts.items()}
            
            # Find most probable state
            optimal_state = max(probabilities, key=probabilities.get)
            
            # Convert binary string to field parameters
            field_params = self._state_to_field_params(optimal_state)
            
            return {
                'optimal_state': optimal_state,
                'probability': float(probabilities[optimal_state]),  # Convert numpy float to Python float
                'field_parameters': field_params
            }
        except Exception as e:
            print(f"Error in _process_measurement_results: {str(e)}")
            return {
                'optimal_state': '0' * self.num_qubits,
                'probability': 0.0,
                'field_parameters': {
                    'field_strength': 0.0,
                    'normalized_parameters': 0.0
                }
            }
    
    def _state_to_field_params(self, state: str) -> Dict:
        """
        Convert quantum state to magnetic field parameters.
        
        Args:
            state (str): Binary string representing quantum state
            
        Returns:
            Dict: Magnetic field parameters
        """
        try:
            # Convert binary string to field parameters
            state_int = int(state, 2)
            
            # Map to field parameters (example mapping)
            strength = float((state_int / (2**self.num_qubits - 1)) * 100)  # Convert to Python float
            norm_params = float(state_int / (2**self.num_qubits - 1))  # Convert to Python float
            
            return {
                'field_strength': strength,
                'normalized_parameters': norm_params
            }
        except Exception as e:
            print(f"Error in _state_to_field_params: {str(e)}")
            return {
                'field_strength': 0.0,
                'normalized_parameters': 0.0
            }
    
    def visualize_circuit(self) -> None:
        """Visualize the quantum circuit."""
        print(self.circuit.draw())

if __name__ == "__main__":
    # Example usage
    optimizer = QuantumMagneticOptimizer(num_qubits=4)
    optimizer.create_base_circuit()
    optimizer.apply_magnetic_field_data(
        field_strength=0.5,
        direction=[1.0, 0.0, 0.0]
    )
    results = optimizer.optimize_field_configuration({
        'target_strength': 0.5,
        'target_direction': [1.0, 0.0, 0.0]
    })
    print("Optimized Configuration:", results)
