import numpy as np
import scipy
import pandas as pd

def notch_filter(sig, srate, bandcut = (48,52), order = 4, ftype = 'butter', axis = -1):

    """
    IIR-Filter to notch/cut 50 or 60 Hz of a signal
    """
    band = [bandcut[0], bandcut[1]]
    Wn = [e / srate * 2 for e in band]
    sos = scipy.signal.iirfilter(order, Wn, analog=False, btype='bandstop', ftype=ftype, output='sos')
    filtered_sig = scipy.signal.sosfiltfilt(sos, sig, axis=axis)
    return filtered_sig

def iirfilt(sig, srate, lowcut=None, highcut=None, order = 4, ftype = 'butter', axis = -1):
    """
    IIR-Filter of signal
    -------------------
    Inputs : 
    - sig : 1D numpy vector
    - srate : sampling rate of the signal
    - lowcut : lowcut of the filter. Lowpass filter if lowcut is None and highcut is not None
    - highcut : highcut of the filter. Highpass filter if highcut is None and low is not None
    - order : N-th order of the filter (the more the order the more the slope of the filter)
    - ftype : Type of the IIR filter, could be butter or bessel or other ..
    """

    if lowcut is None and not highcut is None:
        btype = 'lowpass'
        cut = highcut

    if not lowcut is None and highcut is None:
        btype = 'highpass'
        cut = lowcut

    if not lowcut is None and not highcut is None:
        btype = 'bandpass'

    if btype in ('bandpass', 'bandstop'):
        band = [lowcut, highcut]
        assert len(band) == 2
        Wn = [e / srate * 2 for e in band]
    else:
        Wn = float(cut) / srate * 2

    filter_mode = 'sos'
    sos = scipy.signal.iirfilter(order, Wn, analog=False, btype=btype, ftype=ftype, output=filter_mode)
    filtered_sig = scipy.signal.sosfiltfilt(sos, sig, axis=axis)

    return filtered_sig


def detect_cross(sig, thresh):
    rises, = np.where((sig[:-1] <=thresh) & (sig[1:] >thresh)) # detect where upward crossing
    decays, = np.where((sig[:-1] >=thresh) & (sig[1:] <thresh)) # detect where downward crossing
    if rises.size > 0 and decays.size > 0:
        if rises[0] > decays[0]: # first point detected has to be a rise
            decays = decays[1:] # so remove the first decay if is before first rise
        if rises[-1] > decays[-1]: # last point detected has to be a decay
            rises = rises[:-1] # so remove the last rise if is after last decay
        return pd.DataFrame.from_dict({'rises':rises, 'decays':decays}, orient = 'index').T
    else:
        return None