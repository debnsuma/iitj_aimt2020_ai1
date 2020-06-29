# Author : Suman Debnath
# Email : debnath.1@iitj.ac.in
# Roll No : MT19AIE321
# M.Tech-AI(2020)
# Date : 29th June 2020

#######################################
#  Programming assignment (Fractal-3) #
#######################################

### Importing the Modules 

import copy
import fileinput

# Extract the data from the user input 
def read_input_data(all_data):
    
    # No. of Nodes
    no_nodes = int(all_data[0])

    # Node Domains
    node_domain = []
    for i in range(1, no_nodes+1):
        d = all_data[i].split(",")
        d = [_.strip()  for _ in d]
        node_domain.append(d)
    
    _node_numbers = list(range(no_nodes))
    domains = dict.fromkeys(_node_numbers, None)
    for i, j in zip(domains, node_domain):
        domains[i] = j

    # Node Conditional Dependency Matrix
    node_con_dep = []
    for i in range(no_nodes+1, 2*no_nodes+1):
        d = all_data[i].split()
        d = [int(_.strip()) for _ in d]
        node_con_dep.append(d)
        
    # Total No. of Samples
    no_samples = int(all_data[2*no_nodes+1])
    
    # All samples
    samples = []
    start_inx = 2*no_nodes + 2
    for i in range(start_inx, len(all_data)):
        d = all_data[i].split(",")
        d = [_.strip()  for _ in d]
        samples.append(d)
    

    return no_nodes, domains, node_con_dep, no_samples, samples
   
def check_dependency(node, node_con_dep):
    
    dependency_vector = []
    
    for i in node_con_dep:
        dependency_vector.append((i[node]))

    if sum(dependency_vector) != 0:
        return True
    else:
        return False

def get_dependency(node_numbers, node_con_dep):
    
    node_dependency = dict.fromkeys(node_numbers, None)
    for node in node_numbers:
        
        dependency_vector = []
        for i in node_con_dep:
            dependency_vector.append((i[node]))
        
        #print(f"dependence vector for node {node} is {dependency_vector}")
        
        _depends_on = []
        for n, flag in enumerate(dependency_vector):
            if flag != 0:
                #print(node, n)
                _depends_on.append(n)
        node_dependency[node] = _depends_on
        
        #print(node_dependency)
    return node_dependency

# To mimic itertool 
def extend_list(list1,list2):
    temp=[];temp=copy.deepcopy(list1);temp.append(list2)
    return temp

def combination(list1, list2):
    return [extend_list(item1,item2) if type(item1) is list else [item1,item2] for item1 in list1 for item2 in list2]

def list_combination(list_of_variables): 
    node_combinations=[]
    no_of_variables=len(list_of_variables)
    node_combinations=list_of_variables[0]
    for i in range(no_of_variables-1):
        node_combination = combination(node_combinations,list_of_variables[i+1])
        node_combinations=node_combination
    return node_combinations

#### Main Starts here 

# Reading the data from the input 

# ### Raw Data from STDIN/File  - FOR LAPTOP
# data = [] 
# with open("input.txt") as f:
#     data = f.readlines()

### Raw Data from STDIN/File - FOR Hacker Rank
data = []
for line in fileinput.input():
    data.append(line)
    
data = [ d.rstrip()  for d in data]

no_nodes, node_domains, node_con_dep, no_samples, samples = read_input_data(data)

## Details of Dependent Nodes
node_numbers = list(range(no_nodes))
node_dependency = get_dependency(node_numbers, node_con_dep)

## Initializing the dict for Independent and Dependent RV/Nodes based on Node Condition Dependency 
independent_nodes = {}
dependent_nodes = {}

for i in range(no_nodes):
    if check_dependency(i, node_con_dep):
        dependent_nodes[i] = {}
    else:
        independent_nodes[i] = {}  

## Finding the probability of Independent RV/Node and update "independent_nodes" dict 
for n in independent_nodes:
    independent_nodes[n] = dict.fromkeys(node_domains[n])
    for d in node_domains[n]:
        node_domain_prob = dict({d: 0})
        _node_d = []

        for sample in samples:
            _node_d.append(sample[n])
        node_domain_prob[d] = _node_d.count(d) / len(samples)
        
        independent_nodes[n][d] =  node_domain_prob[d]
    
## Finding the probability of Dependent RV/Node and update "dependent_nodes" dict 

### Storing each sample row in separate node hash
node_values = {}
for i in node_numbers:
    node_values[i] = []
for s in samples:
    for i in range(len(s)):
        node_values[i].append(s[i])

### Looping over all dependent node
for n in dependent_nodes.keys():
    parent_nodes = node_dependency[n]
    _possible_parent_domain = []
    
    for p in parent_nodes:
        _possible_parent_domain.append(node_domains[p])
    
    parent_conditions = list_combination(_possible_parent_domain)
#     print(parent_conditions)
    
    for child_domain in node_domains[n]:
#         print(child_domain)

        for condition in parent_conditions:
            if not isinstance(condition, list):
                condition = [condition]
#             print(f"condition : {condition}")
            idx = [] 
            for pn in range(len(parent_nodes)):
#                 print(condition)
                # Finding the index of each sample for "pn" parent node with domain as condition[pn]
                _idx = [i for i, x in enumerate(node_values[parent_nodes[pn]]) if x == condition[pn]]
                idx.append(_idx)
#                 print(idx)

            # Finding the intersection of all the parents
            idx = set.intersection(*map(set,idx))      
            child_value = [node_values[n][i] for i in idx]                
            chile_samples = len(child_value)
            try:
                node_domain_prob = child_value.count(child_domain)/chile_samples
            except ZeroDivisionError:
                node_domain_prob = 0 
            
            #Svaing the probability in the "dependent_nodes" hash
#             print(condition)
            _ = condition.copy()
            _.insert(0, child_domain)
            dependent_nodes[n][str(_)] = node_domain_prob
#             print(f"Pribability: [{condition}] : {node_domain_prob}")


### Merging both the probabilities in a single list and sorting it based on Node number
all_nodes = {}
all_nodes.update(dependent_nodes)
all_nodes.update(independent_nodes)

all_nodes_sorted_list = sorted(all_nodes.items())

### Printing the domain probability

all_probs = [] 

for node in all_nodes_sorted_list:
    domain_probs = []
    for domain_prob in node[1].values():
        domain_probs.append(str(domain_prob))
#     print(domain_probs)
    _p = " ".join(domain_probs)
    all_probs.append(_p)
#         domain_prob += node[1][domain]

for p in all_probs:
    print(p)


