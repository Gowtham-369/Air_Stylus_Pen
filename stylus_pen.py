# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import cv2
import numpy as np
import glob
import img2pdf
import os
import time
from collections import deque


# %%
# Outline for all variables
# PATH = os.getcwd()#gives cur working dir
PATH =  "E:/PythonTutorials/OpenCV/Stylus/Downloads/"
download_counter = 1
# color
colors = [(255,0,0),(0,255,0),(0,0,255)]
colorIndex = 0

#list of deque of points for a color
bpoints = [deque(maxlen = 512)]
gpoints = [deque(maxlen = 512)]
rpoints = [deque(maxlen = 512)]

#index for easy access to next deque

bindex = 0
gindex = 0
rindex = 0

kernel = np.ones((5,5),np.uint8)
# for morphological operations

th = 2 #default thickness
t1 = True #default to true
t2 = False 
t3 = False

switch_theme = False #change for background


# %%
# trackbar
def setValues(x):
    pass

# cv2.namedWindow("Color detectors",cv2.WINDOW_NORMAL)
cv2.namedWindow("Color detectors")
# [[30, 62, 144], [151, 244, 245]]
cv2.createTrackbar("Upper Hue","Color detectors",179,179,setValues)
cv2.createTrackbar("Upper Saturation","Color detectors",255,255,setValues)
cv2.createTrackbar("Upper Value","Color detectors",255,255,setValues)
cv2.createTrackbar("Lower Hue","Color detectors",0,179,setValues)
cv2.createTrackbar("Lower Saturation","Color detectors",0,255,setValues)
cv2.createTrackbar("Lower Value","Color detectors",0,255,setValues)

load_from_disk = True
if load_from_disk:
    penval = np.load("penval.npy")

#camera 
camera = cv2.VideoCapture(0)

#set resolution of camera frame
def make_720():
    camera.set(3,1280)
    camera.set(4,720)

make_720()



