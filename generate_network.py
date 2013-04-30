# Using the magic encoding
# -*- coding: utf-8 -*-
from __future__ import division
import networkx as nx
import sys, gzip
import pymongo
from collections import OrderedDict
import numpy
import datetime
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import matplotlib.ticker as tic

import os

matplotlib.use('TkAGG')

def init_path():
	try:
		os.chdir(sys.argv[1])
		if not os.path.exists("Graphs"):
			os.makedirs("Graphs")
			os.chdir(sys.argv[1] + "\\Graphs")
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
	
	   def __init__(self, start, end):
	   	 
	   	 self.edge_density_dict = self.get_dictionary(start, end, 0.0)		
	   	 self.newuser_percentage_dict = self.get_dictionary(start, end, 0.0)
	   	 self.olduser_percentage_dict = self.get_dictionary(start, end, 0.0)
	   	 self.connected_component_dict = self.get_dictionary(start, end, 0)
	   	 self.growth_gcc_dict = self.get_dictionary(start, end, 0)
	   	 self.non_connected_nodes_dict = self.get_dictionary(start, end, 0)
	   	 self.avg_hashtag_activity = []
	   	 self.avg_tweet_per_user = 0.0
	   	 self.prev_users = set([])
	   	 self.new_user_list=Ddict(dict)
	   	 self.user_day_distribution={}
	   	 self.user_list=[]
                 self.date_tweet=self.get_dictionary(start, end, 0)
	   	 self.hashtag = ''
	         self.week_bucket={}
	         self.user_timestamp=Ddict(dict)
                 self.batch_week_contribution=Ddict(dict)
                 
	   def edge_density(self, date, graph):
	   	 vertices = len(graph.nodes())
	   	 edges = len(graph.edges())
	   	 density = 0
	   	 print vertices, edges
	   	 try:
	   	  if vertices > 0:
	   		 density = float((2 * edges)) / float((vertices * (vertices - 1)))
	   		 self.edge_density_dict[date] = density
	   		 print "Edge Density", density
	   	 except:
	   	 	 print 'Edge_density Passed'
	   		 pass
	   
	   def non_connected_nodes(self, date, graph):	   	   
	   	   
	   	   try:
	   	   	    
	   	   	    self.non_connected_nodes_dict[date] =len(nx.maximal_independent_set(graph, None))
	   	   	    print 'Maximal Independent Set',len(nx.maximal_independent_set(graph, None))
	   	   except:
	   	   	  print 'Non Connected Component'
	   	   	  pass

	   def tweet_activity(self, datetimes):   	
                  try:
                          for dt in datetimes:
                                  if dt in self.date_tweet:
                                          self.date_tweet[dt]=datetimes[dt]
	          except:
                          pass
	   def connected_components(self, date, graph):
	   	   try:
	   	        self.connected_component_dict[date] = nx.number_connected_components(graph)
	   	        
	   	   except:
	   	   		print 'Connected Passed'
	   	   		raise
	   
	   def size_gaint_connected_components(self, date, graph):
	   	   try:
	   	   		self.growth_gcc_dict[date] = len(list(nx.connected_component_subgraphs(graph)[0])) / len(graph.nodes())	   	   
	   	   		
	   	   except:
	   	   	    print 'Giant Passed'
	   	   	    pass
	       	   
	   def percentage_new_user(self, date, graph):

                        
	   		new_users = set([])
	   		for node in graph.nodes():
	   	   	   if node not in self.prev_users:
	   	   	   	  new_users.add(node)
	   	   	new_delta = 0.0
	   	   	old_delta = 0.0
	   	   	try:
	   	   		new_delta = float(len(new_users))# / float(len(graph.nodes()))
                                for user in new_users:   
                                        self.new_user_list[date][user]=0
	   	   		old_delta = (float(len(graph.nodes())) - float(len(new_users)))# / float(len(graph.nodes()))
	   	   	except:
	   	   		new_delta = 0.0
	   	   		old_delta = 0.0
	   	   		print 'Percentage Passed'
	   	   		raise
	   	   	self.newuser_percentage_dict[date] = new_delta
	   	   	self.olduser_percentage_dict[date] = old_delta
	   	   	
	   	   	self.prev_users = new_users	   
	   
	   def average_tweets(self):	   	   

	   	   user_dict = {}
	   	   
	   	   for user in self.user_list:
	   	   	   if user in user_dict:
	   	   	   	  user_dict[user] += 1
	   	   	   else:
	   	   	   	  user_dict[user] = 1
	   	   
                   for date in self.new_user_list:
                           total=0
                           for user in self.new_user_list[date]:
                                   if user in user_dict:
                                      total+=user_dict[user]
                           self.user_day_distribution[date]=total                             
                   self.user_day_distribution=OrderedDict(sorted(self.user_day_distribution.items(), key=lambda t: t[0]))
                   

	   def week_users_activity(self,user_timestamp):

                   self.user_timestamp=user_timestamp
                   user_week=Ddict(dict)
                   for key in self.user_timestamp:
                       for day in self.user_timestamp[key]:
                                 dt=datetime.strptime(day, "%Y-%m-%d").date()
                                 if  dt in self.week_bucket:
                                     weekday=self.week_bucket[dt]
                                     if weekday in user_week[key]:
                                             user_week[key][self.week_bucket[dt]]+= self.user_timestamp[key][day]
                                     else:
                                             user_week[key][self.week_bucket[dt]]= self.user_timestamp[key][day]
                   batch_week_contribution=Ddict(dict)
                   for day in self.new_user_list:
                            batch_week_contribution[day]=self.batch_util()
                   for day in self.new_user_list:
                       for user in self.new_user_list[day]:
                           for wkdy in user_week[user]:
                               batch_week_contribution[day][wkdy]+=user_week[user][wkdy]
                   self.batch_week_contribution=batch_week_contribution
                   self.batch_week_contribution=OrderedDict(sorted(self.batch_week_contribution.items(), key=lambda t: t[0]))
                   
                            
           def batch_util(self):
               temp={}
               for i in range(1,6):
                       temp[i]=0
               return temp        
                   
	   def get_dictionary(self, start, end, value):
	
		 dictionary = {}
		 start = start.split('-')
		 end = end.split('-')
		 start = datetime(int(start[0]), int(start[1]), int(start[2]))
		 end = datetime(int(end[0]), int(end[1]), int(end[2]))
		 step = timedelta(days=1)
		 while start <= end:
			date = start.strftime('%Y-%m-%d')
			dictionary[date] = value
			start += step
		 dictionary = OrderedDict(sorted(dictionary.items(), key=lambda t: t[0]))	
		 return dictionary

           def get_weeks_bucket(self,start,end):

        	 dictionary = {}
        	 week_dict={}
		 start = start.split('-')
		 end = end.split('-')
		 start = datetime(int(start[0]), int(start[1]), int(start[2]))
		 end = datetime(int(end[0]), int(end[1]), int(end[2]))
		 step = timedelta(days=1)
		 while start <= end:
			date = start.strftime('%Y-%m-%d')
			dictionary[date] = 0
			start += step
		 dictionary=OrderedDict(sorted(dictionary.items(), key=lambda t: t[0]))	
		 for key in dictionary:
                    dt=datetime.strptime(key, "%Y-%m-%d").date()
                    week_day=dt.weekday()
                    if week_day in week_dict:
                            week_dict[week_day].append(dt)
                    else:
                            lists=[dt]
                            week_dict[week_day]=lists
                 week_dict = OrderedDict(sorted(week_dict.items(), key=lambda t: t[0]))
                 week_bucket={}
                 
                 for key in week_dict:
                     index=0
                     days=week_dict[key]
                     for day in days:
                         index+=1    
                         if index in week_bucket:
                            week_bucket[index].append(day)
                         else:
                                 lists=[day]
                                 week_bucket[index]=lists
                                 
                 week_bucket = OrderedDict(sorted(week_bucket.items(), key=lambda t: t[0]))
                 for key in week_bucket:
                     dates=week_bucket[key]
                     for dt in dates:
                         self.week_bucket[dt]=key
                                   
	   	 
	   	 

