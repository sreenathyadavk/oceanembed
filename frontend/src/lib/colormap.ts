const S=['#0d1b4c','#1f4e9c','#2a8fbd','#4cc3a5','#e8e07a','#f39c4a','#d9432e','#8f1d2c'];
const rgb=(h:string)=>[1,3,5].map(i=>parseInt(h.slice(i,i+2),16));
export const gradientCss=`linear-gradient(90deg,${S.join(',')})`;
export function colorAt(t:number):[number,number,number]{
  const x=Math.min(1,Math.max(0,t))*(S.length-1),i=Math.min(S.length-2,Math.floor(x)),f=x-i,a=rgb(S[i]),b=rgb(S[i+1]);
  return [0,1,2].map(k=>Math.round(a[k]+(b[k]-a[k])*f)) as [number,number,number];
}
