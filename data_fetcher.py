import requests
import numpy as np
from typing import Dict, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class MagneticFieldDataFetcher:
    def __init__(self):
        """Initialize the data fetcher with public API endpoints."""
        # Space Weather Database API (public, no key required)
        self.space_weather_api = "https://services.swpc.noaa.gov/json/rtsw/rtsw_mag_1m.json"
        # Geomagnetism API (public, no key required)
        self.geomag_api = "https://geomag.usgs.gov/ws/data/"
        
    async def fetch_space_weather_data(self) -> Dict:
        """
        Fetch real-time space weather magnetic field data.
        Returns:
            Dict: Space weather magnetic field data
        """
        try:
            response = requests.get(self.space_weather_api)
            response.raise_for_status()
            data = response.json()
            
            # Get the most recent measurement
            latest = data[-1] if data else None
            if latest:
                return {
                    'timestamp': latest.get('time_tag', ''),
                    'bx': float(latest.get('bx_gsm', 0)),
                    'by': float(latest.get('by_gsm', 0)),
                    'bz': float(latest.get('bz_gsm', 0)),
                    'bt': float(latest.get('bt', 0)),
                    'source': 'NOAA SWPC'
                }
            raise ValueError("No space weather data available")
            
        except Exception as e:
            logger.error(f"Error fetching space weather data: {e}")
            return {}
            
    async def fetch_geomag_data(self, 
                              observatory: str = "BOU",
                              starttime: Optional[str] = None,
                              endtime: Optional[str] = None) -> Dict:
        """
        Fetch geomagnetic field data from USGS.
        Args:
            observatory (str): Observatory code (e.g., "BOU" for Boulder)
            starttime (str): Start time in ISO format
            endtime (str): End time in ISO format
        Returns:
            Dict: Geomagnetic field data
        """
        try:
            if not starttime:
                starttime = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if not endtime:
                endtime = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                
            params = {
                'id': observatory,
                'starttime': starttime,
                'endtime': endtime,
                'elements': 'X,Y,Z,F',
                'format': 'json'
            }
            
            response = requests.get(
                f"{self.geomag_api}/{observatory}/",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            # Get the most recent measurement
            if data.get('values'):
                latest = data['values'][-1]
                return {
                    'timestamp': latest.get('time', ''),
                    'x': float(latest.get('x', 0)),
                    'y': float(latest.get('y', 0)),
                    'z': float(latest.get('z', 0)),
                    'f': float(latest.get('f', 0)),
                    'source': f'USGS {observatory}'
                }
            raise ValueError("No geomagnetic data available")
            
        except Exception as e:
            logger.error(f"Error fetching geomagnetic data: {e}")
            return {}
            
    async def combine_magnetic_data(self) -> Dict:
        """
        Combine data from multiple sources and calculate field parameters.
        Returns:
            Dict: Combined magnetic field data
        """
        try:
            space_data = await self.fetch_space_weather_data()
            geomag_data = await self.fetch_geomag_data()
            
            # Combine the data sources
            if space_data and geomag_data:
                # Calculate combined field strength
                space_strength = np.sqrt(
                    space_data['bx']**2 + 
                    space_data['by']**2 + 
                    space_data['bz']**2
                )
                geomag_strength = geomag_data['f']
                
                # Weight the contributions (can be adjusted)
                space_weight = 0.4
                geomag_weight = 0.6
                
                combined_strength = (
                    space_strength * space_weight +
                    geomag_strength * geomag_weight
                )
                
                # Normalize directions
                space_dir = np.array([
                    space_data['bx'],
                    space_data['by'],
                    space_data['bz']
                ])
                space_dir = space_dir / np.linalg.norm(space_dir)
                
                geomag_dir = np.array([
                    geomag_data['x'],
                    geomag_data['y'],
                    geomag_data['z']
                ])
                geomag_dir = geomag_dir / np.linalg.norm(geomag_dir)
                
                # Combine directions
                combined_dir = (
                    space_dir * space_weight +
                    geomag_dir * geomag_weight
                )
                combined_dir = combined_dir / np.linalg.norm(combined_dir)
                
                return {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'field_strength': float(combined_strength),
                    'field_direction': combined_dir.tolist(),
                    'sources': {
                        'space_weather': space_data,
                        'geomagnetic': geomag_data
                    }
                }
                
            # If one source fails, use the other
            elif space_data:
                return {
                    'timestamp': space_data['timestamp'],
                    'field_strength': float(space_data['bt']),
                    'field_direction': [
                        float(space_data['bx']/space_data['bt']),
                        float(space_data['by']/space_data['bt']),
                        float(space_data['bz']/space_data['bt'])
                    ],
                    'sources': {'space_weather': space_data}
                }
                
            elif geomag_data:
                return {
                    'timestamp': geomag_data['timestamp'],
                    'field_strength': float(geomag_data['f']),
                    'field_direction': [
                        float(geomag_data['x']/geomag_data['f']),
                        float(geomag_data['y']/geomag_data['f']),
                        float(geomag_data['z']/geomag_data['f'])
                    ],
                    'sources': {'geomagnetic': geomag_data}
                }
                
            raise ValueError("No magnetic field data available from any source")
            
        except Exception as e:
            logger.error(f"Error combining magnetic data: {e}")
            return {}

if __name__ == "__main__":
    import asyncio
    
    async def test_fetcher():
        fetcher = MagneticFieldDataFetcher()
        data = await fetcher.combine_magnetic_data()
        print("Combined Magnetic Field Data:")
        print(json.dumps(data, indent=2))
    
    asyncio.run(test_fetcher())
