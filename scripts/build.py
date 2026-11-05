import json,os,sys
SRC=sys.argv[1]; OUT=sys.argv[2]
books=[('bukhari','Sahih al-Bukhari','صحيح البخاري','Imam al-Bukhari','الإمام البخاري',256),
('muslim','Sahih Muslim','صحيح مسلم','Imam Muslim','الإمام مسلم',261),
('abudawud','Sunan Abi Dawud','سنن أبي داود','Imam Abu Dawud','الإمام أبو داود',275),
('tirmidhi',"Jami' at-Tirmidhi",'جامع الترمذي','Imam at-Tirmidhi','الإمام الترمذي',279),
('nasai',"Sunan an-Nasa'i",'سنن النسائي',"Imam an-Nasa'i",'الإمام النسائي',303),
('ibnmajah','Sunan Ibn Majah','سنن ابن ماجه','Imam Ibn Majah','الإمام ابن ماجه',273),
('malik','Muwatta Malik','موطأ مالك','Imam Malik','الإمام مالك',179),
('nawawi','Forty Hadith of an-Nawawi','الأربعون النووية','Imam an-Nawawi','الإمام النووي',676),
('qudsi','Forty Hadith Qudsi','الأحاديث القدسية','Compiled collection','مجموعة',None)]
LIMIT=1_600_000
index=[]
for bid,en,ar,auth,authar,died in books:
  langs={}
  for l in ['eng','ara','ind']:
    p=f'{SRC}/{l}-{bid}.min.json'
    if os.path.exists(p): langs[l]=json.load(open(p))
  meta=langs['eng']['metadata']
  bysec={}
  rows={}
  for l,d in langs.items():
    for h in d['hadiths']:
      n=h['hadithnumber']; key=str(n)
      r=rows.setdefault(key,{'n':n,'b':h['reference']['book'] if 'reference' in h else 0})
      r[l]=h['text'].strip()
      if l=='eng' and h.get('grades'): r['g']='; '.join(f"{g['grade']} ({g['name']})" for g in h['grades'][:2])
  rng=[(float(v['hadithnumber_first']),float(v['hadithnumber_last']),k) for k,v in meta['section_details'].items() if not (v['hadithnumber_first']==0 and v['hadithnumber_last']==0)]
  for r in rows.values():
    for a,b2,k in rng:
      if a<=r['n']<=b2: r['b']=k;break
  for r in rows.values():
    if not any(r.get(l) for l in ['ara','eng','ind']): continue
    bysec.setdefault(r['b'],[]).append(r)
  secs=[];chunk=[];size=0;ci=0
  def flush():
    global chunk,size,ci
    if chunk:
      json.dump({s:v for s,v in chunk},open(f'{OUT}/{bid}-{ci}.json','w'),ensure_ascii=False,separators=(',',':'))
      ci+=1;chunk=[];size=0
  for sk in sorted(bysec,key=lambda x:(9e9 if str(x)=='0' and min(r['n'] for r in bysec[x])>1 else float(x))):
    rs=sorted(bysec[sk],key=lambda r:r['n'])
    data=[[r['n'],r.get('ara',''),r.get('eng',''),r.get('ind',''),r.get('g','')] for r in rs]
    s=len(json.dumps(data,ensure_ascii=False).encode())
    if size and size+s>LIMIT: flush()
    chunk.append((str(sk),data));size+=s
    name=('Additional narrations' if str(sk)=='0' and data[0][0]>1 else None) or meta['sections'].get(str(sk),'') or ('Introduction' if str(sk)=='0' else f'Book {sk}')
    secs.append({'k':str(sk),'t':name,'c':len(data),'f':data[0][0],'l':data[-1][0],'ch':ci})
  flush()
  index.append({'id':bid,'en':en,'ar':ar,'auth':auth,'authar':authar,'died':died,'langs':list(langs),'secs':secs,'total':sum(s['c'] for s in secs),'chunks':ci})
  print(bid,ci,'chunks',sum(s['c'] for s in secs))
json.dump(index,open(f'{OUT}/index.json','w'),ensure_ascii=False,separators=(',',':'))
