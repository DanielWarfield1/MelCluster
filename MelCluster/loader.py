from tkinter import *
from tkinter import filedialog
import pandas as pd

#gets a list of files from a dialog
def get_files_dialog(verbose = False):
    
    if verbose: print('Opening file browser...')
    
    #not making tkinter window
    Tk().withdraw()
    #opening file dialog
    file_path_string = filedialog.askopenfilenames()
    
    if verbose: print('files selected: {}'.format(file_path_string))

    return file_path_string

#loads and parses from .txt files
#calls various versions
def load_from_txt(file_paths, verbose=False, version=2):
    
    if version == 1:
        if verbose: print('')
        try:
            return load_from_txt_v1(file_paths, verbose)
        except KeyboardInterrupt:
            raise
        except Exception  as e:
            print(IOError('Error loading input file'))
            raise e
    elif version == 2:
        if verbose: print('')
        try:
            return load_from_txt_v2(file_paths, verbose)
        except KeyboardInterrupt:
            raise
        except Exception  as e:
            print(IOError('Error loading input file'))
            raise e
    else:
        raise ValueError('Invalid loading version')

"""
version 1:
    - starts with a name (disregards, uses actual file name)
    - each typical line contains 25 floats (25 mels)
    representing one timestep
    - beats are annotated by 
    FLAG plug-in: (plugin name) preset: (int) pitch: (int) velocity: (int)
"""
def load_from_txt_v1(file_paths, verbose=False, use_full_path_name=False, fill_missing_mels=True):

    agg_df = None

    for file_path in file_paths:

        if verbose: print('loading data from {}'.format(file_path))

        #getting source file flag
        if use_full_path_name:
            source_file = file_path
        else:
            source_file = file_path.split('/')[-1]

        #presetting other flags
        beat_index = -1
        plug_in = None
        preset = None
        pitch = None
        velocity = None

        with open (file_path, "r") as myfile:

            #reading file (skipping name line)
            data = myfile.read().splitlines()

            #creating df for this file
            num_points = len([line for line in data[1:] if 'FLAG' not in line])
            df = pd.DataFrame(columns = ['mel_{}'.format(idx) for idx in range(25)]+ \
                ['src', 'beatIdx', 'plug_in', 'preset', 'pitch', 'velocity'],
                index=range(num_points+1))

            dataidx = -1
            for lineidx,line in enumerate(data[1:]):
                if verbose and dataidx%1000 == 0:
                    print(' - datum {}'.format(dataidx))

                #found a new beat
                if 'FLAG' in line:

                    try:
                        #updating flags
                        split = line.split(': ')
                        beat_index+=1
                        plug_in = split[1].split(' ')[0]
                        preset = int(split[2].split(' ')[0])
                        pitch = int(split[3].split(' ')[0])
                        velocity = int(split[4])
                        continue
                    except Exception as e:
                        print('error parsing, check for missing value or out of order')
                        print(line)
                        raise e

                #data row
                else:
                    dataidx +=1
                    #getting mels
                    mels = [float(item) for item in line.split()]
                    #adding missing zero value mels to the end
                    if fill_missing_mels:
                        for missing in range(25-len(mels)):
                            mels.append(0)
                    #adding to df
                    try:
                        df.loc[dataidx] = mels + [source_file, beat_index, plug_in, preset, pitch, velocity]
                    except Exception as e:
                        if verbose: print('error on line {}'.format(lineidx))

            #aggregating output
            if agg_df is None:
                agg_df = df
            else:
                if verbose: print('df appended')
                agg_df = agg_df.append(df)
    if verbose:
        print('loaded data!')
        print('aggregate df shape: {}'.format(agg_df.shape))
        print('aggregate df head: ')
        print(agg_df.head())

    return agg_df


"""
version 2:
    - starts with a name (disregards, uses actual file name)
    - each typical line contains 25 floats (25 mels)
    representing one timestep
    - beats are annotated by 
    FLAG instrument: () pitch: () velocity: ()

"""
def load_from_txt_v2(file_paths, verbose=False, use_full_path_name=False, fill_missing_mels=True):

    agg_df = None

    for file_path in file_paths:

        if verbose: print('loading data from {}'.format(file_path))

        #getting source file flag
        if use_full_path_name:
            source_file = file_path
        else:
            source_file = file_path.split('/')[-1]

        #presetting other flags
        beat_index = -1
        instrument = None
        pitch = None
        velocity = None

        with open (file_path, "r") as myfile:

            #reading file (skipping name line)
            data = myfile.read().splitlines()

            #creating df for this file
            num_points = len([line for line in data[1:] if 'FLAG' not in line])
            df = pd.DataFrame(columns = ['mel_{}'.format(idx) for idx in range(25)]+ \
                ['src', 'beatIdx', 'instrument', 'pitch', 'velocity'],
                index=range(num_points+1))

            dataidx = -1
            for lineidx,line in enumerate(data[1:]):
                if verbose and dataidx%1000 == 0:
                    print(' - datum {}'.format(dataidx))

                #found a new beat
                if 'FLAG' in line:

                    try:
                        #updating flags
                        beat_index+=1
                        split = line.split(': ')
                        instrument = split[1].split(' ')[0]
                        pitch = int(split[2].split(' ')[0])
                        velocity = int(split[3])

                        continue
                    except Exception as e:
                        print('error parsing, check for missing value or out of order')
                        print(line)
                        raise e

                #data row
                else:
                    dataidx +=1
                    #getting mels
                    mels = [float(item) for item in line.split()]
                    #adding missing zero value mels to the end
                    if fill_missing_mels:
                        for missing in range(25-len(mels)):
                            mels.append(0)
                    #adding to df
                    try:
                        df.loc[dataidx] = mels + [source_file, beat_index, instrument, pitch, velocity]
                    except Exception as e:
                        if verbose: print('error on line {}'.format(lineidx))

            #aggregating output
            if agg_df is None:
                agg_df = df
            else:
                if verbose: print('df appended')
                agg_df = agg_df.append(df)
    if verbose:
        print('loaded data!')
        print('aggregate df shape: {}'.format(agg_df.shape))
        print('aggregate df head: ')
        print(agg_df.head())

    return agg_df

if __name__ == '__main__':
    
    files = get_files_dialog(verbose=True)
    df = load_from_txt(files, verbose=True, version=2)
    print(df)