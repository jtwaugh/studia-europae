import json
bm=json.load(open('/home/claude/build/basemap.json'))
data=open('/home/claude/build/data2.json').read().replace('</','<\\/')
t=open('/home/claude/build/template.html').read()
for k,v in {'__LAND__':bm['land'],'__LAKES__':bm['lakes'],'__RIV1__':bm['rivers']['1'],'__RIV2__':bm['rivers']['2'],'__RIV3__':bm['rivers']['3'],'__FIT__':json.dumps(bm['fit']),'__W__':str(bm['W']),'__H__':str(bm['H']),'__DATA__':data}.items():
    t=t.replace(k,v)
import os; os.makedirs('/home/claude/site',exist_ok=True)
open('/home/claude/site/index.html','w').write(t)
import shutil; shutil.copy('/home/claude/build/relief.jpg','/home/claude/site/relief.jpg')
print(len(t)//1024,'KB')
