// Function to update tables with fresh data
function updateTables(data) {
    
    const getStatusPriority = (status) => {
        // Define the order/priority for each status
        const statusPriority = {
            'pending': 1,
            'active': 2,
            'completed': 3
        };
        return statusPriority[status.toLowerCase()] || 99; // Default priority
    };

    const updateTable = (tableId, columns, data, actions = []) => {
        const table = document.getElementById(tableId);
        let tbody = table.querySelector('tbody');
        if (!tbody) {
            tbody = document.createElement('tbody');
            table.appendChild(tbody);
        }
        tbody.innerHTML = '';

        // Sort data based on status priority for 'calls' table
        if (tableId === 'calls') {
            data.sort((a, b) => getStatusPriority(a.status) - getStatusPriority(b.status));
        }

        data.forEach(row => {
            const tr = document.createElement('tr');

            if (tableId === 'calls') {
                switch (row.status.toLowerCase()) {
                    case 'active':
                        tr.className = 'status-active';
                        break;
                    case 'pending':
                        tr.className = 'status-pending';
                        break;
                    case 'completed':
                        tr.className = 'status-completed';
                        break;
                    default:
                        break;
                }
            }

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
    
    setTimeout(fetchData, 1000);
}

function renderCallsTable(calls) {
    const table = document.getElementById('calls');
    table.innerHTML = `<tr>
                            <th>Status</th>
                            <th>Sid</th>
                            <th>Caller</th>
                            <th>Agent</th>
                       </tr>`;
    calls.forEach(call => {
        const row = document.createElement('tr');
        // Assign class based on status
        row.className = `status-${call.status.toLowerCase()}`;

        row.innerHTML = `<td>${call.status}</td>
                         <td>${call.sid}</td>
                         <td>${call.caller}</td>
                         <td>${call.agent}</td>`;
        table.appendChild(row);
    });
}

// Start fetching data
fetchData();