def connect_db():

    client = pymongo.MongoClient("localhost", 27017)
    db = client.follower_network
    return db
   

def read_timeline():
    global final_features_list
    fread = open(sys.argv[2], 'r').readlines()
    lists=[]
    i=799
    while i <=3250:
	lists.append(i)
	lists.append(i+9)
	i+=10
    
    #for j in range(0,len(lists),2):
    final_features_list=[]    
    for line in range(len(fread)):
                try:
                    generate_graph_util(fread[line])
                except:
                        print 'graph Passed'
                        raise
    plot_graph('current')
    
    
def generate_graph_util(read):
	global final_features_list
	user_timestamp,date_tweet,timestamps, user_lists, dep_network, hashtag = generate_graph(read)
	print hashtag
	feature_set = Feature_Set('2012-04-01', '2012-04-30')
	feature_set.get_weeks_bucket('2012-03-10', '2012-05-20')
        
	feature_set.hashtag = hashtag
	feature_set.user_list=user_lists
	feature_set.tweet_activity(date_tweet)
	final_features_list.append(generate_dependent_graph(dep_network, feature_set,user_timestamp))
	
	'''ind_network,hashtag=generate_graph(read)
	features=Feature_Set('2012-03-01','2012-05-30')
	features.hashtag=hashtag
	generate_independent_graph(ind_network,features)
	'''
	
