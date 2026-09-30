// DEMO ONLY: deterministic synthetic field. Not model output. Replace via predictionService.
import {BOUNDS,DEPTHS,Grid} from '@/types/ocean';
const g=(x:number,s:number)=>Math.exp(-(x*x)/(2*s*s));
const doy=(d:string)=>{const t=new Date(d+'T00:00:00Z');return Math.floor((+t-Date.UTC(t.getUTCFullYear(),0,0))/864e5)};
export function temperatureAt(lat:number,lon:number,z:number,day:number){
  const s=Math.sin(((day-110)/365)*2*Math.PI); // + = SW monsoon
  const up=Math.max(0,s), win=Math.max(0,-s);
  let ts=30.2-0.2*Math.max(0,lat-10)-1.6*win*(lat-5)/25-3.2*up*g(lon-56,4)*g(lat-14,5)-1.4*up*g(lon-74,2.5)*g(lat-12,5);
  const eddy=1.5*Math.sin(lat*0.9+lon*0.55+day*0.03)*Math.cos(lon*0.32-lat*0.5-day*0.02)-1.0*Math.tanh((lat-20-0.08*(lon-75))/1.2);
  const H=140+30*Math.sin(lon*0.2+lat*0.1);
  const deep=4.5+2.5*g(lon-58,7)*g(lat-20,7); // Gulf/Red Sea outflow-like warm tongue
  const f=0.65*Math.exp(-Math.pow(z/H,1.3))+0.35*Math.exp(-z/800);
  const env=Math.exp(-Math.pow((z-120)/260,2))+0.15;
  return deep+(ts-deep)*f+eddy*env;
}
export function generateTemperatureField({date,depth}:{date:string;depth:number}):Grid{
  const w=144,h=60,day=doy(date),data:number[]=new Array(w*h);let min=1e9,max=-1e9;
  for(let j=0;j<h;j++)for(let i=0;i<w;i++){
    const t=temperatureAt(BOUNDS.s+(j+.5)*25/h,BOUNDS.w+(i+.5)*60/w,depth,day);
    data[j*w+i]=t;if(t<min)min=t;if(t>max)max=t;}
  return {w,h,data,min,max};
}
export const profileAt=(date:string,lat:number,lon:number)=>{const d=doy(date);return DEPTHS.map(z=>({depth:z,predicted:+temperatureAt(lat,lon,z,d).toFixed(2)}))};
