import pandas as pd
import json
import glob
import os

def load_network_data():
    """
    Scans the directory for JSON logs and returns a cleaned, time-sorted DataFrame.
    """
    # get all .json files in the Dragino Path.
    target_path = os.path.join('dataset', 'Dragino DDS75-LB Ultrasonic Distance Sensor', '**', '*.json')
    files = glob.glob(target_path, recursive=True)
    
    if not files:
        raise FileNotFoundError(f"No JSON files found in {target_path}")

    data_list = []
    parse_count = 0 # to count how many JSONs were parsesd

    # iterate through all the files and add each into the data list
    print(f"> Parsing {len(files)} files...") 
    for file in files: 
        with open(file, 'r') as f:
            try:
                parse_count += 1

                c = json.load(f)
                rx = c.get('rxInfo', [{}])[0] # receive information
                tx = c.get('txInfo', {}) # transmission information

                obj = c.get('object', {}) # should be the decoded data from the sensor
                
                data_list.append({
                    'time': c.get('time'), # data timestamp
                    'fCnt': c.get('fCnt'), # frame count (should increment by 1 for each 'message')
                    'rssi': rx.get('rssi'), # sig. stregth indicator
                    'snr': rx.get('snr'), # sig. noise to ratio
                    'spreading_factor': tx.get('modulation', {}).get('lora', {}).get('spreadingFactor'),
                    'battery': obj.get('Bat'),
                    'distance': obj.get('distance') # gap between sensor and liquid?
                })
            except Exception:
                # ignore parsing fails for now
                continue

    # use pandas data frame to sort data by 'time'            
    df = pd.DataFrame(data_list)

    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'], format='mixed')
        df = df.sort_values('time')
    
    print(f"> Finished parsing {parse_count}/{len(files)} files...") 
        
    return df