def generate_graph(line):
        
   db = connect_db()
   start='2012-03-31'
   start=datetime.strptime(start, "%Y-%m-%d").date()
   end='2012-05-01'
   end=datetime.strptime(end, "%Y-%m-%d").date()
   hash_network = {}
   chunks = line.split(',')
   temp=chunks[0]
   hashtag=temp.split(' ')[0]
   temp=chunks[0]
   date_tweet={}  
   time=float(temp.split(' ')[1])
   dt=get_date(time)
   dt=datetime.strptime(dt, "%Y-%m-%d").date()
   if dt > start and dt < end:
      hash_network[get_date(time)] = []
   else:
      hash_network['2012-04-01']=[]
      
   chunks = chunks[1:]
   timestamps = []
   user_lists = []
   
   user_timestamp=Ddict(dict)
   
   for chunk in chunks:
       temp = chunk.split(' ')
       if len(temp) > 1:    
         time = float(temp[1].strip())
         timestamps.append(time)
         date = get_date(time)
         dt=date
         dt=datetime.strptime(dt, "%Y-%m-%d").date()
         if dt > start and dt < end:
           twitter_id = temp[0].strip()
           if date in date_tweet:
                   date_tweet[date]+=1
           else:
                   date_tweet[date]=1
           if twitter_id in user_timestamp:
                   if date in user_timestamp[twitter_id]:
                           user_timestamp[twitter_id][date]+=1
                   if date not in user_timestamp[twitter_id]:
                           user_timestamp[twitter_id][date]=1
           if twitter_id not in user_timestamp:
                    user_timestamp[twitter_id][date]=1
                    
                           
                           
           user_lists.append(twitter_id)
           if date in hash_network:
                   node_list = hash_network[date]
                   if twitter_id:
                           node_list.append(twitter_id)
                           
                   hash_network[date] = node_list
           else:
              node_list = []
              node_list.append(twitter_id)
              hash_network[date] = node_list
           
   return user_timestamp,OrderedDict(sorted(date_tweet.items(), key=lambda t: t[0])),timestamps, user_lists, OrderedDict(sorted(hash_network.items(), key=lambda t: t[0])), hashtag
     
def features_util(features, date, graph,user_timestamp):

	features.edge_density(date, graph)
	features.connected_components(date, graph)
	features.percentage_new_user(date, graph)
        #features.week_users_activity(user_timestamp)
	features.size_gaint_connected_components(date, graph)

	features.non_connected_nodes(date, graph)
        
        
def polish(feature_dict):
	feature_list = list(feature_dict)
	prev_value = feature_dict[feature_list[0]]
	for i in range(1, len(feature_list)):
		current_value = feature_dict[feature_list[i]]
		if current_value == 0.0:
			feature_dict[feature_list[i]] = prev_value
			current_value = prev_value		    	 
		prev_value = current_value
	
	
