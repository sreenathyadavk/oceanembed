export const DEPTHS=[0,5,10,20,30,50,75,100,125,150,200,300,500,700,1000];
export const BOUNDS={s:5,n:30,w:45,e:105};
export interface Grid{w:number;h:number;data:number[];min:number;max:number}
export interface ProfilePoint{depth:number;predicted:number;glorys?:number;argo?:number}
export interface Metrics{rmse:number;mae:number;bias:number;correlation:number}
export interface PredictionRequest{date:string;depth:number;latitude:number;longitude:number}
export interface PredictionResult{predictionMap:Grid;pointTemperature:number;profile:ProfilePoint[];metrics:Metrics|null;source:'demo'|'model'}
