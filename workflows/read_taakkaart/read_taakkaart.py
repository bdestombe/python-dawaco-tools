"""
Extract values from taakkaart Word documents and save them to a CSV file.

Dependencies:
- olefile: https://pypi.org/project/olefile/
Instructions:
1. Install the olefile library using pip:
    pip install olefile
2. Run the script and provide the folder path containing the Word documents and the output CSV file name.
"""

import csv
import os
import re
from datetime import datetime

import olefile


def extract_values(text):
    """
    Extract key-value pairs from the text content of a Word document.

    Parameters
    ----------
    text : str
        The text content of the Word document.

    Returns
    -------
    dict
        A dictionary containing the extracted key-value pairs.
    """
    # Updated regular expression pattern to handle names with spaces
    pattern = r'(.+?):\s*[_\s]*(\d+(?:[.,]\d+)?)'
    matches = re.findall(pattern, text)
    return {name.strip(): value.replace(',', '.') for name, value in matches}

def extract_date_from_filename(filename):
    """
    Extract the date from the filename of a Word document.

    Parameters
    ----------
    filename : str
        The filename of the Word document.

    Returns
    -------
    str
        The extracted date in 'YYYY-MM-DD' format, or None if no date is found.
    """
    pattern = r'(\d{2}-\d{2}-\d{4})\.doc$'
    match = re.search(pattern, filename)
    if match:
        date_str = match.group(1)
        return datetime.strptime(date_str, '%d-%m-%Y').strftime('%Y-%m-%d')
    return None

def extract_text_from_doc(file_path):
    """
    Extract the text content from a Word document.

    Parameters
    ----------
    file_path : str
        The path to the Word document file.

    Returns
    -------
    str
        The text content of the Word document.
    """
    try:
        ole = olefile.OleFileIO(file_path)
        word_stream = ole.openstream('WordDocument')
        content = word_stream.read().decode('utf-8', errors='ignore')
        ole.close()
        return content  # noqa: TRY300
    except olefile.OleError:
        return ""

def process_document(file_path):
    """
    Process a Word document to extract values.

    Parameters
    ----------
    file_path : str
        The path to the Word document file.

    Returns
    -------
    dict
        A dictionary containing the extracted values.
    """
    try:
        content = extract_text_from_doc(file_path)
        return extract_values(content)
    except olefile.OleError:
        return {}
    except FileNotFoundError:
        return {}
    except UnicodeDecodeError:
        return {}

def main():
    """
    Extract values from Word documents and save them to a CSV file.

    The user is prompted to enter the folder path containing the Word documents and the output CSV file name.

    The extracted values are written to the CSV file with the following columns:
    - Filename: The name of the Word document file.
    - Date: The date extracted from the filename in 'YYYY-MM-DD' format.
    - Other columns: The extracted key-value pairs from the Word documents.
    """
    folder_path = input("Enter the folder path containing the Word documents: ")
    output_file = input("Enter the name of the output CSV file: ")

    all_values = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.doc'):
            file_path = os.path.join(folder_path, filename)
            values = process_document(file_path)
            values['Filename'] = filename
            date = extract_date_from_filename(filename)
            if date:
                values['Date'] = date
            all_values.append(values)

    # Get all unique keys
    fieldnames = set()
    for values in all_values:
        fieldnames.update(values.keys())
    fieldnames = sorted(fieldnames)

    # Ensure 'Filename' and 'Date' are the first columns
    if 'Date' in fieldnames:
        fieldnames.remove('Date')
        fieldnames.insert(0, 'Date')
    if 'Filename' in fieldnames:
        fieldnames.remove('Filename')
        fieldnames.insert(0, 'Filename')

    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for values in all_values:
            writer.writerow(values)


if __name__ == "__main__":
    main()
