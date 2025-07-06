// =============================================
// PolyBase Admin - CRUD + ENUM + Recherche globale Levenshtein
// Buttons + global search + robustification
// specification: Esteban Barracho (v.7 26/06/2025)
// implement: Esteban Barracho (v.7 26/06/2025)
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

    let tableData = [];
    let tableStructure = [];
    let tableName = "";
    let importedRows = [];
    let importIndex = 0;
    let filteredData = null;

    // --- Chargement des tables disponibles ---
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

    // --- Recherche globale toutes tables/colonnes (Levenshtein) ---
    searchForm.onsubmit = function (e) {
        e.preventDefault();
        const val = searchInput.value.trim();
        if (!val) {
            filteredData = null;
            renderTable();
            return;
        }
        // Recherche fuzzy globale (back FastAPI)
        fetch(`/admin/search_global?query=${encodeURIComponent(val)}`)
            .then(res => res.json())
            .then(results => {
                if (!results.length) {
                    dataTable.innerHTML = "<tr><td>Aucun résultat dans aucune table</td></tr>";
                    return;
                }
                // Affichage des résultats groupés par table + colonne, score et bouton "Voir ligne"
                let html = `<thead><tr><th>Table</th><th>Colonne</th><th>Valeur trouvée</th><th>Identifiant</th><th>Score</th><th>Action</th></tr></thead><tbody>`;
                results.forEach(r => {
                    html += `<tr>
                        <td>${r.table}</td>
                        <td>${r.col}</td>
                        <td>${r.value}</td>
                        <td>${r.id || ""}</td>
                        <td>${r.score}</td>
                        <td>${r.id && r.table ? `<button class="action-btn update-btn" data-table="${r.table}" data-id="${r.id}">Voir & éditer</button>` : ""}</td>
                    </tr>`;
                });
                html += "</tbody>";
                dataTable.innerHTML = html;

                // Listener "Voir & éditer" : charge la table et préremplit pour édition rapide
                document.querySelectorAll('.update-btn').forEach(btn => {
                    btn.onclick = () => {
                        tableSelect.value = btn.dataset.table;
                        loadAll();
                        setTimeout(() => {
                            // Sélectionne la ligne à éditer
                            fetch(`/admin/table/${btn.dataset.table}`)
                                .then(res => res.json())
                                .then(data => {
                                    let row = data.find(x => {
                                        // id peut être string ou int, donc == pas ===
                                        return String(x[Object.keys(x).find(k=>k.startsWith("id_"))]) == btn.dataset.id;
                                    });
                                    if(row) startEditRow(row);
                                });
                        }, 700); // Laisse le temps au select de recharger la structure
                    };
                });
            });
    };

    // --- Chargement des données ---
    function loadTableData() {
        fetch(`/admin/table/${tableName}`)
            .then(res => res.json())
            .then(data => {
                tableData = data;
                renderTable();
            });
    }

    // --- Chargement de la structure ---
    function loadTableStructure() {
        fetch(`/admin/table/${tableName}/structure`)
            .then(res => res.json())
            .then(struct => {
                tableStructure = struct;
                renderInsertForm();
            });
    }

    // --- Affichage du tableau de données avec actions ---
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
                `<td>${row[c] != null ? row[c] : ""}</td>`
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

        // Ajoute listeners
        document.querySelectorAll('.update-btn').forEach(btn => {
            btn.onclick = () => startEditRow(rows[btn.dataset.index]);
        });
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.onclick = () => deleteRow(rows[btn.dataset.index]);
        });

        // Supprime la surbrillance après 2s
        if (highlightValue) {
            setTimeout(() => {
                document.querySelectorAll('.highlight-row').forEach(row => {
                    row.classList.remove('highlight-row');
                });
            }, 2000);
        }
        formUpdate.style.display = "none";
    }

    // --- Export Excel ---
    exportBtn.onclick = () => {
        if (!tableData.length) return alert("Aucune donnée à exporter !");
        let ws = XLSX.utils.json_to_sheet(tableData);
        let wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, tableName);
        XLSX.writeFile(wb, `${tableName}.xlsx`);
    };

    // --- Import Excel (pré-remplissage ligne par ligne) ---
    importBtn.onclick = () => importFile.click();
    importFile.onchange = e => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = evt => {
            const data = new Uint8Array(evt.target.result);
            const workbook = XLSX.read(data, {type: 'array'});
            const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
            const rows = XLSX.utils.sheet_to_json(firstSheet, {defval: ""});
            if (!rows.length) return alert("Le fichier est vide.");
            importedRows = rows;
            importIndex = 0;
            prefillFormWithImport();
        };
        reader.readAsArrayBuffer(file);
    };

    function prefillFormWithImport() {
        if (!importedRows.length || importIndex >= importedRows.length) {
            alert("Toutes les lignes importées ont été traitées.");
            importedRows = [];
            importIndex = 0;
            if (formInsert.querySelector('form')) formInsert.querySelector('form').reset();
            return;
        }
        const form = formInsert.querySelector('form');
        const currentRow = importedRows[importIndex];
        tableStructure.forEach(col => {
            if (form[col.name]) {
                form[col.name].value = currentRow[col.name] !== undefined ? currentRow[col.name] : '';
            }
        });
        let btnZone = form.querySelector('#import-btn-zone');
        if (!btnZone) {
            btnZone = document.createElement('div');
            btnZone.id = "import-btn-zone";
            btnZone.style.marginTop = "10px";
            form.appendChild(btnZone);
        }
        btnZone.innerHTML = `
            <button type="button" id="validate-row-btn">Insérer cette ligne</button>
            <button type="button" id="skip-row-btn">Ignorer cette ligne</button>
            <span style="margin-left:10px; color:#666;">Ligne ${importIndex + 1} sur ${importedRows.length}</span>
        `;
        form.querySelector('#validate-row-btn').onclick = () => form.requestSubmit();
        form.querySelector('#skip-row-btn').onclick = () => { importIndex++; prefillFormWithImport(); };
    }

    // --- Génération dynamique du formulaire avec ENUMs <select> ---
    function renderInsertForm() {
        if (!tableStructure.length) {
            formInsert.innerHTML = "";
            return;
        }
        let html = `<form id="insert-form"><h3>Ajouter une entrée</h3>`;
        tableStructure.forEach(col => {
            if (/^id_/.test(col.name)) return; // Jamais saisir l'id manuellement
            html += `<label>${col.name}${col.nullable ? "" : ' <span class="red-star">*</span>'}<br>`;
            if (col.type.toLowerCase().startsWith("enum")) {
                let options = [];
                let match = col.type.match(/\((.*?)\)/);
                if (match) {
                    options = match[1].split(',').map(v => v.trim().replace(/'/g, ""));
                }
                html += `<select name="${col.name}" ${col.nullable ? "" : "required"}>`;
                html += `<option value="">-- Sélectionner --</option>`;
                options.forEach(opt => {
                    html += `<option value="${opt}">${opt}</option>`;
                });
                html += `</select>`;
            } else {
                html += `
                    <input type="${typeToInput(col.type)}" 
                        name="${col.name}" 
                        ${col.nullable ? "" : "required"}
                        ${col.type === "number" && col.precision ? `step="any"` : ""}
                        ${col.maxLength ? `maxlength="${col.maxLength}"` : ""}
                    >`;
            }
            html += `</label>`;
        });
        html += `<div class="validation-error" id="form-error"></div>
                 <button type="submit">Insérer</button></form>`;
        formInsert.innerHTML = html;
        document.getElementById('insert-form').onsubmit = onInsert;
    }

    // --- Validation et envoi du formulaire d'insertion ---
    function onInsert(e) {
        e.preventDefault();
        const form = e.target;
        let obj = {};
        let valid = true;
        let msg = "";
        tableStructure.forEach(col => {
            if (/^id_/.test(col.name)) return;
            let val = form[col.name].value.trim();
            if (!col.nullable && !val) {
                valid = false;
                msg += `Champ ${col.name} obligatoire.<br>`;
            }
            if (col.type.toLowerCase().startsWith("enum")) {
                // Le <select> garantit la valeur
            } else if (col.type === "number" && val && isNaN(val)) {
                valid = false;
                msg += `Champ ${col.name} doit être numérique.<br>`;
            }
            obj[col.name] = val || null;
        });
        document.getElementById('form-error').innerHTML = msg;
        if (!valid) return;
        fetch(`/admin/table/${tableName}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(obj)
        }).then(res => {
            if (res.ok) {
                loadTableData();
                form.reset();
                document.getElementById('form-error').innerHTML = "";
                if (importedRows.length) {
                    importIndex++;
                    prefillFormWithImport();
                }
            } else {
                res.text().then(t => document.getElementById('form-error').innerHTML = t);
            }
        });
    }

    function typeToInput(type) {
        type = type.toLowerCase();
        if (type.includes('int') || type.includes('decimal') || type === 'number') return "number";
        if (type === "date") return "date";
        if (type === "boolean" || type === "tinyint(1)") return "checkbox";
        return "text";
    }

    // --- Utilitaire pour récupérer la clé primaire id_ ---
    function getRowId(row) {
        return Object.keys(row).find(k => /^id_/.test(k)) ? row[Object.keys(row).find(k => /^id_/.test(k))] : null;
    }

    // --- Edition d'une ligne (formulaire update dynamique) ---
    function startEditRow(row) {
        formInsert.style.display = "none";
        // Structure identique à renderInsertForm, mais préremplie et sans l'ID
        let html = `<form id="update-form"><h3>Modifier cette entrée</h3>`;
        tableStructure.forEach(col => {
            if (/^id_/.test(col.name)) return; // jamais éditer l'id
            html += `<label>${col.name}${col.nullable ? "" : ' <span class="red-star">*</span>'}<br>`;
            if (col.type.toLowerCase().startsWith("enum")) {
                let options = [];
                let match = col.type.match(/\((.*?)\)/);
                if (match) {
                    options = match[1].split(',').map(v => v.trim().replace(/'/g, ""));
                }
                html += `<select name="${col.name}" ${col.nullable ? "" : "required"}>`;
                html += `<option value="">-- Sélectionner --</option>`;
                options.forEach(opt => {
                    html += `<option value="${opt}"${row[col.name] == opt ? " selected" : ""}>${opt}</option>`;
                });
                html += `</select>`;
            } else {
                html += `<input type="${typeToInput(col.type)}" 
                    name="${col.name}" 
                    value="${row[col.name] !== null && row[col.name] !== undefined ? row[col.name] : ''}"
                    ${col.nullable ? "" : "required"}
                    ${col.type === "number" && col.precision ? `step="any"` : ""}
                    ${col.maxLength ? `maxlength="${col.maxLength}"` : ""}
                >`;
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
            let valid = true;
            let msg = "";
            tableStructure.forEach(col => {
                if (/^id_/.test(col.name)) return;
                let val = this[col.name].value.trim();
                if (!col.nullable && !val) {
                    valid = false;
                    msg += `Champ ${col.name} obligatoire.<br>`;
                }
                if (col.type === "number" && val && isNaN(val)) {
                    valid = false;
                    msg += `Champ ${col.name} doit être numérique.<br>`;
                }
                obj[col.name] = val || null;
            });
            document.getElementById('form-update-error').innerHTML = msg;
            if (!valid) return;
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

    // --- Suppression d'une ligne ---
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
