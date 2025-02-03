"""
Extract values from taakkaart Word documents and save them to a CSV file.

Dependencies:
- olefile: https://pypi.org/project/olefile/
Instructions:
1. Install the olefile library using pip:
    pip install olefile
2. Run the script and provide the folder path containing the Word documents and the output CSV file name.
"""

import os
import re
from datetime import datetime

import olefile
import pandas as pd


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
    keys_starts_ends = [
        ("Volume", "Volume:", "m3"),
        ("Flow", "Flow:", "m3/h"),
    ]
    out = {}
    for key, start, end in keys_starts_ends:
        pattern = rf"{start}\s*_*(\d+\.\d+)_*\s*{end}"
        match = re.search(pattern, text)
        out[key] = float(match.group(1)) if match else None
    return out


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
    return datetime.strptime(filename.split()[-1], "%d-%m-%Y.doc")


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
        with olefile.OleFileIO(file_path) as ole:
            word_stream = ole.openstream("WordDocument")
            content = word_stream.read().decode("latin-1", errors="ignore")
            y = content
            y = re.sub(
                r"[^\x0A,\u00c0-\u00d6,\u00d8-\u00f6,\u00f8-\u02af,\u1d00-\u1d25,\u1d62-\u1d65,\u1d6b-\u1d77,\u1d79-\u1d9a,\u1e00-\u1eff,\u2090-\u2094,\u2184-\u2184,\u2488-\u2490,\u271d-\u271d,\u2c60-\u2c7c,\u2c7e-\u2c7f,\ua722-\ua76f,\ua771-\ua787,\ua78b-\ua78c,\ua7fb-\ua7ff,\ufb00-\ufb06,\x20-\x7E]",
                r"*",
                y,
            )
            # Isolate the body of the text from the rest of the gibberish
            p = re.compile(r"\*{300,433}((?:[^*]|\*(?!\*{14}))+?)\*{15,}")
            result = re.findall(p, y)
            # remove * left in the capture group
            content = result[0].replace("*", "")
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


def create_monthly_range(start_date, end_date):
    """
    Create date ranges with monthly timestamps anchored at both the first and last days of each month.

    Parameters
    ----------
    start_date (str): Start date in 'YYYY-MM-DD' format
    end_date (str): End date in 'YYYY-MM-DD' format

    Returns
    -------
    tuple: (month_starts, month_ends) where each is a pd.DatetimeIndex
    """
    # Convert strings to datetime if needed
    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date)
    if isinstance(end_date, str):
        end_date = pd.to_datetime(end_date)

    # Create date range with month start frequency
    month_starts = pd.date_range(
        start=start_date - pd.DateOffset(months=1),
        end=end_date,
        freq="MS",  # Month Start frequency
    )

    # Create date range with month end frequency
    month_ends = pd.date_range(
        start=start_date,
        end=end_date + pd.DateOffset(months=1),
        freq="ME",  # Month End frequency
    )

    # Convert to lists for modification
    month_starts = month_starts.tolist()
    month_ends = month_ends.tolist()

    # Replace first date with actual start date
    month_starts[0] = start_date

    # Replace last date with actual end date
    month_ends[-1] = end_date

    # Convert back to DatetimeIndex
    month_starts = pd.DatetimeIndex(month_starts)
    month_ends = pd.DatetimeIndex(month_ends)

    return month_starts, month_ends


def interpolate_at_dates(known_series, target_dates):
    """
    Interpolate values at specific dates using a reference series.

    Parameters
    ----------
    known_series (pd.Series): Series with known values and DatetimeIndex
    target_dates (pd.DatetimeIndex): Dates at which to interpolate values

    Returns
    -------
    pd.Series: New series with interpolated values at target dates
    """
    # Combine known values with target dates
    # We set NaN for target dates to be interpolated
    combined_index = known_series.index.union(target_dates)
    combined_series = pd.Series(index=combined_index, dtype=float)

    # Fill in known values
    combined_series[known_series.index] = known_series

    # Interpolate
    interpolated = combined_series.interpolate(method="time")

    # Return only the values at target dates
    return interpolated[target_dates]


def main():
    r"""
    Extract values from Word documents and save them to a CSV file.

    The user is prompted to enter the folder path containing the Word documents and the output CSV file name.

    The extracted values are written to the CSV file with the following columns:
    - Filename: The name of the Word document file.
    - Date: The date extracted from the filename in 'YYYY-MM-DD' format.
    - Other columns: The extracted key-value pairs from the Word documents.
    C:\Users\tombb\OneDrive - PWN\Werkmappen\Wateroverlast duin\Taakkaart bemaling
    C:\Users\tombb\OneDrive - PWN\Werkmappen\Wateroverlast duin\out.csv
    """
    # folder_path = input("Enter the folder path containing the Word documents: ")
    folder_path = r"C:\Users\tombb\OneDrive - PWN\Gedeelde documenten - PWN.01218 - BE MOD grondwaterbeheersing\3. Omgeving\3.2 Vergunningen\Vergunning tijdelijke maatregelen\Taakkaart bemaling"
    # folder_path = r"C:\Users\tombb\OneDrive - PWN\Werkmappen\Wateroverlast duin\Taakkaart bemaling"
    output_file = r"C:\Users\tombb\OneDrive - PWN\Werkmappen\Wateroverlast duin\out.csv"
    output_file2 = r"C:\Users\tombb\OneDrive - PWN\Werkmappen\Wateroverlast duin\out2.csv"
    # output_file = input("Enter the name of the output CSV file: ")

    all_values = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".doc"):
            file_path = os.path.join(folder_path, filename)
            values = process_document(file_path)
            values["Filename"] = filename
            date = extract_date_from_filename(filename)
            if date:
                values["Date"] = date
            all_values.append(values)

    df = pd.DataFrame(all_values).sort_values(by=["Volume", "Date"]).set_index("Date")
    df.to_csv(output_file, index=False, sep=";", decimal=",")

    # df.Volume.diff()
    df = df.iloc[1:]
    starts, ends = create_monthly_range(df.index[0], df.index[-1])
    volume_start = interpolate_at_dates(df.Volume, starts)
    volume_end = interpolate_at_dates(df.Volume, ends)
    duration = (volume_end.index - volume_start.index) / pd.Timedelta(hours=1)
    volume_diff = volume_end.values - volume_start.values
    df2 = pd.DataFrame(
        data={
            "start_date": starts,
            "end_date": ends,
            "m3": volume_diff,
            "m3 sinds start": volume_end.values - volume_start.values[0],
            "m3/h": volume_diff / duration,
        },
        index=volume_end.index,
    )
    df2.to_csv(output_file2, index=False, sep=";", decimal=",")

    print(f"Values extracted from Word documents have been saved to '{output_file}'.")


if __name__ == "__main__":
    main()
