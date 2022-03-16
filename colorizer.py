from asyncore import write 
from platform import release
from turtle import width
import cv2
from cv2 import CV_16S, FONT_HERSHEY_SIMPLEX, LINE_AA, destroyAllWindows, putText, resize, waitKey
from cv2 import dnn_Model
from cv2 import VideoWriter
import numpy as np 
import time 
from os.path import splitext, basename, join  
import tensorflow

class Colorizer: 
    def __init__(self, use_cuda=False, height = 480, width = 600):
        (self.height, self.width) = height, width

        self.colorModel = cv2.dnn.readNetFromCaffe("model/colorization_deploy_v2.prototxt",
        caffeModel="model/colorization_release_v2.caffemodel")
        if use_cuda:
            self.colorModel.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.colorModel.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

        clusterCenters= np.load("model/pts_in_hull.npy")
        clusterCenters = clusterCenters.transpose().reshape(2, 313, 1, 1)

        self.colorModel.getLayer(self.colorModel.getLayerId('class8_ab')).blobs = [clusterCenters.astype(np.float32)]
        self.colorModel.getLayer(self.colorModel.getLayerId('conv8_313_rh')).blobs = [np.full([1,313], 2.606, np.float32)]

    def processImage(self, imgName):
        self.img = cv2.imread(imgName)
        self.img = cv2.resize(self.img, (self.width, self.height))

        self.processFrame()
        a = cv2.imwrite(join("output", basename(imgName) ), self.imgFinal)
        #print(self.imgFinal)
        #print(a)
        # cv2.imshow("Output", self.imgFinal)
        # cv2.waitKey(0)
        return "output/" + imgName

    def processVideo(self, videoName):

        capture_duration = 180

        cap = cv2.VideoCapture(videoName)

        if(cap.isOpened() == False):
            print("Error opening video")
            return

        (success, self.img) = cap.read()

        prevFrameTime = 0
        nextFrameTime = 0 

        fourcc = cv2.VideoWriter_fourcc(*"MJPG") 
        out = cv2.VideoWriter(filename = (join("output", splitext(basename(videoName))[0] + '.avi')), fourcc = fourcc, fps = (int(cap.get(cv2.CAP_PROP_FPS))), frameSize =(self.width*2, self.height))
        
        start_time = time.time()

        while success and ( int(time.time() - start_time) < capture_duration ):
            
            self.img = cv2.resize(self.img, (self.width, self.height))

            self.processFrame()
            out.write(self.imgFinal)

            nextFrameTime = time.time()
            fps = 1/(nextFrameTime - prevFrameTime)
            prevFrameTime = nextFrameTime

            fps = "FPS" + str(int(fps))

            cv2.putText(self.imgFinal, fps, (5,25), cv2.FONT_HERSHEY_SIMPLEX, 1,
            (255,255,255), 2, cv2.LINE_AA)

            key = cv2.waitKey (1) & 0xFF
            if key == ord("q"):
                break

            (success, self.img) = cap.read()

        cap.release()
        out.release()
        cv2.destroyAllWindows()
        

        return '3333'#"output/" + videoName

            #cv2.imshow("Output", self.imgFinal)


        #     key = cv2.waitKey (1) & 0xFF
        #     if key == ord("q"):
        #         break
        #     (success, self.img) = cap.read()

        # cap.release()
        # out.release()
        # cv2.destroyAllWindows()

    # def processVideo(self, videoName):
    #     cap = cv2.VideoCapture(videoName)

    #     if(cap.isOpened() == False):
    #         print("Error opening video")
    #         return

    #     (success, self.img) = cap.read()

    #     prevFrameTime = 0
    #     nextFrameTime = 0 

    #     fourcc = cv2.VideoWriter_fourcc(*"MJPG") 
    #     out = cv2.VideoWriter(filename = (join("output", splitext(basename(videoName))[0] + '.avi')), fourcc = fourcc, fps = (int(cap.get(cv2.CAP_PROP_FPS))), frameSize =(self.width*2, self.height))

    #     while success: 
    #         self.img = cv2.resize(self.img, (self.width, self.height))

    #         self.processFrame()
    #         out.write(self.imgFinal)

    #         nextFrameTime = time.time()
    #         fps = 1/(nextFrameTime - prevFrameTime)
    #         prevFrameTime = nextFrameTime

    #         fps = "FPS" + str(int(fps))

    #         cv2.putText(self.imgFinal, fps, (5,25), cv2.FONT_HERSHEY_SIMPLEX, 1,
    #         (255,255,255), 2, cv2.LINE_AA)

    #     #return "output/" + self.imgFinal 
    #     #return "Output" + self.imgFinal


    #         key = cv2.waitKey (1) & 0xFF
    #         if key == ord("q"):
    #             break
    #         (success, self.img) = cap.read()

    #     cap.release()
    #     out.release()
    #     cv2.destroyAllWindows()


    def processFrame(self):
        imgNormalized = (self.img[:,:,[2,1,0]]*1.0/255).astype(np.float32)

        imgLab = cv2.cvtColor(imgNormalized, cv2.COLOR_RGB2Lab)
        channe1L = imgLab[:,:,0]


        imgLabResized = cv2.cvtColor(cv2.resize(imgNormalized, (224,224)), cv2.COLOR_RGB2Lab)
        channel1LResized = imgLabResized[:,:,0]
        channel1LResized -= 50

        self.colorModel.setInput(cv2.dnn.blobFromImage(channel1LResized))
        result = self.colorModel.forward()[0,:,:,:].transpose((1,2,0))

        resultResized = cv2.resize(result, (self.width, self.height))

        self.imgOut = np.concatenate((channe1L[:,:,np.newaxis], resultResized), axis = 2)
        self.imgOut = np.clip(cv2.cvtColor(self.imgOut, cv2.COLOR_LAB2BGR), 0, 1)
        self.imgOut = np.array((self.imgOut)*255, dtype= np.uint8)

        self.imgFinal = np.hstack((self.img, self.imgOut))
