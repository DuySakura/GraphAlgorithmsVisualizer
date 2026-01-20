import networkx as nx
from flask import Flask, render_template, jsonify, request
from algorithm import DROMDP


app = Flask(__name__)

def create_graph(data, isDirected):
    raw_edges = data['graph']['edges']
    edges = []

    for edge in raw_edges:
        edges.append((edge['source'], edge['target'], {'weight': edge['weight'], 'id': edge['id']}))

    G = nx.DiGraph() if isDirected else nx.Graph()
    G.add_edges_from(edges)

    return G

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/mst', methods=['POST'])
def find_mst():
    try:
        data = request.get_json()
        G = create_graph(data, isDirected=False)

        mst_res = nx.minimum_spanning_edges(G)
        total_weight = 0
        edge_ids = []

        for _, _, data in mst_res:
            total_weight += data['weight']
            edge_ids.append(data['id'])

        return jsonify({'totalWeight': total_weight, 'edgeIds': edge_ids})

    except Exception as e:
        return jsonify({'error': str(e)})
    
@app.route('/api/shortest', methods=['POST'])
def find_shortest_path():
    try:
        data = request.get_json()
        start = data['startNode']
        end = data['endNode']
        G = create_graph(data, isDirected=True)

        if start not in G:
            return {'error': f'Đỉnh {start} không có trong đồ thị'}
        if end not in G:
            return {'error': f'Đỉnh {end} không có trong đồ thị'}

        distance = 0
        path_nodes = nx.shortest_path(G, start, end, weight='weight')
        path_edges = []

        for i in range(len(path_nodes)-1):
            distance += G[path_nodes[i]][path_nodes[i+1]]['weight']
            path_edges.append(G[path_nodes[i]][path_nodes[i+1]]['id'])

        return jsonify({'distance': distance, 'pathNodes': path_nodes, 'pathEdges': path_edges})
    
    except nx.NetworkXNoPath:
        return jsonify({'distance': -1, 'start': start, 'end': end})
    
    except Exception as e:
        return jsonify({'error': str(e)})
    
@app.route('/api/dromd', methods=['POST'])
def find_dromd():
    try:
        data = request.get_json()
        pop_size = int(data['popSize'])
        generations = int(data['generations'])
        pc = float(data['pc'])
        pm = float(data['pm'])

        G = create_graph(data, isDirected=False)
        nodes = list(G.nodes())
        edges = G.edges()
        nodes_mapper = {name: i for i, name in enumerate(nodes)}
        adj_sets = [set() for _ in range(len(nodes))]
        
        for source, target in edges:
            u, v = nodes_mapper[source], nodes_mapper[target]

            if u == v:
                continue

            adj_sets[u].add(v)
            adj_sets[v].add(u)

        G_clean = [sorted(list(neighbor)) for neighbor in adj_sets]
        DROMDP_solver = DROMDP(graph=G_clean, pop_size=pop_size, generations=generations, pc=pc, pm=pm)
        best_val, best_individual = DROMDP_solver.solve()
        solution = []

        for i, val in enumerate(best_individual):
            label = nodes[i] if nodes else i
            solution.append([label, int(val)])

        return jsonify({'bestVal': int(best_val), 'bestSolution': solution})


    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run()
