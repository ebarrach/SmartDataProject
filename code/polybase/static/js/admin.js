// =============================================
// specification: Esteban Barracho (v.1 26/06/2025)
// implement: Esteban Barracho (v.3.4 07/07/2025)
// =============================================
document.addEventListener("DOMContentLoaded", () => {
    const tableSelect = document.getElementById('table-select');
    const reloadBtn = document.getElementById('reload-btn');
    const exportBtn = document.getElementById('export-btn');
    const importBtn = document.getElementById('import-btn');
    const importFile = document.getElementById('import-file');
    const dataTable = document.getElementById('data-table');
    const currentTable = document.getElementById('current-table');
    const formInsert = document.getElementById('form-insert');
    const formUpdate = document.getElementById('form-update');
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');

    const ENUM_LABELS = {
        statut: {
            'a_faire': 'À faire',
            'en_cours': 'En cours',
            'termine': 'Terminé'
        },
        nature_cout: {
            'interne': 'Interne',
            'externe': 'Externe',
            'logiciel': 'Logiciel',
            'matériel': 'Matériel',
            'sous-traitant': 'Sous-traitant'
        },
        mode_facturation: {
            'horaire': 'Horaire',
            'forfaitaire': 'Forfaitaire'
        },
        statut_facture: {
            'emise': 'Émise',
            'payee': 'Payée',
            'en_attente': 'En attente'
        },
        type_personnel: {
            'interne': 'Interne',
            'externe': 'Externe'
        }
    };

    function getEnumLabel(colName, value) {
        return (ENUM_LABELS[colName] && ENUM_LABELS[colName][value]) || value;
    }

    function sanitizeInput(col, value) {
        if (col.type.toLowerCase().includes("boolean")) {
            return value === "true" || value === "1" || value === "on" ? true : false;
        }
        return value;
    }

    function isDateField(col) {
        return col.type.toLowerCase().includes("date");
    }

    let tableData = [];
    let tableStructure = [];
    let tableName = "";
    let importedRows = [];
    let importIndex = 0;
    let filteredData = null;

    fetch('/admin/tables')
        .then(res => res.json())
        .then(tables => {
            tableSelect.innerHTML = "";
            tables.forEach(tbl => {
                let opt = document.createElement('option');
                opt.value = tbl;
                opt.text = tbl;
                tableSelect.appendChild(opt);
            });
            if (tables.length) {
                tableSelect.value = tables[0];
                loadAll();
            }
        });

    tableSelect.addEventListener('change', () => {
        filteredData = null;
        loadAll();
    });
    reloadBtn.onclick = () => {
        filteredData = null;
        loadTableData();
    };

    function loadAll() {
        tableName = tableSelect.value;
        currentTable.textContent = tableName;
        filteredData = null;
        loadTableData();
        loadTableStructure();
        formUpdate.style.display = "none";
    }

    searchForm.onsubmit = function (e) {
        e.preventDefault();
        const val = searchInput.value.trim();
        if (!val) {
            filteredData = null;
            renderTable();
            return;
        }
        fetch(`/admin/search_global?query=${encodeURIComponent(val)}`)
            .then(res => res.json())
            .then(results => {
                if (!results.length) {
                    dataTable.innerHTML = "<tr><td>Aucun résultat dans aucune table</td></tr>";
                    return;
                }
                let html = `<thead><tr><th>Table</th><th>Colonne</th><th>Valeur trouvée</th><th>Identifiant</th><th>Score</th><th>Action</th></tr></thead><tbody>`;
                results.forEach(r => {
                    html += `<tr>
                        <td>${r.table}</td>
                        <td>${r.col}</td>
                        <td>${getEnumLabel(r.col, r.value)}</td>
                        <td>${r.id || ""}</td>
                        <td>${r.score}</td>
                        <td>${r.id && r.table ? `<button class="action-btn update-btn" data-table="${r.table}" data-id="${r.id}">Voir & éditer</button>` : ""}</td>
                    </tr>`;
                });
                html += "</tbody>";
                dataTable.innerHTML = html;
                document.querySelectorAll('.update-btn').forEach(btn => {
                    btn.onclick = () => {
                        tableSelect.value = btn.dataset.table;
                        loadAll();
                        setTimeout(() => {
                            fetch(`/admin/table/${btn.dataset.table}`)
                                .then(res => res.json())
                                .then(data => {
                                    let row = data.find(x => {
                                        return String(x[Object.keys(x).find(k => k.startsWith("id_"))]) == btn.dataset.id;
                                    });
                                    if (row) startEditRow(row);
                                });
                        }, 700);
                    };
                });
            });
    };

    function loadTableData() {
        fetch(`/admin/table/${tableName}`)
            .then(res => res.json())
            .then(data => {
                tableData = data;
                renderTable();
            });
    }

    function loadTableStructure() {
        fetch(`/admin/table/${tableName}/structure`)
            .then(res => res.json())
            .then(struct => {
                tableStructure = struct;
                renderInsertForm();
            });
    }

    function renderTable(data = null, highlightValue = "") {
        const rows = data || tableData;
        if (!rows.length) {
            dataTable.innerHTML = "<tr><td>Aucune donnée</td></tr>";
            return;
        }
        let cols = Object.keys(rows[0]);
        let ths = cols.map(c => `<th>${c}</th>`).join("") + "<th>Actions</th>";
        let trs = rows.map((row, i) => {
            let isHighlighted = highlightValue && Object.values(row).some(field => (field + "").toLowerCase().includes(highlightValue));
            let tds = cols.map(c =>
                `<td>${getEnumLabel(c, row[c]) != null ? getEnumLabel(c, row[c]) : ""}</td>`
            ).join("");
            return `<tr${isHighlighted ? ' class="highlight-row"' : ''}>
                ${tds}
                <td>
                    <button class="update-btn action-btn" data-index="${i}">Modifier</button>
                    <button class="delete-btn action-btn" data-index="${i}">Supprimer</button>
                </td>
            </tr>`;
        }).join("");
        dataTable.innerHTML = `<thead><tr>${ths}</tr></thead><tbody>${trs}</tbody>`;

        document.querySelectorAll('.update-btn').forEach(btn => {
            btn.onclick = () => startEditRow(rows[btn.dataset.index]);
        });
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.onclick = () => deleteRow(rows[btn.dataset.index]);
        });

        if (highlightValue) {
            setTimeout(() => {
                document.querySelectorAll('.highlight-row').forEach(row => {
                    row.classList.remove('highlight-row');
                });
            }, 2000);
        }
        formUpdate.style.display = "none";
    }

    function renderInsertForm() {
        if (!tableStructure.length) {
            formInsert.innerHTML = "";
            return;
        }
        let html = `<form id="insert-form"><h3>Ajouter une entrée</h3>`;
        tableStructure.forEach(col => {
            if (/^id_/.test(col.name)) return;
            html += `<label>${col.name}${col.nullable ? "" : ' <span class="red-star">*</span>'}<br>`;
            if (ENUM_LABELS[col.name]) {
                html += `<select name="${col.name}" ${col.nullable ? "" : "required"}>`;
                html += `<option value="">-- Sélectionner --</option>`;
                Object.entries(ENUM_LABELS[col.name]).forEach(([val, label]) => {
                    html += `<option value="${val}">${label}</option>`;
                });
                html += `</select>`;
            } else {
                html += `<input type="${isDateField(col) ? 'date' : 'text'}" name="${col.name}" ${col.nullable ? "" : "required"}>`;
            }
            html += `</label>`;
        });
        html += `<div class="validation-error" id="form-error"></div>
                 <button type="submit">Insérer</button></form>`;
        formInsert.innerHTML = html;
        document.getElementById('insert-form').onsubmit = onInsert;
    }

    function startEditRow(row) {
        formInsert.style.display = "none";
        let html = `<form id="update-form"><h3>Modifier cette entrée</h3>`;
        tableStructure.forEach(col => {
            if (/^id_/.test(col.name)) return;
            html += `<label>${col.name}${col.nullable ? "" : ' <span class="red-star">*</span>'}<br>`;
            if (ENUM_LABELS[col.name]) {
                html += `<select name="${col.name}" ${col.nullable ? "" : "required"}>`;
                html += `<option value="">-- Sélectionner --</option>`;
                Object.entries(ENUM_LABELS[col.name]).forEach(([val, label]) => {
                    html += `<option value="${val}"${row[col.name] == val ? " selected" : ""}>${label}</option>`;
                });
                html += `</select>`;
            } else {
                html += `<input type="${isDateField(col) ? 'date' : 'text'}" name="${col.name}" value="${row[col.name] != null ? row[col.name] : ''}" ${col.nullable ? "" : "required"}>`;
            }
            html += `</label>`;
        });
        html += `<div class="validation-error" id="form-update-error"></div>
            <button type="submit" class="update-btn action-btn">Mettre à jour</button>
            <button type="button" onclick="
            document.getElementById('form-update').style.display='none';
            document.getElementById('form-insert').style.display='block';
        " class="delete-btn action-btn">Annuler</button>
    </form>`;
        formUpdate.innerHTML = html;
        formUpdate.style.display = "block";
        document.getElementById('update-form').onsubmit = function (e) {
            e.preventDefault();
            let obj = {};
            tableStructure.forEach(col => {
                if (/^id_/.test(col.name)) return;
                obj[col.name] = sanitizeInput(col, this[col.name].value.trim()) || null;
            });
            const id = getRowId(row);
            fetch(`/admin/table/${tableName}/${id}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(obj)
            }).then(res => {
                if (res.ok) {
                    loadTableData();
                    formUpdate.style.display = "none";
                    formInsert.style.display = "block";
                } else {
                    res.text().then(t => document.getElementById('form-update-error').innerHTML = t);
                }
            });
        };
    }

    function getRowId(row) {
        return Object.keys(row).find(k => /^id_/.test(k)) ? row[Object.keys(row).find(k => /^id_/.test(k))] : null;
    }

    function onInsert(e) {
        e.preventDefault();
        const form = e.target;
        let obj = {};
        tableStructure.forEach(col => {
            if (/^id_/.test(col.name)) return;
            obj[col.name] = sanitizeInput(col, form[col.name].value.trim()) || null;
        });
        fetch(`/admin/table/${tableName}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(obj)
        }).then(res => {
            if (res.ok) {
                loadTableData();
                form.reset();
                document.getElementById('form-error').innerHTML = "";
            } else {
                res.text().then(t => document.getElementById('form-error').innerHTML = t);
            }
        });
    }

    function deleteRow(row) {
        const id = getRowId(row);
        if (!id) return alert("Impossible de trouver l'identifiant.");
        if (!confirm("Confirmer la suppression de cette entrée ?")) return;
        fetch(`/admin/table/${tableName}/${id}`, {
            method: "DELETE"
        }).then(res => {
            if (res.ok) {
                loadTableData();
            } else {
                res.text().then(t => {
                    try {
                        const json = JSON.parse(t);
                        alert(json.detail || "Erreur inconnue");
                    } catch (e) {
                        alert("Erreur : suppression impossible.\n" + t.slice(0, 300));
                    }
                });
            }
        });
    }
});
