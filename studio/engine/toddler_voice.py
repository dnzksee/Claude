"""Yetişkin kadın sesini küçük çocuk sesine dönüştürür (WORLD vokoderi):
perde (F0) çocuğun perdesine taşınır, gırtlak/ağız boşluğu tınısı (formantlar) küçültülür."""
import numpy as np, pyworld as pw, wave, sys

def load(p):
    w=wave.open(p); fs=w.getframerate()
    x=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float64)/32768
    return x, fs

def save(p, x, fs):
    x=np.clip(x/ (np.abs(x).max()+1e-9)*0.9, -1, 1)
    w=wave.open(p,"wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(fs); w.writeframes((x*32767).astype(np.int16).tobytes()); w.close()

def toddler(x, fs, f0_target=330.0, formant=1.2, swing=1.25):
    f0,t=pw.harvest(x,fs,f0_floor=90,f0_ceil=700,frame_period=5.0)
    sp=pw.cheaptrick(x,f0,t,fs); ap=pw.d4c(x,f0,t,fs)
    v=f0>0
    med=np.median(f0[v])
    # perde: medyanı hedefe taşı, tonlamayı (şarkı söyler gibi) biraz genişlet
    lf=np.log(np.where(v,f0,1.0)); lm=np.log(med)
    f0n=np.where(v, np.exp(np.log(f0_target)+(lf-lm)*swing), 0.0)
    # formant: spektral zarfı frekans ekseninde genişlet (küçük ağız/gırtlak)
    n=sp.shape[1]; k=np.arange(n)
    src=np.clip(k/formant,0,n-1)
    spn=np.empty_like(sp)
    for i in range(sp.shape[0]):
        spn[i]=np.interp(src,k,sp[i])
    apn=np.empty_like(ap)
    for i in range(ap.shape[0]):
        apn[i]=np.interp(src,k,ap[i])
    return pw.synthesize(f0n,spn,apn,fs,frame_period=5.0)

if __name__=="__main__":
    src,dst,f0t,fm=sys.argv[1],sys.argv[2],float(sys.argv[3]),float(sys.argv[4])
    x,fs=load(src); save(dst,toddler(x,fs,f0t,fm),fs)