def plot_graph(ids):	
	ids=str(ids)
	global final_features_list
	edge_density_ddict = Ddict(dict)
	new_user_ddict = Ddict(dict)
	connected_component_ddict = Ddict(dict)
	growth_gcc_ddict = Ddict(dict)
	old_user_ddict = Ddict(dict)
	non_connected_component_ddict = Ddict(dict)
	user_activity_ddict = Ddict(dict)
	user_contribution_ddict=Ddict(dict)
	tweet_activity_ddict = Ddict(dict)
	
	
	for features in final_features_list:
	    polish(features.edge_density_dict)	
	    edge_density_ddict[features.hashtag]['x'] = list(features.edge_density_dict.keys())
	    edge_density_ddict[features.hashtag]['y'] = list(features.edge_density_dict.values())
	generate_plot(edge_density_ddict, "Edge Density", "Dates", "Density", "Edge_Density",ids,True)
        for features in final_features_list:        
                polish(features.newuser_percentage_dict)
		new_user_ddict[features.hashtag]['x'] = list(features.newuser_percentage_dict.keys())
		new_user_ddict[features.hashtag]['y'] = list(features.newuser_percentage_dict.values())
        generate_plot(new_user_ddict, "New Users", "Dates", "Growth Rate", "New Users",ids, True)
	for features in final_features_list:
                
		polish(features.connected_component_dict)
		connected_component_ddict[features.hashtag]['x'] = list(features.connected_component_dict.keys())
		connected_component_ddict[features.hashtag]['y'] = list(features.connected_component_dict.values())
	generate_plot(connected_component_ddict, "Connected Components", "Dates", "#Connected Component", "Connected Components",ids, True)
	
	for features in final_features_list:
		polish(features.growth_gcc_dict)
		growth_gcc_ddict[features.hashtag]['x'] = list(features.growth_gcc_dict.keys())
		growth_gcc_ddict[features.hashtag]['y'] = list(features.growth_gcc_dict.values())
	generate_plot(growth_gcc_ddict, "GCC Growth", "Dates", "Growth of GCC", "GCC Growth",ids, True)
	for features in final_features_list:
		polish(features.olduser_percentage_dict)
		old_user_ddict[features.hashtag]['x'] = list(features.olduser_percentage_dict.keys())
		old_user_ddict[features.hashtag]['y'] = list(features.olduser_percentage_dict.values())
	generate_plot(old_user_ddict, "Retention of Users", "Dates", "User Retention", "User_Dropouts",ids, True)
        for features in final_features_list:
		polish(features.non_connected_nodes_dict)
		non_connected_component_ddict[features.hashtag]['x'] = list(features.non_connected_nodes_dict.keys())
		non_connected_component_ddict[features.hashtag]['y'] = list(features.non_connected_nodes_dict.values())
	generate_plot(non_connected_component_ddict, "Independent Nodes", "Dates", "Independent Nodes", "Non Connected Components",ids, True)

        for features in final_features_list:
            polish(features.date_tweet)    
            tweet_activity_ddict[features.hashtag]['x']=list(features.date_tweet.keys())
            tweet_activity_ddict[features.hashtag]['y']=list(features.date_tweet.values())
        generate_plot(tweet_activity_ddict, "Tweet Activity", "Dates", "Tweet Count ", "Tweet Activity",ids, True)
        
	for features in final_features_list:		
		user_activity_ddict[features.hashtag]['x'] =list(features.user_day_distribution.keys())
		user_activity_ddict[features.hashtag]['y'] =list(features.user_day_distribution.values())
	generate_histogram(user_activity_ddict,"Days", "Contribution")	

        '''for features in final_features_list:
                x=[]
                y=[]
                
                for dt in features.batch_week_contribution.keys():
                    temp=[]
                    for i in range(0,5):
                        temp.append(dt)
                    y.append(temp)
                    t=[]
                    for val in features.batch_week_contribution[dt]: 
                        t.append(features.batch_week_contribution[dt][val])
                    x.append(t)    
                    
                user_contribution_ddict[features.hashtag]['x']=x
                user_contribution_ddict[features.hashtag]['y']=y
        generate_user_activity(user_contribution_ddict) 		
	#generate_histogram(user_activity_ddict,"Days", "Contribution")	
        '''
def generate_user_activity(user_contribution_ddict):	
        import numpy as np
        figure=plt.figure(figsize=(6*3.13,4*3.13))
        for hashtag in user_contribution_ddict:
            xlist=user_contribution_ddict[hashtag]['x']
            ylist=user_contribution_ddict[hashtag]['y']
            for index in range(len(xlist)):
                x=xlist[index]
                
                y=ylist[index]
                y = dates.datestr2num(y)
                plt.plot(x,y)
        plt.show()
        plt.close()
             
