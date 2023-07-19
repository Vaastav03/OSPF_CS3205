#headers
# NAME:Pitchika Vaastav
# Roll Number:CS20B060
# Course: CS3205 Jan. 2023 semester
# Lab number: 5
# Date of submission: April 28th , 2023
# I confirm that the source file is entirely written by me without
# resorting to any dishonest means.
# Website(s) that I used for basic programming code are:
# URL(s):www.geeksforgeeks.org/dijkstras-shortest-path-algorithm-greedy-algo-7/
import socket
import sys
import random
import time
import threading
import os
#flag for limiting the number of times updation takes place
flag=0

#function to send hello messages to the neighbours of a given router
def hello(rsock,hi,i,neighbours):
    #until termination
    while flag!=1:
            #send hello messages to all the neighbours who have weights attached to them
            hmsg="HELLO "+str(i)
            for j in range(len(neighbours)):
                if neighbours[j]!=(-1,-1):
                    rsock.sendto(hmsg.encode(),('localhost',10000+j))
            #sleep for the hello interval to maintain the rate of sending the hello messages
            time.sleep(hi)
#function to process the recieved messages
def reply(rsock,i,neighbours,currtable):
    #intialising all sequence numbers to -1 intially
    seq_num=[-1]*len(neighbours)
    while flag!=1:
        #recieve the message
        smsg=rsock.recvfrom(1024)
        #parsing the recieved message
        msg=smsg[0].decode()
        #parsing the port number of the sender
        portnum=int(smsg[1][1])
        msg=msg.strip().split()
        #if the message is a hello message
        if msg[0]=="HELLO":
            #send a hello reply message to the sender where the cost of the edge is randomly chosen between the given values in the graph
            minc,maxc=neighbours[int(msg[1])]
            dist=random.randint(minc,maxc)
            msgtobesent="HELLOREPLY "+str(i)+" "+str(msg[1])+" "+str(dist)
            rsock.sendto(msgtobesent.encode(),('localhost',10000+int(msg[1])))
        #if the message is a LSA message
        elif msg[0]=="LSA":
            #parse the message and obtain the source id, sequence number, number of entries
            srcid=int(msg[1])
            seqnum=int(msg[2])
            nume=int(msg[3])
            #if the sequence number is greater than the current sequence number then update the routing table and broadcast the message to all the neighbours
            if seq_num[srcid]<seqnum:
                seq_num[srcid]=seqnum
                #obtain the destination ids from the entries in LSA and update the current routing table
                for i in range(4,2*nume+4,2):
                    destid=int(msg[i])
                    #if there was no edge earlier or the edge existing earlier had a greater cost value then update it with the value given in the entry
                    if (currtable[srcid][destid]==-1) or (currtable[srcid][destid]>int(msg[i+1])):
                        currtable[srcid][destid]=int(msg[i+1])
                #broadcast the message to all the neighbours except the source
                for i in range(len(neighbours)):
                    if i!=srcid and neighbours[i]!=(-1,-1):
                        rsock.sendto(smsg[0],('localhost',10000+i))
        #if the message is a hello reply message then just update the routing table entry
        elif msg[0]=="HELLOREPLY":
            currtable[int(msg[2])][int(msg[1])]=int(msg[3])

#function to create lsa packets and broadcast them
def lsa(rsock,lsai,i,neighbours,currtable):
    seqnum=0
    while flag!=1:
        time.sleep(lsai)
        #create the lsa packet in the given format
        msgtobesent="LSA "+str(i)+" "+str(seqnum)
        c=0
        #entries in the lsa packet
        entries=" "
        for j in range(len(currtable[i])):
            if currtable[i][j]!=-1:
                entries+=str(j)+" "+str(currtable[i][j])+" "
                c+=1
        #append number of entries and entries in the LSA header
        msgtobesent+=" "+str(c)+entries
        #broadcast the message to all the neighbours
        for j in range(len(neighbours)):
            if neighbours[j]!=(-1,-1):
                rsock.sendto(msgtobesent.encode(),('localhost',10000+j))
        seqnum+=1
        time.sleep(lsai)

# def outp(currtable):
#     for i in currtable:
#         print(i)

#dijkstra's algorithm to find the shortest path
def dijkstra(g,src,destn):
    dist=[sys.maxsize] * len(g)
    v=len(g)
    paths={src: [src]}
    dist[src]=0
    sptSet=[False]*len(g)
    for i in range(v):
        currv=-1
        for j in range(v):
            if sptSet[j]==False and (currv==-1 or dist[j]<dist[currv]):
                currv=j
        sptSet[currv]=True
        for j in range(v):
            if g[currv][j]>0 and sptSet[j]==False:
                if dist[j]>dist[currv]+g[currv][j]:
                    dist[j]=dist[currv]+g[currv][j]
                    paths[j]=paths[currv]+[j]
    return dist[destn],paths[destn]

