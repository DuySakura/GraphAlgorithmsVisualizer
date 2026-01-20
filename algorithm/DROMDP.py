import numpy as np


class DROMDP:
    def __init__(self, graph, rng_seed=2, pop_size=100, generations=300, pc=0.9, pm = 0.3, elitism_rate=0.1, heuristic_ratio : np.array = np.array([0.4, 0.4, 0.2])):
        self.graph = graph
        self.rng = np.random.default_rng(seed=rng_seed)
        self.vertices = len(graph)
        self.pop_size = pop_size
        self.generations = generations
        self.pc = pc
        self.pm = pm
        self.elitism = int(self.pop_size * elitism_rate)
        self.heuristic_ratio = heuristic_ratio
        rank = np.arange(1, pop_size + 1)
        self.rank_prob = rank / np.sum(rank)

    def heuristic_1(self):
        individual = np.zeros(self.vertices, dtype=np.int8)
        unvisited = set(range(self.vertices))
        while unvisited:
            if len(unvisited) == 1:
                individual[unvisited.pop()] = 2
                break
            vertex = self.rng.choice(tuple(unvisited))
            individual[vertex] = 3
            unvisited.discard(vertex)
            for neighbor in self.graph[vertex]:
                individual[neighbor] = 0
                unvisited.discard(neighbor)
        return individual
                
    def heuristic_2(self):
        individual = np.zeros(self.vertices, dtype=np.int8)
        visited = np.zeros(self.vertices, dtype=bool)
        permuted_vertices = self.rng.permutation(self.vertices)
        for vertex in permuted_vertices:
            if visited[vertex]:
                continue
            if len(self.graph[vertex]) == 0:
                individual[vertex] = 2
                continue
            individual[vertex] = 3
            for neighbor in self.graph[vertex]:
                individual[neighbor] = 0
                visited[neighbor] = True
        return individual

    def heuristic_3(self):
        individual = np.zeros(self.vertices, dtype=np.int8)
        deg_of_vertices = np.zeros(self.vertices, dtype=np.int32)
        for i in range(self.vertices):
            deg_of_vertices[i] = len(self.graph[i])
        sorted_deg_of_vertices = np.argsort(deg_of_vertices)[::-1]
        visited = np.zeros(self.vertices, dtype=bool)
        for vertex in sorted_deg_of_vertices:
            if visited[vertex]:
                continue
            if deg_of_vertices[vertex] == 0:
                individual[vertex] = 2
                continue
            individual[vertex] = 3
            for neighbor in self.graph[vertex]:
                if not visited[neighbor]:
                    individual[neighbor] = 0
                    visited[neighbor] = True
        return individual

    def init_population(self, pop_size=None):
        if pop_size == None:
            pop_size = self.pop_size
        population = np.zeros((pop_size, self.vertices))
        ratio_arr = np.array(self.heuristic_ratio)
        heuristic_size = (pop_size * ratio_arr).astype(int)
        heuristic_func = [getattr(self, f'heuristic_{i+1}') for i in range(len(self.heuristic_ratio))]
        cur_size = 0
        for size, func in zip(heuristic_size, heuristic_func):
            for _ in range(size):
                population[cur_size] = func()
                cur_size += 1
        while cur_size < pop_size:
            heuristic_idx = self.rng.choice(len(self.heuristic_ratio), p=self.heuristic_ratio)
            population[cur_size] = heuristic_func[heuristic_idx]()
            cur_size += 1
        return population

    def refine(self, individual):
        deg_2 = np.zeros(self.vertices, dtype=np.int32)
        deg_3 = np.zeros(self.vertices, dtype=np.int32)
        for vertex in np.where(individual == 2)[0]:
            for neighbor in self.graph[vertex]:
                deg_2[neighbor] += 1
        for vertex in np.where(individual == 3)[0]:
            for neighbor in self.graph[vertex]:
                deg_3[neighbor] += 1
        permuted_indices = self.rng.permutation(self.vertices)
        for vertex in permuted_indices:
            if individual[vertex] == 0:
                if deg_2[vertex] < 2 and deg_3[vertex] < 1:
                    individual[vertex] = 2
                    for neighbor in self.graph[vertex]:
                        deg_2[neighbor] += 1
        permuted_indices = self.rng.permutation(self.vertices)
        for vertex in permuted_indices:
            if individual[vertex] == 2 and deg_2[vertex] > 0:
                individual[vertex] = 3
                for neighbor in self.graph[vertex]:
                    deg_2[neighbor] -= 1
                    deg_3[neighbor] += 1
        for vertex in permuted_indices:
            val = individual[vertex]
            if deg_2[vertex] > 1 or deg_3[vertex] > 0:
                if val == 2:
                    for neighbor in self.graph[vertex]:
                        if individual[neighbor] == 0 and deg_2[neighbor] < 3 and deg_3[neighbor] == 0:
                            break
                    else:    
                        individual[vertex] = 0
                        for neighbor in self.graph[vertex]:
                            deg_2[neighbor] -= 1
                elif val == 3:
                    for neighbor in self.graph[vertex]:
                        if individual[neighbor] == 0 and deg_2[neighbor] < 2 and deg_3[neighbor] < 2:
                            break
                    else:
                        individual[vertex] = 0
                        for neighbor in self.graph[vertex]:
                            deg_3[neighbor] -= 1
            if val == 3:
                for neighbor in self.graph[vertex]:
                    if individual[neighbor] == 0 and deg_2[neighbor] < 1 and deg_3[neighbor] == 1:
                        break
                else:
                    individual[vertex] = 2
                    for neighbor in self.graph[vertex]:
                        deg_2[neighbor] += 1
                        deg_3[neighbor] -= 1
        
    def tournament_selection(self, candidates=3):
        idxs = self.rng.choice(self.pop_size, size=candidates, replace=False)
        winner = self.population[idxs[np.argmin(self.fitness_val[idxs])]]
        return winner
    
    def rank_selection(self):
        sorted_idxs = np.argsort(self.fitness_val)[::-1]
        winner = self.population[self.rng.choice(sorted_idxs, p=self.rank_prob)]
        return winner
    
    def crossover(self, par_1, par_2):
        offspring_1, offspring_2 = par_1.copy(), par_2.copy()
        if self.rng.random() < self.pc:
            idxs = self.rng.choice(self.vertices, size=int(self.vertices * 0.3), replace=False)
            for idx in idxs:
                offspring_1[idx], offspring_2[idx] = offspring_2[idx], offspring_1[idx]
            self.refine(offspring_1)
            self.refine(offspring_2)
        return offspring_1, offspring_2
    
    def mutation(self, par):
        offspring = par.copy()
        if self.rng.random() < self.pm:
            potential_indices = np.where(offspring > 0)[0]
            if len(potential_indices) == 0:
                return offspring
            max_mutation = max(1, int(len(potential_indices) * 0.15))
            idxs = self.rng.choice(potential_indices, size=self.rng.integers(1, max_mutation+1), replace=False)
            offspring[idxs] = 0
            self.refine(offspring)
        return offspring
    
    def solve(self):
        self.population = self.init_population()
        self.fitness_val = np.sum(self.population, axis=1)
        best_val = np.min(self.fitness_val)
        best_individual = self.population[np.argmin(self.fitness_val)].copy()
        for _ in range(self.generations):
            new_population = []
            elite_idxs = np.argsort(self.fitness_val)[:self.elitism]
            for idx in elite_idxs:
                new_population.append(self.population[idx].copy())
            while len(new_population) < self.pop_size:
                par_1, par_2 = self.tournament_selection(), self.rank_selection()
                offspring_1, offspring_2 = self.crossover(par_1, par_2)
                offspring_1, offspring_2 = self.mutation(offspring_1), self.mutation(offspring_2)
                new_population.extend([offspring_1, offspring_2])
            self.population = np.array(new_population[:self.pop_size], dtype=np.int8)
            self.fitness_val = np.sum(self.population, axis=1)
            if best_val > np.min(self.fitness_val):
                best_val = np.min(self.fitness_val)
                best_individual = self.population[np.argmin(self.fitness_val)].copy()
        return best_val, best_individual
