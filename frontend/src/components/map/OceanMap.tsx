'use client';
import {useEffect,useRef} from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import {colorAt} from '@/lib/colormap';
import {BOUNDS,Grid} from '@/types/ocean';
const COORDS:[[number,number],[number,number],[number,number],[number,number]]=[[BOUNDS.w,BOUNDS.n],[BOUNDS.e,BOUNDS.n],[BOUNDS.e,BOUNDS.s],[BOUNDS.w,BOUNDS.s]];
function toUrl(gr:Grid){
  const c=document.createElement('canvas');c.width=gr.w;c.height=gr.h;const x=c.getContext('2d')!,im=x.createImageData(gr.w,gr.h);
  for(let j=0;j<gr.h;j++)for(let i=0;i<gr.w;i++){
    const raw = gr.data[j*gr.w+i];
    const k=((gr.h-1-j)*gr.w+i)*4;
    if(isNaN(raw)) {
      im.data.set([0,0,0,0],k);
    } else {
      const v=(raw-gr.min)/(gr.max-gr.min||1),[r,g,b]=colorAt(v);
      im.data.set([r,g,b,235],k);
    }
  }
  x.putImageData(im,0,0);return c.toDataURL();
}
export default function OceanMap({grid,point,onSelect}:{grid:Grid|null;point:{lat:number;lon:number};onSelect:(lat:number,lon:number)=>void}){
  const el=useRef<HTMLDivElement>(null),map=useRef<maplibregl.Map|undefined>(undefined),mk=useRef<maplibregl.Marker|undefined>(undefined),ready=useRef(false),gridRef=useRef<Grid|null>(grid),cb=useRef(onSelect);
  cb.current=onSelect;gridRef.current=grid;
  const apply=()=>{const m=map.current;if(!m||!ready.current||!gridRef.current)return;const url=toUrl(gridRef.current),s=m.getSource('field') as maplibregl.ImageSource|undefined;
    if(s){try{s.updateImage({url,coordinates:COORDS})}catch(e){}}else{m.addSource('field',{type:'image',url,coordinates:COORDS});
      m.addLayer({id:'field',type:'raster',source:'field',paint:{'raster-resampling':'linear','raster-fade-duration':300}});
      m.addLayer({id:'land',type:'fill',source:'c','source-layer':'countries',paint:{'fill-color':'#0c1723'}});
      m.addLayer({id:'borders',type:'line',source:'c','source-layer':'countries',paint:{'line-color':'#5d7a93','line-width':.8}});}};
  useEffect(()=>{
    const m=new maplibregl.Map({container:el.current!,attributionControl:{compact:true},
      style:{version:8,sources:{c:{type:'vector',url:'https://demotiles.maplibre.org/tiles/tiles.json'}},layers:[{id:'bg',type:'background',paint:{'background-color':'#06121f'}}]},
      bounds:[[BOUNDS.w,BOUNDS.s],[BOUNDS.e,BOUNDS.n]],fitBoundsOptions:{padding:16},maxBounds:[[25,-10],[125,45]]});
    m.addControl(new maplibregl.NavigationControl({showCompass:false}),'top-right');
    m.on('load',()=>{ready.current=true;apply();});
    m.on('click',e=>{const{lat,lng}=e.lngLat;if(lat>=BOUNDS.s&&lat<=BOUNDS.n&&lng>=BOUNDS.w&&lng<=BOUNDS.e)cb.current(lat,lng);});
    const d=document.createElement('div');d.className='h-3.5 w-3.5 rounded-full border-[2.5px] border-white bg-cy shadow-[0_0_8px_rgba(0,0,0,0.4)] pointer-events-none transition-transform hover:scale-125';
    mk.current=new maplibregl.Marker({element:d}).setLngLat([point.lon,point.lat]).addTo(m);map.current=m;
    return()=>{m.remove()};// eslint-disable-next-line
  },[]);
  useEffect(apply,[grid]);
  useEffect(()=>{mk.current?.setLngLat([point.lon,point.lat])},[point]);
  return <div ref={el} className="h-full w-full" role="application" aria-label="Interactive map of the North Indian Ocean. Click to inspect a location."/>;
}
