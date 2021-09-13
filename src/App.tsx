//h5web/lib docs https://h5web-docs.panosc.eu/?path=/story/getting-started--page&globals=measureEnabled:false
import { ColorBar, DataCurve, CurveType } from "@h5web/lib";
import Slider from './components/Slider'
import {
  HeatmapVis,
  HeatmapMesh,
  ScaleType,
  TooltipMesh,
  useDomain,
  VisCanvas,
  PanZoomMesh,
} from "@h5web/lib";
import React, { useEffect,useState,useRef } from "react";
import "./styles.css";
import ndarray from "ndarray";
import {getDomain} from "./utils"
import type {Domain} from "./utils"
//import {getDomain } from "@h5web/lib/h5web/vis-packs/core/utils";
import axios, { AxiosAdapter, CancelTokenSource } from "axios"
import { SSL_OP_NO_TLSv1_2 } from "constants";


const dataPath3:string="th_8_2.h5/entry/data/data"
const dataPath2:string="tomo.h5/2-AstraReconCpu/data"
const dataPath=dataPath2
const withDownsample=true

const axiosClient=axios.create({
  baseURL: 'http://localhost:8081/demo_data/',
  timeout: 10000,
  decompress:false,
  headers:{"Accept":"*/*"}
});

interface Entity{
  item_type:string;
  path:string;
  object_type:string;
  shape:number[];
  values:number[][];
  downsampled:number;
  
}
const defaultEntity:Entity={
  item_type:"default",
  path:"default",
  object_type:"default",
  shape:[0,0,0],
  values:[[]],
  downsampled:0
}

export default function App() {
  const [currentEntity, setCurrentEntity]= useState<Entity>(defaultEntity)
  const [currentIndex,setCurrentIndex]=useState<number>(0)
  const [cancelSource,setCancelSource]=useState<CancelTokenSource>()

  function fetchWithDownsample(key:number){
    if (cancelSource !== undefined){cancelSource.cancel("Prev request cancelled")}  //cancel prev request. Only full size image requests are cancelled
    let newCancelSource=axios.CancelToken.source()
    setCancelSource(newCancelSource)
    axiosClient.get(dataPath+"["+ key.toString()+"]"+"?downsample=true")
      .then(function (response) {
        setCurrentEntity(response.data)
        //fetch full size image after the downsampled one has been received
        axiosClient.get(dataPath+"["+ key.toString()+"]"+"?downsample=false",{cancelToken:newCancelSource.token})
        .then(function (response) {
          setCurrentEntity(response.data)
        })
        .catch(function (error) {
          console.log(error);
        })

      })
      .catch(function (error) {
        console.log(error);
      })
  }
  function fetchImage(key:number){
    if (cancelSource !== undefined){cancelSource.cancel("Prev request cancelled")}  //cancel prev request. Only full size image requests are cancelled
    let newCancelSource=axios.CancelToken.source()
    setCancelSource(newCancelSource)
    //fetch full size image 
    axiosClient.get(dataPath+"["+ key.toString()+"]"+"?downsample=false",{cancelToken:newCancelSource.token})
    .then(function (response) {
      setCurrentEntity(response.data)
    })
    .catch(function (error) {
      console.log(error);
    })

      
  }
  
  function onChange(value:any){
    setCurrentIndex(value)
    if (withDownsample){fetchWithDownsample(value)}
    else{fetchImage(value)}
    
  }
  useEffect(()=>{
    if (withDownsample){fetchWithDownsample(0)}
    else{fetchImage(0)}
    },[])
  
  let downsampleSize=0
  if (currentEntity.downsampled===0){downsampleSize=1}else{downsampleSize=currentEntity.downsampled}
  const flatValues=currentEntity.values.flat() as number[]
  const shape=currentEntity.shape
  const dataDomain = getDomain(flatValues) 
  
  //const dataDomain=[-2,19] as Domain
  return (
    <div style={{ display: "flex", height:'100vh'}}>
      <Slider max={shape[0]} currentIndex={currentIndex} onChange={(value:any)=>{onChange(value)}}/>
      <VisCanvas
        abscissaConfig={{
          visDomain: [0, shape[1]],
          showGrid: true,
          isIndexAxis: false,
        }} /* x axis config*/
        ordinateConfig={{
          visDomain: [0, shape[2]],
          showGrid: true,
          isIndexAxis: true,
        }} /* y axis config*/
        
      >
        <HeatmapMesh
          rows={shape[1]/downsampleSize}
          cols={shape[2]/downsampleSize}
          values={flatValues}
          domain={dataDomain}
          scaleType={ScaleType.Linear}
          colorMap={"Cool"}
          // alphaDomain={[0, 1]}
          // alphaValues={Array.from({ length: 10000 }, () => 1)}
        />
        <PanZoomMesh/>

      </VisCanvas>

      <ColorBar
        domain={dataDomain}
        scaleType={ScaleType.Linear}
        colorMap={"Cool"}
        invertColorMap={false}
      />
    </div>
  );
}
