// basket.js - Logic for the Databasket Research Suite

const BASKET_KEY = 'myCollection';
const NOTES_KEY = 'agki_basket_notes';

// --- Storage Management ---

function getBasket() {
    try {
        return JSON.parse(localStorage.getItem(BASKET_KEY) || '[]');
    } catch (e) {
        return [];
    }
}

function setBasket(ids) {
    localStorage.setItem(BASKET_KEY, JSON.stringify(ids));
    updateBasketCount();
}

function addToBasket(id) {
    const basket = getBasket();
    if (!basket.includes(id)) {
        basket.push(id);
        setBasket(basket);
    }
}

function removeFromBasket(id) {
    let basket = getBasket();
    basket = basket.filter(itemId => itemId != id);
    setBasket(basket);
    // Also cleanup notes? Maybe keep them in case of re-add.
}

function clearBasket() {
    if(confirm('Are you sure you want to remove all items from your basket?')) {
        setBasket([]);
        renderBasket();
    }
}

function updateBasketCount() {
    const count = getBasket().length;
    const badge = document.getElementById('basketCountBadge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline-flex' : 'none';
    }
}

// --- Annotations ---

function getNotes() {
    try {
        return JSON.parse(localStorage.getItem(NOTES_KEY) || '{}');
    } catch (e) {
        return {};
    }
}

function saveNote(id, text) {
    const notes = getNotes();
    if (text.trim() === '') {
        delete notes[id];
    } else {
        notes[id] = text;
    }
    localStorage.setItem(NOTES_KEY, JSON.stringify(notes));
}

// --- Rendering ---

function initBasketPage() {
    // Check for shared IDs in URL
    const params = new URLSearchParams(window.location.search);
    const sharedIds = params.get('ids');
    if (sharedIds) {
        const ids = sharedIds.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n));
        if (ids.length > 0) {
            if(confirm(`Load ${ids.length} shared items into your basket? This will merge with your current collection.`)) {
                const current = getBasket();
                const newSet = new Set([...current, ...ids]);
                setBasket(Array.from(newSet));
                // Clean URL
                window.history.replaceState({}, document.title, window.location.pathname);
            }
        }
    }

    renderBasket();
}

function renderBasket() {
    const container = document.getElementById('basketTableBody');
    const emptyState = document.getElementById('emptyState');
    const tableContainer = document.getElementById('basketContainer');
    const basketIds = getBasket();
    const notes = getNotes();

    if (!container) return;

    if (basketIds.length === 0) {
        tableContainer.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }

    tableContainer.style.display = 'block';
    emptyState.style.display = 'none';
    container.innerHTML = '';

    // Retrieve full data objects
    const items = basketIds.map(id => APP_DATA.inscriptions.find(i => i.id == id)).filter(Boolean);

    items.forEach(item => {
        const note = notes[item.id] || '';
        const tr = document.createElement('tr');
        
        // Tags preview
        const tags = (item.themes_display || []).slice(0, 3).map(t => `<span class="badge tiny">${t}</span>`).join(' ');
        
        tr.innerHTML = `
            <td><input type="checkbox" class="basket-select" value="${item.id}"></td>
            <td><a href="inscriptions/${item.id}.html" class="id-link">PHI-${item.id}</a></td>
            <td>${item.region || 'Unknown'}</td>
            <td>${item.date_str || 'Undated'}</td>
            <td><div class="tags-cell">${tags}</div></td>
            <td class="actions-cell">
                <button class="btn-icon" onclick="toggleNoteRow(${item.id})" title="Add/Edit Note">📝</button>
                <button class="btn-icon danger" onclick="removeItem(${item.id})" title="Remove">✕</button>
            </td>
        `;
        container.appendChild(tr);

        // Note Row (Hidden by default unless note exists)
        const noteTr = document.createElement('tr');
        noteTr.id = `note-row-${item.id}`;
        noteTr.className = note ? 'note-row open' : 'note-row';
        noteTr.innerHTML = `
            <td colspan="6" class="note-cell">
                <div class="note-wrapper">
                    <strong>My Annotation:</strong>
                    <textarea id="note-${item.id}" placeholder="Add your private research notes here..." onchange="saveNote(${item.id}, this.value)">${note}</textarea>
                </div>
            </td>
        `;
        container.appendChild(noteTr);
    });

    // Update selection count
    updateSelectionState();
}

