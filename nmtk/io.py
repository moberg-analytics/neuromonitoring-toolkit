import numpy as np
import pycns
from pathlib import Path

def load_with_pycns(folder, stream_name, index_selection_slice=None, datetimes_selection_slice=None):
    folder = Path(folder)
    cns_reader = pycns.CnsReader(folder)

    stream = cns_reader.streams[stream_name]

    if datetimes_selection_slice is not None:
        signal, times = stream.get_data(sel=datetimes_selection_slice, with_times=True, apply_gain=True, time_as_second=True)
    elif index_selection_slice is not None:
        signal, times = stream.get_data(isel=index_selection_slice, with_times=True, apply_gain=True, time_as_second=True)
    else:
        signal, times = stream.get_data(with_times=True, apply_gain=True, time_as_second=True)

    srate = 1 / np.median(np.diff(times))

    if 'EEG' in stream_name:
        channel_names = stream.channel_names
        return signal, srate, channel_names
    else:
        return signal, srate

if __name__ == "__main__":
    print(load_with_pycns(folder = '/crnldata/REA_NEURO_MULTI_ICU/raw_data/MF12/', stream_name='CO2'))