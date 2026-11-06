"""Audit ekstraksi terjemah an-Nabhani: setiap baris isi PDF harus ada di teks hasil.
Pakai: python -X utf8 scripts/audit_nabhani.py <folder ht> [kitab ...]
Baris \"hilang\" yang wajar: daftar isi, katalog (KDT), kepala halaman. Selain itu = bug."""
import sys,re,glob,os
S=sys.argv[1]; only=sys.argv[2:]; sys.argv=['x',S,S+'/_audit_out',S+'/ar']
import os as _o; sys.path.insert(0,_o.path.dirname(_o.path.abspath(__file__)))
import build_nabhani as B, pymupdf
from collections import Counter
PUA=re.compile('[\ue000-\uf8ff]')
n=lambda s: re.sub(r'\W','',PUA.sub('',s)).lower()
for lang in ('id','en'):
  for f in sorted(glob.glob(f'{S}/{lang}/*.pdf')):
    bid=os.path.basename(f)[:-4]
    if only and bid not in only: continue
    d=pymupdf.open(f); secs=B.extract(f,lang)
    ext=n(' '.join(x for t,it in secs for k,x in it))
    tot=miss=0; ex=[]
    for p in range(len(d)):
      for b in d[p].get_text('dict')['blocks']:
        if b.get('type')!=0: continue
        for l in b['lines']:
          t=PUA.sub('',''.join(s['text'] for s in l['spans'])); k=n(t)
          if len(k)<30 or re.search(r'[\u0600-\u06ff]',t) or re.search(r'(\.\s?\.\s?\.\s?\.|_{4,}|~\s*\d)',t): continue
          tot+=1
          if k[3:-3] not in ext: miss+=1; ex.append((p+1,t[:70]))
    print(f'{lang} {bid:14} secs={len(secs):3} baris={tot:5} hilang={miss:4} ({100*miss/max(tot,1):.1f}%)', ex[:3] if miss else '')
