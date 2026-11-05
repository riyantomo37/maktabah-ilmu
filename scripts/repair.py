import json,re,sys
D=sys.argv[1]
DIA=re.compile('[ً-ٰٟۖ-ۭ‏‎]')
tot=fixed=0
for b in ['bukhari','muslim','abudawud','tirmidhi','nasai','ibnmajah','malik']:
  p=f'{D}/ara-{b}.min.json'; a=json.load(open(p,encoding='utf-8',errors='replace'))
  a1={h['hadithnumber']:h['text'] for h in json.load(open(f'{D}/ara1-{b}.min.json',encoding='utf-8',errors='replace'))['hadiths']}
  for h in a['hadiths']:
    if '�' not in h['text']: continue
    tot+=1
    w=h['text'].split(' '); w1=a1.get(h['hadithnumber'],'').split(' ')
    # align by stripped words: find index of corrupted words
    out=[]
    ok=True
    # map tokens: compare stripped tokens sequentially
    s=[DIA.sub('',x) for x in w]; s1=[DIA.sub('',x) for x in w1]
    for i,x in enumerate(w):
      if '�' in x:
        cand=None
        # find best candidate in s1 near position i with matching prefix/suffix
        pre=s[i].split('�')[0]; suf=s[i].split('�')[-1]
        for j in range(max(0,i-15),min(len(s1),i+15)):
          y=s1[j]
          if '�' not in y and y.startswith(pre) and y.endswith(suf) and len(y)>=len(pre)+len(suf) and (s[j-1:j]==s1[j-1:j] or True):
            # check neighbors match
            if (i>0 and j>0 and s[i-1]==s1[j-1]) or (i+1<len(s) and j+1<len(s1) and s[i+1]==s1[j+1]):
              cand=w1[j];break
        if cand is None: ok=False; out.append(re.sub('\ufffd+','\u25cc',x))
        else: out.append(cand)
      else: out.append(x)
    h['text']=re.sub('\ufffd+','\u25cc',' '.join(out))
    if ok: fixed+=1

  json.dump(a,open(p,'w',encoding='utf-8'),ensure_ascii=False)
print(tot,fixed)
