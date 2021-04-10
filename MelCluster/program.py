import MelCluster.loader as loader
import MelCluster.plotter as plotter
import MelCluster.processor as proc
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

#defining globals
n = 10
win_size=200
idx = 0
short = False
verbose = True
short_label_all = True

#plot config globals
plt_style='plug_in'
plt_size='distance'
plt_hue='src'

#high level function that loads
def load_win():

    global n, win_size, idx, short, verbose

    files = loader.get_files_dialog(verbose=verbose)
    df_mel = loader.load_from_txt(files, verbose=verbose).reset_index(drop=True)

    return df_mel

#calculates the distance from the reference point
def calculate_distance(df):

    global n, win_size, idx, short, verbose

    df['distance'] = proc.calc_dist_from(proc.get_feats(df),idx)
    return df

#summarizes and reduces to tsne
def summarize(df_mel):

    global n, win_size, idx, short, verbose

    df_sum = proc.win_process_beats(df_mel, win_size=win_size, verbose=verbose)
    df_sum = calculate_distance(df_sum)

    return df_sum

#reduces summarized data to 2d w/ tsne
def tsne_reduce(df_sum):
    df_tsne = proc.tsne_process_beats(df_sum)

    return df_tsne

#high level function that plots tsne and labels the closest n points to a certain point
def plot_n_closest(df):

    global n, win_size, idx, short, verbose, short_label_al

    ax = sns.scatterplot(data=df, x='tsne_0', y='tsne_1', style=plt_style, size=plt_size, hue=plt_hue)
    ax = sns.scatterplot(ax=ax, data=df.loc[[idx]], x='tsne_0', y='tsne_1',s=1000,alpha=0.5)
    df_close = df.nsmallest(n, ['distance'])
    ax = sns.scatterplot(ax=ax, data=df_close, x='tsne_0', y='tsne_1',s=500,alpha=0.1)
    plotter.label_closest_n(df, n, ax, size=10, short=short, short_label_all=short_label_all)
    plt.show()

#prints a lookup where the index corresponds to a specific point
def print_index_list(df):

    global n, win_size, idx, short, verbose

    pd.set_option('max_colwidth', None)
    pd.set_option('max_columns', None)
    pd.set_option('max_rows', None)

    print(df[['src','beatIdx', 'distance']])

    pd.set_option('max_colwidth', 50)
    pd.set_option('max_columns', None)
    pd.set_option('max_rows', 15)

#plots the mel spectrogram found from n closest
def plot_n_closest_mel(df, df_mel):

    global n, win_size, idx, short, verbose

    close_df = df.nsmallest(n, ['distance'])
    plotter.plot_mel_set_by_window(df_mel, close_df, win_size, verbose=verbose)
        
#prompts the user to set variables
def set_key_vars(df_sum, df_mel, execute=True):

    global n, win_size, idx, short, verbose, short_label_all

    try:    
        win_size = int(input('window size ({}): '.format(win_size)))
        if execute: 
            print('re-featurizing...')
            df_sum = summarize(df_mel)
            print(df_sum)
    except:
        print('invalid, retaining value')
    try:
        idx = int(input('index of point being analyzed ({}): '.format(idx)))
        if execute:
            print('recalculating distances...')
            df_mel = calculate_distance(df_mel)
    except Exception as e:
        print('invalid, retaining value')

    print('\n')

    return df_sum, df_mel

#configures plotting
def set_plt_config(df):

    global plt_style, plt_size, plt_hue
    global n, win_size, idx, short, verbose, short_label_all

    print('available columns: ')
    cols = list(df.columns)
    print(cols)

    try:
        n = int(input('number of points to analyze - n ({}): '.format(n)))
    except:
        print('invalid, retaining value')

    try:
        inval = input('plt_style ({}): '.format(plt_style))
        if inval not in cols:
            raise Exception('')
        plt_style = inval
    except Exception as e:
        print('invalid, retaining value')

    try:
        inval = input('plt_size ({}): '.format(plt_size))
        if inval not in cols:
            raise Exception('')
        plt_size = inval
    except:
        print('invalid, retaining value')

    try:
        inval = input('plt_hue ({}): '.format(plt_hue))
        if inval not in cols:
            raise Exception('')
        plt_hue = inval
    except:
        print('invalid, retaining value')

    try:
        inval = input('short annotate all ({}): '.format(short_label_all)).lower()
        if inval == '':
            raise Exception('')
        short_label_all = inval in ("yes", "true", "t", "1")
    except:
        print('invalid, retaining value')

    try:
        inval = input('verbose ({}): '.format(verbose)).lower()
        if inval == '':
            raise Exception('')
        verbose = inval in ("yes", "true", "t", "1")
    except:
        print('invalid, retaining value')

    try:
        inval = input('short annotation for n closest ({}): '.format(short)).lower()
        if inval == '':
            raise Exception('')
        short = inval in ("yes", "true", "t", "1")
    except:
        print('invalid, retaining value')

#run the program
def main():
    global n, win_size, idx, short, verbose, short_label_all
    global plt_style, plt_size, plt_hue

    df_mel = None
    df_sum = None
    df_tsne = None

    while True:
        print('\n======Requesting input======\n')
        ans = input('Load and preprocess: L\nToggle verbose: V\nSet key variable: S\nExit: X\n\nInput: ').lower()

        #loading
        if ans=='l':

            print('\n======Requesting input files======')
            print('note: multi select is allowed')
            df_mel = load_win()
            df_sum = summarize(df_mel)
            df_tsne = tsne_reduce(df_sum)
            print('loading successful')
            print('\n')

            #manipulating loaded data
            while True:
                print('\n======Requesting input======\n')
                ans = input('Load and preprocess: L\nSet key variable: S\nPlot scatter from n closest: PS\nPlot mel spec from n closest: PM\nConfig Plot: C\nExit: X\n\nInput: ').lower()
                if ans=='ps':
                    df_tsne = tsne_reduce(df_sum)
                    print('======Point Lookup======')
                    print_index_list(df_tsne)
                    plot_n_closest(df_tsne)

                if ans=='pm':
                    plot_n_closest_mel(df_sum, df_mel)
                elif ans=='l':
                    break
                elif ans=='c':
                    df_tsne = tsne_reduce(df_sum)
                    set_plt_config(df_tsne)
                elif ans=='s':
                    df_sum, df_mel = set_key_vars(df_sum, df_mel)

                elif ans=='x':
                    ans = input('Are you sure you want to exit? (y/n):\n\nInput: ')
                    if ans == 'y':
                        return


        elif ans=='v':
            verbose = not verbose
            print('\nVerbose now {}\n'.format(verbose))

        elif ans=='s':

            df_sum, df_mel = set_key_vars(df_sum, df_mel, execute=False)

        #exiting
        elif ans=='x':
            ans = input('Are you sure you want to exit? (y/n):\n\nInput: ')
            if ans == 'y':
                return


if __name__ == '__main__':
    main()