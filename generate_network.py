from __future__ import division
import networkx as nx
import sys,gzip
import pymongo
from collections import OrderedDict
import numpy
import datetime
import matplotlib.pyplot as plt
from datetime import datetime,timedelta
from datetime import date
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
	   	 self.olduser_percentage_dict=self.get_dictionary(start,end,0.0)
	   	 self.connected_component_dict=self.get_dictionary(start,end,0)
	   	 self.growth_gcc_dict=self.get_dictionary(start,end,0)
	   	 self.non_connected_nodes_dict=self.get_dictionary(start,end,0)
	   	 self.avg_hashtag_activity=[]
	   	 self.avg_tweet_per_user=0.0
	   	 self.prev_users=set([])
	   	 self.hashtag=''
	     
	   def edge_density(self,date,graph):
	   	 vertices=len(graph.nodes())
	   	 edges=len(graph.edges())
	   	 density=0
	   	 print vertices,edges
	   	 try:
	   	  if vertices>0:
	   		 density=float((2*edges))/float((vertices*(vertices-1)))
	   		 self.edge_density_dict[date]=density
	   	 except:
	   	 	 print 'Edge_density Passed'
	   		 pass
	   
	   def non_connected_nodes(self,date,graph):	   	   
	   	   count=0
	   	   try:
	   	   		for node in graph.nodes():
	   	   	   		if graph.degree(node)==0:
	   	   	   	  		count+=1
	   	   	   	self.non_connected_nodes_dict[date]=count
	   	   except:
	   	   	  print 'Non Connected Component'
	   	   	  pass

	   def average_tweet_time(self,datetimes):   	
	   	  
	   	  if len(datetimes)>1:
	   	  	self.avg_hashtag_activity=[float(datetimes[i])-float(datetimes[i-1]) for i in range(1, len(datetimes))]
	   	  
	   
	   def connected_components(self,date,graph):
	   	   try:
	   	        self.connected_component_dict[date]=nx.number_connected_components(graph)
	   	        print nx.number_connected_components(graph)
	   	   except:
	   	   		print 'Connected Passed'
	   	   		pass
	   
	   def size_gaint_connected_components(self,date,graph):
	   	   try:
	   	   		self.growth_gcc_dict[date]=len(list(nx.connected_component_subgraphs(graph)[0]))/len(graph.nodes())	   	   
	   	   		
	   	   except:
	   	   	    print 'Giant Passed'
	   	   	    pass
	       	   
	   def percentage_new_user(self,date,graph):
	   		new_users=set([])
	   		for node in graph.nodes():
	   	   	   if node not in self.prev_users:
	   	   	   	  new_users.add(node)
	   	   	new_delta=0.0
	   	   	old_delta=0.0
	   	   	try:
	   	   		new_delta=float(len(new_users))/float(len(graph.nodes()))
	   	   		old_delta=(float(len(graph.nodes()))-float(len(new_users)))/float(len(graph.nodes()))
	   	   	except:
	   	   		new_delta=0.0
	   	   		old_delta=0.0
	   	   		print 'Percentage Passed'
	   	   		pass	
	   	   	self.newuser_percentage_dict[date]=new_delta
	   	   	self.olduser_percentage_dict[date]=old_delta
	   	   	
	   	   	self.prev_users=new_users	   
	   
	   def average_tweets(self,user_list):	   	   
	   	   user_dict={}
	   	   
	   	   for user in user_list:
	   	   	   if user in user_dict:
	   	   	   	  user_dict[user]+=1
	   	   	   else:
	   	   	   	  user_dict[user]=1
	   	   avg=0.0
	   	   for user in user_dict:
	   	   	   avg+=user_dict[user]
	   	   	   
	   	   try:	   
	   	   		self.avg_tweet_per_user=avg/len(user_dict)
	   	   		print self.avg_tweet_per_user
	   	   except:
	   	   	     self.avg_tweet_per_user=0.0
	   	   	     pass
                	       	 

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
    global final_features_list
    fread=open(sys.argv[2],'r').readlines()
    big_chunk=[]
    index=0
    
    print len(fread)
    for line in range(len(fread)):
    	try:
    	    generate_graph_util(fread[line])
        except:
        	print 'graph Passed'
        	pass
    plot_graph()
        
def generate_graph_util(read):
	
	global final_features_list
	
	timestamps,user_lists,dep_network,hashtag=generate_graph(read)
	print hashtag
	feature_set=Feature_Set('2012-03-01','2012-05-30')
	feature_set.hashtag=hashtag
	feature_set.average_tweet_time(timestamps)
	feature_set.average_tweets(user_lists)
	final_features_list.append(generate_dependent_graph(dep_network,feature_set))
	
	'''ind_network,hashtag=generate_graph(read)
	features=Feature_Set('2012-03-01','2012-05-30')
	features.hashtag=hashtag
	generate_independent_graph(ind_network,features)
	'''
	
