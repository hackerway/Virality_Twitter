import networkx as nx
import sys,gzip
import pymongo
import generate_network as gen_net

def file_reader():
   try:
       fread=gzip.open("follower_list.dat.gz")
       fread=fread.readlines()
       read_follower(fread)
   except:
       print "Passes"
       pass



def read_follower(reader):  

    index=1
    db=gen_net.connect_db()
    for line in reader:
        print 'Record: ',index
        index+=1
        div=line.split(':')
        user=str(div[0].strip())
        following=div[1].split(',')
        for follow in following:
            try: 
                if follow!=None or follow!=' ':
                    value=str(follow.strip())
                    db.my_collection.save({"followee":user,"follower":value})             
            except:
                                        
                    pass
    db.my_collection.create_index('followee')      

