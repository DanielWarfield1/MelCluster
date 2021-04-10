# MelCluster
Library and python programs for  Mel spectrogram data clustering

This is minimal documentation primarily for usage.

## Installing

from a cloned repo

> ...\path\to\pip\\...\pip install -e ...\path\to\library\\...MelCluster

from github directly

> ...\path\to\pip\\...\pip install git+https://github.com/DanielWarfield1/MelCluster

## Files

### loader

contains functions for parsing Mel spectrogram data. New versions can be added to adjust for different file versions. adding these to __load_from_txt__ _should_ allow new file types to be added without significant modification

### Plotter

Set of helper functions, primarily for annotation of scatter plots and plotting mel spectrogram data. Most scatterplot functionality is handled by __seaborn__

### Processor

A set of functions for manipulating certain flags in pandas data frames, as well as handling trimming of beats, mel spectrogram summarizations, batch processing, tsne reduction, and distance calculation

### Program

A file which, when run in a shell, employs functionality from the previous modules. It includes a few high level wrappers for functionality which should be tied together, and a state machine in __main__ which accepts inputs from the user.

## Program Usage

if the current value is appropriate when prompted (in parentheses) simply press enter to accept it. Graphs must be closed to continue.

### Load and preprocess: L

this input opens a tkinter window, allowing the user to multiselect files to input. the tkinter window outputs a list of full paths as strings. _note: this version does not include an updated loader, and thus inconsistent flags may result in an error_

### Toggl verbose: V

toggles verbose output. In general, verbose output should probably remain on.

### Set key variables: S

changes key variables. After data is loaded this will require re-computation.

- window size of mel spectrogram being analyzed (larger=more computation)
- the index of the point being analyzed (must be valid)

### Config Plot: C

changes variables which influence visualization

- number of points influences both the tsne plot and mel spectrogram plot. Generally between 5 and 40
- various stylings, which can be viewed here: https://seaborn.pydata.org/generated/seaborn.scatterplot.html
- short annotate all: if all points show their index
- verbose output (same as toggle)
- short annotate for n closest: do the close values show just their index (t), or more information (f)

### Plot scatter from n closest: PS

plots a scatterplot in a matplotlib axis which displays a t-sne cluster, as well as data pertaining to the point being analyzed. There are navigation tools in the bottom left

### Plot mel spec from n closest: PS

plots the mel spec for the n closest, which correspond to the t-sne plot from running __PS__. The labels are (_index in data_), beat: _index of beat in source file_, src: _source file_. this can be somewhat modified by adjusting setting sin the bottom left.

## Notes:

### Loader modification

the loader is expected to output a pandas dataframe, where each row corresponds to a timestamp. The columns have the following format:

- mel_0 through mel_24, for the 25 mels
- src: the source file
- beatIdx: the index of the beat in the source file
- various other flags

I have yet to test another loader, so It's unknown if some of the other included flags are needed for operation. In general, the mel flags, the src flag, and the beatIdx flag are the only ones that are generally used.

a loader modification should be injectable into __load_from_txt__, and by changing the default version flag, the new load scheme should be adopted by the entire library.



