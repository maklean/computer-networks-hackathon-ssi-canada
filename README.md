# Forensic analysis tool for LoRaWAN IoT sensors.
It parses raw gateway logs to analyze signal quality, packet loss, battery behavior, and sensor state over time.

The app includes a fleet dashboard and a packet-by-packet replay mode for investigating network reliability issues.

## Files

- main.py – app entry point and navigation  
- data_loader.py – loads and parses gateway JSON logs  
- dashboard_view.py – fleet-level metrics and trend charts  
- replay_view.py – forensic daily replay with live telemetry  
- network_logic.py – packet loss detection and sensor calculations  
- constants.py – calibration values and thresholds  
- dataset/ – raw LoRaWAN gateway logs  

## Running the App

Clone Repo:
```bash
git clone <repo>
cd computer-networks-hackathon-ssi-canada
```

Activate Venv:
```bash
python -m venv venv
```

_Windows:_
```bash
venv\Scripts\activate
```

_Mac/Linux:_
```bash
source venv/bin/activate
```

Install requirements:
```bash
pip install -r requirements.txt
```

Run app:
```bash
streamlit run main.py
```
