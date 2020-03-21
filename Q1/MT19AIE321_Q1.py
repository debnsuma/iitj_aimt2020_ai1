# Author : Suman Debnath
# Email : debnath.1@iitj.ac.in
# Roll No : MT19AIE321
# M.Tech-AI(2020)
# Date : 17th March 2020

#################################
#  Solution for Question No. 1  #
#################################

### Importing the Modules 
import fileinput

### Get Tree Function
def get_tree(total_no_node, real_path_costs):
    nodes = list(range(1, total_no_node+1))
    tree = dict.fromkeys(nodes, [])
    for p in real_path_costs:
        if tree[p[0][0]] == []:
            tree[p[0][0]] = [[p[0][1], p[1]]]
        else:
            tree[p[0][0]].append([p[0][1], p[1]])
    
    return tree

### Get Path Cost Function
def get_cost(trace, tree):
    final_cost = 0
    for i in range(len(trace)-1):
        k = tree[trace[i]]
        for item in k:
            if item[0] == trace[i+1]:
                final_cost += item[1]
        # print(trace[i], k)
    
    return final_cost


### Raw Data from STDIN/File - FOR Hacker Rank
data = []
for line in fileinput.input():
    data.append(line)
data = [ d.rstrip().split()  for d in data]
 
# ### Raw Data from STDIN/File  - FOR LAPTOP 
# with open("astar_theory.txt") as f:
#     data = f.readlines()
# data = [ d.rstrip().split()  for d in data]

### Total No of Nodes (line no. 1)
total_no_node = int(data[0][0])

### Heuristic Values (line no. 2)
heuristic_each_node = [int(i) for i in data[1]]
H = {}
for i, j in enumerate(heuristic_each_node):
    H[i+1] =  j

### Start and Goal Node (line no. 3)
start_node = int(data[2][0])
end_node = int(data[2][1])

### Start node, end node and the actual cost of the edge. (line no. 4 and above)
_real_path_costs = [ i for i in data[4:]]
real_path_costs = []
for i in _real_path_costs:
    j = [int(k) for k in i[:2]]
    real_path_costs.append([tuple(j), int(i[2])])
real_path_costs.sort()  

### Get the tree
tree = get_tree(total_no_node, real_path_costs)

### A* Algo 
open_queue = []
close_queue = []

# Initialization with the starting node 
last_cost = H[start_node]
open_queue.append([[start_node], last_cost])

present_node = open_queue[0][0][-1]
trace = open_queue[0][0]

expanded_node = []
expanded_node.append(present_node)

while present_node != end_node:
    
#     print("######################################")
#     print(f"Present Node {present_node}")
    for c in tree[present_node]:
        till_now = trace.copy()
        till_now.append(c[0])
        till_now_cost = get_cost(till_now, tree) + H[c[0]]
        open_queue.append([till_now, till_now_cost])

    del open_queue[0]
    close_queue.append(present_node)
#     print(f"Closed Node {close_queue}")

    open_queue.sort(key = lambda x: x[1])
#     print("Sorted Open Queue")
#     print(open_queue)
        
    present_node = open_queue[0][0][-1]
    trace = open_queue[0][0]
#     print("######################################")
#     print(f"Expanding Node : {present_node}")
    expanded_node.append(present_node)

# print("######################################")
optimal_path_cost = open_queue[0][1]
# print(f"Expanded Nodes are: {expanded_node}")

## Final Output
for t in expanded_node:
    print(t, end = " ")
print("\n" + str(optimal_path_cost))
