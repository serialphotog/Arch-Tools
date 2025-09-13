import argparse
import csv
import os
import sys

from pyproj import CRS, Transformer

UTM_ROW = 0
NAME_ROW = 1
OTHER_NUMBERS_ROW = 2
SPAN_ROW = 3
HEIGHT_ROW = 4
LATITUDE_ROW = 5
LONGITUDE_ROW = 6
SPAN_ENTRY_ROW = 7
NOTES_ROW = 8

def _utm_to_latlon(utm: str):
    # Some of the UTM fields contains junk, clean it up
    utm = utm.strip().replace("Â", "").replace("\xa0", "").replace("?", "").replace(",", "")

    try:
        zone_band, easting, northing = utm.split("-")
    except Exception as e:
        print(f'Failed to unpack {utm}')
        try:
            utm = utm.replace("S", "S-")
            zone_band, easting, northing = utm.split("-")
            print(f'Successfully recovered UTM')
        except Exception as e:
            print(f'\033[91m Failed once again to convert {utm} \033[0m')
            return -1, -1

    # Extract the zone number (e.g. 12T)
    zone_number = int(zone_band[:-1])
    hemisphere = "north" if zone_band[-1] >= "N" else "south"

    # Define the UTM CRS
    utm_crs = CRS.from_dict({
        "proj": "utm",
        "zone": zone_number,
        "south": hemisphere == "south"
    })

    # Define the target CRS (WGS84 lat/lon)
    wgs84_crs = CRS.from_epsg(4326)

    lat = -1
    lon = -1
    try:
        transformer = Transformer.from_crs(utm_crs, wgs84_crs, always_xy=True)
        lon, lat = transformer.transform(float(easting), float(northing))
    except Exception as e:
        print(f'Error processing {utm}: {e}')

    return lat, lon

def _valid_command_line(args) -> bool:
    if not args.in_path:
        print(f'You must supply an input CSV file')
        return False
    if not args.out_path:
        print(f'You must supply an output CSV file')
        return False
    
    # Ensure the input CSV file exists
    if not os.path.isfile(args.in_path):
        print(f'Could not find the input CSV: {args.in_path}')
        return False
    
    # Check if the output file already exists
    if os.path.isfile(args.out_path):
        # Just delete the file if it exists
        print(f'Removing existing {args.out_path}')
        os.remove(args.out_path)
    
    return True

def main():
    parser = argparse.ArgumentParser(description='A simple tool to convert NABS UTM to decimal degrees')
    parser.add_argument('--input', '-i', dest='in_path', help='Path to the input CSV')
    parser.add_argument('--output', '-o', dest='out_path', help='Path to the output CSV')
    args = parser.parse_args()

    # Validate the command line args
    if not _valid_command_line(args=args):
        sys.exit(-1)

    # Perform the conversion 
    input_file = args.in_path
    output_file = args.out_path

    print(f'Parsing {input_file}')
    entries = []
    with open(input_file, 'r') as csv_file:
        reader = csv.reader(csv_file)

        # Skp the first row as that just contains the column names
        next(reader, None)

        # Process each row in the file 
        total_rows = 0
        total_converted = 0
        for row in reader:
            # Filter for non-empty rows
            if any(row):
                total_rows += 1

                # Build the entry
                entry = {
                    'UTM': row[UTM_ROW],
                    'Converted': '',
                    'Name': row[NAME_ROW],
                    'Other Numbers': row[OTHER_NUMBERS_ROW],
                    'Span': row[SPAN_ROW],
                    'Height': row[HEIGHT_ROW],
                    'Latitude': row[LATITUDE_ROW],
                    'Longitude': row[LONGITUDE_ROW],
                    'Span Entry': row[SPAN_ENTRY_ROW],
                }

                # Add the notes row, if present
                if len(row) == 9:
                    entry['Notes'] = row[NOTES_ROW]

                if row[UTM_ROW]:
                    lat, lon = _utm_to_latlon(row[UTM_ROW])
                    entry['Converted'] = f'{lat}, {lon}'
                    total_converted += 1

                entries.append(entry)
        
        print(f'Read {total_rows} rows and converted {total_converted} entries')

    # Write the output
    with open(output_file, 'w') as csv_file:
        print(f'Writing output to {output_file}')

        fieldnames = ['UTM', 'Converted', 'Name', 'Other Numbers', 'Span',
                      'Height', 'Latitude', 'Longitude', 'Span Entry']
        if "Notes" in entries[0]:
            fieldnames.append('Notes')

        total = 0
        for entry in entries:
            with open(output_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)

                # Only write the header once
                if f.tell() == 0:
                    writer.writeheader()
                
                # Write the row
                writer.writerow(entry)
                total += 1

        print(f'Wrote {total} entries to {output_file}')

if __name__ == '__main__':
    main()
