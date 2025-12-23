from .utils import iirfilt, detect_cross
import scipy
import pandas as pd
import numpy as np

def compute_icp(raw_icp, srate, date_vector = None, lowcut = 0.1, highcut = 10, order = 4, ftype = 'butter', peak_prominence = 0.5, h_distance_s = 0.3, rise_amplitude_limits = (0,20), amplitude_at_trough_low_limit = -10):
    """
    Detection of ICP pulses
    """
    icp_filt = iirfilt(raw_icp, srate, lowcut = lowcut, highcut = highcut, order = order, ftype = ftype)
    maximums,_ = scipy.signal.find_peaks(icp_filt, distance = int(srate * h_distance_s), prominence = peak_prominence)
    minimums,_ = scipy.signal.find_peaks(-icp_filt, distance = int(srate * h_distance_s), prominence = peak_prominence)
    if minimums[0] > maximums[0]: # first point detected has to be a minimum
        maximums = maximums[1:] # so remove the first maximum if is before first minimum
    if maximums[-1] > minimums[-1]: # last point detected has to be a minimum
        maximums = maximums[:-1] # so remove the last maximum if is after last minimum

    peak_index = maximums
    trough_index = minimums[np.searchsorted(minimums, peak_index) - 1]

    detection = pd.DataFrame()
    detection['trough_ind'] = trough_index
    detection['trough_time'] =  detection['trough_ind'] / srate
    next_trough_inds = trough_index[1:]
    next_trough_inds = np.append(next_trough_inds, np.nan)
    detection['next_trough_ind'] = next_trough_inds
    detection['next_trough_time'] =  detection['next_trough_ind'] / srate
    detection['peak_ind'] = peak_index
    detection['peak_time'] =  detection['peak_ind'] / srate
    detection = detection.iloc[:-1,:]
    detection['next_trough_ind'] = detection['next_trough_ind'].astype(int)
    detection['rise_duration'] = detection['peak_time'] - detection['trough_time']
    detection['decay_duration'] = detection['next_trough_time'] - detection['peak_time']
    detection['total_duration'] = detection['rise_duration'] + detection['decay_duration']

    detection['amplitude_at_trough'] = raw_icp[detection['trough_ind']]
    detection['amplitude_at_peak'] = raw_icp[detection['peak_ind']]
    detection['amplitude_at_next_trough'] = raw_icp[detection['next_trough_ind']]

    detection['rise_amplitude'] = detection['amplitude_at_peak'] - detection['amplitude_at_trough']
    detection['decay_amplitude'] = detection['amplitude_at_peak'] - detection['amplitude_at_next_trough']

    if not date_vector is None:
        detection['trough_date'] =  date_vector[detection['trough_ind']].astype('datetime64[ns]')
        detection['peak_date'] =  date_vector[detection['peak_ind']].astype('datetime64[ns]')
        detection['next_trough_date'] =  date_vector[detection['next_trough_ind']].astype('datetime64[ns]')
    
    #cleaning
    detection_clean = detection.copy()
    detection_clean = detection_clean[(detection_clean['amplitude_at_trough'] >= amplitude_at_trough_low_limit)]
    detection_clean = detection_clean[(detection_clean['rise_amplitude'] >= rise_amplitude_limits[0]) & (detection_clean['rise_amplitude'] <= rise_amplitude_limits[1]) ]

    return detection_clean.reset_index(drop = True)


