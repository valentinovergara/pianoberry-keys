"""Render every voice without opening an audio device; optionally save WAV previews."""
import argparse
import ctypes as C
import math
from pathlib import Path
import struct
import sys
import wave
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ivorybox.engine import Synth
from ivorybox.presets import PRESETS

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--soundfont',default='/usr/share/sounds/sf2/FluidR3_GM.sf2')
    parser.add_argument('--output-dir',type=Path)
    args=parser.parse_args()
    if args.output_dir:args.output_dir.mkdir(parents=True,exist_ok=True)
    peaks={}
    for preset in PRESETS:
        synth=Synth(args.soundfont,preset=preset,audio=False)
        try:
            render=synth.lib.fluid_synth_write_float
            render.restype=C.c_int
            render.argtypes=[C.c_void_p,C.c_int,C.c_void_p,C.c_int,C.c_int,C.c_void_p,C.c_int,C.c_int]
            size=480
            left=(C.c_float*size)();right=(C.c_float*size)()
            frames=bytearray();peak=0.0
            # An original generic C-major arpeggio and a release tail, not a game melody.
            for block in range(400):
                if block in (0,40,80,120):synth.send('noteon',0,(60,64,67,72)[block//40],85)
                if block in (35,75,115,200):synth.send('noteoff',0,{35:60,75:64,115:67,200:72}[block])
                if render(synth.synth,size,left,0,1,right,0,1)!=0:raise RuntimeError('Rendering failed: '+preset)
                for l,r in zip(left,right):
                    if not math.isfinite(l) or not math.isfinite(r):raise RuntimeError('Nonfinite sample: '+preset)
                    peak=max(peak,abs(l),abs(r))
                    if args.output_dir:
                        frames.extend(struct.pack('<hh',int(max(-1,min(1,l))*32767),int(max(-1,min(1,r))*32767)))
            if not .0001<peak<.98:raise RuntimeError('Silent or clipping voice: '+preset+' peak='+str(peak))
            peaks[preset]=round(peak,4)
            if args.output_dir:
                with wave.open(str(args.output_dir/(preset+'.wav')),'wb') as out:
                    out.setnchannels(2);out.setsampwidth(2);out.setframerate(48000);out.writeframes(frames)
            print(preset+': OK; peak='+str(peaks[preset]),flush=True)
        finally:synth.close()
    print('All '+str(len(peaks))+' voices rendered successfully.')

if __name__=='__main__':main()
