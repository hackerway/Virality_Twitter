import networkx as nx
import sys,gzip
import pymongo
import datetime
from collections import OrderedDict
import numpy
import matplotlib.pyplot as plt

class Ddict(dict):
	def __init__(self, default=None):
		self.default = default

	def __getitem__(self, key):
		if not self.has_key(key):
			self[key] = self.default()
		return dict.__getitem__(self, key)


def connect_db():

   client = pymongo.MongoClient("localhost", 27017)
   db = client.follower_network
   return db
   
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
	db=connect_db()
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


def read_timeline():
    
    fread=open('timeline.data','r').readlines()
    big_chunk=[]
    #for line in range(3,10):
    generate_graph(fread[3])



def generate_graph(line):
        
   db=connect_db()
   hash_network={}
   chunks=line.split(',')
   hashtag=chunks[0].split(' ')[0]
   time=int(chunks[0].split(' ')[1])
   hash_network[get_date(time)]=[]
   chunks=chunks[1:]
   
   for chunk in chunks:
       temp=chunk.split(' ')
       if len(temp)>1:    

           time=float(temp[1].strip())
           date=get_date(time)
           twitter_id=temp[0].strip()

           if date in hash_network:
                   node_list=hash_network[date]
                   if twitter_id:
                           node_list.append(twitter_id)
                   hash_network[date]=node_list
           else:
              node_list=[]
              node_list.append(twitter_id)
              hash_network[date]=node_list
           
   ordered_network = OrderedDict(sorted(hash_network.items(), key=lambda t: t[0]))
   generate_dependent_graph(db,ordered_network)
   #generate_independent_graph(db,ordered_network)
   
def generate_dependent_graph(db,network):
   
   index=0
   for time in network:
       if index==0:
          prev_list=network[time]
          graph=nx.Graph()
          graph.add_nodes_from(prev_list)
          graph=add_egdes(db,graph,prev_list)
          #print nx.connected_component_subgraphs(graph)
          draw_graph(graph,time)
           
       else:
               
           current_list=network[time]
           current_list.extend(prev_list)
           graph=nx.Graph()
           graph.add_nodes_from(current_list)
           graph=add_egdes(db,graph,current_list)
           #print nx.connected_component_subgraphs(graph)
           draw_graph(graph,time)
           prev_list=current_list
       index+=1    
 
def generate_independent_graph(db,network):

    for time in network:
        current_list=network[time]
        graph=nx.Graph()
        graph.add_nodes_from(current_list)
        graph=add_egdes(db,graph,current_list)
        draw_graph(graph,time)             

   
def add_egdes(db,graph,nodes):

    for node1 in nodes:
            for node2 in nodes:
                first_flag=False
                for first in db.my_collection.find({'follower':str(node1),'followee':str(node2)}):
                     if first:
                             first_flag=True
                             
                second_flag=False         
                for second in db.my_collection.find({'follower':str(node2),'followee':str(node1)}):
                     if second:
                             second_flag=True
                if first_flag==True or second_flag==True:
                        graph.add_edge(node1,node2)
    return graph                    

def get_edge_density(graph):

    vertices=len(graph.nodes())
    edges=len(graph.edges())
    density=0
    try:
      if vertices>0:
       density=(2*edges)/(vertices*(vertices-1))
    except:
        pass
    return density


def percentage_new_users():
    print 'rohit'
    

def number_connected_components(): 
   print 'rohit'


def growth_gcc():
	print 'rohit'        

def get_date_dictionary(start,end):
	
	dictionary={}
	start=start.split('-')
	sday=int(start[-1])
	smonth=int(start[1])
	syear=int(start[0])
	end=end.split('-')
	eday=int(end[-1])
	emonth=int(end[1])
	eyear=int(end[0])
	start=datetime.datetime(syear,smonth,sday)
	end=datetime.datetime(eyear,emonth,eday)
	step=datetime.timedelta(days=1)
	while start<=end:
		date=start.strftime('%Y-%m-%d')
		dictionary[date]=[]
		start+=step
	dictionary=OrderedDict(sorted(dictionary.items(), key=lambda t: t[0]))	
	return dictionary	

def get_date(timestamp):

    time= datetime.datetime.fromtimestamp(float(timestamp))
    date='-'.join([str(time.year),str(time.month),str(time.day)])
    return date      
   

def draw_graph(graph,time):

        nx.draw_random(graph)
        plt.show()
        

def main():
   global follower_dict
   follower_dict=Ddict(dict)
   read_timeline()
   

if __name__=='__main__':
	   main()


