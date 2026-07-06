(async function () {
  const params = new URLSearchParams(window.location.search);
  const id = parseInt(params.get("id"), 10);
  const root = document.getElementById("detailContent");

  const res = await fetch("data/fortresses.json");
  const fortresses = await res.json();
  const f = fortresses.find(x => x.id === id);

  if (!f) {
    root.innerHTML = "<p>해당 왜성 정보를 찾을 수 없습니다.</p>";
    return;
  }

  document.title = `${f.name} — 왜성 기록관`;
  const photos = f.photos || [];

  root.innerHTML = `
    <div class="detail-header">
      <div class="pd-no">CATALOGUE No.${String(f.id).padStart(2, "0")}</div>
      <h1>${f.name}<span class="hanja">${HANJA[f.id] || ""}</span></h1>
      ${f.alias ? `<div class="alias">별칭 · ${escapeHtml(f.alias)}</div>` : ""}
      <span class="badge ${f.status || ""}">${f.status || "정보없음"}</span>
    </div>
    <table class="meta-table">
      <tr><th>소재지</th><td>${escapeHtml(f.address || "-")}</td></tr>
      <tr><th>축조시기</th><td>${escapeHtml(f.era || "-")}</td></tr>
      <tr><th>발굴이력</th><td>${escapeHtml(f.excavation || "-")}</td></tr>
      <tr><th>문화재 지정</th><td>${escapeHtml(f.heritage || "-")}</td></tr>
    </table>
    ${f.lat && f.lng ? '<div id="detailMap"></div>' : ""}
    ${f.overview
      ? `<h2>개요</h2><div class="overview-box">${escapeHtml(f.overview)}</div>
         <p class="source-note">출처: 왜성 보고서 발간 준비자료(${escapeHtml(f.overview_source)}) — 조사팀 자체 원고에서 발췌.</p>`
      : `<p class="source-note">아직 정리된 개요 원고가 없습니다.</p>`}
    ${photos.length
      ? `<h2>사진자료 <small style="font-size:.6em;color:var(--muted)">(${photos.length})</small></h2>
         <div class="photo-grid">${photos.map((p, i) => `
          <figure class="photo-card" data-idx="${i}">
            <img src="${p.file}" alt="${escapeHtml(p.caption || "")}" loading="lazy">
            <figcaption>${escapeHtml(p.caption || "")}<span class="photo-credit">${escapeHtml(p.credit || "")}</span></figcaption>
          </figure>`).join("")}</div>`
      : ""}
  `;

  if (f.lat && f.lng) {
    const map = L.map("detailMap").setView([f.lat, f.lng], 14);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
      attribution: "&copy; OpenStreetMap contributors &copy; CARTO",
      maxZoom: 19,
    }).addTo(map);
    const icon = L.divIcon({
      className: "",
      html: `<div class="seal-marker">${String(f.id).padStart(2, "0")}</div>`,
      iconSize: [28, 28], iconAnchor: [14, 14],
    });
    L.marker([f.lat, f.lng], { icon }).addTo(map)
      .bindTooltip(f.name, { className: "seal-tip", direction: "top", offset: [0, -15], permanent: true });
  }

  document.querySelectorAll(".photo-card").forEach(card => {
    card.addEventListener("click", () => Lightbox.open(photos, parseInt(card.dataset.idx, 10)));
  });
})();
