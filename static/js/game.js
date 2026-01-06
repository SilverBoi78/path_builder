const board = document.getElementById('board');
const submitButton = document.getElementById('submitMove');
const clearButton = document.getElementById('clearSelection');
const tilesPlacedDisplay = document.getElementById('tilesPlaced');

let selectedMoves = [];
let grid = boardData.grid;

const colorMap = {
    'red': 'rgb(239, 68, 68)',
    'purple': 'rgb(168, 85, 247)',
    'blue': 'rgb(59, 130, 246)'
};

function getPlayerColor(playerNum) {
    if (playerNum === 1) return colorMap[player1Color];
    if (playerNum === 2) return colorMap[player2Color];
    return 'rgb(107, 114, 128)';
}

function renderBoard() {
    board.innerHTML = '';
    
    for (let row = 0; row < 10; row++) {
        const rowDiv = document.createElement('div');
        rowDiv.className = 'flex';
        
        for (let col = 0; col < 10; col++) {
            const cell = document.createElement('div');
            cell.className = 'w-12 h-12 border border-gray-700 cursor-pointer hover:border-gray-500';
            cell.dataset.row = row;
            cell.dataset.col = col;
            
            const cellValue = grid[row][col];
            
            if (cellValue === 1) {
                cell.style.backgroundColor = getPlayerColor(1);
            } else if (cellValue === 2) {
                cell.style.backgroundColor = getPlayerColor(2);
            } else if (cellValue === 3) {
                cell.style.backgroundColor = 'rgb(107, 114, 128)';
            } else {
                cell.style.backgroundColor = 'rgb(17, 24, 39)';
            }
            
            const isSelected = selectedMoves.some(m => m.row === row && m.col === col);
            if (isSelected) {
                cell.style.border = '3px solid white';
            }
            
            if (gameStatus === 'active' && isMyTurn()) {
                cell.addEventListener('click', () => handleCellClick(row, col));
            }
            
            rowDiv.appendChild(cell);
        }
        
        board.appendChild(rowDiv);
    }
}

function isMyTurn() {
    if (currentTurn === 1 && currentUserId === player1Id) return true;
    if (currentTurn === 2 && currentUserId === player2Id) return true;
    return false;
}

function handleCellClick(row, col) {
    if (grid[row][col] !== 0) return;
    
    const existingIndex = selectedMoves.findIndex(m => m.row === row && m.col === col);
    
    if (existingIndex !== -1) {
        selectedMoves.splice(existingIndex, 1);
    } else {
        if (selectedMoves.length >= 2) {
            alert('You can only place 2 tiles per turn!');
            return;
        }
        
        const tileType = document.querySelector('input[name="tileType"]:checked').value;
        selectedMoves.push({ row, col, type: tileType });
    }
    
    updateUI();
}

function updateUI() {
    tilesPlacedDisplay.textContent = selectedMoves.length;
    submitButton.disabled = selectedMoves.length !== 2;
    renderBoard();
}

clearButton.addEventListener('click', () => {
    selectedMoves = [];
    updateUI();
});

submitButton.addEventListener('click', async () => {
    if (selectedMoves.length !== 2) return;
    
    try {
        const response = await fetch(`/game/${gameId}/move`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ moves: selectedMoves })
        });
        
        const data = await response.json();
        
        if (data.success) {
            grid = data.board.grid;
            currentTurn = data.current_turn;
            selectedMoves = [];
            updateUI();
            
            if (data.status === 'completed') {
                setTimeout(() => {
                    location.reload();
                }, 1000);
            }
        } else {
            alert(data.error || 'Invalid move!');
        }
    } catch (error) {
        alert('Error submitting move: ' + error.message);
    }
});

setInterval(async () => {
    if (gameStatus !== 'active' && gameStatus !== 'waiting') return;
    
    try {
        const response = await fetch(`/game/${gameId}`);
        const html = await response.text();
        
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const scriptTag = doc.querySelector('script');
        
        if (scriptTag) {
            const boardMatch = scriptTag.textContent.match(/const boardData = ({.*?});/);
            const turnMatch = scriptTag.textContent.match(/let currentTurn = (\d+);/);
            const statusMatch = scriptTag.textContent.match(/const gameStatus = '(\w+)';/);
            
            if (boardMatch) {
                const newBoard = JSON.parse(boardMatch[1]);
                grid = newBoard.grid;
            }
            
            if (turnMatch && parseInt(turnMatch[1]) !== currentTurn) {
                currentTurn = parseInt(turnMatch[1]);
            }
            
            if (statusMatch && statusMatch[1] !== gameStatus) {
                location.reload();
            }
            
            renderBoard();
        }
    } catch (error) {
        console.error('Error polling game state:', error);
    }
}, 3000);

renderBoard();