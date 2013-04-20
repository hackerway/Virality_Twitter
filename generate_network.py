from __future__ import division
import networkx as nx
import sys,gzip
import pymongo
from collections import OrderedDict
import numpy
import datetime
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import date,timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import os


def init_path():
	try:
		os.chdir(sys.argv[1])
		if not os.path.exists("Graphs"):
			os.makedirs("Graphs")
			os.chdir(sys.argv[1]+"\\Graphs")
	except:
		print 'Path doesnt exists'
		sys.exit()
	
class Ddict(dict):
	def __init__(self, default=None):
		self.default = default

	def __getitem__(self, key):
		if not self.has_key(key):
			self[key] = self.default()
		return dict.__getitem__(self, key)


class Feature_Set:
	
	   def __init__(self,start,end):
	   	 
	   	 self.edge_density_dict=self.get_dictionary(start,end,0.0)		
	   	 self.newuser_percentage_dict=self.get_dictionary(start,end,0.0)
	   	 self.connected_component_dict=self.get_dictionary(start,end,0)
	   	 self.growth_gcc_dict=self.get_dictionary(start,end,0)
	   	 self.prev_users=set([])
	   	 self.hashtag=''
	     
	   def edge_density(self,date,graph):
	   	 vertices=len(graph.nodes())
	   	 edges=len(graph.edges())
	   	 density=0
	   	 try:
	   	  if vertices>0:
	   		 density=float((2*edges))/float((vertices*(vertices-1)))
	   		 self.edge_density_dict[date]=density
	   	 except:
	   		 pass
	   		
	   
	   def connected_components(self,date,graph):
	   	   try:
	   	        self.connected_component_dict[date]=nx.number_connected_components(graph)
	   	   except:
	       	    pass
	   
	   def size_gaint_connected_components(self,date,graph):
	   	   try:
	   	   		self.growth_gcc_dict[date]=len(list(nx.connected_component_subgraphs(graph)[0]))/len(graph.nodes())	   	   
	   	   		
	   	   except:
	       	    pass
	   def percentage_new_user(self,date,graph):
	   		new_users=set([])
	   		for node in graph.nodes():
	   	   	   if node not in self.prev_users:
	   	   	   	  new_users.add(node)
	   	   	delta=0.0
	   	   	try:
	   	   		delta=float(len(new_users))/float(len(graph.nodes()))
	   	   	except:
	   	   		delta=0.0
	   	   		pass	
	   	   	self.newuser_percentage_dict[date]=delta
	   	   	self.prev_users=new_users	   
	       

	   def get_dictionary(self,start,end,value):
	
		 dictionary={}
		 start=start.split('-')
		 end=end.split('-')
		 start=datetime(int(start[0]),int(start[1]),int(start[2]))
		 end=datetime(int(end[0]),int(end[1]),int(end[2]))
		 step=timedelta(days=1)
		 while start<=end:
			date=start.strftime('%Y-%m-%d')
			dictionary[date]=value
			start+=step
		 dictionary=OrderedDict(sorted(dictionary.items(), key=lambda t: t[0]))	
		 return dictionary	

def connect_db():

    client = pymongo.MongoClient("localhost", 27017)
    db = client.follower_network
    return db
   

def read_timeline():
    
    fread=open(sys.argv[2],'r').readlines()
    big_chunk=[]
    index=0
    #check 367
    for line in range(368,len(fread)):
    	try:
     		generate_graph_util(fread[line])
        except:
        	pass
def generate_graph_util(read):
	
	dep_network,hashtag=generate_graph(read)
	feature_set=Feature_Set('2012-04-01','2012-04-30')
	feature_set.hashtag=hashtag
	generate_dependent_graph(dep_network,feature_set)
	print hashtag
	ind_network,hashtag=generate_graph(read)
	features=Feature_Set('2012-04-01','2012-04-30')
	features.hashtag=hashtag
	generate_independent_graph(ind_network,features)
	
	
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
           
   return OrderedDict(sorted(hash_network.items(), key=lambda t: t[0])),hashtag
   
   
