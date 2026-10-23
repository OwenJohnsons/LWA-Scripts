import h5py
import numpy as np
from your import Your, Writer
from your.formats.filwriter import make_sigproc_object
from tqdm import tqdm
import argparse
import datetime

# filename = "/lustre/owenj/powerbeams/Crab/061329_113548951533b319538"
# hdr = "/lustre/owenj/powerbeams/Crab/061329_113548951533b319538.meta.json"
# output_path = "/lustre/owenj/powerbeams/"

def parse_args():
    parser = argparse.ArgumentParser(description="Convert HDF5 powerbeam data to filterbank format.")
    parser.add_argument("-i", type=str, required=True, help="Path to the input HDF5 file.")
    parser.add_argument("-hdr", type=str, default=None, help="Path to .json header file (optional, assumes voltage path with .meta.json by default).")
    parser.add_argument("-o", type=str, default="/lustre/owenj/powerbeams/", help="Directory to save the output filterbank file.")
    parser.add_argument("--source", type=str, default="UNKNOWN", help="Source name for the filterbank header.")
    parser.add_argument("--chunk-size", type=int, default=10000, help="Number of time samples per chunk.")
    return parser.parse_args()

def main():
    args = parse_args()
    filename = args.i
    hdr = args.hdr if args.hdr else filename + ".meta.json"
    output_path = args.o
    source = args.source

    # -- read hdr --
    for line in open(hdr, "r"):
        if "OBS_START_MJD" in line:
            obs_mjd = line.split(":")[1].strip().replace('"', '').replace(',', '')
            obs_mjd = float(obs_mjd)
        # "OBS_START_MPM": "41400000",
        if "OBS_START_MPM" in line:
            obs_mpm = line.split(":")[1].strip().replace('"', '').replace(',', '')
            obs_mpm = (int(obs_mpm)/1000)/86400

    print("")
    obs_mjd = obs_mjd + obs_mpm
    print(f"Observation start MJD: {obs_mjd:.6f}")
    # obs in YYYY-MM-DDTHH:MM:SS format
    obs_datetime = datetime.datetime.fromtimestamp((obs_mjd - 40587) * 86400)
    obs_datetime = obs_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    print(f"Observation start datetime: {obs_datetime}")

    with h5py.File(filename, "r") as f:
        obs = f["Observation1"]
        nchan = obs.attrs['nChan']
        tsamp_v = obs.attrs['tInt'] # s
        tuning = obs["Tuning1"]
        ra_hrs = obs.attrs['RA']
        dec_deg = obs.attrs['Dec']

        # Keep datasets on disk and read in chunks
        xx = f["Observation1/Tuning1/XX"]
        yy = f["Observation1/Tuning1/YY"]
        nsamples = xx.shape[0]

        time = obs["time"]
        freq = tuning["freq"]

        bw_mhz = (freq[-1] - freq[0])/1e6
        fres = bw_mhz/nchan
        print("Frequency range [MHz]:", freq[0]/1e6, freq[-1]/1e6)
        print("Bandwidth [MHz]:", bw_mhz)
        print(f"Frequency resolution [MHz]: {fres:.4f}")
        print(f"Observation duration [s]: {tsamp_v*len(xx):.3f}")
        # data = (time_samples, frequency_channels)
        print("Data shape:", xx.shape)

        sigproc_object = make_sigproc_object(
            rawdatafile=f"{source}_{obs_datetime}.fil",
            source_name=source,
            nchans=nchan,
            foff=-fres, #MHz
            fch1=freq[-1]/1e6, # MHz
            tsamp=tsamp_v, # seconds
            tstart=obs_mjd, #MJD
            src_raj=ra_hrs, # HHMMSS.SS
            src_dej=dec_deg, # DDMMSS.SS
            machine_id=0,
            nbeams=0,
            ibeam=0,
            nbits=32,
            nifs=1,
            barycentric=0,
            pulsarcentric=0,
            telescope_id=6,
            data_type=0,
            az_start=-1,
            za_start=-1,
        )

        sigproc_object.write_header(f"{output_path}/{source}_{obs_datetime}.fil")

        # Read, sum, flip, and write each chunk
        for start in tqdm(range(0, nsamples, args.chunk_size), desc="Writing filterbank", unit="chunk"):
            end = min(start + args.chunk_size, nsamples)

            xx_chunk = xx[start:end, :]
            yy_chunk = yy[start:end, :]
            stokes_I = xx_chunk + yy_chunk
            stokes_I = np.flip(stokes_I, axis=1)

            sigproc_object.append_spectra(stokes_I, f"{output_path}/{source}_{obs_datetime}.fil")

        print(f"Filterbank file written to {output_path}/{source}_{obs_datetime}.fil")

if __name__ == "__main__":
    main()