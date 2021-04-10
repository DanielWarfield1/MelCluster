import pandas as pd
import numpy as np
import itertools
from sklearn.manifold import TSNE

#converts a loaded mel spectrogram into 

#reduces columns with "feat_" into 2 columns
def tsne_reduce_feats(df):
    x = df.values
    x_embedded = TSNE(n_components=2).fit_transform(x).astype(float)
    return x_embedded

#gets the mels out of a df
def get_mels(df):
    #getting mels
    mel_cols = [col for col in df.columns if 'mel_' in col]
    df_mel = df[mel_cols]

    #handling various issues
    df_mel = df_mel.astype('float')
    df_mel = df_mel.replace([np.inf, -np.inf], np.nan).fillna(0)

    return df_mel

#gets non mels out of df
def get_not_mels(df):
    not_mel_cols = [col for col in df.columns if 'mel_' not in col]
    return df[not_mel_cols]

#gets features out of df
def get_feats(df):
    #getting mels
    feat_cols = [col for col in df.columns if 'feat_' in col]
    df_feat = df[feat_cols]

    #handling various issues
    df_feat = df_feat.astype('float')
    df_feat = df_feat.replace([np.inf, -np.inf], np.nan).fillna(0)

    return df_feat

#gets non features out of df
def get_not_feats(df):
    not_cols = [col for col in df.columns if 'feat_' not in col]
    return df[not_cols]

#in a df, subsamples based on source file and beat index
def trim_by_beats(df, srcs, beat_idxs, verbose=False):
    
    if verbose: print('extracting {} ({})'.format(srcs, beat_idxs))

    #making sure list
    if not isinstance(beat_idxs, list):
        beat_idxs = [beat_idxs]
    if not isinstance(srcs, list):
        srcs = [srcs]

    #trimming down df to pertinent data
    df = df[df['src'].isin(srcs)]
    df = df[df['beatIdx'].isin(beat_idxs)]

    return df

#given a source file, beat index, and window size, gets n timestamps
def trim_by_beat_window(df, srcs, beat_idxs, win_size, verbose=False):

    if verbose: print('extracting {} ({}), with win size {}'.format(srcs, beat_idxs,win_size))

    #making sure list
    if not isinstance(beat_idxs, list):
        beat_idxs = [beat_idxs]
    if not isinstance(srcs, list):
        srcs = [srcs]

    res_df = None
    print(beat_idxs)
    print(srcs)
    idxs = [list(zip(x,beat_idxs))[0] for x in itertools.permutations(srcs,len(beat_idxs))]
    if verbose: print('getting these: {}'.format(idxs))
    for src, bIdx in idxs:
        if verbose: print('getting window for {} ({})'.format(src, bIdx))

        #gettig data at or past start of window
        win_df = df = df[df['src'] == src]
        win_df = win_df[win_df['beatIdx'] >= bIdx]

        #getting first n
        win_df = win_df.head(win_size)

        #appending
        if res_df is None:
            res_df = win_df
        else:
            res_df = res_df.append(win_df)

    return res_df

#takes mels (without flags, using get_mels) to summarize all each timestep
def summarize_timesteps(df):
    data = df.T.reset_index(drop=True)
    max_ = data.max().fillna(0)
    centroid = ((data.T*data.index).T.sum()/data.sum()).fillna(0)

    return pd.DataFrame({'max':max_, 'centroid':centroid})

#takes mel spectrogram data from loader
#for each beat, gets a window and featurizes it
def win_process_beats(df, win_size=200, verbose=False):

    if verbose: print('batch processing beats with windows of size {}'.format(win_size))

    res = None

    #getting info for next datum to detect change
    next_src = df['src'].shift()
    next_beat_idx = df['beatIdx'].shift()

    #iterating over all beats
    beats = df[(df['src'] != next_src) | (df['beatIdx'] != next_beat_idx)].index
    for beat in beats:
        #getting window after beat
        this_df = df.loc[beat:].head(win_size)

        #ensuring theres one source (for when multiple sources are selected)
        if len(this_df['src'].value_counts()) != 1:
            continue
        else:
            #aggregating features and flags
            this_feat = summarize_timesteps(get_mels(this_df)).values.flatten()
            this_feat = pd.Series(this_feat, index = ['feat_{}'.format(idx) for idx, _ in enumerate(this_feat)]) 
            this_flags = get_not_mels(df).loc[beat]
            this_data = this_flags.append(this_feat)
            if res is None:
                res = pd.DataFrame(this_data).T
            else:
                res = res.append(this_data, ignore_index=True)

    return res.replace([np.inf, -np.inf], np.nan).fillna(0)

#plots featurized data from batch process
#for each beat, gets a window, featurizes it, then t-sne reduces the features
def tsne_process_beats(df, verbose=False):
    tsne_df = pd.DataFrame(tsne_reduce_feats(get_feats(df)), columns = ['tsne_0', 'tsne_1'])
    flags = get_not_feats(df)
    return pd.concat([tsne_df, flags], axis=1)

#calculates the linear distance of all points relative to a single point
#assumes all input data is used in column form
def calc_dist_from(df, idx):
    df = df - df.loc[idx]
    s = df.apply(np.linalg.norm, axis=1)
    return s

if __name__ == '__main__':
    import MelCluster.loader as loader
    import MelCluster.plotter as plotter
    import matplotlib.pyplot as plt
    import seaborn as sns

    #basic featurization
    if False:
        files = loader.get_files_dialog(verbose=True)
        df = loader.load_from_txt(files, verbose=True)
        df = trim_by_beat_window(df, files[0].split('/')[-1], [3], 200, verbose = True).reset_index(drop=True)
        summary = summarize_timesteps(get_mels(df))
        ax = plotter.plot_mel(df, verbose=True, show=False)
        summary.plot(ax=ax)
        plt.show()

    #batch featurization
    if False:
        files = loader.get_files_dialog(verbose=True)
        df = loader.load_from_txt(files, verbose=True).reset_index(drop=True)
        df = win_process_beats(df, win_size=200, verbose=True)
        df = tsne_process_beats(df)
        print(df.columns)
        sns.scatterplot(data=df, x='tsne_0', y='tsne_1', style='plug_in', size='pitch', hue='src')
        plt.show()

    #N closest
    if False:
        index_of_interest = 2

        files = loader.get_files_dialog(verbose=True)
        df = loader.load_from_txt(files, verbose=True).reset_index(drop=True)
        df = win_process_beats(df, win_size=200, verbose=True)
        df['distance'] = calc_dist_from(get_feats(df),index_of_interest)
        df = tsne_process_beats(df)
        ax = sns.scatterplot(data=df, x='tsne_0', y='tsne_1', style='plug_in', size='distance', hue='src')
        ax = sns.scatterplot(ax=ax, data=df.loc[[index_of_interest]], x='tsne_0', y='tsne_1',s=1000,alpha=0.5)
        plotter.label_closest_n(df, 20, ax, size=10)
        print(df.columns)
        plt.show()

    #plot N closest mels
    if True:
        index_of_interest = 2
        n=12
        files = loader.get_files_dialog(verbose=True)
        df_mel = loader.load_from_txt(files, verbose=True).reset_index(drop=True).dropna()
        df = win_process_beats(df_mel, win_size=100, verbose=True)
        df['distance'] = calc_dist_from(get_feats(df),index_of_interest)
        close_df = df.nsmallest(n, ['distance'])
        plotter.plot_mel_set_by_window(df_mel, close_df, win_size=100, verbose=True)