def features_util(features,date,graph):
	
	features.edge_density(date,graph)
	features.connected_components(date, graph)
	features.percentage_new_user(date, graph)
	features.size_gaint_connected_components(date, graph)

def plot_graph(features,type_folder):	
	
	if not os.path.exists(features.hashtag+"\\"+type_folder):
		os.makedirs(features.hashtag+"\\"+type_folder)
		
	generate_plot(list(features.edge_density_dict.keys()),list(features.edge_density_dict.values()),"Edge Density "+features.hashtag,"Dates","Density",features.hashtag+"\\"+type_folder+"\\Edge_Density")
	generate_plot(list(features.newuser_percentage_dict.keys()),list(features.newuser_percentage_dict.values()),"Percentage of New Users "+features.hashtag,"Dates","Value",features.hashtag+"\\"+type_folder+"\\New_Users")
	generate_plot(list(features.connected_component_dict.keys()),list(features.connected_component_dict.values()),"Connected Component "+features.hashtag,"Dates","Connected Components",features.hashtag+"\\"+type_folder+"\\Connected_Components")
	generate_plot(list(features.growth_gcc_dict.keys()),list(features.growth_gcc_dict.values()),"GCC Growth "+features.hashtag,"Dates","Growth Rate",features.hashtag+"\\"+type_folder+"\\GCC_Growth")
    
def generate_plot(x,y,title,labelX,labelY,filename):

    figure=plt.figure()
    x=dates.datestr2num(x)
    #print '######################'+title+'#######################'
    #print y
    
    plt.title(title)
    plt.ylabel(labelY)
    plt.xlabel(labelX)
    figure.autofmt_xdate()
    plt.plot_date(x, y, fmt="r-",color='orange')
    plt.savefig(filename,dpi=(600))
    plt.close()

def generate_dependent_graph(network,features):
   db=connect_db()
   index=0
   for time in network:
       if index==0:
          prev_list=network[time]
          graph=nx.Graph()
          graph.add_nodes_from(prev_list)
          graph=add_egdes(db,graph,prev_list)
          features_util(features,time,graph)
          draw_graph(graph,time,features,"dependent")        
       else:
               
           current_list=network[time]
           current_list.extend(prev_list)
           
           graph=nx.Graph()
           graph.add_nodes_from(current_list)
           graph=add_egdes(db,graph,current_list)
           prev_list=current_list
           features_util(features,time,graph)
           draw_graph(graph,time,features,"dependent")
       index+=1    
   
   plot_graph(features,"dependent")
    
def generate_independent_graph(network,features):
	
    db=connect_db()
    for time in network:
    	current_list=network[time]
        graph=nx.Graph()
        graph.add_nodes_from(current_list)
        graph=add_egdes(db,graph,current_list)
        draw_graph(graph,time,features,"independent")             
        features_util(features,time,graph)
    
    plot_graph(features,"independent")
   
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



       
def get_date(timestamp):
    
    time= datetime.fromtimestamp(float(timestamp))
    return time.strftime('%Y-%m-%d')
          
   

def draw_graph(graph,time,features,type_folder):
	    
	    
	    
	    try:
	    
	    	nx.draw_random(graph,node_color='#A0CBE2',edge_color='Green',with_labels=False)
	    	
	    	if not os.path.exists(features.hashtag+"\\"+type_folder):
			   os.makedirs(features.hashtag+"\\"+type_folder)
	    	filename=features.hashtag+"\\"+type_folder+"\\"+str(time)+"_graph.png"	    
	    	plt.savefig(filename)
	    	plt.close()
	    except:
	    	plt.close()
	    	pass	

def main():
   global follower_dict
   init_path()
   follower_dict=Ddict(dict)
   read_timeline()
   

if __name__=='__main__':
	   main()