def generate_graph(line):
        
   db=connect_db()
   hash_network={}
   chunks=line.split(',')
   hashtag=chunks[0].split(' ')[0]
   time=int(chunks[0].split(' ')[1])
   hash_network[get_date(time)]=[]
   chunks=chunks[1:]
   timestamps=[]
   user_lists=[]
   for chunk in chunks:
       temp=chunk.split(' ')
       if len(temp)>1:    

           time=float(temp[1].strip())
           timestamps.append(time)
           date=get_date(time)
           twitter_id=temp[0].strip()
           user_lists.append(twitter_id)
           if date in hash_network:
                   node_list=hash_network[date]
                   if twitter_id:
                           node_list.append(twitter_id)
                   hash_network[date]=node_list
           else:
              node_list=[]
              node_list.append(twitter_id)
              hash_network[date]=node_list
           
   return timestamps,user_lists,OrderedDict(sorted(hash_network.items(), key=lambda t: t[0])),hashtag
   
   
def features_util(features,date,graph):
	
	features.edge_density(date,graph)
	features.connected_components(date, graph)
	features.percentage_new_user(date, graph)
	features.size_gaint_connected_components(date, graph)
	features.non_connected_nodes(date,graph)
	
def plot_graph():	
	global final_features_list
	edge_density_ddict=Ddict(dict)
	new_user_ddict=Ddict(dict)
	connected_component_ddict=Ddict(dict)
	growth_gcc_ddict=Ddict(dict)
	old_user_ddict=Ddict(dict)
	non_connected_component_ddict=Ddict(dict)
	avg_hashtag_activity_ddict=Ddict(dict)
	avg_tweet_peruser_dict={}
	print "I AM HERE"
	#if not os.path.exists(features.hashtag+"\\"+type_folder):
		#os.makedirs(features.hashtag+"\\"+type_folder)
	for features in final_features_list:
	    edge_density_ddict[features.hashtag]['x']=list(features.edge_density_dict.keys())
	    edge_density_ddict[features.hashtag]['y']=list(features.edge_density_dict.values())
	generate_plot(edge_density_ddict,"Edge Density","Dates","Density","Edge_Density",True)
	    
	for features in final_features_list:
		new_user_ddict[features.hashtag]['x']=list(features.newuser_percentage_dict.keys())
		new_user_ddict[features.hashtag]['y']=list(features.newuser_percentage_dict.values())
	generate_plot(new_user_ddict,"New Users","Dates","Growth Rate","New Users",True)
	
	for features in final_features_list:
		connected_component_ddict[features.hashtag]['x']=list(features.connected_component_dict.keys())
		connected_component_ddict[features.hashtag]['y']=list(features.connected_component_dict.values())
	generate_plot(connected_component_ddict,"Connected Components","Dates","Number of Connected Component","Connected Components",True)
	
	for features in final_features_list:
		growth_gcc_ddict[features.hashtag]['x']=list(features.growth_gcc_dict.keys())
		growth_gcc_ddict[features.hashtag]['y']=list(features.growth_gcc_dict.values())
	generate_plot(growth_gcc_ddict,"GCC Growth","Dates","Growth of GCC","GCC Growth",True)
	
	for features in final_features_list:
		old_user_ddict[features.hashtag]['x']=list(features.olduser_percentage_dict.keys())
		old_user_ddict[features.hashtag]['y']=list(features.olduser_percentage_dict.values())
	generate_plot(old_user_ddict,"Retention of Users","Dates","User Retention","User_Dropouts",True)
	
	for features in final_features_list:
		non_connected_component_ddict[features.hashtag]['x']=list(features.non_connected_nodes_dict.keys())
		non_connected_component_ddict[features.hashtag]['y']=list(features.non_connected_nodes_dict.values())
	generate_plot(growth_gcc_ddict,"Individual Nodes","Dates","Number of Independent Nodes","Non Connected Components",True)
	
	for features in final_features_list:
		avg_hashtag_activity_ddict[features.hashtag]['y']=features.avg_hashtag_activity
		temp=[]
		for i in range(1,len(features.avg_hashtag_activity)+1):temp.append(i)
		avg_hashtag_activity_ddict[features.hashtag]['x']=temp
	generate_plot(avg_hashtag_activity_ddict,"Tweet Activity","Index","Time Lag","Tweet Activity",False)	
	
	xaxis=[]
	yaxis=[]
	for features in final_features_list:
		xaxis.append(features.hashtag)
		yaxis.append(features.avg_tweet_per_user)
		
	generate_histogram("Average Tweet per User","HashTag","Average Tweets per User",xaxis,yaxis)

