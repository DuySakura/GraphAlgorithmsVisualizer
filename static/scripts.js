const BACKEND_URL = '';

let network = null;
let nodes = new vis.DataSet([]);
let edges = new vis.DataSet([]);
let abortController = null;

const options = {
    manipulation: {
        enabled: false,
        initiallyActive: true,
        addNode: function(nodeData, callback) {
            const label = prompt('Nhập tên đỉnh: ', '');

            if (!label) {
                callback(null);
                return;
            }

            if (nodes.get(label)) {
                alert(`Đỉnh ${label} đã tồn tại`)
                callback(null);
                return;
            }

            nodeData.id = label;
            nodeData.label = label;
            callback(nodeData);
        }, 
        addEdge: function(edgeData, callback) {
            const isDirected = (document.getElementById('algo-select').value === 'shortest');

            if (isDirected) {
                edgeData.id = `${edgeData.from}-${edgeData.to}`;
                edgeData.arrows = 'to';
            } else {
                const sorted = [edgeData.from, edgeData.to].sort();
                edgeData.id = `${sorted[0]}-${sorted[1]}`
            }

            if (edges.get(edgeData.id)) {
                alert(`Cạnh ${edgeData.id} đã tồn tại`)
                callback(null);
                return;
            }

            const weightStr = prompt(`Nhập trọng số cho cạnh ${edgeData.id}: `, '');
            const weight = Number(weightStr);

            if (!weightStr) {
                callback(null);
                return;
            }

            if (isNaN(weight) || weight <= 0) {
                alert('Trọng số phải là số dương');
                callback(null);
                return;
            }
            
            edgeData.weight = weight;
            edgeData.label = weightStr;
            callback(edgeData);
        }, 
        editEdge: false,
        deleteNode: true, 
        deleteEdge: true
    },
    physics: {
        stabilization: true,
        barnesHut: { springLength: 150 }
    },
    edges: {
        arrows: { to: { enabled: false } },
        font: { align: 'top' },
        smooth: false
    }
};

window.onload = function() {
    const container = document.getElementById('network');
    const data = { nodes: nodes, edges: edges };
    network = new vis.Network(container, data, options);

    network.on('doubleClick', function(params) {
        if (params.edges.length === 1) {
            const edgeId = params.edges[0];
            editEdgeWeight(edgeId);
        }
    });
};

function switchTab(mode) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById(`tab-${mode}`).classList.add('active');
    document.querySelector(`button[onclick*="'${mode}'"]`).classList.add('active');

    if (network) {
        if (mode == 'draw') {
            network.setOptions({
                manipulation: { enabled: true },
                interaction: { dragView: true }
            });
        } else {
            network.setOptions({
                manipulation: { enabled: false }
            });
            network.disableEditMode()
        }
    }
}

function toggleAlgoInputs() {
    const algo = document.getElementById('algo-select').value;
    const shortestInputs = document.getElementById('shortest-inputs');
    const dromdInputs = document.getElementById('dromd-inputs')

    if (algo === 'mst') {
        shortestInputs.style.display = 'none';
        dromdInputs.style.display = 'none';
        network.setOptions({
            edges: { arrows: { to: { enabled: false }}}
        });
    } else if (algo === 'shortest') {
        shortestInputs.style.display = 'block';
        dromdInputs.style.display = 'none';
        network.setOptions({
            edges: { arrows: { to: { enabled: true }}}
        });
    } else {
        shortestInputs.style.display = 'none';
        dromdInputs.style.display = 'block';
        network.setOptions({
            edges: { arrows: { to: { enabled: false }}}
        });
    }
}

function resetColor() {
    const nodeUpdates = nodes.getIds().map(id => ({
        id: id,
        color: { background: '#D2E5FF' } 
    }));
    const edgeUpdates = edges.getIds().map(id => ({
        id: id,
        color: { color: '#848484' },
        width: 1
    }));

    nodes.update(nodeUpdates);
    edges.update(edgeUpdates);
    document.getElementById('result-text').innerText = "...";
}

function resetGraph() {
    nodes.clear();
    edges.clear();
    document.getElementById('result-text').innerText = "...";
}

function handleTextInput() {
    const text = document.getElementById('graph-input').value.trim();
    if (!text) return;
    parse(text, true);
}

function handleFileInput() {
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => parse(e.target.result, false);
        reader.readAsText(file);
        fileInput.value = '';
    }
}

function parse(content, isHeaderPass) {
    nodes.clear(); 
    edges.clear();
    
    const isDirected = (document.getElementById('algo-select').value === 'shortest')
    const lines = content.split('\n');
    const addedNodes = new Map();
    const addedEdges = new Map();

    for (let line of lines) {
        line = line.trim()
        if (line === '' || line.startsWith('%') || line.startsWith('#')) continue;
        if (!isHeaderPass) {
            isHeaderPass = true;
            continue;
        }

        const parts = line.trim().split(/\s+/);
        if (parts.length >= 2) {
            const u = parts[0];
            const v = parts[1];
            const w = parts.length > 2 ? Number(parts[2]) : 1;

            if (isNaN(w) || w <= 0) {
                alert(`Lỗi dữ liệu tại dòng: "${line}"`);
                nodes.clear();
                edges.clear();
                return;
            }

            if (!addedNodes.has(u)) addedNodes.set(u, { id: u, label: u });
            if (!addedNodes.has(v)) addedNodes.set(v, { id: v, label: v });

            let edgeId;
            if (isDirected) edgeId = `${u}-${v}`;
            else edgeId = `${[u, v].sort()[0]}-${[u, v].sort()[1]}`;

            if (addedEdges.has(edgeId)) {
                const exist = addedEdges.get(edgeId);
                exist.weight = w;
                exist.label = String(w);
            } else {
                addedEdges.set(edgeId, {
                    id: edgeId,
                    from: isDirected ? u : [u, v].sort()[0],
                    to: isDirected ? v : [u, v].sort()[1],
                    weight: w,
                    label: String(w),
                    arrows: isDirected ? 'to' : undefined
                });
            }
        }
    }

    if (isDirected) {
        addedEdges.forEach(edge => {
            const reverseId = `${edge.to}-${edge.from}`
            if (addedEdges.has(reverseId)) edge.smooth = { enabled: true, type: 'curvedCW', roundness: 0.2 };
        });
    }

    nodes.add(Array.from(addedNodes.values()));
    edges.add(Array.from(addedEdges.values()))

    network.fit();
}

