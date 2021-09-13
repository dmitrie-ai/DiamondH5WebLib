//h5web/lib docs https://h5web-docs.panosc.eu/?path=/story/getting-started--page&globals=measureEnabled:false
import { ColorBar, DataCurve,CurveType } from "@h5web/lib";
import {
  HeatmapMesh,
  ScaleType,
  TooltipMesh,
  useDomain,
  VisCanvas,
  PanZoomMesh
} from "@h5web/lib";
import React from "react";
import "./styles.css";
import ndarray from 'ndarray';
import { getDomain } from '@h5web/lib';
import axios from "axios"
import { useState,useEffect } from "react";
import reportWebVitals from "./reportWebVitals";



const scaleType = ScaleType.Linear;
const colorMap = "Cool";
const dataPath1:string="example-data.h5/scan_1/data_1/image"
const dataPath2:string="ceo2_cal.nxs/entry/calibration_data/data"
const dataPath3:string="th_8_2.h5/entry/data/data"

const axiosClient=axios.create({
  baseURL: 'http://localhost:8081/demo_data/',
  timeout: 10000,
  decompress:true,
  headers:{"Accept":"*/*"}

});

export default function App() {
  const [responseData,setResponseData]=useState("")
  const [dataArray,setDataArray]=useState()
  //const [responseData,setResponseData]=useState<{shape:number[],values:number[][]}>({shape:[],values:[[]]})
  useEffect(()=>{
    console.time("timer1")
    axiosClient.get(dataPath2)
    .then(function (response) {
      setResponseData(response.data)
      console.log("response data: ",response)
      console.timeEnd("timer1")
      
      
    })
    .catch(function (error) {
      console.log(error);
    })},[])

  
  return (
    <div style={{ display: "flex", height: "800px",width:"800px" }}>
      
      
    </div>
  );
}
