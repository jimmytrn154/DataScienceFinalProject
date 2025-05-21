import os
import glob
import json
import pandas as pd

# Directory containing your JSON files
data_dir = 'newApproach'

records = []

# Loop through all JSON files dynamically
for filepath in glob.glob(os.path.join(data_dir, '*.json')):
    with open(filepath, 'r') as f:
        j = json.load(f)
    booking_date = j.get('booking_date')
    travel_date = j.get('travel_date')
    
    # Process both best_flights and other_flights
    for flight_list_key in ['best_flights', 'other_flights']:
        for itin in j['data'].get(flight_list_key, []):
            rec = {
                'booking_date': booking_date,
                'travel_date': travel_date,
                'route_type': itin.get('type')
            }
            
            # First leg details
            first_leg = itin['flights'][0]
            rec['travel_class'] = first_leg.get('travel_class')
            rec['flight_number'] = first_leg.get('flight_number')
            
            # Core numeric features
            rec['price'] = itin.get('price')
            rec['total_duration'] = itin.get('total_duration')
            # rec['n_legs'] = len(itin['flights'])
            rec['n_stops'] = len(itin.get('layovers', []))
            
            # Average legroom
            # legrooms = []
            # for leg in itin['flights']:
            #     lr = leg.get('legroom')
            #     if isinstance(lr, str):
            #         # Strip non-numeric characters
            #         val = ''.join(ch for ch in lr if ch.isdigit() or ch == '.')
            #         if val:
            #             legrooms.append(float(val))
            #     elif isinstance(lr, (int, float)):
            #         legrooms.append(float(lr))
            # rec['avg_legroom'] = sum(legrooms) / len(legrooms) if legrooms else None
            
            # Carbon emissions
            ce = itin.get('carbon_emissions', {})
            rec['carbon_this'] = ce.get('this_flight')
            # rec['carbon_route_typ'] = ce.get('typical_for_this_route')
            # rec['carbon_diff_pct'] = ce.get('difference_percent')
            
            # Delay flag
            rec['delayed_any'] = any(leg.get('often_delayed_by_over_30_min', False) for leg in itin['flights'])
            
            # Layover durations
            layovers = itin.get('layovers', [])
            rec['layover_total_duration'] = sum(stop.get('duration', 0) for stop in layovers)
            
            # Derived features
            rec['days_to_departure'] = (
                pd.to_datetime(travel_date) - pd.to_datetime(booking_date)
            ).days
            # rec['price_per_minute'] = rec['price'] / rec['total_duration'] if rec['total_duration'] else None
            # rec['price_per_leg'] = rec['price'] / rec['n_legs'] if rec['n_legs'] else None
            # rec['is_direct'] = 1 if rec['n_stops'] == 0 else 0
            rec['avg_stop_duration'] = (
                rec['layover_total_duration'] / rec['n_stops'] if rec['n_stops'] else 0
            )
            
            records.append(rec)

# Create DataFrame and save to CSV
df = pd.DataFrame(records)
output_path = os.path.join(data_dir, 'merged_flights.csv')
df.to_csv(output_path, index=False)

# Display first few rows
df.head()