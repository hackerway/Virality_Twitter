import networkx as nx
import sys,gzip
import pymongo
import datetime
from collections import OrderedDict
import numpy
import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from datetime import datetime
from datetime import date, timedelta


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
	   	   self.connected_component_dict[date]=nx.number_connected_components(graph)
	   
	   
	   def size_gaint_connected_components(self,date,graph):
	   	   self.growth_gcc_dict[date]=nx.connected_component_subgraphs(graph)[0]	   	   
	   
	   def percentage_new_user(self,date,graph):
	   		new_users=set([])
	   		for node in graph.nodes():
	   	   	   if node not in self.prev_users:
	   	   	   	  new_users.add(node)
	   	   	if len(self.prev_users)==0:temp=1
	   	   	else:temp=len(self.prev_users)
	   	   	delta=float((len(new_users)-len(self.prev_users)))/float(temp)
	   	   	self.newuser_percentage_dict[date]=delta
	   	   	self.prev_users=new_users	   
	       

	   def get_dictionary(self,start,end,value):
	
		 dictionary={}
		 start=start.split('-')
		 end=end.split('-')
		 start=datetime.datetime(int(start[0]),int(start[1]),int(start[2]))
		 end=datetime.datetime(int(end[0]),int(end[1]),int(end[2]))
		 step=datetime.timedelta(days=1)
		 while start<=end:
			date=start.strftime('%Y-%m-%d')
			dictionary[date]=value
			start+=step
		 dictionary=OrderedDict(sorted(dictionary.items(), key=lambda t: t[0]))	
		 return dictionary	


class TimeSeries:
	
	def generate_plot(self,x,y,title,labelX,labelY,filename):
		figure=plt.figure()
		x=dates.datestr2num(x)
		plt.title(title)
		plt.ylabel(labelY)
		plt.xlabel(labelX)
		figure.autofmt_xdate()
		plt.plot_date(x, y, fmt="r-",color='orange')
		plt.savefig(filename,dpi=(600))
    	plt.close()
	    


def connect_db():

   client = pymongo.MongoClient("localhost", 27017)
   db = client.follower_network
   return db
   

def read_timeline():
    
    fread=open('timeline.data','r').readlines()
    big_chunk=[]
    #for line in range(3,10):
    generate_graph(fread[3])

def generate_graph_util(read):
	
	feature_set=Feature_Set('2012-04-01','2012-04-30')
	
	
	
	


def generate_graph(line,features):
        
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
   generate_dependent_graph(db,ordered_network,features)
   #generate_independent_graph(db,ordered_network)
   
def generate_dependent_graph(db,network,features):
   
   index=0
   for time in network:
       if index==0:
          prev_list=network[time]
          graph=nx.Graph()
          graph.add_nodes_from(prev_list)
          graph=add_egdes(db,graph,prev_list)
          draw_graph(graph,time)
           
       else:
               
           current_list=network[time]
           current_list.extend(prev_list)
           graph=nx.Graph()
           graph.add_nodes_from(current_list)
           graph=add_egdes(db,graph,current_list)
           draw_graph(graph,time)
           prev_list=current_list
       index+=1    
 
def generate_independent_graph(db,network,features):

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