#function to update the routing table and write it to the output
def spf(currtable,spfi,ofd,i):
    now=0
    while now<=100:
        time.sleep(spfi)
        #change the time stamp
        now+=spfi
        #output the routing table
        ofd.write("Routing Table for Node No. "+str(i)+" at Time "+str(now)+"\n")
        ofd.write("Destination\t\t Path \t\t Cost\n")
        for j in range(len(currtable)):
            if j!= i:
                c,p=dijkstra(currtable,i,j)
                ofd.write(str(j)+"     \t\t")
                for k in range(len(p)):
                    ofd.write(str(p[k])+" ")
                ofd.write("\t\t"+str(c)+"\n")
    flag=1
    print(now)
    print("ROUTING TABLE FOR NODE "+str(i)+" WRITTEN TO OUTPUT FILE")
    ofd.close()

#graph is stored in the for of a list which contains the cost of the edge between the nodes    
graph=[]
#this dictionary stores the edges and their weights
edgew={}

#parsing the command line arguments
#incorrect format
if len(sys.argv)!=13:
    print(len(sys.argv))
    print("INVALID INPUT FORMAT")
    exit()
#parsing the command line arguments and intiaising them
#node identifier value
nid=int(sys.argv[2])
#input filename
ifn=sys.argv[4]
ifd=open(ifn,"r")
#parsing input file
inp=ifd.readline().strip().split()
numr=int(inp[0])
nume=int(inp[1])
#parsing input file to get the edges and their costs
for i in ifd:
    inp=i.strip().split()
    edgew[(int(inp[0]),int(inp[1]))]=(int(inp[2]),int(inp[3]))
    edgew[(int(inp[1]),int(inp[0]))]=(int(inp[2]),int(inp[3]))
#initialising the graph
for i in range(numr):
    node=[]
    for j in range(numr):
        if (i,j) in edgew:
            node.append(edgew[(i,j)])
        else:
            node.append((-1,-1))
    graph.append(node)
#output filename
ofn=sys.argv[6]
#default sleep time values and updating to the given values
hi = 1
hi=int(sys.argv[8])
lsai=5
lsai=int(sys.argv[10])
spfi=15
spfi=int(sys.argv[12])
#storing the threads in the list
hellothreads=[]
replythreads=[]
lsathreads=[]
spfthread=[]
#creating threads for each router
for i in range(0,numr):
    # print("Main loop")
    #current routing table
    currtable=[[-1 for j in range(numr)]for k in range(numr)]
    # print(currtable)
    #socket for sending and receiving messages
    rsock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #binding it to the given port number
    rsock.bind(('localhost',10000+i))
    #intialising the thread to send hello, recieve hello, create and broadcast lsa packets 
    tid0=threading.Thread(target=hello,args=(rsock,hi,i,graph[i]))
    tid1=threading.Thread(target=reply,args=(rsock,i,graph[i],currtable))
    tid2=threading.Thread(target=lsa,args=(rsock,lsai,i,graph[i],currtable))
    # tid3=threading.Thread(target=outp,args=(currtable))
    #creating the output file in the given format
    outf=ofn+"-"+str(i)+'.txt'
    ofd=open(outf,'w')
    #creating the thread for shortest path computation and updation
    tid3=threading.Thread(target=spf,args=(currtable,spfi,ofd,i))
    #storing the threads in the list
    hellothreads.append(tid0)
    replythreads.append(tid1)
    lsathreads.append(tid2)
    spfthread.append(tid3)

count=0
#starting the threads to recieve messages
for i in replythreads:
    print("Reciever thread up for router "+str(count))
    count+=1
    i.start()
#starting the thread to send hello messages
count=0
for i in hellothreads:
    #sleep times are used for synchronisation
    time.sleep(1)
    print("Hello Sender thread up for router "+str(count))
    count+=1
    i.start()
time.sleep(5)
#starting the thread to send lsa packets
count=0
for i in lsathreads:
    print("LSA thread up for router "+str(count))
    count+=1
    i.start()
    time.sleep(1)
#starting the thread to compute shortest path
count=0
for i in spfthread:
    print("SPF thread up for router "+str(count))
    count+=1
    i.start()
#setting the flag to 1 to stop the threads