def generate_histogram(user_activity_ddict,xlabel,ylabel):
	import numpy as np
	figure=plt.figure(figsize=(6*3.13,4*3.13))
	width = .3
	ax = plt.axes()
        nrow=1
        for feature in user_activity_ddict:
                ax=plt.subplot(3,3,nrow)
                nrow+=1
        
                x=user_activity_ddict[feature]['x']
                dates=[]
                for dt in x:
                        dates.append(datetime.strptime(dt, "%Y-%m-%d").date())
                        
                y=user_activity_ddict[feature]['y']
                width=0.8
                ax.bar(range(len(dates)), y, width=width,label=feature.decode('utf8'))
                ax.set_xticks(np.arange(len(dates)) + width/2)
                ax.set_xticklabels(dates, rotation=60)
                ax.legend(loc='upper right',prop={'size':10})
                
	plt.show()
	figure.savefig('AverageTweetsPerHashtags.png', dpi=(600))
	plt.close()
	
def generate_plot(dictionary, title, labelX, labelY, filename,ids, flag):
   import numpy as np
   
   figure=plt.figure(figsize=(6*3.13,4*3.13))
   
   plt.title(title)
   hspace = 1.0
   nrow=1
   plt.subplots_adjust( hspace=hspace )
   figure.autofmt_xdate()
   for hashtag in dictionary:
    	x = dictionary[hashtag]['x']
    	x = dates.datestr2num(x)
    	y = dictionary[hashtag]['y']
     	plt.subplot(3,3,nrow)
        nrow+=1
        plt.ylabel(labelY)
        plt.xlabel(labelX)
        plt.xticks(rotation=30)
      	plt.plot_date(x, y, '-',color='green', linewidth=2.0, label=hashtag.decode('utf8'))
      	plt.legend(loc='best',prop={'size':10})
      	
   plt.show()
   figure.savefig(filename+ids,dpi=(1200))
   plt.close()

def generate_dependent_graph(network, features,user_timestamp):
   global follower_dict
   db = connect_db()
   follower_dict = Ddict(dict)
   index = 0
   current_graph = nx.Graph()
   for time in network:
       if index == 0:
          prev_list = network[time]
          current_graph = nx.Graph()
          current_graph.add_nodes_from(prev_list)
          current_graph = add_egdes(db, current_graph)          
          features_util(features, time, current_graph,user_timestamp)
                            
       else:               
           current_list = network[time]
           current_graph.add_nodes_from(current_list)
           current_graph = add_egdes(db, current_graph)
           features_util(features, time, current_graph,user_timestamp)
       index += 1
       
   features.average_tweets()
   return features
    
def generate_independent_graph(network, features):
	
    db = connect_db()
    for time in network:
    	current_list = network[time]
        graph = nx.Graph()
        graph.add_nodes_from(current_list)
        graph = add_egdes(db, graph, current_list)
        features_util(features, time, graph)
        
    plot_graph(features, "independent")
   

def add_egdes(db, graph):

    global follower_dict 
    new_node_set=[]
    for node1 in graph.nodes():
    	if node1 not in follower_dict:
                new_node_set.append(node1)
                for first in db.my_collection.find({'followee':str(node1)}):
          			    if first:
          			    	follower_dict[node1][first['follower']]=1
          			    	
    for node1 in new_node_set:
        for node2 in graph.nodes():
             if node1!=node2:     
          	if node1 in follower_dict:
          		if node2 in follower_dict[node1]:
          			graph.add_edge(node1,node2)
          			#print 'Hit',node1," ",node2
          	elif node2 in follower_dict:
          		if node1 in follower_dict[node2]:
          			graph.add_edge(node1,node2)
          			#print 'Hit',node1," ",node2
          			
          			    
    return graph
       
def get_date(timestamp):
    
    time = datetime.fromtimestamp(float(timestamp))
    return time.strftime('%Y-%m-%d')
          
   

def draw_graph(graph, time, features, type_folder):

	    try:
	    
	    	# nx.draw_random(graph,node_color='#A0CBE2',edge_color='Green',with_labels=False)
	    	
	    	if not os.path.exists(features.hashtag + "\\" + type_folder):
			   os.makedirs(features.hashtag + "\\" + type_folder)
	    	filename = features.hashtag + "\\" + type_folder + "\\" + str(time) + "_graph.graphml"	    
	    	nx.write_graphml(graph, filename)
	    	# plt.savefig(filename)
	    	# plt.close()
	    except:
	        raise
	    		

def main():
   global final_features_list
   global follower_dict
   final_features_list = []
   init_path()
   follower_dict = Ddict(dict)
   read_timeline()
   
   	
if __name__ == '__main__':
	   main()


