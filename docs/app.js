(() => {
  "use strict";

  const book = window.BOOK_DATA;
  const reader = document.querySelector("#reader");
  const nav = document.querySelector("#chapter-nav");
  const rail = document.querySelector("#section-rail");
  const search = document.querySelector("#chapter-search");
  const searchStatus = document.querySelector("#search-status");
  const sidebar = document.querySelector("#sidebar");
  const scrim = document.querySelector("#sidebar-scrim");
  const menuButton = document.querySelector("#menu-button");
  const progressBar = document.querySelector("#reading-progress-bar");
  const backToTop = document.querySelector("#back-to-top");

  if (!book || !Array.isArray(book.chapters)) {
    reader.innerHTML = '<div class="empty-state">書稿資料載入失敗，請重新整理頁面。</div>';
    return;
  }

  const escapeHtml = (value) => String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

  const groupMap = new Map();
  book.chapters.forEach((chapter) => {
    if (!groupMap.has(chapter.group)) groupMap.set(chapter.group, []);
    groupMap.get(chapter.group).push(chapter);
  });

  function navMarkup(chapters = book.chapters) {
    const allowed = new Set(chapters.map((chapter) => chapter.id));
    return [...groupMap.entries()].map(([group, items]) => {
      const visible = items.filter((item) => allowed.has(item.id));
      if (!visible.length) return "";
      return `<section class="nav-group">
        <h2 class="nav-group-title">${escapeHtml(group)}</h2>
        ${visible.map((chapter) => `<button class="chapter-link" type="button" data-chapter="${chapter.id}">
          <span class="chapter-index">${chapter.id}</span>${escapeHtml(chapter.title)}
        </button>`).join("")}
      </section>`;
    }).join("");
  }

  function renderNav(chapters = book.chapters) {
    nav.innerHTML = navMarkup(chapters);
    nav.querySelectorAll("[data-chapter]").forEach((button) => {
      button.addEventListener("click", () => {
        location.hash = `chapter-${button.dataset.chapter}`;
        closeSidebar();
      });
    });
    syncActiveLink();
  }

  function closeSidebar() {
    sidebar.classList.remove("open");
    scrim.classList.remove("visible");
    menuButton.setAttribute("aria-expanded", "false");
    document.body.style.overflow = "";
  }

  function openSidebar() {
    sidebar.classList.add("open");
    scrim.classList.add("visible");
    menuButton.setAttribute("aria-expanded", "true");
    document.body.style.overflow = "hidden";
    search.focus();
  }

  function syncActiveLink(id = "") {
    nav.querySelectorAll(".chapter-link").forEach((link) => {
      const active = link.dataset.chapter === id;
      link.classList.toggle("active", active);
      if (active) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
  }

  function chapterButton(chapter, direction) {
    if (!chapter) return "<span></span>";
    return `<button class="chapter-nav-button" type="button" data-go="${chapter.id}">
      <span>${direction}</span><strong>${escapeHtml(chapter.title)}</strong>
    </button>`;
  }

  function wireChapterButtons() {
    reader.querySelectorAll("[data-go]").forEach((button) => {
      button.addEventListener("click", () => { location.hash = `chapter-${button.dataset.go}`; });
    });
  }

  function renderHome() {
    document.title = `${book.title}｜線上全文`;
    syncActiveLink();
    rail.innerHTML = "";
    reader.innerHTML = `<section class="home">
      <p class="eyebrow">線上完整書稿</p>
      <h1>${escapeHtml(book.title)}</h1>
      <p class="motto">${escapeHtml(book.motto)}</p>
      <p class="intro">從修道的根基出發，經由德、氣、神而進入符籙、科儀與濟世之用。章節不是各自分離的知識，而是一條由內在修持走向人間實踐的路。</p>
      <div class="home-actions">
        <button class="primary-action" id="start-reading" type="button">從導論開始</button>
        <button class="secondary-action" id="read-all" type="button">一次展開全文</button>
      </div>
      <div class="book-stats" aria-label="全書統計">
        <div class="book-stat"><strong>${book.chapterCount}</strong><span>篇章單元</span></div>
        <div class="book-stat"><strong>10</strong><span>主題篇章</span></div>
        <div class="book-stat"><strong>${Math.round(book.characters / 10000)} 萬</strong><span>約略字元</span></div>
      </div>
    </section>`;
    document.querySelector("#start-reading").addEventListener("click", () => { location.hash = "chapter-00"; });
    document.querySelector("#read-all").addEventListener("click", () => { location.hash = "all"; });
  }

  function renderChapter(id) {
    const chapterIndex = book.chapters.findIndex((chapter) => chapter.id === id);
    if (chapterIndex < 0) {
      renderHome();
      return;
    }
    const chapter = book.chapters[chapterIndex];
    const previous = book.chapters[chapterIndex - 1];
    const next = book.chapters[chapterIndex + 1];
    document.title = `${chapter.title}｜${book.title}`;
    syncActiveLink(id);
    reader.innerHTML = `<article>
      <header class="chapter-header">
        <p class="chapter-kicker">${escapeHtml(chapter.group)}</p>
        <h1>${escapeHtml(chapter.title)}</h1>
        <p class="chapter-meta">第 ${chapterIndex + 1}／${book.chapterCount} 單元</p>
      </header>
      <div class="prose">${chapter.html}</div>
      <nav class="chapter-nav-buttons" aria-label="前後章節">
        ${chapterButton(previous, "上一篇")}
        ${chapterButton(next, "下一篇")}
      </nav>
    </article>`;
    rail.innerHTML = chapter.toc.length ? `<div class="section-rail-title">本章段落</div>${chapter.toc.map((item) => `<a href="#${item.id}" data-section-link>${escapeHtml(item.label)}</a>`).join("")}` : "";
    rail.querySelectorAll("[data-section-link]").forEach((link) => {
      link.addEventListener("click", (event) => {
        event.preventDefault();
        document.getElementById(link.getAttribute("href").slice(1))?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
    wireChapterButtons();
  }

  function renderAll() {
    document.title = `全文閱讀｜${book.title}`;
    syncActiveLink();
    rail.innerHTML = "";
    reader.innerHTML = `<article>
      <header class="all-book-header">
        <p class="eyebrow">完整書稿</p>
        <h1>${escapeHtml(book.title)}</h1>
        <p class="intro">全書 ${book.chapterCount} 個單元已依序展開。可用瀏覽器頁面搜尋快速找字，也可從左側目錄切回單章閱讀。</p>
      </header>
      ${book.chapters.map((chapter) => `<section class="all-chapter" id="all-${chapter.id}">
        <div class="all-chapter-label">${escapeHtml(chapter.group)} · ${chapter.id}</div>
        <h2>${escapeHtml(chapter.title)}</h2>
        <div class="prose">${chapter.html}</div>
      </section>`).join("")}
    </article>`;
  }

  function renderSearchResults(query, matches) {
    document.title = `搜尋「${query}」｜${book.title}`;
    rail.innerHTML = "";
    syncActiveLink();
    reader.innerHTML = `<section class="search-page">
      <p class="eyebrow">全書搜尋</p>
      <h1>「${escapeHtml(query)}」</h1>
      <p class="intro">找到 ${matches.length} 個相關篇章。</p>
      <div>${matches.map((chapter) => {
        const text = chapter.searchText;
        const position = text.toLocaleLowerCase().indexOf(query.toLocaleLowerCase());
        const start = Math.max(0, position - 45);
        const excerpt = `${start > 0 ? "…" : ""}${text.slice(start, start + 130)}${text.length > start + 130 ? "…" : ""}`;
        return `<article class="search-result">
          <button type="button" data-go="${chapter.id}">${escapeHtml(chapter.title)}</button>
          <p>${escapeHtml(excerpt)}</p>
        </article>`;
      }).join("")}</div>
    </section>`;
    wireChapterButtons();
  }

  function route({ preserveScroll = false } = {}) {
    const raw = location.hash.slice(1) || "home";
    if (raw === "all") renderAll();
    else if (raw.startsWith("chapter-")) renderChapter(raw.replace("chapter-", ""));
    else renderHome();
    if (!preserveScroll) window.scrollTo({ top: 0, behavior: "instant" });
    reader.focus({ preventScroll: true });
    updateProgress();
  }

  function updateProgress() {
    const total = document.documentElement.scrollHeight - window.innerHeight;
    const percent = total > 0 ? Math.min(100, Math.max(0, (window.scrollY / total) * 100)) : 0;
    progressBar.style.width = `${percent}%`;
    backToTop.classList.toggle("visible", window.scrollY > 700);
  }

  let searchTimer;
  search.addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      const query = search.value.trim();
      if (!query) {
        renderNav();
        searchStatus.textContent = "";
        return;
      }
      const lowered = query.toLocaleLowerCase();
      const matches = book.chapters.filter((chapter) => chapter.searchText.toLocaleLowerCase().includes(lowered));
      renderNav(matches);
      searchStatus.textContent = `找到 ${matches.length} 個篇章`;
      renderSearchResults(query, matches);
    }, 180);
  });

  menuButton.addEventListener("click", () => sidebar.classList.contains("open") ? closeSidebar() : openSidebar());
  scrim.addEventListener("click", closeSidebar);
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") closeSidebar(); });
  document.querySelector("#full-book-button").addEventListener("click", () => { location.hash = "all"; });
  backToTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));

  const fontSizes = [17, 19, 21, 23];
  let fontIndex = Number(localStorage.getItem("book-font-index") || 1);
  fontIndex = Number.isInteger(fontIndex) && fontIndex >= 0 && fontIndex < fontSizes.length ? fontIndex : 1;
  document.documentElement.style.setProperty("--reading-size", `${fontSizes[fontIndex]}px`);
  document.querySelector("#font-button").addEventListener("click", () => {
    fontIndex = (fontIndex + 1) % fontSizes.length;
    document.documentElement.style.setProperty("--reading-size", `${fontSizes[fontIndex]}px`);
    localStorage.setItem("book-font-index", String(fontIndex));
  });

  const themeButton = document.querySelector("#theme-button");
  const savedTheme = localStorage.getItem("book-theme");
  if (savedTheme === "dark" || (!savedTheme && matchMedia("(prefers-color-scheme: dark)").matches)) document.body.classList.add("dark");
  themeButton.addEventListener("click", () => {
    document.body.classList.toggle("dark");
    localStorage.setItem("book-theme", document.body.classList.contains("dark") ? "dark" : "light");
  });

  window.addEventListener("hashchange", () => route());
  window.addEventListener("scroll", updateProgress, { passive: true });
  renderNav();
  route();
})();