function toggleNoteRow(id) {
    const row = document.getElementById(`note-row-${id}`);
    row.classList.toggle('open');
}

function removeItem(id) {
    removeFromBasket(id);
    renderBasket();
}

// --- Bulk Actions ---

function toggleSelectAll(source) {
    document.querySelectorAll('.basket-select').forEach(cb => cb.checked = source.checked);
    updateSelectionState();
}

function updateSelectionState() {
    // Could enable/disable buttons based on selection count
    const count = document.querySelectorAll('.basket-select:checked').length;
    // document.getElementById('compareBtn').disabled = count < 2;
}

function getSelectedIds() {
    return Array.from(document.querySelectorAll('.basket-select:checked')).map(cb => cb.value);
}

function compareSelected() {
    const ids = getSelectedIds();
    if (ids.length < 2) {
        alert('Please select at least 2 items to compare.');
        return;
    }
    // Redirect to compare page
    window.location.href = `compare.html?ids=${ids.join(',')}`;
}

// --- Sharing & Export ---

function generateShareLink() {
    const ids = getBasket().join(',');
    const url = `${window.location.origin}${window.location.pathname}?ids=${ids}`;
    
    navigator.clipboard.writeText(url).then(() => {
        alert('Shareable link copied to clipboard!');
    }, () => {
        prompt("Copy this link to share your collection:", url);
    });
}

function exportBasket(format) {
    const basketIds = getBasket();
    const items = basketIds.map(id => APP_DATA.inscriptions.find(i => i.id == id)).filter(Boolean);
    const notes = getNotes();

    let content = '';
    let type = '';
    let filename = `agki_basket_${new Date().toISOString().slice(0,10)}`;

    if (format === 'csv') {
        const headers = ['ID', 'Region', 'Date', 'Completeness', 'Personal Notes', 'Themes'];
        const rows = items.map(item => {
            const note = (notes[item.id] || '').replace(/"/g, '""');
            return [
                item.id,
                `"${(item.region || '').replace(/"/g, '""')}"`,
                `"${(item.date_str || '').replace(/"/g, '""')}"`,
                item.completeness,
                `"${note}"`,
                `"${(item.themes_display || []).join('; ').replace(/"/g, '""')}"`
            ].join(',');
        });
        content = headers.join(',') + '\n' + rows.join('\n');
        type = 'text/csv';
        filename += '.csv';
    } else {
        const exportData = items.map(item => ({
            ...item,
            personal_note: notes[item.id] || null
        }));
        content = JSON.stringify(exportData, null, 2);
        type = 'application/json';
        filename += '.json';
    }

    downloadFile(content, filename, type);
}

function generateCitation() {
    const basketIds = getBasket();
    const items = basketIds.map(id => APP_DATA.inscriptions.find(i => i.id == id)).filter(Boolean);
    
    // Simple Chicago-style attempt
    const citations = items.map(item => {
        return `PHI ${item.id}. ${item.region}. ${item.date_str || 'n.d.'}. AGKI Epigraphy Tool. Accessed ${new Date().toLocaleDateString()}.`;
    }).join('\n\n');

    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal">
            <h3>Citations (Chicago Style)</h3>
            <textarea style="width:100%; height:200px; margin-bottom:1rem;">${citations}</textarea>
            <button class="button" onclick="this.closest('.modal-overlay').remove()">Close</button>
        </div>
    `;
    document.body.appendChild(modal);
}

// --- Utils ---

function downloadFile(content, filename, type) {
    const blob = new Blob([content], { type: type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Expose globally
window.basket = {
    init: initBasketPage,
    get: getBasket,
    add: addToBasket,
    addMany: addManyToBasket,
    remove: removeFromBasket
};