def generate_histogram(title,xlabel,ylabel,x,y):
	import numpy as np
	pos = np.arange(len(x))
	width = .3     # gives histogram aspect to the bar diagram
	ax = plt.axes()
	ax.set_xticks(pos + (width / 2))
	ax.set_xticklabels(x)
	plt.title(title)
	plt.ylabel(ylabel)
	plt.xlabel(xlabel)
	plt.bar(pos,y, width, color='g')
	plt.show()		
	plt.savefig('AverageTweetsPerHashtags.svg',dpi=(600))
	plt.close()
	
def generate_plot(dictionary,title,labelX,labelY,filename,flag):
   figure=plt.figure()
   plt.title(title)
   plt.ylabel(labelY)
   plt.xlabel(labelX)
   figure.autofmt_xdate()
   for hashtag in dictionary:
    	x=dictionary[hashtag]['x']
    	if flag==True:
    	 	x=dates.datestr2num(x)
     	y=dictionary[hashtag]['y']
     	if flag==True:
      		plt.plot_date(x,y,'-',linewidth=2.0,label=str(hashtag))
      	else:
      		plt.plot(x,y,linewidth=3.0)		
   plt.legend(loc='upper left')
   plt.show()
   plt.savefig(filename,dpi=(600))
   

def generate_dependent_graph(network,features):
   
   db=connect_db()
   index=0
   prev_graph_object=nx.Graph()
   
   for time in network:
       if index==0:
          prev_list=network[time]
          graph=nx.Graph()
          graph.add_nodes_from(prev_list)
          graph=add_egdes(db,graph,prev_list)
          features_util(features,time,graph)
          prev_graph_object=graph
          #draw_graph(graph,time,features,"dependent")        
       else:
               
           current_list=network[time]
           graph=nx.Graph()           
           graph.add_nodes_from(current_list)
           graph=add_egdes(db,graph,current_list)
           graph.add_nodes_from(prev_graph_object)
           graph.add_edges_from(prev_graph_object.edges())
           prev_graph_object=graph
           
           features_util(features,time,graph)
       index+=1    
           #draw_graph(graph,time,features,"dependent")
   
   return features
    
def generate_independent_graph(network,features):
	
    db=connect_db()
    for time in network:
    	current_list=network[time]
        graph=nx.Graph()
        graph.add_nodes_from(current_list)
        graph=add_egdes(db,graph,current_list)
        #draw_graph(graph,time,features,"independent")             
        features_util(features,time,graph)
    
    plot_graph(features,"independent")
   
def add_egdes(db,graph,nodes):

    follower_dict={}
    
    
    for node1 in nodes:
            for node2 in nodes:
                first_flag=False
                second_flag=False
                if node1!=node2:
                 	if node1 in follower_dict:
                 		if follower_dict[node1]==node2:
                 			break
                 	if node2 in follower_dict:
                 		if follower_dict[node2]==node1:
                 			break
                 		
                 	for first in db.my_collection.find({'follower':str(node1),'followee':str(node2)}):
                 		if first:
                 			 follower_dict[node1]=node2
                 			 follower_dict[node2]=node1
                 			 first_flag=True
                 	if first_flag==False:    
					 	for second in db.my_collection.find({'follower':str(node2),'followee':str(node1)}):
					 	    if second:
					 	    	follower_dict[node1]=node2
                 			 	follower_dict[node2]=node1
                 			 	second_flag=True
                	if first_flag==True or second_flag==True:
                        	 graph.add_edge(node1,node2)
    return graph                    



       
def get_date(timestamp):
    
    time= datetime.fromtimestamp(float(timestamp))
    return time.strftime('%Y-%m-%d')
          
   

def draw_graph(graph,time,features,type_folder):

	    try:
	    
	    	#nx.draw_random(graph,node_color='#A0CBE2',edge_color='Green',with_labels=False)
	    	
	    	if not os.path.exists(features.hashtag+"\\"+type_folder):
			   os.makedirs(features.hashtag+"\\"+type_folder)
	    	filename=features.hashtag+"\\"+type_folder+"\\"+str(time)+"_graph.graphml"	    
	    	nx.write_graphml(graph,filename)
	    	#plt.savefig(filename)
	    	#plt.close()
	    except:
	        raise
	    		

def main():
   global final_features_list
   final_features_list=[]
   init_path()
   follower_dict=Ddict(dict)
   read_timeline()
   
   	
if __name__=='__main__':
	   main()


