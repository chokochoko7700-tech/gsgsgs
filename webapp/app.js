const tg = window.Telegram?.WebApp;
tg?.ready();
tg?.expand();

const $ = (id) => document.getElementById(id);
const form = $("form"), input = $("username"), btn = $("btn");
const statusBox = $("status"), statusText = $("statusText"), countEl = $("count");
const spinner = $("spinner"), barFill = $("barFill");
const results = $("results"), empty = $("empty");
const filterWrap = $("filterWrap"), filter = $("filter"), copyAll = $("copyAll");

let source = null;
let found = [];

const USERNAME_RE = /^[A-Za-z0-9._-]{2,40}$/;

function setRunning(running) {
  btn.disabled = running;
  btn.textContent = running ? "…" : "Qidirish";
  spinner.classList.toggle("stop", !running);
  barFill.classList.toggle("full", !running);
}

function addResult({ site, url }) {
  found.push({ site, url });
  const host = new URL(url).hostname;
  const li = document.createElement("li");
  li.dataset.key = (site + " " + url).toLowerCase();
  li.innerHTML = `
    <a href="#" rel="noopener">
      <img loading="lazy" alt="" src="https://www.google.com/s2/favicons?sz=64&domain=${encodeURIComponent(host)}">
      <span class="meta"><span class="site"></span><span class="url"></span></span>
      <span class="arrow">›</span>
    </a>`;
  li.querySelector(".site").textContent = site;
  li.querySelector(".url").textContent = url;
  li.querySelector("a").addEventListener("click", (e) => {
    e.preventDefault();
    tg ? tg.openLink(url) : window.open(url, "_blank");
  });
  results.appendChild(li);
  countEl.textContent = found.length;
  applyFilter();
}

function applyFilter() {
  const q = filter.value.trim().toLowerCase();
  for (const li of results.children) li.style.display = !q || li.dataset.key.includes(q) ? "" : "none";
}

function start(username) {
  source?.close();
  found = [];
  results.innerHTML = "";
  countEl.textContent = "0";
  empty.classList.add("hidden");
  filterWrap.classList.add("hidden");
  statusBox.classList.remove("hidden");
  statusText.textContent = `@${username} qidirilmoqda…`;
  setRunning(true);

  const qs = new URLSearchParams({ username, initData: tg?.initData || "" });
  source = new EventSource(`/api/search?${qs}`);

  source.addEventListener("found", (e) => {
    addResult(JSON.parse(e.data));
    filterWrap.classList.remove("hidden");
    tg?.HapticFeedback?.selectionChanged();
  });
  source.addEventListener("done", (e) => {
    const { count } = JSON.parse(e.data);
    finish(count ? `Tayyor — ${count} ta profil topildi` : "Hech narsa topilmadi");
    tg?.HapticFeedback?.notificationOccurred("success");
  });
  source.addEventListener("fail", (e) => finish("⚠️ " + JSON.parse(e.data).error));
  source.onerror = () => {
    if (btn.disabled) finish("⚠️ Aloqa uzildi. Mini app'ni Telegram ichidan oching.");
  };
}

function finish(text) {
  source?.close();
  source = null;
  statusText.textContent = text;
  setRunning(false);
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const username = input.value.trim().replace(/^@/, "");
  if (!USERNAME_RE.test(username)) {
    tg?.showAlert ? tg.showAlert("Faqat harf, raqam, . _ - (2–40 belgi)") : alert("Username noto'g'ri");
    return;
  }
  input.blur();
  start(username);
});

filter.addEventListener("input", applyFilter);

copyAll.addEventListener("click", async () => {
  const text = found.map((r) => `${r.site}: ${r.url}`).join("\n");
  try {
    await navigator.clipboard.writeText(text);
    copyAll.textContent = "✓ Nusxalandi";
    setTimeout(() => (copyAll.textContent = "Nusxalash"), 1500);
  } catch {
    tg?.showAlert?.("Nusxalab bo'lmadi");
  }
});
