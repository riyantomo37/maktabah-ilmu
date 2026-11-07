import json,os,sys,re
SRC=sys.argv[1]; OUT=sys.argv[2]
LIMIT=1_600_000
index=json.load(open(f'{OUT}/index.json'))
index=[b for b in index if b['id'] in ('bukhari','muslim','abudawud','tirmidhi','nasai','ibnmajah','malik','nawawi','qudsi')]
qinfo=json.load(open(f'{SRC}/q-info.json'))['chapters']
def q(e): 
  m={}
  for v in json.load(open(f'{SRC}/q/{e}.json'))['quran']: m[(v['chapter'],v['verse'])]=v['text']
  return m
QAR=q('ara-quranuthmanihaf')
def fixq(s): return s.replace('�','')
def emit(bid,meta,secs_rows):
  """secs_rows: list of (key,title,title_ar,rows)"""
  secs=[];chunk=[];size=0;ci=0
  def flush():
    nonlocal chunk,size,ci
    if chunk:
      json.dump({k:v for k,v in chunk},open(f'{OUT}/{bid}-{ci}.json','w'),ensure_ascii=False,separators=(',',':'));ci+=1;chunk=[];size=0
  for k,tt,ta,rows in secs_rows:
    if not rows: continue
    s=len(json.dumps(rows,ensure_ascii=False).encode())
    if size and size+s>LIMIT: flush()
    chunk.append((k,rows));size+=s
    secs.append({'k':k,'t':tt,'ta':ta,'c':len(rows),'f':rows[0][0],'l':rows[-1][7] if len(rows[-1])>7 and rows[-1][7] else rows[-1][0],'ch':ci})
  flush()
  e=dict(meta);e.update({'id':bid,'secs':secs,'total':sum(s['c'] for s in secs),'chunks':ci})
  index.append(e);print(bid,ci,'chunks',e['total'])
def clean(s): return (s or '').replace('�','').strip()
# ---- Quran
EN=q('eng-mohammedmarmadu');ID={k:re.sub(r"(?<=[^\s\d(])\d{1,4}\)",'',v) for k,v in q('ind-indonesianislam').items()};JA=q('jpn-ryoichimita')
secs=[]
for c in qinfo:
  ch=c['chapter'];rows=[]
  for v in c['verses']:
    k=(ch,v['verse']);rows.append([v['verse'],clean(QAR[k]),clean(EN.get(k)),clean(ID.get(k)),'',clean(JA.get(k))])
  secs.append((str(ch),f"{c['name']} · {c['englishname']}",c['arabicname'],rows))
emit('quran',{'en':"The Noble Qur'an",'ar':'القرآن الكريم','auth':'Revelation from Allah','authar':'كلام الله','died':None,'langs':['ara','eng','ind','jpn'],'kind':'quran','cat':'quran',
  'src':"Uthmani Hafs text; Indonesian: Kemenag RI; English: M. Pickthall; Japanese: Ryoichi Mita — via fawazahmed0/quran-api"},secs)
# ---- Tafsir
def taf(slug):
  m={}
  p=f'{SRC}/t/{slug}'
  for i in range(1,115):
    d=json.load(open(f'{p}/{i}.json'));d=d['ayahs'] if isinstance(d,dict) else d
    for a in d: m[(a['surah'],a['ayah'])]=clean(a['text'])
  return m
def tafsir_book(bid,meta,langs):
  T={l:taf(s) for l,s in langs.items()}
  secs=[]
  for c in qinfo:
    ch=c['chapter'];rows=[];prev=None
    for v in c['verses']:
      k=(ch,v['verse']);cur={l:T[l].get(k,'') for l in T}
      if prev is not None and all(cur[l]==prev[l] or not cur[l] for l in T) and any(cur[l] for l in T):
        r=rows[-1];r[6]+=f" ﴿{v['verse']}﴾ "+clean(QAR[k]);r[7]=v['verse'];continue
      prev=cur
      rows.append([v['verse'],cur.get('ar',''),cur.get('en',''),cur.get('id',''),'',cur.get('ja',''),clean(QAR[k]),None])
    for r in rows:
      if r[7] is None: r.pop()
    secs.append((str(ch),f"{c['name']} · {c['englishname']}",c['arabicname'],rows))
  emit(bid,meta,secs)
