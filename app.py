import networkx as nx
from flask import Flask, render_template, jsonify, request


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/mst', methods=['POST'])
def find_mst():
    try:
        data = request.get_json()
        raw_edges = data['graph']['edges']
        edges = []

        for edge in raw_edges:
            edges.append((edge['source'], edge['target'], {'weight': edge['weight'], 'id': edge['id']}))

        G = nx.Graph()
        G.add_edges_from(edges)

        mst_res = nx.minimum_spanning_edges(G)
        total_weight = 0
        edge_ids = []

        for _, _, data in mst_res:
            total_weight += data['weight']
            edge_ids.append(data['id'])

        return jsonify({'totalWeight': total_weight, 'edgeIds': edge_ids})

    except Exception as e:
        return jsonify({'error': str(e)})
    
@app.route('/api/shortest-path', methods=['POST'])
def find_shortest_path():
    try:
        data = request.get_json()
        start = data['startNode']
        end = data['endNode']
        raw_edges = data['graph']['edges']
        edges = []

        for edge in raw_edges:
            edges.append((edge['source'], edge['target'], {'weight': edge['weight'], 'id': edge['id']}))

        G = nx.DiGraph()
        G.add_edges_from(edges)

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
    

if __name__ == '__main__':
    app.run()
