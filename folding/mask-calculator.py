import argparse
import numpy as np
from sigpyproc.readers import FilReader

def get_args():
    parser = argparse.ArgumentParser(description='Calculate channes to mask for a given filterbank file')
    parser.add_argument('--filename', '-p', type=str, help='Path to filterbank file', required=True)
    parser.add_argument('--freq_min',  '-f1', type=float, help='Start frequency to mask', required=True)
    parser.add_argument('--freq_max', '-f2', type=float, help='End frequency to mask', required=True)
    return parser.parse_args()

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx 

def main():
    filterbank = FilReader(get_args().filename)    
    header = filterbank.header
    
    nchans = header.nchans
    fch1 = header.fch1
    bw = header.foff
    
    frequency_array = [fch1 + i*bw for i in range(nchans)]    
    frequency_array = frequency_array[::-1]           
    
    freq_min = get_args().freq_min
    freq_max = get_args().freq_max
    
    freq_min, idx_min = find_nearest(frequency_array, freq_min)
    freq_max, idx_max = find_nearest(frequency_array, freq_max)
    
    print(f'Masking values: {idx_min} -- {idx_max}')
    print(f'Frequency values: {freq_min:.3f} -- {freq_max:.3f}')
    
if __name__ == '__main__':
    main()