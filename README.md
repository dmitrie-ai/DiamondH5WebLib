# Image Series Prototype
Diamond Light Source Summer Internship.\
This prototype was created with h5web/lib(https://www.npmjs.com/package/@h5web/lib) and React.\
![image](https://user-images.githubusercontent.com/72915468/133271025-44e2087b-0856-403d-82fd-46541b52182f.png)


## Server
Simple server made with flask.\
Made specifically for sending images from an image stack. Option is available to downsample and/or compress(using gzip) the response via the variables at the top of `main.py`. Downsampling block size can also be set via the variable at the top of `main.py`

### HTTP GET Request 
Requests are of the form http://localhost:8081/location-of-image-stack-relative-to-server-folder[image-number]?downsample=true where the URL encoded parameter `downsample` indicates whether to request a downsampled image or not.\
Example request: http://localhost:8081/demo_data[3]?downsample=true

### Starting server
Run `python main.py` in the server folder.


## Client

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).


In the project directory, you can run:
### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.\
You will also see any lint errors in the console.