function editEdgeWeight(edgeId) {
    const edge = edges.get(edgeId)
    const weightStr = prompt(`Nhập trọng số mới cho cạnh ${edge.id}: `, String(edge.weight));
    const weight = Number(weightStr);

    if (!weightStr) {
        return;
    }

    if (isNaN(weight) || weight <= 0) {
        alert('Thay đổi không hợp lệ')
        return;
    }

    edges.update({
        id: edgeId,
        weight: weight,
        label: weightStr
    })
}

async function runAlgorithm() {
    resetColor();
    const type = document.getElementById('algo-select').value;
    const graphData = {
        edges: edges.get().map(e => ({
            id: e.id,
            source: e.from, 
            target: e.to, 
            weight: e.weight
        })),
    };
    
    let payload = { graph: graphData };

    if (type === 'shortest') {
        const start = document.getElementById('start-node').value.trim();
        const end = document.getElementById('end-node').value.trim();

        if (!start || !end) { 
            alert("Thiếu điểm đầu/cuối");
            return;
        }

        payload.startNode = start; 
        payload.endNode = end;
    } else if (type == 'dromd') {
        const size = document.getElementById('pop-size').value;
        const generations = document.getElementById('generations').value;
        const pc = document.getElementById('pc').value;
        const pm = document.getElementById('pm').value;

        payload.popSize = size;
        payload.generations = generations;
        payload.pc = pc;
        payload.pm = pm;
    }

    document.getElementById('loading-overlay').classList.remove('hidden');
    document.getElementById('result-text').innerText = "Đang chạy...";

    if (abortController) abortController.abort();
    abortController = new AbortController();
    const signal = abortController.signal;

    try {
        let endpoint;

        if (type === 'mst') {
            endpoint = '/api/mst'
        } else if (type === 'shortest') {
            endpoint = '/api/shortest'
        } else {
            endpoint = '/api/dromd'
        }
        
        const response = await fetch(`${BACKEND_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            signal: signal
        });

        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        
        const result = await response.json();
        handleBackendResult(type, result);
    } catch (error) {
        if (error.name === 'AbortError') {
            document.getElementById('result-text').innerText = "Đã hủy tác vụ!";
            console.log("User cancelled request");
        } else {
            console.error("Lỗi:", error);
            document.getElementById('result-text').innerText = "Lỗi: " + error.message;
        }
    } finally {
        document.getElementById('loading-overlay').classList.add('hidden');
        abortController = null;
    }
}

function handleBackendResult(type, data) {
    if (data.error) {
        document.getElementById('result-text').innerText = `Lỗi từ server: ${data.error}`;
        return;
    }

    if (type === 'mst') {
        document.getElementById('result-text').innerText = `Tổng trọng số MST: ${data.totalWeight}`;
        
        if (data.edgeIds) {
            const edgeUpdates = data.edgeIds
                .filter(id => edges.get(id))
                .map(id => ({
                    id: id,
                    color: 'red',
                    with: 3
                }));

            edges.update(edgeUpdates)
        }
    } else if (type === 'shortest') {
        if (data.distance === -1 || data.distance === Infinity) {
            document.getElementById('result-text').innerText = `Không tìm thấy đường đi từ ${data.start} đến ${data.end}`;
            return;
        }

        document.getElementById('result-text').innerText = `Khoảng cách ngắn nhất: ${data.distance}`;

        if (data.pathNodes) {
            const nodeUpdates = data.pathNodes
                .filter(id => nodes.get(id))
                .map(id => ({
                    id: id, 
                    color: { background: '#ffcc00' } 
                }));

            nodes.update(nodeUpdates);
        }

        if (data.pathEdges) {
            const edgeUpdates = data.pathEdges
                .filter(id => edges.get(id))
                .map(id => ({
                    id: id, 
                    color: { color: 'green' }, 
                    width: 3 
                }));

            edges.update(edgeUpdates);
        }
    } else {
        document.getElementById('result-text').innerText = `Tổng trọng số DROMD: ${data.bestVal}`;
        const legend = document.getElementById('legend-container');
        if (legend) legend.style.display = 'block';

        if (data.bestSolution) { 
            const colorMap = {
                3: { background: '#FF4136', border: '#B10DC9' },
                2: { background: '#2ECC40', border: '#01FF70' },
                0: { background: '#DDDDDD', border: '#AAAAAA' }
            };

            const nodeUpdates = data.bestSolution
                .filter(item => nodes.get(item[0]))
                .map(item => {
                    const nodeId = item[0];
                    const label = item[1];

                    return {
                        id: nodeId,
                        color: colorMap[label] || { background: '#97C2FC' },
                        title: `ID: ${nodeId} - Label: ${label}`
                    };
                });
            
            nodes.update(nodeUpdates);
        }
    }
}

function cancelAlgorithm() {
    if (abortController) {
        abortController.abort();
    }
}