# Terjemah Indonesia Jalalain ditambahkan sesudahnya dengan scripts/import_jalalayn_id.py (Tanzil id.jalalayn)
tafsir_book('jalalayn',{'en':'Tafsir al-Jalalayn','ar':'تفسير الجلالين','auth':'Jalaluddin al-Mahalli & Jalaluddin as-Suyuthi','authar':'جلال الدين المحلي وجلال الدين السيوطي','died':911,'langs':['ara','eng'],'kind':'tafsir','cat':'quran','src':'spa5k/tafsir_api (Arabic; English tr. Feras Hamza)'},{'ar':'ar-tafsir-al-jalalayn','en':'en-al-jalalayn'})
tafsir_book('mukhtasar',{'en':'Al-Mukhtasar fi Tafsir','ar':'المختصر في التفسير','auth':'Markaz Tafsir li ad-Dirasat al-Quraniyyah','authar':'مركز تفسير للدراسات القرآنية','died':None,'langs':['ara','eng','ind','jpn'],'kind':'tafsir','cat':'quran','src':'spa5k/tafsir_api'},{'ar':'ar-tafsir-al-mukhtasar','en':'en-tafsir-al-mukhtasar','id':'indonesian-mokhtasar','ja':'japanese-mokhtasar'})
tafsir_book('saadi',{'en':"Tafsir as-Sa'di",'ar':'تيسير الكريم الرحمن','auth':"Abdurrahman bin Nashir as-Sa'di",'authar':'عبد الرحمن بن ناصر السعدي','died':1376,'langs':['ara','ind'],'kind':'tafsir','cat':'quran','src':'spa5k/tafsir_api'},{'ar':'ar-tafsir-as-saadi','id':'id-tafsir-as-saadi'})
tafsir_book('ibnkatsir',{'en':'Tafsir Ibn Kathir','ar':'تفسير القرآن العظيم','auth':'Imam Ibn Kathir','authar':'الإمام ابن كثير','died':774,'langs':['ara'],'kind':'tafsir','cat':'quran','src':'spa5k/tafsir_api (Arabic original)'},{'ar':'ar-tafsir-ibn-kathir'})
# ---- gading (Arabic + Indonesian), sections of 200
def gd(bid,f,meta):
  d=sorted(json.load(open(f'{SRC}/{f}')),key=lambda x:x['number'])
  secs=[]
  for i in range(0,len(d),200):
    part=d[i:i+200];rows=[[x['number'],clean(x['arab']),'',clean(x['id'])] for x in part]
    secs.append((str(i//200+1),f"Hadits {part[0]['number']}–{part[-1]['number']}",'',rows))
  emit(bid,meta,secs)
gd('ahmad','gd-ahmad.json',{'en':'Musnad Imam Ahmad','ar':'مسند الإمام أحمد','auth':'Imam Ahmad bin Hanbal','authar':'الإمام أحمد بن حنبل','died':241,'langs':['ara','ind'],'kind':'hadith','cat':'hadith','partial':True,'src':'gadingnst/hadith-api (tafsirq.com)'})
gd('darimi','gd-darimi.json',{'en':'Sunan ad-Darimi','ar':'سنن الدارمي','auth':'Imam ad-Darimi','authar':'الإمام الدارمي','died':255,'langs':['ara','ind'],'kind':'hadith','cat':'hadith','src':'gadingnst/hadith-api (tafsirq.com)'})
# ---- hadith-json (Arabic + English, chapters)
def hj(bid,f,meta):
  h=json.load(open(f'{SRC}/{f}'))
  by={}
  for x in h['hadiths']:
    e=x['english'];en=clean(((e.get('narrator') or '')+'\n'+(e.get('text') or '')).strip())
    by.setdefault(x['chapterId'],[]).append([x['idInBook'],clean(x['arabic']),en])
  secs=[]
  for c in h['chapters']:
    rows=sorted(by.get(c['id'],[]),key=lambda r:r[0])
    secs.append((str(c['id']),clean(c['english']),clean(c['arabic']),rows))
  emit(bid,meta,secs)
hj('riyadhus','hj-riyad_assalihin.json',{'en':'Riyad as-Salihin','ar':'رياض الصالحين','auth':'Imam an-Nawawi','authar':'الإمام النووي','died':676,'langs':['ara','eng'],'kind':'hadith','cat':'adab','src':'AhmedBaset/hadith-json'})
hj('bulugh','hj-bulugh_almaram.json',{'en':'Bulugh al-Maram','ar':'بلوغ المرام','auth':"Ibn Hajar al-'Asqalani",'authar':'ابن حجر العسقلاني','died':852,'langs':['ara','eng'],'kind':'hadith','cat':'adab','src':'AhmedBaset/hadith-json'})
hj('adab','hj-aladab_almufrad.json',{'en':'Al-Adab al-Mufrad','ar':'الأدب المفرد','auth':'Imam al-Bukhari','authar':'الإمام البخاري','died':256,'langs':['ara','eng'],'kind':'hadith','cat':'adab','src':'AhmedBaset/hadith-json'})
hj('syamail','hj-shamail_muhammadiyah.json',{'en':"Shama'il Muhammadiyah",'ar':'الشمائل المحمدية','auth':'Imam at-Tirmidhi','authar':'الإمام الترمذي','died':279,'langs':['ara','eng'],'kind':'hadith','cat':'sirah','src':'AhmedBaset/hadith-json'})
hj('misykat','hj-mishkat_almasabih.json',{'en':'Mishkat al-Masabih','ar':'مشكاة المصابيح','auth':'Al-Khatib at-Tabrizi','authar':'الخطيب التبريزي','died':741,'langs':['ara','eng'],'kind':'hadith','cat':'hadith','src':'AhmedBaset/hadith-json'})
for b in index:
  b.setdefault('kind','hadith')
  b.setdefault('cat','sittah' if b['id'] in ('bukhari','muslim','abudawud','tirmidhi','nasai','ibnmajah') else ('adab' if b['id'] in ('nawawi','qudsi') else 'hadith'))
json.dump(index,open(f'{OUT}/index.json','w'),ensure_ascii=False,separators=(',',':'))
