import re
import datetime as dt
from datetime import datetime
import time
import random
import json
import sys
import requests
import os
import pickle
import cv2
import numpy as np
import cPickle
import multiprocessing as mp


root = "/datasets/sagarj/instaSample6000/"

post_dir = root + "meta/"
videos_dir = root + "videos/"
frame_dir = root + "faces/"

frontal_face_cascade = cv2.CascadeClassifier('../haarcascades/haarcascade_frontalface_default.xml')
profile_face_cascade = cv2.CascadeClassifier('../haarcascades/haarcascade_profileface.xml')

faceNumber = "../Logs/instaFaceCounts.pk"


def process_frontal(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.waitKey(20)
    faces = []
    faces = frontal_face_cascade.detectMultiScale(gray, 1.3, 5)
    return len(faces)
    

def process_profile(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.waitKey(20)
    eyes = []
    eyes = profile_face_cascade.detectMultiScale(gray)
    return len(eyes)

def processVideo(videoPath , facesPath , postID , pool):
    print "Working with %s" %videoPath
    cap = cv2.VideoCapture(videoPath)
    totFrames = 0
    flaggedFrames = 0
    faces = 0
    profiles = 0
    i = 0
    while True:
        ret, frame = cap.read()
        if ret:
            procs = []
            totFrames += 1
            cv2.waitKey(20)
            
            f = pool.apply_async(process_frontal, (frame,))
            p = pool.apply_async(process_profile, (frame,))

            num_front= f.get(timeout=1) 
            num_profile = p.get(timeout=1)
            
            faces+= num_front
            profiles+=num_profile
            
            if(num_front>0 or num_profile>0):
                flaggedFrames+=1
        else:
            logline = str(postID) + "," + str(totFrames) + "," + str(flaggedFrames) + "," + str(faces) + ","+ str(profiles)
            print logline
            logfile = open(faceNumber, 'a+')
            cPickle.dump(logline , logfile);
            logfile.close()
            break
    

def readJson(path):
    f = open(path)
    data = json.loads(f.read())
    return data

def getPosts(postsDir):
    crawledPosts = os.listdir(postsDir)
    posts = []
    for post in crawledPosts:
        record = readJson(postsDir + post)
        #p = record['data']
        if isinstance(record,dict):
            posts.append(record)
    return posts

def getMappingDict(postList):
    mapping = dict()
    for p in postList:
        postId = p['meta']['Meta']['media']['code']
        vidName = postId
        mapping[postId] = vidName
    return mapping


#MAin Loop: Runs only once and is reculated using Cron jobs
if __name__ == '__main__':
    
    postList = getPosts(post_dir)
    mappingDict = getMappingDict(postList)
    pool = mp.Pool(processes=2) 
    
    for k in mappingDict: 
        postID = k
        print "Processing video %s" %(str(k))
        processVideo(videos_dir+mappingDict[k]+".mp4" ,frame_dir , postID ,pool)
    print "Done Counting faces from %d Videos" %(len(mappingDict.keys()))