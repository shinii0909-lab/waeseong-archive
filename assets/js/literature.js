(async function () {
  const res = await fetch("data/literature.json");
  const items = await res.json();

  const body = document.getElementById("litBody");
  const search = document.getElementById("litSearch");
  const categorySel = document.getElementById("litCategory");
  const langSel = document.getElementById("litLang");
  const heldChk = document.getElementById("litHeld");
  const countEl = document.getElementById("litCount");

  const categories = [...new Set(items.map(i => i.category))].sort();
  categories.forEach(c => {
    const opt = document.createElement("option");
    opt.value = c; opt.textContent = c;
    categorySel.appendChild(opt);
  });

  function render(list) {
    body.innerHTML = "";
    let lastDecade = null;
    const frag = document.createDocumentFragment();

    list.forEach(i => {
      const decade = i.year ? `${Math.floor(parseInt(i.year, 10) / 10) * 10}년대` : "연도미상";
      if (decade !== lastDecade) {
        lastDecade = decade;
        const dr = document.createElement("tr");
        dr.className = "decade-row";
        dr.innerHTML = `<td colspan="5">${decade}</td>`;
        frag.appendChild(dr);
      }
      const tr = document.createElement("tr");
      const journalCell = [i.journal, i.publisher].filter(Boolean).join(" · ");
      const tags =
        (i.held ? `<span class="tag held">소장</span>` : "") +
        (i.lang === "일문" ? `<span class="tag jp">日</span>` : "");
      tr.innerHTML = `
        <td class="year">${i.year || "-"}</td>
        <td>${escapeHtml(i.author || "-")}</td>
        <td class="title">${escapeHtml(i.title)} ${tags}</td>
        <td>${escapeHtml(journalCell || "-")}</td>
        <td style="color:var(--muted);font-size:.78rem">${i.category}</td>
      `;
      frag.appendChild(tr);
    });
    body.appendChild(frag);
    countEl.innerHTML = `총 <b>${list.length}</b>건`;
  }

  function applyFilter() {
    const q = search.value.trim().toLowerCase();
    const cat = categorySel.value;
    const lang = langSel.value;
    const heldOnly = heldChk.checked;
    const filtered = items.filter(i => {
      const text = `${i.author || ""} ${i.title} ${i.journal || ""} ${i.publisher || ""}`.toLowerCase();
      return (!q || text.includes(q))
        && (!cat || i.category === cat)
        && (!lang || i.lang === lang)
        && (!heldOnly || i.held);
    });
    render(filtered);
  }

  search.addEventListener("input", applyFilter);
  categorySel.addEventListener("change", applyFilter);
  langSel.addEventListener("change", applyFilter);
  heldChk.addEventListener("change", applyFilter);
  render(items);
})();
