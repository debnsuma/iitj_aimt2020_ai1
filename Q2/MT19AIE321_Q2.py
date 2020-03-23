# Author : Suman Debnath
# Email : debnath.1@iitj.ac.in
# Roll No : MT19AIE321
# M.Tech-AI(2020)
# Date : 21th March 2020

#################################
#  Solution for Question No. 2  #
#################################

### Importing the Modules 
import random
import time
import sys
import fileinput

### Raw Data from STDIN/File - FOR Hacker Rank
data = []
for line in fileinput.input():
    size_of_matrix = int(line)

# Global Variables 
population = size_of_matrix * 50
generations = size_of_matrix * 20

## Create Square Matrix
def create_squar_matrix(n, start=1, end=4, best_array=False):
    
    if not best_array:
        array = []
        for row in range(n):
            inner_array = []
            for col in range(n):
                inner_array.append(random.randint(start, end))
            array.append(inner_array)  
    else:
        temp_container = list(range(1, (n*n)+1))
        array = []
        for row in range(n):
            inner_array = []
            for col in range(n):
                inner_array.append(temp_container.pop(0))
            array.append(inner_array)  
    
    return array

## Transpose of a 2D List
def transpose(list1): 
    
    list1_transpose =[[row[i] for row in list1] for i in range(len(list1[0]))] 
    
    return list1_transpose

## Agent Class
class Agent:
    
    def __init__(self, n, best_array=False):
        
        self.best_array = best_array
        
        if not self.best_array:
            # self.array = np.random.randint(low=1, high=5, size=(n, n))
            self.array = create_squar_matrix(n)
            self.fitness = 0 
        else:
            max_range = n*n + 1
            # self.array = np.reshape(range(1, max_range), (n,n))
            self.array = create_squar_matrix(n, best_array=self.best_array)
            self.fitness = 0
            
        fitness_value_hash = {}
#         for index, x in np.ndenumerate(self.array):
#             fitness_value_hash[index] = 0
        indexes = [(ix,iy) for ix, row in enumerate(self.array) for iy, i in enumerate(row)]   
        values = [self.array[ix][iy] for ix, row in enumerate(self.array) for iy, i in enumerate(row)] 
        for index in indexes:
            fitness_value_hash[index] = 0

        self.fitness_value_hash = fitness_value_hash
        
    def __str__(self):
        return (f"Array: \n {self.array} \nFitness: {self.fitness}")
#         return (f"Fitness: {self.fitness}")

## Get Adjusent Block Function
def get_adjusent(array, i_row, j_column):
    
    neighbours = {}
    try:
        left_element = i_row, j_column - 1
#         neighbours[left_element] = (array[left_element[0], left_element[1]])
        neighbours[left_element] = (array[left_element[0]][left_element[1]])
    except IndexError:
        pass
    try: 
        right_element = i_row, j_column + 1
#         neighbours[right_element] = (array[right_element[0], right_element[1]])
        neighbours[left_element] = (array[left_element[0]][left_element[1]])
    except IndexError:
        pass
    try:
        up_element = i_row - 1, j_column
#         neighbours[up_element] = (array[up_element[0], up_element[1]])
        neighbours[up_element] = (array[up_element[0]][up_element[1]])
    except IndexError:
        pass
    try:
        down_element = i_row + 1, j_column
#         neighbours[down_element] = (array[down_element[0], down_element[1]])
        neighbours[down_element] = (array[down_element[0]][down_element[1]])
    except IndexError:
        pass
    # Removing the negative index(-1) neighbour
    marker = []
    for i in neighbours.keys():
        if -1 in i:
            marker.append(i)
    if marker != []:
        for i in marker:
            del neighbours[i]    
    return neighbours

## Initiate Agents
def init_agents(population, size):
    
    return [Agent(size) for _ in range(population)]
    
## Fitness Function
def fitness(agents):
    
    for agent in agents:
        fitness_value_hash = {}
#         for index, x in np.ndenumerate(agent.array):
        indexes = [(ix,iy) for ix, row in enumerate(agent.array) for iy, i in enumerate(row)]   
        values = [agent.array[ix][iy] for ix, row in enumerate(agent.array) for iy, i in enumerate(row)] 
        for i in zip(indexes, values):
            index = i[0]
            x = i[1]
            fitness_value_each_element = 0
#             adjusent_to_x = get_adjusent(agent.array, *index)
            adjusent_to_x = get_adjusent(agent.array, index[0], index[1])
            for colour in adjusent_to_x.values():
                if colour == x:
                    pass
                else:
                    fitness_value_each_element += 1

            fitness_value_hash[index] = fitness_value_each_element
     #       print(f"Element Index {index}, Fitness Value {fitness_value_each_element}")
        
        agent.fitness_value_hash = fitness_value_hash
        agent.fitness = sum(fitness_value_hash.values())
        
    return agents

## Selection Function 
def selection(agents):
    
    agents = sorted(agents, key=lambda agent: agent.fitness, reverse=True)
    
    agents = agents[:int(.1 * len(agents))]
    
    return agents

## CrossOver Function
def crossover(agents):
    
    offsprings = []
    
    for _ in range((population - len(agents))//2):
        
        parent1 = random.choice(agents)
        parent2 = random.choice(agents)
        
        child1 = Agent(size_of_matrix)
        child2 = Agent(size_of_matrix)
        
        split = random.randint(0, size_of_matrix - 1) 
        
#         child1.array = np.concatenate((parent1.array[0:split], parent2.array[split:size_of_matrix]))
#         child2.array = np.concatenate((parent2.array[0:split], parent1.array[split:size_of_matrix]))
        child1.array = parent1.array[0:split] + parent2.array[split:size_of_matrix]
        child2.array = parent2.array[0:split] + parent1.array[split:size_of_matrix]
        
        child1.array = transpose(child1.array)
        child2.array = transpose(child2.array)
        
        offsprings.append(child1)
        offsprings.append(child2)
        
    agents.extend(offsprings)
    
    return agents

### Get the best array 
def get_best_array(size_of_matrix):
    
    best_array = Agent(size_of_matrix, best_array=True)
    best = [best_array]
    fitness(best)
    b_array = best[0]
    max_score_to_stop = b_array.fitness
#     print(best_array.array)
    return max_score_to_stop
    
## Genetic Algorithm
def ga():
    
    max_score_to_stop = get_best_array(size_of_matrix)
    agents = init_agents(population, size_of_matrix)
    time.sleep(3)
    
    for generation in range(generations):
        
#         print(f"Since Generation: {generation}, Best Fitness We Got {agents[0].fitness}, Fitness We Are Looking for {max_score_to_stop}")
        
        agents = fitness(agents)
        agents = selection(agents)
        agents = crossover(agents)
        #agents = mutation(agents)
        
        agents = fitness(agents)
        
        time.sleep(.2)
#         print("Sleeping..")
        for agent in agents:
            # print(agent.fitness, max_score_to_stop )
            if agent.fitness == max_score_to_stop:
#                 print("Got the best array")
#                 print(agent.array)
#                 print(f"Fitness of the Above Array {agent.fitness}")
                for i in agent.array:
                    for j in i:
                        print(j, end=" ")
                    print("")
                    
                sys.exit(0)


ga()

