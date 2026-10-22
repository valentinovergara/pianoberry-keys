from pathlib import Path
import lzma,re,json,urllib.request,hashlib,concurrent.futures,time
root=Path(__file__).resolve().parent/'offline'
pkgs={}
for index,base in [('bookworm','https://deb.debian.org/debian/'),('updates','https://deb.debian.org/debian/'),('security','https://deb.debian.org/debian-security/')]:
 text=lzma.decompress((root/(index+'.xz')).read_bytes()).decode()
 for para in text.split('\n\n'):
  fields={}; key=None
  for line in para.splitlines():
   if line.startswith(' ') and key: fields[key]+='\n'+line
   elif ': ' in line: key,value=line.split(': ',1); fields[key]=value
  if 'Package' in fields:
   fields['_base']=base;pkgs[fields['Package']]=fields
providers={}
for n,p in pkgs.items():
 for virtual in p.get('Provides','').split(','):
  key=virtual.strip().split(' ')[0]
  if key:providers.setdefault(key,n)
targets=['python3-mido','python3-rtmidi','libfluidsynth3','fluid-soundfont-gm']
selected={}
def add(n):
 n=n.split(':')[0]
 if n not in pkgs:n=providers.get(n,n)
 if n in selected:return
 if n not in pkgs:raise RuntimeError('Dependencia no resuelta: '+n)
 p=selected[n]=pkgs[n]
 for dep in (p.get('Pre-Depends','')+','+p.get('Depends','')).split(','):
  if not dep.strip():continue
  choices=[re.split(r'[\s(:]',x.strip())[0] for x in dep.split('|')]
  choice=next((c for c in choices if c in pkgs or c in providers),None)
  if not choice:raise RuntimeError((n,dep))
  add(choice)
for n in targets:add(n)
out=root/'repo';out.mkdir(exist_ok=True)
print('Paquetes:',len(selected),'MB:',round(sum(int(p['Size']) for p in selected.values())/1e6),flush=True)
def download(item):
 n,p=item;filename=Path(p['Filename']).name;dest=out/filename
 def valid():return dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest()==p['SHA256']
 if not valid():
  for attempt in range(4):
   try:
    req=urllib.request.Request(p['_base']+p['Filename'],headers={'User-Agent':'IvoryBox-offline-setup/0.1'})
    with urllib.request.urlopen(req,timeout=90) as response,dest.open('wb') as f:
     while chunk:=response.read(1024*1024):f.write(chunk)
    if not valid():raise RuntimeError('SHA incorrecto: '+n)
    break
   except Exception:
    if attempt==3:raise
    time.sleep(2)
 return n
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 for n in pool.map(download,selected.items()):print('OK',n,flush=True)
sections=[]
for n,p in sorted(selected.items()):
 fields={k:v for k,v in p.items() if not k.startswith('_')}
 fields['Filename']='./'+Path(p['Filename']).name
 sections.append('\n'.join(k+': '+v for k,v in fields.items()))
(out/'Packages').write_text('\n\n'.join(sections)+'\n')
(root/'manifest.json').write_text(json.dumps({n:{'version':p['Version'],'sha256':p['SHA256'],'filename':Path(p['Filename']).name} for n,p in selected.items()},indent=2)+'\n')
print('REPOSITORIO_OFFLINE_VERIFICADO',flush=True)
