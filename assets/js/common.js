/* 공용: 왜성 한자 표기 + 라이트박스 */

const HANJA = {
  1: "蔚山倭城", 2: "西生浦倭城", 3: "梁山倭城", 4: "弧浦倭城", 5: "林浪浦倭城",
  6: "機張倭城", 7: "釜山倭城", 8: "子城臺倭城", 9: "中央洞倭城", 10: "東萊倭城",
  11: "加德倭城", 12: "城北倭城", 13: "竹島倭城", 14: "龜浦倭城", 15: "影島倭城",
  16: "農所倭城", 17: "馬沙倭城", 18: "安骨浦倭城", 19: "熊川倭城", 20: "子馬倭城",
  21: "明洞倭城", 22: "馬山倭城", 23: "望晉倭城", 24: "固城倭城", 25: "永登浦倭城",
  26: "松眞浦倭城", 27: "長門浦倭城", 28: "見乃梁倭城", 29: "泗川倭城", 30: "南海倭城",
  31: "順天倭城",
};

function escapeHtml(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/* ── 라이트박스 ───────────────────────────────────────────── */
const Lightbox = (function () {
  let photos = [];
  let idx = 0;
  let el = null;

  function build() {
    el = document.createElement("div");
    el.className = "lightbox";
    el.innerHTML = `
      <button class="lb-close" aria-label="닫기">&times;</button>
      <button class="lb-prev" aria-label="이전">&#8249;</button>
      <button class="lb-next" aria-label="다음">&#8250;</button>
      <figure class="lb-figure">
        <img class="lb-img" src="" alt="">
        <figcaption class="lb-caption">
          <span class="lb-text"></span>
          <span class="lb-credit"></span>
          <span class="lb-counter"></span>
        </figcaption>
      </figure>`;
    document.body.appendChild(el);

    el.querySelector(".lb-close").addEventListener("click", close);
    el.querySelector(".lb-prev").addEventListener("click", () => move(-1));
    el.querySelector(".lb-next").addEventListener("click", () => move(1));
    el.addEventListener("click", (e) => { if (e.target === el) close(); });
    document.addEventListener("keydown", (e) => {
      if (!el.classList.contains("open")) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") move(-1);
      if (e.key === "ArrowRight") move(1);
    });
  }

  function render() {
    const p = photos[idx];
    el.querySelector(".lb-img").src = p.file;
    el.querySelector(".lb-img").alt = p.caption || "";
    el.querySelector(".lb-text").textContent = p.caption || "";
    el.querySelector(".lb-credit").textContent = p.credit || "";
    el.querySelector(".lb-counter").textContent = `${idx + 1} / ${photos.length}`;
    const multi = photos.length > 1;
    el.querySelector(".lb-prev").style.display = multi ? "" : "none";
    el.querySelector(".lb-next").style.display = multi ? "" : "none";
  }

  function move(d) {
    idx = (idx + d + photos.length) % photos.length;
    render();
  }

  function open(list, startIdx) {
    if (!el) build();
    photos = list;
    idx = startIdx || 0;
    render();
    el.classList.add("open");
    document.body.style.overflow = "hidden";
  }

  function close() {
    el.classList.remove("open");
    document.body.style.overflow = "";
  }

  return { open };
})();
