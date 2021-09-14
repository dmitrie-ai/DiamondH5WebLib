# Image Series Prototype
Diamond Light Source Summer Internship.\
This prototype was created with h5web/lib(https://www.npmjs.com/package/@h5web/lib) and React.\
![image](https://user-images.githubusercontent.com/72915468/133271025-44e2087b-0856-403d-82fd-46541b52182f.png)


## Server
Simple server made with flask.\
Made specifically for sending images from an image stack. Option is available to downsample and/or compress(using gzip) the response via the variables at the top of main.py. Downsampling block size can also be set via the variable at the top of main.py

### HTTP GET Request 
Requests are of the form http://localhost:8081/location-of-image-stack-relative-to-server-folder[image-number]?downsample=true where the URL encoded parameter `downsample` indicates whether to request a downsampled image or not.\
Example request: http://localhost:8081/demo_data[3]?downsample=true \

### JSON Response
Properties: 
- downsampled : The downsampling ratio. 0 if no downsampling has been done. E.g. If ratio is 4 then the block size is 16
- item-type   : The type of item received. In our case, it will always be "time-series"
- object-type : "h5_object"
- path        : Path to the particular image received relative to the server folder. E.g. "demo_data/tomo.h5/2-AstraReconCpu/data[0]"
- shape       : Shape of the image series from which the received image is from. E.g. [768,576,768]
- values      : Array of data values.


### Starting server
Run `python main.py` in the server folder.


## Client

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

### Starting Client
1. Run `npm install` in the main directory to install the dependencies.
2. Open src/App.tsx and modify `dataFolder` to point toward the folder where the hdf5 file is located relative to the server directory. Example: `dataFolder="demo_data"` 
3. Modify `dataPath` to point towards the image stack. Example: `dataPath="tomo.h5/2-AstraReconCpu/data"`
4. Modify `port` to the port where the local server is running(will be shown in console when you start the server).
5. Modify `enableDownsampling` to indicate whether you want the downsampling feature enabled.
6. Modify `decompress` to indicate whether you want the responses to be decompressed(gzip).
7. Run `npm start` in the main directory to run the app.
8. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.\
You will also see any lint errors in the console.


