import json, numpy as np
from shapely.geometry import shape, box, mapping
from shapely.ops import transform, unary_union
from pyproj import Transformer
from PIL import Image, ImageFilter
Image.MAX_IMAGE_PIXELS=None
PROJ="+proj=lcc +lat_1=38 +lat_2=62 +lat_0=50 +lon_0=14 +datum=WGS84 +units=km"
F=Transformer.from_crs("EPSG:4326",PROJ,always_xy=True)
I=Transformer.from_crs(PROJ,"EPSG:4326",always_xy=True)
X0,X1,Y0,Y1=-3000,3100,-2600,2950   # km (data extent)
CORE=(-2150,2300,-2120,2520)  # fit frame: Iceland..Kazan, North Cape..Cairo
S=2.5  # km per svg unit
W=round((X1-X0)/S); H=round((Y1-Y0)/S)
NE='/tmp/claude-0/dl/ne/'
frame=box(X0-50,Y0-50,X1+50,Y1+50)
geoclip=box(-45,15,75,80)
def proj(g): return transform(lambda x,y,z=None: F.transform(x,y), g)
def tosvg(x,y): return ((x-X0)/S, (Y1-y)/S)
def path(g, prec=1):
    out=[]
    def ring(coords, close):
        pts=[tosvg(x,y) for x,y in coords]
        s='M'+' '.join(f'{px:.{prec}f},{py:.{prec}f}' for px,py in pts)
        return s+('Z' if close else '')
    def rec(g):
        t=g.geom_type
        if t=='Polygon':
            out.append(ring(g.exterior.coords,True)); [out.append(ring(r.coords,True)) for r in g.interiors]
        elif t=='LineString': out.append(ring(g.coords,False))
        elif t.startswith('Multi') or t=='GeometryCollection': [rec(x) for x in g.geoms]
    rec(g); return ''.join(out)
def load(f): return json.load(open(NE+f+'.geojson'))['features']
# land
land=[]
for ft in load('ne_10m_land'):
    g=shape(ft['geometry']).intersection(geoclip)
    if g.is_empty: continue
    g=proj(g).intersection(frame)
    if not g.is_empty: land.append(g)
land=unary_union(land).simplify(1.2)
land=land.buffer(0)
# drop tiny islands
if land.geom_type=='MultiPolygon':
    from shapely.geometry import MultiPolygon
    land=MultiPolygon([p for p in land.geoms if p.area>12])
landd=path(land)
# lakes
lakes=[]
for f in ['ne_10m_lakes','ne_10m_lakes_europe']:
    for ft in load(f):
        g=shape(ft['geometry'])
        if not g.intersects(geoclip): continue
        g=proj(g.intersection(geoclip)).intersection(frame)
        if not g.is_empty and g.area>30: lakes.append(g)
lakesu=unary_union(lakes).simplify(1.2)
lakesd=path(lakesu)
# rivers: by scalerank
riv={1:[],2:[],3:[]}
seen=0
for f in ['ne_10m_rivers_lake_centerlines','ne_10m_rivers_europe']:
    for ft in load(f):
        p=ft['properties']; sr=p.get('scalerank',10)
        if p.get('featurecla','').lower().startswith('lake'): continue
        g=shape(ft['geometry'])
        if not g.intersects(geoclip): continue
        g=proj(g.intersection(geoclip)).intersection(frame)
        if g.is_empty: continue
        g=g.simplify(1.5)
        cls=1 if sr<=3 else 2 if sr<=6 else 3 if sr<=9 else None
        if cls: riv[cls].append(g)
rivd={k:path(unary_union(v)) for k,v in riv.items()}
# mountain range labels
labels=[]
for ft in load('ne_10m_geography_regions_polys'):
    p=ft['properties']
    if p.get('FEATURECLA') not in ('Range/mtn','Plateau','Desert','Peninsula','Plain','Basin','Lowland'): continue
    if p.get('SCALERANK',9)>4: continue
    g=shape(ft['geometry'])
    if not g.intersects(geoclip): continue
    c=g.representative_point()
    x,y=F.transform(c.x,c.y)
    if X0<x<X1 and Y0<y<Y1:
        sx,sy=tosvg(x,y); labels.append({'n':p.get('NAME'),'c':p.get('FEATURECLA'),'x':round(sx),'y':round(sy),'r':p.get('SCALERANK')})
# relief raster
RS=2.0
RW=round((X1-X0)/RS); RH=round((Y1-Y0)/RS)
xs=X0+(np.arange(RW)+0.5)*RS; ys=Y1-(np.arange(RH)+0.5)*RS
XX,YY=np.meshgrid(xs,ys)
lon,lat=I.transform(XX,YY)
src=np.asarray(Image.open('/tmp/claude-0/dl/bm/mpl_toolkits/basemap_data/shadedrelief.jpg').convert('RGB')).astype(np.float32)/255
sh,sw,_=src.shape
px=np.clip(((lon+180)/360*sw).astype(int),0,sw-1); py=np.clip(((90-lat)/180*sh).astype(int),0,sh-1)
rgb=src[py,px]
L=0.3*rgb[...,0]+0.59*rgb[...,1]+0.11*rgb[...,2]
Li=Image.fromarray((L*255).astype(np.uint8))
blur=np.asarray(Li.filter(ImageFilter.GaussianBlur(14))).astype(np.float32)/255
shade=(L-blur)*2.6
# elevation proxy: hypsometric warmth (R-G) and brightness of snow
warm=np.clip((rgb[...,0]-rgb[...,1])*4+0.1,0,1)
elev=np.clip(warm,0,1)
out=0.5+shade-0.10*elev
out=np.clip(out,0,1)
img=Image.fromarray((out*255).astype(np.uint8))
img.save('/home/claude/build/relief.jpg',quality=80,optimize=True)
Image.fromarray((elev*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)).save('/home/claude/build/elev.jpg',quality=75,optimize=True)
json.dump({'W':W,'H':H,'land':landd,'lakes':lakesd,'rivers':rivd,'labels':labels,
 'proj':{'def':PROJ,'X0':X0,'Y1':Y1,'S':S},'fit':[(CORE[0]-X0)/S,(Y1-CORE[3])/S,(CORE[1]-CORE[0])/S,(CORE[3]-CORE[2])/S],'relief':{'w':RW,'h':RH}},open('/home/claude/build/basemap.json','w'))
print(W,H,len(landd),len(lakesd),{k:len(v) for k,v in rivd.items()},len(labels),RW,RH)
