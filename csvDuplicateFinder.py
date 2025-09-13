import argparse
import pandas as pd
import os
import sys

def _prompt_user_for_yes_or_no(question, default="yes"):
    """
    Prompts the user for the answer to a yes or no question.

    :param question: The question to display to the user.
    :param default: The default answer. Defaults to "yes".

    :returns: True if the user chose yes, else returns False.

    :throws: ValueError if an invalid default answer is provided.
    :throws: ValueError if a mapping for a default answer could not be found.
    """
    # Answers to treat as valid options
    valid = {"yes": True, "y": True, "no": False, "n": False}

    # Build the prompt for the question, taking into account the default option
    if default is None:
        prompt = "[y/n]"
    elif default == "yes" or default == "y":
        prompt = "[Y/n]"
    elif default == "no" or default == "n":
        prompt = "[y/N]"
    else:
        raise ValueError(f"Invalid default answer: {default}")
    
    # Prompt the user for input
    answer = input(f"{question} {prompt}").lower()
    if default is not None and answer == '':
        if default in valid:
            return valid[default]
        else:
            raise ValueError(f"No mapping found for default of {default}")
    elif answer in valid:
        return valid[answer]
    
    # Invalid choice, re-prompt the user
    return _prompt_user_for_yes_or_no(question, default)

def _validateCommandLine(args) -> bool:
    """
    Validates all of the command line arguments.

    :param args: The command line arguments to validate.

    :returns: True if the arguments are valid, else False.
    """
    # Ensure we have the required arguments
    if not args.in_path:
        print(f'You must supply an input CSV file.')
        return False
    if not args.out_path:
        print(f'You must supply an output CSV file.')
        return False

    # Ensure the input CSV file exists
    if not os.path.isfile(args.in_path):
        print(f'Could not find the input CSV: {args.in_path}')
        return False

    # Check if the output file already exists
    if os.path.isfile(args.out_path):
        overwrite = _prompt_user_for_yes_or_no(f'Output CSV {args.out_path} ' \
                                               'already exists. Overwrite it?',
                                               'no')
        
        if overwrite:
            print(f'Removing existing file: {args.out_path}')
            os.remove(args.out_path)
        else:
            print(f'Output CSV exists. Aborting.')
            return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description="A simple tool for finding duplicate entries in CSV landform data.")
    parser.add_argument('--input', '-i', dest='in_path', help='Path to the input CSV')
    parser.add_argument('--output', '-o', dest='out_path', help='Path to the output CSV')
    parser.add_argument('--latitude', dest='latitude_column', help="Specify the name of the latitude column. Defaults to \"latitude\"")
    parser.add_argument('--longitude', dest='longitude_column', help="Specify the name of the longitude column. Defaults to \"longitude\"")
    args = parser.parse_args()

    # Validate the command line args
    if not _validateCommandLine(args=args):
        sys.exit()

    # Perform the analysis
    input_file = args.in_path
    output_file = args.out_path
    latitude_column = 'latitude'
    if (args.latitude_column):
        latitude_column = args.latitude_column
    longitude_column = 'longitude'
    if (args.longitude_column):
        longitude_column = args.longitude_column

    df = pd.read_csv(input_file)

    # Filter out ones that don't have a lat/lon
    df = df.dropna(subset=[latitude_column, longitude_column])
    df = df[(df[latitude_column] != "") & (df[longitude_column] != "")]

    # Group by the lat/lon values
    groups = df.groupby([latitude_column, longitude_column])

    duplicate_groups = []
    for (lat, lon), group in groups:
        if len(group) > 1: # only report the duplicates
            print(f'\nDuplicate group for latitude={lat}, longitude={lon}:')
            print(group.to_string(index=False))

            # Add a marker column for clarity
            group = group.copy()
            group["duplicate_group"] = f"{lat},{lon}"

            duplicate_groups.append(group)

    # Combine all duplicate groups into one data frame
    if duplicate_groups:
        result = pd.concat(duplicate_groups, ignore_index=True)
        result.to_csv(output_file, index=False)
        print(f'\n✅ Duplicate report saved to {output_file}')
    else:
        print('\n🎉 No duplicates found!')

if __name__ == '__main__':
    main()