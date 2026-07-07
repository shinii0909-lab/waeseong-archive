kakao.maps.load(function () {
(async function () {
  const [fortresses, literature] = await Promise.all([
    fetch("data/fortresses.json").then(r => r.json()),
    fetch("data/literature.json").then(r => r.json()),
  ]);

  /* 히어로 통계 */
  const totalPhotos = fortresses.reduce((n, f) => n + (f.photos ? f.photos.length : 0), 0);
  document.getElementById("statPhoto").textContent = totalPhotos;
  document.getElementById("statLit").textContent = literature.length;

  /* ── 지도 (카카오맵) ── */
  const map = new kakao.maps.Map(document.getElementById("map"), {
    center: new kakao.maps.LatLng(35.12, 128.6),
    level: 9,
  });
  map.addControl(new kakao.maps.ZoomControl(), kakao.maps.ControlPosition.LEFT);

  const geocoded = fortresses.filter(f => f.lat && f.lng);
  if (geocoded.length) {
    const bounds = new kakao.maps.LatLngBounds();
    geocoded.forEach(f => bounds.extend(new kakao.maps.LatLng(f.lat, f.lng)));
    map.setBounds(bounds, 40, 40, 40, 40);
  }
  window.addEventListener("resize", () => kakao.maps.event.trigger(map, "resize"));

  const markers = {};
  fortresses.filter(f => f.lat && f.lng).forEach(f => {
    const el = document.createElement("div");
    el.className = "seal-marker";
    el.dataset.id = f.id;
    el.title = f.name;
    el.textContent = String(f.id).padStart(2, "0");
    el.addEventListener("click", () => selectFortress(f));

    const overlay = new kakao.maps.CustomOverlay({
      position: new kakao.maps.LatLng(f.lat, f.lng),
      content: el,
      yAnchor: 0.5,
      xAnchor: 0.5,
      zIndex: 10,
    });
    overlay.setMap(map);
    markers[f.id] = { overlay, el, lat: f.lat, lng: f.lng };
  });

  /* ── 목록 / 상세 패널 ── */
  const listEl = document.getElementById("fortressList");
  const detailEl = document.getElementById("panelDetail");
  const panelHead = document.getElementById("panelHead");
  const searchBox = document.getElementById("searchBox");
  const statusFilter = document.getElementById("statusFilter");
  let selectedId = null;

  function markerEl(id) {
    const m = markers[id];
    return m ? m.el : null;
  }

  function renderList(list) {
    listEl.innerHTML = "";
    list.forEach(f => {
      const li = document.createElement("li");
      if (f.id === selectedId) li.classList.add("active");
      const thumb = f.photos && f.photos.length
        ? `<img class="thumb" src="${f.photos[0].file}" alt="" loading="lazy">`
        : `<div class="thumb empty">無</div>`;
      li.innerHTML = `
        <span class="cat-no">No.${String(f.id).padStart(2, "0")}</span>
        ${thumb}
        <div class="fmeta">
          <div><span class="fname">${f.name}</span><span class="fhanja">${HANJA[f.id] || ""}</span></div>
          <div class="faddr">${f.address || ""}</div>
        </div>`;
      li.addEventListener("click", () => selectFortress(f));
      listEl.appendChild(li);
    });
  }

  function applyFilter() {
    const q = searchBox.value.trim().toLowerCase();
    const st = statusFilter.value;
    const filtered = fortresses.filter(f => {
      const text = `${f.name} ${f.alias || ""} ${f.address || ""} ${HANJA[f.id] || ""}`.toLowerCase();
      return (!q || text.includes(q)) && (!st || f.status === st);
    });
    renderList(filtered);
  }

  function showList() {
    selectedId = null;
    document.querySelectorAll(".seal-marker.sel").forEach(el => el.classList.remove("sel"));
    detailEl.innerHTML = "";
    listEl.style.display = "";
    panelHead.style.display = "";
    applyFilter();
  }

  function selectFortress(f) {
    selectedId = f.id;
    document.querySelectorAll(".seal-marker.sel").forEach(el => el.classList.remove("sel"));
    const me = markerEl(f.id);
    if (me) me.classList.add("sel");
    if (f.lat && f.lng) {
      map.setLevel(Math.min(map.getLevel(), 4));
      map.panTo(new kakao.maps.LatLng(f.lat, f.lng));
    }

    listEl.style.display = "none";
    panelHead.style.display = "none";

    const photos = f.photos || [];
    const metaRow = (k, v) => v ? `<div class="row"><span class="k">${k}</span><span>${escapeHtml(v)}</span></div>` : "";

    detailEl.innerHTML = `
      <div class="panel-detail">
        <button class="panel-back">&larr; 전체 목록</button>
        <div class="pd-head">
          <div class="pd-no">CATALOGUE No.${String(f.id).padStart(2, "0")}</div>
          <h3>${f.name}<span class="hanja">${HANJA[f.id] || ""}</span></h3>
          ${f.alias ? `<div class="alias">별칭 · ${escapeHtml(f.alias)}</div>` : ""}
        </div>
        <div class="pd-meta">
          ${metaRow("소재지", f.address)}
          ${metaRow("축조시기", f.era)}
          ${metaRow("발굴이력", f.excavation)}
          ${metaRow("문화재", f.heritage)}
        </div>
        <div class="pd-photos">
          <h4>사진자료 ${photos.length ? `(${photos.length})` : ""}</h4>
          ${photos.length
            ? `<div class="pd-photo-grid">${photos.map((p, i) =>
                `<img src="${p.file}" alt="${escapeHtml(p.caption || "")}" loading="lazy" data-idx="${i}">`).join("")}</div>`
            : `<div class="pd-nophoto">등록된 사진이 없습니다.</div>`}
        </div>
        <a class="pd-link" href="fortress.html?id=${f.id}">전체 기록 보기</a>
      </div>`;

    detailEl.querySelector(".panel-back").addEventListener("click", showList);
    detailEl.querySelectorAll(".pd-photo-grid img").forEach(img => {
      img.addEventListener("click", () => Lightbox.open(photos, parseInt(img.dataset.idx, 10)));
    });
  }

  searchBox.addEventListener("input", applyFilter);
  statusFilter.addEventListener("change", applyFilter);
  renderList(fortresses);
})();
});
