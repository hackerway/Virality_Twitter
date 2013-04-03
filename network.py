import networkx as nx
import sys,gzip
import pickle

class Ddict(dict):
    def __init__(self, default=None):
        self.default = default

    def __getitem__(self, key):
        if not self.has_key(key):
            self[key] = self.default()
        return dict.__getitem__(self, key)


def file_reader():
   try:        
   	fread=gzip.open(sys.argv[1])
        fread=fread.readlines()
        read_follower(fread)
   except:
        print 'Pass'
        raise

def read_timeline():
    
    fread=open('timeline.data','r').readlines()
    big_chunk=[]
    print fread[1]


def read_follower(reader):  
    global follower_dict
    index=0 
    for line in reader:
              index+=1                
              '''div=line.split(':')
       		user=str(div[0].strip())
        	following=div[1].split(',')
        	for follow in following:
          		try: 
            			if follow:
            				follower_dict[user][str(follow.strip())]=1
          		except:
                                pass
               '''
                                          			
    print index      
   
def gen_independent_graph():

   global ind_graph
   global followers_dict

   ind_graph=Ddict(dict)
   big_chunk=read_timeline()
   
   for chunk in big_chunk:
       first=chunk[0].split(' ')
       hashtag=first[0].strip()
       time=first[1].strip()
       ind_graph[hashtag][time]=nx.Graph()
       chunk=chunk[1:]
       for user in chunk:
           user=user.split(' ')
           time=user[0].strip()
           id=user[1].strip()
           if time in ind_graph[hashtag]:
              graph=ind_graph[hashtag][time]
              graph.add_node(user)
           else:
              graph=nx.graph()
              graph.add_node(user)
              ind_graph[hashtag][time]=graph
   
   for hashtag in ind_graph:
       for time in ind_graph[hashtag]:
           graph=ind_graph[hashtag][time]
           for node in graph.nodes():
               for other in graph.nodes():
                   if node!=other:
                      if node in  followers_dict[other]:
                         if other in followers_dict[node]:
                            graph.add_edge(node,other)
           ind_graph[hashtag][time]=graph
   
    
   
   
   gen_dependent_graph(big_chunk)



def gen_dependent_graph(big_chunk):
   
   global dep_graph
   dep_graph={}
   for chunk in big_chunk:
       hashtag=chunk[0].split(' ').strip()
       chunk=chunk[1:]
       graph=nx.graph()
       for user in chunk:
           id=user.split(' ')[1]
           graph.add_node(id)
       dep_graph[hashtag]=graph
   
   for hashtag in dep_graph:
      graph=dep_graph[hashtag]
      for node in graph.nodes():
               for other in graph.nodes():
                   if node!=other:
                      if node in  followers_dict[other]:
                         if other in followers_dict[node]:
                            graph.add_edge(node,other)
      dep_graph[hashtag]=graph
   
     
    
        

    
def directed_graph():
   
    #give weights and direction to the graph
    print 'Rohit'  
def undirected_graph():
    #no wieghts and ignoring the reciprocal
    print 'Alekar'
   






def main():
   global follower_dict
   follower_dict=Ddict(dict)
   
   file_reader()
   #gen_independent_graph()
   

if __name__=='__main__':
       #from timeit import Timer
       #t = Timer("file_reader()", "from __main__ import file_reader")
       main()
       #print t.timeit()

