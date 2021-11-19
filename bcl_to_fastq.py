from datetime import date
from sample_sheet import SampleSheet, Sample
import pandas as pd
import logging
import warnings
import os
import numpy as np

# Catches all warnings and write them in a text file 
# logging.basicConfig(filename="logfile.txt",level=logging.DEBUG)
# logging.captureWarnings(True)

# warning_file = open("logfile.txt", "w")

# def mywarning(message, category, filename, lineno, file=None, line=None):
#     warning_file.write(warnings.formatwarning(message, category, filename, lineno, file))

# warnings.showwarning = mywarning


def compliment(word):
    """This function takes a string and return the reverse-complement of the string.

    Args:
        word (str): a word, eg, TAGTAGGACA

    Returns:
        str: eg, TGTCCTACTA
    """
    try:
        if not word.islower():
            complements = {'A':'T', 'T':'A','G':'C','C':'G'}
            seq = word[::-1]
            letters = [complements[base] for base in seq]
            return ("").join(letters)
        else:
            return "index2"
    except:
        return np.nan

def reverse_comp(file):
    """ This function take a csv file and process only index2 columns that is suppose to be presene from row 20

    Args:
        file (csv): a csv file
    """
    df = pd.read_csv(file)
    df['Unnamed: 9'] = df.loc[:, 'Unnamed: 9'].apply(lambda x : compliment(x))
    conv_filename = os.path.basename(file).replace("bclconvert","bcl2fastqformat")
    header_list = ['[Header]', "", "", "", "", "", "", "", "", "", "", ""]
    df.to_csv(f"{os.getcwd()}/dump/downloads/{conv_filename}", header=header_list, index=False,)


def bcl_to_fastq(input_file, reverse_complement = False):
    """This function takes a csv file and extract the specific data from it and create a new csv file as per the required fastq format

    :param input_file: A csv file
    :type input_file: string
    """
    
    sample_sheet = SampleSheet()

    flag = 0

    input_info_list = []
    input_sample_list = []


    # Extracting specific lines as per the given condtion from the file and appending the values in two different lists
    with open(input_file) as infile:

        for entry in infile:

            entry = entry.strip()
            if "[BCLConvert_Data]" in entry:

                flag = 1

            if "[Cloud_Settings]" in entry:
                flag = 2
            
            if flag == 0:
                input_info_list.append(entry)

            if flag == 1:
                if len(entry) > 0:
                    input_sample_list.append(entry)

    # Creating a list
    input_info_data = [item.split(",") for item in input_info_list]

    # Creating a pandas dataframe from list input_info data
    df_input_info = pd.DataFrame(input_info_data)


    # Creating dictionary from lines with values [Header] to [BCLConvert_Data] using df_input_info dataframe
    mydict = {row[0] : row[1] for _, row in df_input_info.iterrows()}


    # Check after how many rows the header starts
    skip_row_for_header = len(input_info_data)+1

    # Reading the csv file with specific columns and header location using pandas
    input_sample_data = pd.read_csv(input_file, skiprows=skip_row_for_header, usecols=[0,1,2])

    # Storing length of the dataframe in a variable
    i_len = len(input_sample_list)

    # Extracting reqruied data using the dataframe length
    df = input_sample_data.iloc[0:i_len-2,:]

    # Creating vairable for each column
    fc = df.iloc[:, 0]
    sc = df.iloc[:, 1]
    tc = df.iloc[:, 2]

    # [Header] section
    # Adding an attribute with spaces must be done with the add_attr() method
    sample_sheet.Header['IEMFileVersion'] = mydict['FileFormatVersion']
    sample_sheet.Header['Investigator Name'] = ''
    sample_sheet.Header['Experiment Name'] = ''
    sample_sheet.Header['Date'] = date.today()
    sample_sheet.Header['Workflow'] = ''
    sample_sheet.Header['Application'] = ''
    sample_sheet.Header['Instrument Type'] = ''
    sample_sheet.Header['Assay'] = ''
    sample_sheet.Header['Index Adapters'] = ''
    sample_sheet.Header['Description'] = ''
    sample_sheet.Header['Chemistry'] = ''

    # Specify a paired-end kit with 151 template bases per read
    sample_sheet.Reads = [mydict['Read1Cycles'], mydict['Read2Cycles']]

    # Padding values for columns i7_Index_ID and i5_Index_ID
    i7_Index_ID = []
    i5_Index_ID = []
    for i in range(1,len(fc)+1):
        j = f"i7_Index_ID_{i}"
        k = f"i5_Index_ID_{i}"
        i7_Index_ID.append(j)
        i5_Index_ID.append(k)

    # Add a single-indexed sample with both a name, ID, and index
    for i_fc, i_sc, i_tc, i7, i5 in zip(fc, sc, tc, i7_Index_ID, i5_Index_ID):
        sample = Sample(dict(Lane = '',Sample_ID= i_fc, Sample_Name = i_fc, Sample_Plate = '', Sample_Well = '', Index_Plate_Well = '', I7_Index_ID = i7, index= i_sc, I5_Index_ID = i5, index2= i_tc, Sample_Project = '', Description = ''))
        sample_sheet.add_sample(sample)
        conv_filename = os.path.basename(input_file).replace("bclconvert","bcl2fastqformat")
    
    if reverse_complement:        

        # Write the Sample Sheet!
        sample_sheet.write(open(f"{os.getcwd()}/dump/stage/{conv_filename}", 'w'))

        # Reverse compliment of the sample sheet's index2 values
        reverse_comp(f"{os.getcwd()}/dump/stage/{conv_filename}")
    
    else:
        # Write the Sample Sheet!
        sample_sheet.write(open(f"{os.getcwd()}/dump/downloads/{conv_filename}", 'w'))

    return conv_filename

if __name__=="__main__":
    bcl_to_fastq(f"{os.getcwd()}/sample_sheet_bclconvert.csv", True)
