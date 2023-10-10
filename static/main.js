// Function to update tables with fresh data
function updateTables(data) {
    const updateTable = (tableId, columns, data, actions = []) => {
        const table = document.getElementById(tableId);
        let tbody = table.querySelector('tbody');
        if (!tbody) {
            tbody = document.createElement('tbody');
            table.appendChild(tbody);
        }
        tbody.innerHTML = '';
        
        data.forEach(row => {
            const tr = document.createElement('tr');
            columns.forEach(col => {
                const td = document.createElement('td');
                td.textContent = row[col.toLowerCase()];
                tr.appendChild(td);
            });
            actions.forEach(action => {
                const td = document.createElement('td');
                const button = document.createElement('button');
                button.textContent = action.text;
                button.className = 'btn btn-dark my-3';
                button.addEventListener('click', () => action.handler(row));
                td.appendChild(button);
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
    };

    updateTable('calls', ['Status', 'Sid', 'Caller', 'Agent'], data.calls);
    updateTable('available_agents', ['Name', 'Number'], data.available_agents, [{
        text: 'Remove',
        handler: removeAgent
    }]);
}

function removeAgent(agent) {
    fetch(`/remove_agent?name=${agent.name}&number=${agent.number}`)
        .then(response => response.json())
        .then(data => updateTables(data))
        .catch(error => console.error('Error:', error));
}

// Fetch and update data every 5 seconds
function fetchData() {
    fetch('/data')
        .then(response => response.json())
        .then(data => updateTables(data))
        .catch(error => console.error('Error fetching data:', error));
    
    setTimeout(fetchData, 5000);
}

// Start fetching data
fetchData();