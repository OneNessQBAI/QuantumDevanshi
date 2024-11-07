from flask import Flask, send_file, send_from_directory
from flask_socketio import SocketIO, emit
import json
import numpy as np
from datetime import datetime, timezone
import logging
from typing import Dict, Optional
import speech_recognition as sr
from gtts import gTTS
import tempfile
import os
import base64

from quantum_magnetic_optimizer import QuantumMagneticOptimizer
from data_fetcher import MagneticFieldDataFetcher
from particle_measurement import ParticleMeasurementSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

class NumpyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

class QuantumMagneticFieldPipeline:
    def __init__(self, num_qubits: int = 4):
        self.optimizer = QuantumMagneticOptimizer(num_qubits=num_qubits)
        self.data_fetcher = MagneticFieldDataFetcher()
        self.measurement_system = ParticleMeasurementSystem()
        logger.info("Initialized Quantum Magnetic Field Pipeline")

    async def fetch_field_data(self, latitude: float, longitude: float, altitude: float) -> Dict:
        try:
            field_data = await self.data_fetcher.combine_magnetic_data()
            if field_data:
                return field_data

            simulated_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'field_strength': 45.7,
                'field_direction': [0.707, 0.0, 0.707],
                'location': {'latitude': latitude, 'longitude': longitude, 'altitude': altitude}
            }
            logger.info("Using simulated magnetic field data")
            return simulated_data
        except Exception as e:
            logger.error(f"Error fetching field data: {e}")
            return {}

    def optimize_magnetic_field(self, field_data: Dict, target_params: Dict) -> Dict:
        try:
            self.optimizer.create_base_circuit()
            self.optimizer.apply_magnetic_field_data(
                field_strength=field_data['field_strength'],
                direction=field_data['field_direction']
            )
            optimized_config = self.optimizer.optimize_field_configuration(target_params)
            logger.info("Successfully optimized magnetic field configuration")
            return optimized_config
        except Exception as e:
            logger.error(f"Error optimizing magnetic field: {e}")
            return {}

    def measure_particle_interactions(self, field_data: Dict, optimized_field: Dict, particle_properties: Dict) -> Dict:
        try:
            field_vector = np.array(field_data['field_direction']) * field_data['field_strength']
            self.measurement_system.calibrate_sensors(field_vector)
            measurement = self.measurement_system.measure_particle_interaction(
                field_vector,
                particle_properties
            )
            analysis = self.measurement_system.analyze_measurement_series()
            logger.info("Successfully completed particle measurements")
            return analysis
        except Exception as e:
            logger.error(f"Error measuring particle interactions: {e}")
            return {}

    def run_pipeline(self, params: Dict = None) -> Dict:
        if params is None:
            params = {
                'latitude': 0.0,
                'longitude': 0.0,
                'altitude': 400.0,
                'target_params': {
                    'target_strength': 0.5,
                    'target_direction': [1.0, 0.0, 0.0],
                    'precision_threshold': 0.01
                },
                'particle_properties': {
                    'mass': 1.67262192e-27,
                    'charge': 1.60217663e-19,
                    'g_factor': 5.585694713,
                    'velocity': [1e5, 0, 0]
                }
            }

        try:
            field_data = self.fetch_field_data(
                params['latitude'],
                params['longitude'],
                params['altitude']
            )
            if not field_data:
                raise ValueError("Failed to fetch magnetic field data")

            optimized_config = self.optimize_magnetic_field(field_data, params['target_params'])
            measurements = self.measure_particle_interactions(
                field_data,
                optimized_config,
                params['particle_properties']
            )

            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'field_data': field_data,
                'optimized_configuration': optimized_config,
                'measurements': measurements,
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'error': str(e),
                'status': 'error'
            }

def process_speech(audio_data: bytes) -> str:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            temp_audio.write(audio_data)
            temp_audio_path = temp_audio.name

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_audio_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)

        os.unlink(temp_audio_path)
        return text

    except Exception as e:
        logger.error(f"Speech recognition error: {e}")
        return ""

def generate_speech(text: str) -> str:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
            tts = gTTS(text=text, lang='en')
            tts.save(temp_audio.name)

            with open(temp_audio.name, 'rb') as audio_file:
                audio_data = base64.b64encode(audio_file.read()).decode('utf-8')

            os.unlink(temp_audio.name)
            return audio_data

    except Exception as e:
        logger.error(f"Text to speech error: {e}")
        return ""

# Initialize Flask app
app = Flask(__name__, static_url_path='', static_folder=current_dir)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Initialize pipeline
pipeline = QuantumMagneticFieldPipeline()

@app.route('/')
def root():
    return send_file(os.path.join(current_dir, 'index.html'))

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory(current_dir, path)

@socketio.on('optimize')
def handle_optimization(data):
    results = pipeline.run_pipeline(data.get('params'))
    emit('results', {
        'type': 'results',
        'data': json.loads(json.dumps(results, cls=NumpyJSONEncoder))
    })

@socketio.on('speech_to_text')
def handle_speech_to_text(data):
    audio_data = base64.b64decode(data['audio'])
    text = process_speech(audio_data)
    emit('transcription', {
        'type': 'transcription',
        'text': text
    })

@socketio.on('text_to_speech')
def handle_text_to_speech(data):
    text = data['text']
    audio_data = generate_speech(text)
    emit('audio', {
        'type': 'audio',
        'data': audio_data
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Serving files from: {current_dir}")
    # In production, we let gunicorn handle the serving
    if os.environ.get("RENDER"):
        app.logger.info("Running in production mode")
    else:
        socketio.run(app, host='0.0.0.0', port=port, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)
