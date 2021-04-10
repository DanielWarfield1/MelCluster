import matplotlib.pyplot as plt
import MelCluster.processor as processor

#plots data in a mel spectrogram
def plot_mel(df, ax_title=None, ax=None, verbose=False, show=True, t_on_y=False):

    if ax is None:
        ax = plt.axes()

    #getting mels
    df_mel = processor.get_mels(df)

    #getting when beats start
    next_src = df['src'].shift()
    next_beat_idx = df['beatIdx'].shift()
    beats = df[(df['src'] != next_src) | (df['beatIdx'] != next_beat_idx)]

    #plotting image
    ax.imshow(df_mel.T,origin='lower')

    if verbose: print('plotting beats')
    for idx in beats.index:
        ax.axvline(idx, 0, len(df_mel.columns), linewidth=1, color='r')

    #misc
    if ax_title is not None:
        if t_on_y:
            plt.ylabel(ax_title,rotation='horizontal',ha='right')
        else:
            plt.xlabel(ax_title)

    if show:
        plt.show()

    return ax

#given a mel spectrogram df, a list of source files, and a list of beats,
#plot those in the order they appear in the df
#(really only useful with 1 src and a list of continuous beat_idxs)
def plot_mel_by_beats(df, srcs, beat_idxs, ax=None, verbose=False):

    #getting pertinent data
    df = processor.trim_by_beats(df, srcs, beat_idxs, verbose).reset_index(drop=True)

    if verbose: print('plotting {} ({})'.format(srcs, beat_idxs))
    return plot_mel(df, srcs, ax, verbose)

def plot_mel_by_window(df, srcs, beat_idxs, win_size, ax=None, verbose=False, show=True, t_on_y=False, title_pre=''):

    df = processor.trim_by_beat_window(df, srcs, beat_idxs, win_size, verbose).reset_index(drop=True)

    if verbose: print('plotting {} ({})'.format(srcs, beat_idxs))
    return plot_mel(df, title_pre+str(srcs), ax, verbose, show, t_on_y)

#draws text on points corresponding to their source and beatIdx
#assumes an input of a tsne clustering
def label_points(df, ax, size=5, short=False):
    for idx,point in df.iterrows():
        if short:
            ax.text(x=point['tsne_0'],y=point['tsne_1'],s=str(idx), 
                fontdict=dict(color='red',size=size))
        else:
            ax.text(x=point['tsne_0'],y=point['tsne_1'],s=str(idx) + ') ' + point['src'] + ', ' + str(point['beatIdx']), 
                fontdict=dict(color='red',size=size))

#assums a tsne df with a distance channel
def label_closest_n(df, n, ax, size=5, short=False, short_label_all=False):
    df_close = df.nsmallest(n, ['distance'])
    label_points(df_close, ax, size, short)

    if short_label_all:
        label_points(df.drop(index=df_close.index), ax, size, True)

#plots a set of mels, based on a list of valid beats, by window
#df is a mel spectrogram df, beat_df is a df containing src and beatIdx
def plot_mel_set_by_window(df, beat_df, win_size=200, verbose=False):

    n = len(beat_df.index)

    idx=0
    plt.figure()
    for aggIdx, row in beat_df.iterrows():
        if verbose: print('plotting ',idx)
        ax = plt.subplot2grid([n,2], (idx,1), rowspan=1, colspan=1)
        idx+=1
        # equivalent but more general
        plot_mel_by_window(df, row.src, row.beatIdx, win_size=win_size, ax=ax, verbose=verbose, show=False, t_on_y=True, title_pre='({}), beat: {}, src:'.format(aggIdx, row.beatIdx))

    plt.show()


if __name__ == '__main__':
    import MelCluster.loader as loader

    files = loader.get_files_dialog(verbose=True)
    df = loader.load_from_txt(files, verbose=True)
    print(df)
    print('plotting')
    print(files[0].split('/')[-1])
    print('========BY BEATS========')
    plot_mel_by_beats(df, files[0].split('/')[-1], [6,7,8], ax=None, verbose=True)
    print('========BY WINDOW========')
    plot_mel_by_window(df, files[0].split('/')[-1], 6, 600, ax=None, verbose=True)