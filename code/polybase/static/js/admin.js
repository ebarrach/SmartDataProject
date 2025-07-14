// =============================================
// specification: Esteban Barracho (v.1 26/06/2025)
// implement: Esteban Barracho (v.4.1 12/07/2025)
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
        Tache: { statut: { 'a_faire': 'À faire', 'en_cours': 'En cours', 'termine': 'Terminé' } },
        Cout: { nature_cout: { 'interne': 'Interne', 'externe': 'Externe', 'logiciel': 'Logiciel', 'matériel': 'Matériel', 'sous-traitant': 'Sous-traitant' } },
        PrestationCollaborateur: { mode_facturation: { 'horaire': 'Horaire', 'forfaitaire': 'Forfaitaire' } },
        Facture: { statut: { 'emise': 'Émise', 'payee': 'Payée', 'en_attente': 'En attente' } },
        Personnel: { type_personnel: { 'interne': 'Interne', 'externe': 'Externe' } }
    };

    function getEnumLabel(table, colName, value) {
        const enumCols = ENUM_LABELS[table] || {};
        return (enumCols[colName] && enumCols[colName][value]) || value;
    }

    function sanitizeInput(col, valueRaw) {
        const type = col.type.toLowerCase();
        if (type === "boolean") return valueRaw === true || valueRaw === "on";
        if (type.includes("decimal") || type.includes("numeric")) {
            const parsed = parseFloat(String(valueRaw).replace(',', '.'));
            return isNaN(parsed) ? null : parsed;
        }
        if (type.includes("int")) {
            const parsed = parseInt(valueRaw, 10);
            return isNaN(parsed) ? null : parsed;
        }
        if (type.includes("date")) return valueRaw || null;
        return valueRaw === "" ? null : valueRaw;
    }

    function isDateField(col) {
        return col.type.toLowerCase().includes("date");
    }

    function isBooleanField(col) {
        return col.type.toLowerCase() === "boolean";
    }

    function isForeignKey(col) {
        return col.foreign_table !== undefined && col.foreign_table !== null;
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
            console.assert(Array.isArray(tables), "❌ Les tables doivent être retournées sous forme de tableau");
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
        loadTableStructure();
        loadTableData();
        formUpdate.style.display = "none";
    }

    function loadTableData() {
        fetch(`/admin/table/${tableName}`)
            .then(res => res.json())
            .then(data => {
                console.assert(Array.isArray(data), "❌ Les données de la table doivent être un tableau");
                if (data.length > 0) {
                    console.assert(typeof data[0] === "object", "❌ Chaque ligne doit être un objet");
                }
                tableData = data;
                renderTable();
            });
    }

    function loadTableStructure() {
        fetch(`/admin/table/${tableName}/structure`)
            .then(res => res.json())
            .then(struct => {
                console.assert(Array.isArray(struct), "❌ La structure de la table doit être un tableau");
                console.assert(struct.every(col => col.name && col.type), "❌ Chaque colonne doit avoir un nom et un type");
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
            let tds = cols.map(c => {
                if (c === "password") return "<td>********</td>";
                return `<td>${getEnumLabel(tableName, c, row[c]) != null ? getEnumLabel(tableName, c, row[c]) : ""}</td>`;
            }).join("");
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
        const enumCols = ENUM_LABELS[tableName] || {};
        let html = `<form id="insert-form"><h3>Ajouter une entrée</h3>`;
        let foreignKeyPromises = [];

        tableStructure.forEach(col => {
            if (/^id_/.test(col.name)) return;
            html += `<label>${col.name}${col.nullable ? "" : ' <span class="red-star">*</span>'}<br>`;

            if (enumCols[col.name]) {
                html += `<select name="${col.name}" ${col.nullable ? "" : "required"}>`;
                html += `<option value="">-- Sélectionner --</option>`;
                Object.entries(enumCols[col.name]).forEach(([val, label]) => {
                    html += `<option value="${val}">${label}</option>`;
                });
                html += `</select>`;
            } else if (isForeignKey(col)) {
                const refTable = col.foreign_table;
                const selectId = `select-${col.name}`;
                html += `<select name="${col.name}" id="${selectId}" ${col.nullable ? "" : "required"}>`;
                html += `<option value="">-- Chargement... --</option>`;
                html += `</select>`;
                // Stocke la promesse pour récupérer les données référencées
                foreignKeyPromises.push(
                    fetch(`/admin/table/${refTable}`)
                        .then(res => res.json())
                        .then(data => {
                            const select = document.getElementById(selectId);
                            if (!select) return;
                            select.innerHTML = `<option value="">-- Sélectionner --</option>`;
                            if (!data.length) {
                                select.innerHTML = `<option value="" disabled>(aucune donnée)</option>`;
                                return;
                            }
                            const idKey = Object.keys(data[0]).find(k => /^id_/.test(k));
                            const labelKey = Object.keys(data[0]).find(k => k !== idKey) || idKey;
                            data.forEach(row => {
                                select.innerHTML += `<option value="${row[idKey]}">${row[labelKey]}</option>`;
                            });
                        }).catch(() => {
                            const select = document.getElementById(selectId);
                            if (select) select.innerHTML = `<option value="" disabled>(erreur de chargement)</option>`;
                        })
                );
            } else if (isBooleanField(col)) {
                html += `<input type="checkbox" name="${col.name}">`;
            } else {
                const typeInput = col.name === "password" ? "password" : isDateField(col) ? "date" : "text";
                html += `<input type="${typeInput}" name="${col.name}" ${col.nullable ? "" : "required"}>`;
            }

            html += `</label>`;
        });

        html += `<div class="validation-error" id="form-error"></div>
                 <button type="submit">Insérer</button></form>`;
        formInsert.innerHTML = html;
         // Attache le handler après le rendu
        document.getElementById('insert-form').onsubmit = onInsert;
        // Lance tous les fetch de relation
        Promise.all(foreignKeyPromises);
    }

    function startEditRow(row) {
        formInsert.style.display = "none";
        const enumCols = ENUM_LABELS[tableName] || {};
        let html = `<form id="update-form"><h3>Modifier cette entrée</h3>`;
        let foreignKeyPromises = [];

        tableStructure.forEach(col => {
            if (/^id_/.test(col.name)) return;
            html += `<label>${col.name}${col.nullable ? "" : ' <span class="red-star">*</span>'}<br>`;

            if (enumCols[col.name]) {
                html += `<select name="${col.name}" ${col.nullable ? "" : "required"}>`;
                html += `<option value="">-- Sélectionner --</option>`;
                Object.entries(enumCols[col.name]).forEach(([val, label]) => {
                    const selected = row[col.name] == val ? "selected" : "";
                    html += `<option value="${val}" ${selected}>${label}</option>`;
                });
                html += `</select>`;
            } else if (isForeignKey(col)) {
                const refTable = col.foreign_table;
                const selectId = `update-${col.name}`;
                html += `<select name="${col.name}" id="${selectId}" ${col.nullable ? "" : "required"}>`;
                html += `<option value="">-- Chargement... --</option>`;
                html += `</select>`;
                foreignKeyPromises.push(
                    fetch(`/admin/table/${refTable}`)
                        .then(res => res.json())
                        .then(data => {
                            const select = document.getElementById(selectId);
                            if (!select) return;
                            select.innerHTML = `<option value="">-- Sélectionner --</option>`;
                            if (!data.length) {
                                select.innerHTML = `<option value="" disabled>(aucune donnée)</option>`;
                                return;
                            }
                            const idKey = Object.keys(data[0]).find(k => /^id_/.test(k));
                            const labelKey = Object.keys(data[0]).find(k => k !== idKey) || idKey;
                            data.forEach(rowRef => {
                                const selected = row[col.name] == rowRef[idKey] ? "selected" : "";
                                select.innerHTML += `<option value="${rowRef[idKey]}" ${selected}>${rowRef[labelKey]}</option>`;
                            });
                        }).catch(() => {
                            const select = document.getElementById(selectId);
                            if (select) select.innerHTML = `<option value="" disabled>(erreur de chargement)</option>`;
                        })
                );
            } else if (isBooleanField(col)) {
                const checked = row[col.name] ? "checked" : "";
                html += `<input type="checkbox" name="${col.name}" ${checked}>`;
            } else {
                const typeInput = col.name === "password" ? "password" : isDateField(col) ? "date" : "text";
                const val = row[col.name] != null ? row[col.name] : "";
                html += `<input type="${typeInput}" name="${col.name}" value="${val}" ${col.nullable ? "" : "required"}>`;
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
        // Attache le handler après chargement
        document.getElementById('update-form').onsubmit = function (e) {
            e.preventDefault();
            let obj = {};
            tableStructure.forEach(col => {
                if (/^id_/.test(col.name)) return;
                const input = this[col.name];
                if (isBooleanField(col)) {
                    obj[col.name] = input.checked;
                } else {
                    obj[col.name] = sanitizeInput(col, input.value.trim());
                }
            });
            const id = getRowId(row);
            fetch(`/admin/table/${tableName}/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
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

        Promise.all(foreignKeyPromises);
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
            const input = form[col.name];
            if (isBooleanField(col)) {
                obj[col.name] = input.checked;
            } else {
                obj[col.name] = sanitizeInput(col, input.value.trim());
            }
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
    importBtn.onclick = () => {
    const file = importFile.files[0];
    if (!file) return alert("Veuillez choisir un fichier Excel.");
    const formData = new FormData();
    formData.append("file", file);
    fetch(`/admin/import/${tableName}`, {
        method: "POST",
        body: formData
    }).then(res => res.json())
    .then(result => {
        if (result.status === "ok") {
            alert(`${result.inserted} ligne(s) importée(s).`);
            loadTableData();
            // Affiche la suggestion IA
            const suggestionBlock = document.getElementById("suggestion-block");
            const suggestionContent = document.getElementById("suggestion-content");
            if (suggestionBlock && suggestionContent) {
                suggestionContent.innerHTML = result.suggestion || "Aucune suggestion IA reçue.";
                suggestionBlock.style.display = "block";
            }
        } else {
            alert("Erreur d'import : " + JSON.stringify(result));
        }
    }).catch(err => {
        alert("Erreur réseau : " + err.message);
    });
    };
    document.getElementById("toggle-suggestion")?.addEventListener("click", () => {
    const content = document.getElementById("suggestion-content");
    const btn = document.getElementById("toggle-suggestion");
    content.classList.toggle("collapsed");
    btn.textContent = content.classList.contains("collapsed") ? "Déplier" : "Réduire";
    });
    searchForm.addEventListener("submit", e => {
    e.preventDefault();
    const query = searchInput.value.trim();
    if (!query) return;

    fetch(`/admin/search_global?query=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(matches => {
            if (!matches.length) {
                alert("Aucun résultat approximatif trouvé.");
                return;
            }

            const suggestionBlock = document.getElementById("suggestion-block");
            const suggestionContent = document.getElementById("suggestion-content");
            suggestionBlock.style.display = "block";
            suggestionContent.innerHTML = matches.map(match => `
                🔍 <strong>${match.value}</strong> (colonne <code>${match.col}</code> dans <code>${match.table}</code>) 
                <button class="goto-btn" data-table="${match.table}" data-id="${match.id}" style="margin-left:10px;">Voir et éditer</button>
                <br>`).join("");

            document.querySelectorAll(".goto-btn").forEach(btn => {
                btn.addEventListener("click", () => {
                    const tableNameTarget = btn.dataset.table;
                    const rowId = btn.dataset.id;

                    tableSelect.value = tableNameTarget;
                    tableName = tableNameTarget;
                    currentTable.textContent = tableName;

                    loadTableStructure();
                    fetch(`/admin/table/${tableName}`).then(res => res.json()).then(data => {
                        tableData = data;
                        renderTable(data, query.toLowerCase());
                        const entry = data.find(row => {
                            const idField = Object.keys(row).find(k => /^id_/.test(k));
                            return row[idField] == rowId;
                        });
                        if (entry) startEditRow(entry);
                    });
                });
            });
        });
    });
});
