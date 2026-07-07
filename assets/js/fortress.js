kakao.maps.load(function () {
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

  const photos = f.photos || [];
  const pageDesc = [
    `${f.name}(${HANJA[f.id] || ""}) — 소재지 ${f.address || "미상"}, 축조시기 ${f.era || "미상"}.`,
    f.heritage ? `문화재 지정: ${f.heritage}.` : "",
    photos.length ? `사진자료 ${photos.length}건 수록.` : "",
  ].filter(Boolean).join(" ");
  const pageUrl = `https://shinii0909-lab.github.io/waeseong-archive/fortress.html?id=${f.id}`;

  document.title = `${f.name}(${HANJA[f.id] || ""}) — 왜성 기록관`;
  document.getElementById("metaDescription").setAttribute("content", pageDesc);
  document.getElementById("canonicalLink").setAttribute("href", pageUrl);
  document.getElementById("ogTitleTag").setAttribute("content", `${f.name} — 왜성 기록관`);
  document.getElementById("ogDescTag").setAttribute("content", pageDesc);
  document.getElementById("ogUrlTag").setAttribute("content", pageUrl);

  if (f.lat && f.lng) {
    const ld = document.createElement("script");
    ld.type = "application/ld+json";
    ld.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "LandmarksOrHistoricalBuildings",
      "name": f.name,
      "alternateName": HANJA[f.id] || undefined,
      "description": pageDesc,
      "address": f.address,
      "geo": { "@type": "GeoCoordinates", "latitude": f.lat, "longitude": f.lng },
      "url": pageUrl,
    });
    document.head.appendChild(ld);
  }

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
    const center = new kakao.maps.LatLng(f.lat, f.lng);
    const map = new kakao.maps.Map(document.getElementById("detailMap"), { center, level: 4 });
    map.addControl(new kakao.maps.ZoomControl(), kakao.maps.ControlPosition.LEFT);

    const el = document.createElement("div");
    el.className = "seal-marker";
    el.title = f.name;
    el.textContent = String(f.id).padStart(2, "0");
    new kakao.maps.CustomOverlay({ map, position: center, content: el, yAnchor: 0.5, xAnchor: 0.5 });

    const label = document.createElement("div");
    label.className = "seal-tip";
    label.textContent = f.name;
    new kakao.maps.CustomOverlay({ map, position: center, content: label, yAnchor: 2.1, xAnchor: 0.5 });
  }

  document.querySelectorAll(".photo-card").forEach(card => {
    card.addEventListener("click", () => Lightbox.open(photos, parseInt(card.dataset.idx, 10)));
  });
})();
});