while (True):
    
    grabbed,frame = camera.read()
    if not(grabbed):
        break
    
    frame = cv2.resize(frame,(900,700))
    frame = cv2.flip(frame,1)
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    
    notebook = np.zeros((600,600,3))+255
    if switch_theme == True:
        notebook = np.zeros((600,600,3))
    
    #sketchpad screen
    frame = cv2.rectangle(frame,(300,70),(830,600),(0,0,0),3) #square frame

    # 80px *80px color frames
    frame = cv2.rectangle(frame,(300,610),(380,690),(215,215,220),-1) #eraser
    frame = cv2.rectangle(frame,(400,610),(480,690),colors[0],-1) #blue
    frame = cv2.rectangle(frame,(500,610),(580,690),colors[1],-1) #green
    frame = cv2.rectangle(frame,(600,610),(680,690),colors[2],-1) #red
    frame = cv2.circle(frame,(740,650),40,(255,255,255),-1) #clear screen
    
    #download,thickness,checkboxes
    #150px * 50px rectangle
    frame = cv2.rectangle(frame,(300,10),(450,60),(102,0,255),-1) #Download
    frame = cv2.rectangle(frame,(650,10),(655,60),(85,79,80),-1) #thickness 1
    frame = cv2.rectangle(frame,(705,10),(715,60),(85,79,80),-1) #thickness 2
    frame = cv2.rectangle(frame,(765,10),(780,60),(85,79,80),-1) #thickness 3
    
    #checkboxes for thickness(ideal is radio button)
    
    #default check for t1
    frame = cv2.rectangle(frame,(620,40),(640,60),(0,0,0),3) #for t1
    frame = cv2.rectangle(frame,(675,40),(695,60),(0,0,0),3) #for t2
    frame = cv2.rectangle(frame,(735,40),(755,60),(0,0,0),3) #for t3
    if t1 == True:
        #check for t1
        frame = cv2.rectangle(frame,(620,40),(640,60),(255,255,255),-1)
    if t2 == True:
        frame = cv2.rectangle(frame,(675,40),(695,60),(255,255,255),-1) 
    if t3 == True:
        frame = cv2.rectangle(frame,(735,40),(755,60),(255,255,255),-1) 
    
    #Adding Borders to all boxes
    
    frame = cv2.rectangle(frame,(300,610),(380,690),(0,0,0),3) #eraser
    frame = cv2.rectangle(frame,(400,610),(480,690),(0,0,0),3) #blue
    frame = cv2.rectangle(frame,(500,610),(580,690),(0,0,0),3) #green
    frame = cv2.rectangle(frame,(600,610),(680,690),(0,0,0),3) #red
    frame = cv2.circle(frame,(740,650),40,(0,0,0),2) #clear screen
    frame = cv2.rectangle(frame,(300,10),(450,60),(0,0,0),3) #download
    
    #Adding Text to Boxes
    #bottom_left is org
    frame = cv2.putText(frame,"Eraser",(305,655),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,0),2,cv2.LINE_AA)
    frame = cv2.putText(frame,"Blue",(405,655),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,0),2,cv2.LINE_AA)
    frame = cv2.putText(frame,"Green",(505,655),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,0),2,cv2.LINE_AA)
    frame = cv2.putText(frame,"Red",(605,655),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,0),2,cv2.LINE_AA)
    frame = cv2.putText(frame,"Clear",(705,655),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,0),2,cv2.LINE_AA)
    frame = cv2.putText(frame,"Download",(305,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,0),2,cv2.LINE_AA)
    
    #Stylus pen detection
    u_hue = cv2.getTrackbarPos("Upper Hue","Color detectors")
    u_sat = cv2.getTrackbarPos("Upper Saturation","Color detectors")
    u_val = cv2.getTrackbarPos("Upper Value","Color detectors")
    l_hue = cv2.getTrackbarPos("Lower Hue","Color detectors")
    l_sat = cv2.getTrackbarPos("Lower Saturation","Color detectors")
    l_val = cv2.getTrackbarPos("Lower Value","Color detectors")
    
    if (load_from_disk):
        blueUpper = penval[1]
        blueLower = penval[0]
    else:
        #try out the combination of hsv to identigy your pen
        blueUpper = np.array([u_hue,u_sat,u_val])
        blueLower = np.array([l_hue,l_sat,l_val])
    #***************************** OBJECT DETECTION *********************************#
    
    blueMask = cv2.inRange(hsv,blueLower,blueUpper)
    blueMask = cv2.morphologyEx(blueMask,cv2.MORPH_OPEN,kernel)#erode and dilate
    blueMask = cv2.erode(blueMask,kernel,iterations = 2)
     
    # Find contours in the range
    # get boundareies of pen
    cnts,_ = cv2.findContours(blueMask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    center = None
    
    
    #check to see if any contours were found
    if(len(cnts) > 0):
        #sort the cnts and find the largest one
        cnt = sorted(cnts,key = cv2.contourArea,reverse = True)[0]
        
        #Get the radius of the enclosing circle around the found contour
        ((x,y),radius) = cv2.minEnclosingCircle(cnt)
        
        #Draw the circle around the contour
        cv2.circle(frame,(int(x),int(y)),int(radius),(0,255,255),2)#yellow
        
        #get moments to calc center
        M = cv2.moments(cnt)
        if(M['m00'] != 0):
            center = (int(M['m10']/M['m00']),int(M['m01']/M['m00']))
        else:
            center = (0,0)
        #cv2.circle(frame,(int(center[0]),int(center[1])),int(7),(0,0,255),-1)
        
        #cv2.putText(frame,"center x:{},center y:{}".format(center[0],center[1]),(center[0],center[1]),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2,cv2.LINE_AA)
        
        val = list(center)
        if (center[0] > 300):
            
            cv2.circle(frame,(int(center[0]),int(center[1])),int(7),colors[colorIndex],-1)
            if switch_theme:
                cv2.circle(notebook,(int(center[0])-280,int(center[1])-50),int(7),(255,255,255),-1)
            else:
                cv2.circle(notebook,(int(center[0])-280,int(center[1])-50),int(7),(0,0,0),-1)
            
            if(center[1] < 70):
                # Download ,thichkness buttons
                
                if(center[0] > 620 and center[0]<640):
                    #t1
                    t1 = True
                    t2 = False
                    t3 = False
                    bpoints.append(deque(maxlen = 512))
                    bindex += 1
                    gpoints.append(deque(maxlen = 512))
                    gindex += 1
                    rpoints.append(deque(maxlen = 512))
                    rindex += 1
                    
                    th = 2
                elif (center[0]>675 and center[0]<695):
                    #t2
                    t1 = False
                    t2 = True
                    t3 = False
                    bpoints.append(deque(maxlen = 512))
                    bindex += 1
                    gpoints.append(deque(maxlen = 512))
                    gindex += 1
                    rpoints.append(deque(maxlen = 512))
                    rindex += 1
                    
                    th = 3
                elif (center[0]>735 and center[0]<755):
                    #t3
                    t1 = False
                    t2 = False
                    t3 = True
                    bpoints.append(deque(maxlen = 512))
                    bindex += 1
                    gpoints.append(deque(maxlen = 512))
                    gindex += 1
                    rpoints.append(deque(maxlen = 512))
                    rindex += 1
                    
                    th = 5
                elif(center[0]>300 and center[0]<450):
                    #Download button will come here
                    flag = False
                    
                    points = [bpoints,gpoints,rpoints]
                    for i in range(len(points)):
                        for j in range(len(points[i])):
                            for k in range(1,len(points[i][j])):

                                if points[i][j][k-1] is None or points[i][j][k] is None:
                                    continue
                                flag = True
                                x1 = points[i][j][k][0]
                                y1 = points[i][j][k][1]
                                tck = points[i][j][k][2]
                                x2 = points[i][j][k-1][0]
                                y2 = points[i][j][k-1][1]

                                #cv2.line(frame,tuple(points[i][j][k-1][:2]),tuple(points[i][j][k][:2]),colors[i],2)
                                cv2.line(notebook,(x1-280,y1-50),(x2-280,y2-50),colors[i],tck)
                    
                    notebook = cv2.GaussianBlur(notebook,(3,3),0) #smoothing
                    
                    if flag:
                        new_path = PATH+"Downloaded_image_"+str(download_counter)+".jpg"
                        down = cv2.resize(notebook,(1030,500))
                        cv2.imwrite(new_path,down)
                        download_counter += 1
                        
                        cv2.putText(frame,"Download Successfull !",(390,300),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2,cv2.LINE_AA)
                        time.sleep(0.5)
                    else:
                        cv2.putText(frame,"Empty Notebook!",(390,300),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2,cv2.LINE_AA)

                        
            elif (center[1]>600):
                #color pickers,eraser,clear
                if (center[0]>300 and center[0]<=380):
                    #eraser
                    #erase all the points of a particular color
                    if colorIndex == 0:
                        bpoints = [deque(maxlen=512)]
                        bindex = 0
                    elif (colorIndex == 1):
                        gpoints = [deque(maxlen=512)]
                        gindex = 0
                    elif (colorIndex == 2):
                        rpoints = [deque(maxlen=512)]
                        rindex = 0
                        
                elif(center[0]>400 and center[0]<480):
                    #blue
                    colorIndex = 0
                    
                elif (center[0]>500 and center[0]<580):
                    #green
                    colorIndex = 1
                elif (center[0]>600 and center[0]<680):
                    #red
                    colorIndex = 2
                elif (center[0]>700 and center[0]<780):
                    #clear screen
                    #reintialize all points
                    bpoints = [deque(maxlen=512)]   
                    gpoints = [deque(maxlen=512)]   
                    rpoints = [deque(maxlen=512)]
                    bindex = 0
                    gindex = 0
                    rindex = 0
                    
                    if (switch_theme):
                        notebook[:,:,:] = 0
                    else:
                        notebook[:,:,:] = 255
            else:
                #print("We are inside the sktechpad black square!!")
                #important point to be grabbed
                #deque stoes list of (x,y,th)
                val.append(th)
                if (colorIndex == 0):
                    bpoints[bindex].appendleft(val)
                elif (colorIndex == 1):
                    gpoints[gindex].appendleft(val)
                elif (colorIndex == 2):
                    rpoints[rindex].appendleft(val)
        else:
            #print("x cordinate is less than 300px")
            #small check
            if (bindex > 1000 or gindex >1000 or rindex>1000):
                print("Memory Full!!")
                break
                
            #discontinuity points
            #add a new deque to each list
            bpoints.append(deque(maxlen = 512))
            bindex += 1
            gpoints.append(deque(maxlen = 512))
            gindex += 1
            rpoints.append(deque(maxlen = 512))
            rindex += 1
    else:
        print("NO contours detected!!")
    
        
    
    points = [bpoints,gpoints,rpoints]
    for i in range(len(points)):
        for j in range(len(points[i])):
            for k in range(1,len(points[i][j])):
                
                if points[i][j][k-1] is None or points[i][j][k] is None:
                    continue
                x1 = points[i][j][k][0]
                y1 = points[i][j][k][1]
                tck = points[i][j][k][2]
                x2 = points[i][j][k-1][0]
                y2 = points[i][j][k-1][1]
                
                # cv2.line(frame,tuple(points[i][j][k-1][:2]),tuple(points[i][j][k][:2]),colors[i],2)
                cv2.line(frame,(x1,y1),(x2,y2),colors[i],2)
                cv2.line(notebook,(x1-280,y1-50),(x2-280,y2-50),colors[i],tck)
    
    #********************************* END ****************************#
    
    cv2.imshow("Notebook",notebook)
    cv2.imshow("Sketchpad frame",frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.putText(frame,"Processing Notebooks !!",(390,300),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2,cv2.LINE_AA)
        with open("Gowtham_ProjectSWE.pdf","wb") as f:
            f.write(img2pdf.convert(glob.glob(r"Downloads/*.jpg")))

        # time.sleep(0.5)
        break
    
camera.release()
cv2.destroyAllWindows()


