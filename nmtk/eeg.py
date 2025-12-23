import numpy as np
import pandas as pd

def compute_spectral_entropy(power, normalized = True):
    # Normalize the power spectrum
    power /= np.sum(power)
    # Compute entropy
    entropy = -np.sum(power * np.log2(power))
    if normalized:
        entropy = entropy / np.log2(power.size)
    return entropy


def compute_suppression_ratio(sig, srate, threshold_µV = 5, win_size_sec_epoch = 0.240, win_size_sec_moving = 63):
    mask_not_suppressed = np.abs(sig) > threshold_µV
    t = np.arange(sig.size) / srate
    start_wins = np.arange(0, t[-1], win_size_sec_epoch)
    rows = []
    for i, start_win in enumerate(start_wins):
        stop_win = start_win + win_size_sec_epoch
        start_win_ind = int(start_win * srate)
        stop_win_ind = start_win_ind + int(win_size_sec_epoch * srate)
        if stop_win_ind > sig.size:
            break
        mask_not_suppressed_win = mask_not_suppressed[start_win_ind:stop_win_ind]
        is_suppressed = 0 if np.sum(mask_not_suppressed_win) > 0 else 1
        rows.append([start_win, stop_win, is_suppressed])
    df_suppression = pd.DataFrame(rows, columns = ['start_t','stop_t','is_suppressed'])

    if t[-1] < win_size_sec_moving:
        suppression_ratio = df_suppression['is_suppressed'].mean()
        start_wins = np.array([0])
    else:
        start_wins = np.arange(0, t[-1], win_size_sec_moving)
        suppression_ratio = np.zeros(start_wins.size)
        for i, start_win in enumerate(start_wins):
            stop_win = start_win + win_size_sec_moving
            if stop_win > t[-1]:
                stop_win = t[-1]
            local_df_suppression = df_suppression[(df_suppression['start_t'] >= start_win) & (df_suppression['start_t'] < stop_win)]
            suppression_ratio[i] = local_df_suppression['is_suppressed'].mean()
    suppression_ratio *= 100 # transform ratio into percentage
    return suppression_ratio, start_wins