def compute_abp(raw_abp, srate, date_vector = None, lowcut = 0.3, highcut = 10, order = 1, ftype = 'bessel', peak_prominence = 15, h_distance_s = 0.3, rise_amplitude_limits = (15,250), amplitude_at_trough_low_limit = 20, range_first_derivative = 3, compute_cardiac_output = True):
    """
    Detection of ABP (arterial blood pressure) pulses
    """
    assert not np.any(np.isnan(raw_abp)), 'Nans in ABP sig'
    abp_filt = iirfilt(raw_abp, srate, lowcut = lowcut, highcut = highcut, order = order, ftype = ftype)
    maximums,_ = scipy.signal.find_peaks(abp_filt, distance = int(srate * h_distance_s), prominence = peak_prominence)
    minimums,_ = scipy.signal.find_peaks(-abp_filt, distance = int(srate * h_distance_s), prominence = peak_prominence)
    if minimums[0] > maximums[0]: # first point detected has to be a minimum
        maximums = maximums[1:] # so remove the first maximum if is before first minimum
    if maximums[-1] > minimums[-1]: # last point detected has to be a minimum
        maximums = maximums[:-1] # so remove the last maximum if is after last minimum

    peak_index = maximums
    trough_index = minimums[np.searchsorted(minimums, peak_index) - 1]

    detection = pd.DataFrame()
    detection['trough_ind'] = trough_index
    detection['trough_time'] =  detection['trough_ind'] / srate
    next_trough_inds = trough_index[1:]
    next_trough_inds = np.append(next_trough_inds, np.nan)
    detection['next_trough_ind'] = next_trough_inds
    detection['next_trough_time'] =  detection['next_trough_ind'] / srate
    detection['peak_ind'] = peak_index
    detection['peak_time'] =  detection['peak_ind'] / srate
    detection = detection.iloc[:-1,:]
    detection['next_trough_ind'] = detection['next_trough_ind'].astype(int)
    detection['rise_duration'] = detection['peak_time'] - detection['trough_time']
    detection['decay_duration'] = detection['next_trough_time'] - detection['peak_time']
    detection['total_duration'] = detection['rise_duration'] + detection['decay_duration']

    detection['amplitude_at_trough'] = raw_abp[detection['trough_ind']]
    detection['amplitude_at_peak'] = raw_abp[detection['peak_ind']]
    detection['amplitude_at_next_trough'] = raw_abp[detection['next_trough_ind']]

    detection['rise_amplitude'] = detection['amplitude_at_peak'] - detection['amplitude_at_trough']
    detection['decay_amplitude'] = detection['amplitude_at_peak'] - detection['amplitude_at_next_trough']

    if not date_vector is None:
        detection['trough_date'] =  date_vector[detection['trough_ind']].astype('datetime64[ns]')
        detection['peak_date'] =  date_vector[detection['peak_ind']].astype('datetime64[ns]')
        detection['next_trough_date'] =  date_vector[detection['next_trough_ind']].astype('datetime64[ns]')
    
    #cleaning
    detection_clean = detection.copy()
    detection_clean = detection_clean[(detection_clean['amplitude_at_trough'] >= amplitude_at_trough_low_limit)]
    detection_clean = detection_clean[(detection_clean['rise_amplitude'] >= rise_amplitude_limits[0]) & (detection_clean['rise_amplitude'] <= rise_amplitude_limits[1]) ]
    detection_clean = detection_clean.reset_index(drop = True)


    if compute_cardiac_output:
        # dicrotic

        first_derivative = np.gradient(abp_filt)
        second_derivative = np.gradient(first_derivative)

        mask_amp = (abp_filt > np.quantile(abp_filt, 0.25)) & (abp_filt < np.quantile(abp_filt, 0.75))
        mask_1st_derivative = (first_derivative > -range_first_derivative) & (first_derivative < range_first_derivative) # search where first derivative is approachnig 0
        mask_2nd_derivative = second_derivative > 0 # search positive inflexion point

        mask = mask_amp & mask_1st_derivative & mask_2nd_derivative
        crossings = detect_cross(mask, 0.5)
        crossings['rises'] = crossings['rises'] + 1

        detection_clean['dicrotic_notch_ind'] = np.nan
        detection_clean['auc_cardiac_output'] = np.nan

        for i, row in detection_clean.iterrows():
            peak_ind = int(row['peak_ind'])
            next_trough_ind = int(row['next_trough_ind'])

            local_crossings = crossings[(crossings['rises'] > peak_ind) & (crossings['decays'] < next_trough_ind)]

            if local_crossings.shape[0] > 0:
                local_crossings = local_crossings.iloc[0,:]

                first_derivation_dicrotic_zone = first_derivative[local_crossings['rises']:local_crossings['decays']]
                change_derivative_sign_in_dicrotic_zone = (first_derivation_dicrotic_zone[:-1] <= 0) & (first_derivation_dicrotic_zone[1:] > 0)
                if np.any(change_derivative_sign_in_dicrotic_zone):
                    dicrotic_notch_ind = np.where(change_derivative_sign_in_dicrotic_zone)[0][0] + local_crossings['rises']
                else:
                    dicrotic_notch_ind = local_crossings['rises']

                local_sig_cardiac_output = raw_abp[peak_ind:dicrotic_notch_ind] - row['amplitude_at_trough']
                detection_clean.loc[i, 'dicrotic_notch_ind'] = dicrotic_notch_ind
                detection_clean.loc[i,'auc_cardiac_output'] = np.trapz(local_sig_cardiac_output)
        detection_clean['dicrotic_notch_time'] = detection_clean['dicrotic_notch_ind'] / srate
        detection_clean['dicrotic_notch_ind'] = detection_clean['dicrotic_notch_ind'].astype('Int64')
        detection_clean['dicrotic_notch_amplitude'] = raw_abp[detection_clean['dicrotic_notch_ind']]

        if not date_vector is None:
            detection_clean['dicrotic_notch_date'] =  date_vector[detection_clean['dicrotic_notch_ind']].astype('datetime64[ns]')
        
    return detection_clean.reset_index(drop = True)