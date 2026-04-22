(function () {
  const siteData = window.SITE_DATA;
  if (!siteData) return;

  const page = document.body.dataset.page;
  const pageData = siteData.pages[page];
  const app = document.getElementById("app");
  if (!app || !pageData) return;

  document.title = pageData.title + " | " + siteData.config.clubName;

  function createHeader() {
    const header = document.createElement("header");
    header.className = "site-header";
    header.innerHTML = `
      <div class="container header-inner">
        <a class="brand" href="index.html">
          <img class="brand-logo" src="assets/images/apoel-bowling-logo.svg" alt="APOEL Bowling logo">
          <span class="brand-copy">
            <strong>APOEL Bowling</strong>
            <span>${siteData.config.season}</span>
          </span>
        </a>
        <button class="nav-toggle" type="button" aria-label="Toggle navigation">Menu</button>
        <nav class="main-nav" aria-label="Primary navigation">
          ${siteData.nav
            .map(
              (item) => `
                <a class="nav-link" href="${item.href}" ${item.page === page ? 'aria-current="page"' : ""}>
                  ${item.label}
                </a>
              `
            )
            .join("")}
        </nav>
      </div>
    `;

    const toggle = header.querySelector(".nav-toggle");
    toggle.addEventListener("click", () => header.classList.toggle("is-open"));
    return header;
  }

  function createFooter() {
    const footer = document.createElement("footer");
    footer.className = "site-footer";
    footer.innerHTML = `
      <div class="container">
        <div class="footer-card">
          <div class="footer-grid">
            <div>
              <p class="footer-brand">APOEL Bowling</p>
              <p class="footer-note">
                Clean static website structure designed to be easier to edit than Mobirise.
                Main content lives in <span class="inline-code">assets/js/site-data.js</span> and
                standings live in <span class="inline-code">assets/js/standings.js</span>.
              </p>
            </div>
            <div>
              <strong>Contact</strong>
              <div class="footer-list">
                <a href="tel:${siteData.config.phone.replace(/\s+/g, "")}">${siteData.config.phone}</a>
                <a href="mailto:${siteData.config.email}">${siteData.config.email}</a>
                <span>${siteData.config.venue}</span>
              </div>
            </div>
            <div>
              <strong>Quick links</strong>
              <div class="footer-list">
                <a href="agonistiko_programma.html">Πρόγραμμα</a>
                <a href="totalstandings.html">Βαθμολογία</a>
                <a href="xorigi.html">Χορηγοί</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
    return footer;
  }

  function pageHero(data) {
    return `
      <section class="${page === "index" ? "hero" : "page-hero"}">
        <div class="${page === "index" ? "hero-grid" : "page-hero-grid"}">
          <div class="hero-copy">
            <span class="eyebrow">${data.eyebrow}</span>
            <h1>${data.heading}</h1>
            <p>${data.text}</p>
            ${
              data.primaryCta
                ? `<div class="hero-actions">
                    <a class="button button-primary" href="${data.primaryCta.href}">${data.primaryCta.label}</a>
                    <a class="button button-secondary" href="${data.secondaryCta.href}">${data.secondaryCta.label}</a>
                  </div>`
                : ""
            }
          </div>
          ${
            data.image
              ? `<aside class="hero-panel">
                  <span class="panel-badge">${data.panelLabel || "APOEL Bowling"}</span>
                  <img src="${data.image}" alt="${data.panelTitle || data.heading}">
                  <div>
                    <strong>${data.panelTitle || data.heading}</strong>
                    <p class="muted">${data.panelText || ""}</p>
                  </div>
                </aside>`
              : ""
          }
        </div>
      </section>
    `;
  }

  function sectionHead(title, subtitle, copy) {
    return `
      <div class="section-head">
        <div>
          <p class="section-subtitle">${subtitle || ""}</p>
          <h2 class="section-title">${title}</h2>
        </div>
        ${copy ? `<p class="section-copy">${copy}</p>` : ""}
      </div>
    `;
  }

  function renderHome() {
    const data = siteData.pages.index;
    return `
      ${pageHero(data.hero)}
      <section class="section">
        <div class="container">
          ${sectionHead("Quick Access", "BBC League", "Keep your most important team links one tap away.")}
          <div class="grid grid-3">
            ${data.quickLinks
              .map(
                (item) => `
                  <a class="tile" href="${item.href}" target="_blank" rel="noreferrer">
                    <h3>${item.title}</h3>
                    <p>${item.text}</p>
                  </a>
                `
              )
              .join("")}
          </div>
        </div>
      </section>

      <section class="section">
        <div class="container split">
          <article class="split-panel">
            <img src="${data.venue.image}" alt="${data.venue.title}">
            <p class="section-subtitle">Home lane</p>
            <h2 class="section-title">${data.venue.title}</h2>
            <p>${data.venue.text}</p>
            <ul class="list">
              ${data.venue.bullets.map((item) => `<li><strong>${item}</strong></li>`).join("")}
            </ul>
          </article>
          <div class="grid">
            <div class="metric-card">
              <span>Venue</span>
              <strong>${data.venue.subtitle}</strong>
            </div>
            ${data.leaders
              .map(
                (item) => `
                  <div class="metric-card">
                    <span>${item.label}</span>
                    <strong>${item.value}</strong>
                  </div>
                `
              )
              .join("")}
          </div>
        </div>
      </section>

      <section class="section">
        <div class="container">
          ${sectionHead("Συχνές Ερωτήσεις", "FAQ", "Keep the answers visible for players, families, and new members.")}
          <div class="faq-list">
            ${data.faq
              .map(
                (item) => `
                  <article class="faq-item">
                    <strong>${item.q}</strong>
                    <p class="muted">${item.a}</p>
                  </article>
                `
              )
              .join("")}
          </div>
        </div>
      </section>
    `;
  }

  function renderNews() {
    const data = siteData.pages.news;
    return `
      ${pageHero(data.hero)}
      <section class="section">
        <div class="container">
          ${sectionHead("Latest Updates", "Newsroom", "Add or edit news cards inside the data file in a few lines.")}
          <div class="news-list">
            ${data.items
              .map(
                (item) => `
                  <article class="news-card">
                    <img src="${item.image}" alt="${item.title}">
                    <div class="news-meta">
                      <span class="meta-pill">${item.date}</span>
                      <span class="meta-pill">${item.category}</span>
                    </div>
                    <h3>${item.title}</h3>
                    <p class="muted">${item.text}</p>
                  </article>
                `
              )
              .join("")}
          </div>
        </div>
      </section>
    `;
  }

  function renderTeam() {
    const data = siteData.pages.i_omada;
    return `
      ${pageHero(data.hero)}
      <section class="section">
        <div class="container">
          ${sectionHead("Roster", "Team core", "Keep this section lightweight so you can update names and roles quickly.")}
          <div class="roster-grid">
            ${data.roster
              .map(
                (member) => `
                  <article class="roster-card">
                    <span class="roster-role">${member.role}</span>
                    <h3>${member.name}</h3>
                    <p class="muted">${member.bio}</p>
                  </article>
                `
              )
              .join("")}
          </div>
        </div>
      </section>
      <section class="section">
        <div class="container">
          ${sectionHead("Ημερολόγιο Επιτυχιών", "Highlights", "A simple place for milestones and achievements.")}
          <ul class="list">
            ${data.achievements.map((item) => `<li><strong>${item}</strong></li>`).join("")}
          </ul>
        </div>
      </section>
    `;
  }

  function renderSchedule() {
    const data = siteData.pages.agonistiko_programma;
    return `
      ${pageHero(data.hero)}
      <section class="section">
        <div class="container">
          ${sectionHead("Season Calendar", "Fixtures", "Replace the dates or links below whenever a new week is available.")}
          <div class="schedule-list">
            ${data.schedule
              .map(
                (event) => `
                  <article class="schedule-item">
                    <div class="date-badge">
                      <strong>${event.day}</strong>
                      <span>${event.month}</span>
                    </div>
                    <div>
                      <h3>${event.title}</h3>
                      <p class="muted">${event.details}</p>
                    </div>
                    <a class="button button-secondary" href="${event.link}" target="_blank" rel="noreferrer">Άνοιγμα</a>
                  </article>
                `
              )
              .join("")}
          </div>
        </div>
      </section>
    `;
  }

  function standingsState() {
    const defaults = window.STANDINGS_DATA || { rows: [], updatedAt: "", season: "" };
    try {
      const saved = JSON.parse(window.localStorage.getItem("apoel-standings"));
      if (saved && Array.isArray(saved.rows)) return saved;
    } catch (error) {
      console.warn("No saved standings override found", error);
    }
    return defaults;
  }

  function renderStandingsTable(data) {
    const sortedRows = [...data.rows].sort((a, b) => Number(b.points) - Number(a.points) || Number(b.pins) - Number(a.pins));
    return `
      <div class="table-shell">
        <table class="standings-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Team</th>
              <th>Played</th>
              <th>Wins</th>
              <th>Losses</th>
              <th>Pins</th>
              <th>Points</th>
            </tr>
          </thead>
          <tbody>
            ${sortedRows
              .map(
                (row, index) => `
                  <tr>
                    <td class="standings-rank ${index < 3 ? "is-top" : ""}">${index + 1}</td>
                    <td class="${index === 0 ? "is-top" : ""}">${row.team}</td>
                    <td>${row.played}</td>
                    <td>${row.wins}</td>
                    <td>${row.losses}</td>
                    <td>${row.pins}</td>
                    <td class="${index === 0 ? "is-top" : ""}">${row.points}</td>
                  </tr>
                `
              )
              .join("")}
          </tbody>
        </table>
      </div>
    `;
  }

  function renderStandingsEditor(data) {
    return `
      <div class="editor-shell">
        <div class="editor-head">
          <div>
            <strong>Edit mode</strong>
            <p class="muted">Update rows directly in the browser. Save stores the changes on this device. Export gives you JSON to copy into <span class="inline-code">assets/js/standings.js</span>.</p>
          </div>
          <div class="editor-actions">
            <button class="button button-secondary" type="button" id="add-row">Add team</button>
            <button class="button button-secondary" type="button" id="save-local">Save on this device</button>
            <button class="button button-secondary" type="button" id="export-json">Export JSON</button>
            <button class="button button-secondary" type="button" id="reset-local">Reset local changes</button>
          </div>
        </div>
        <div class="editor-grid" id="standings-editor-rows">
          ${data.rows
            .map(
              (row, index) => `
                <div class="editor-row" data-index="${index}">
                  <input name="team" value="${row.team}" aria-label="Team name">
                  <input name="played" type="number" value="${row.played}" aria-label="Played">
                  <input name="wins" type="number" value="${row.wins}" aria-label="Wins">
                  <input name="losses" type="number" value="${row.losses}" aria-label="Losses">
                  <input name="pins" type="number" value="${row.pins}" aria-label="Pins">
                  <input name="points" type="number" value="${row.points}" aria-label="Points">
                  <button class="button button-secondary remove-row" type="button">Remove</button>
                </div>
              `
            )
            .join("")}
        </div>
        <p class="editor-note">Tip: for a permanent update across devices and hosting, paste the exported JSON into <span class="inline-code">assets/js/standings.js</span>.</p>
      </div>
    `;
  }

  function renderStandings() {
    const data = standingsState();
    return `
      ${pageHero(siteData.pages.totalstandings.hero)}
      <section class="section">
        <div class="container">
          ${sectionHead("League Table", "Standings", "No spreadsheet dependency. The table is powered by local site data.")}
          <div class="stats-strip">
            <div class="metric-card">
              <span>Season</span>
              <strong>${data.season || siteData.config.season}</strong>
            </div>
            <div class="metric-card">
              <span>Teams</span>
              <strong>${data.rows.length}</strong>
            </div>
            <div class="metric-card">
              <span>Updated</span>
              <strong>${data.updatedAt || "Set a date"}</strong>
            </div>
          </div>
          <div id="standings-table-wrap">
            ${renderStandingsTable(data)}
          </div>
          ${renderStandingsEditor(data)}
        </div>
      </section>
    `;
  }

  function renderGallery() {
    const data = siteData.pages.gallery;
    return `
      ${pageHero(data.hero)}
      <section class="section">
        <div class="container">
          ${sectionHead("Gallery", "Season moments", "Swap images and captions in the data file whenever you upload new moments.")}
          <div class="gallery-grid">
            ${data.items
              .map(
                (item) => `
                  <article class="gallery-card">
                    <img src="${item.image}" alt="${item.title}">
                    <h3>${item.title}</h3>
                    <p class="muted">${item.text}</p>
                  </article>
                `
              )
              .join("")}
          </div>
        </div>
      </section>
    `;
  }

  function renderBbcTeams() {
    const data = siteData.pages.bbc_teams;
    return `
      ${pageHero(data.hero)}
      <section class="section">
        <div class="container">
          ${sectionHead("BBC League", "Community", "Use this page for team groupings, events, and league context.")}
          <div class="grid grid-3">
            ${data.groups
              .map(
                (item) => `
                  <article class="tile">
                    <h3>${item.title}</h3>
                    <p>${item.text}</p>
                  </article>
                `
              )
              .join("")}
          </div>
        </div>
      </section>
    `;
  }

  function renderSponsors() {
    const data = siteData.pages.xorigi;
    return `
      ${pageHero(data.hero)}
      <section class="section">
        <div class="container">
          ${sectionHead("Partners", "Support network", "Replace or add logos in the data file without touching the layout.")}
          <div class="sponsor-grid">
            ${data.sponsors
              .map(
                (item) => `
                  <article class="sponsor-card">
                    <img src="${item.image}" alt="${item.name}">
                    <h3>${item.name}</h3>
                    <p class="muted">${item.type}</p>
                  </article>
                `
              )
              .join("")}
          </div>
        </div>
      </section>
    `;
  }

  function renderComingSoon() {
    const data = siteData.pages.coming_soon;
    return `
      ${pageHero(data.hero)}
      <section class="section">
        <div class="container">
          <div class="callout">
            Use this page as a placeholder for future league results, player awards, or new archive sections.
          </div>
        </div>
      </section>
    `;
  }

  const pageRenderers = {
    index: renderHome,
    news: renderNews,
    i_omada: renderTeam,
    agonistiko_programma: renderSchedule,
    totalstandings: renderStandings,
    gallery: renderGallery,
    bbc_teams: renderBbcTeams,
    xorigi: renderSponsors,
    coming_soon: renderComingSoon
  };

  const shell = document.createElement("div");
  shell.className = "site-shell";
  shell.appendChild(createHeader());

  const main = document.createElement("main");
  main.className = "page-main";
  main.innerHTML = pageRenderers[page]() || "";
  shell.appendChild(main);
  shell.appendChild(createFooter());
  app.appendChild(shell);

  if (page === "totalstandings") {
    wireStandingsEditor();
  }

  function wireStandingsEditor() {
    const editor = document.getElementById("standings-editor-rows");
    if (!editor) return;

    function collectRows() {
      return Array.from(editor.querySelectorAll(".editor-row")).map((row) => ({
        team: row.querySelector('[name="team"]').value.trim(),
        played: Number(row.querySelector('[name="played"]').value || 0),
        wins: Number(row.querySelector('[name="wins"]').value || 0),
        losses: Number(row.querySelector('[name="losses"]').value || 0),
        pins: Number(row.querySelector('[name="pins"]').value || 0),
        points: Number(row.querySelector('[name="points"]').value || 0)
      })).filter((row) => row.team);
    }

    function currentData() {
      return {
        season: (window.STANDINGS_DATA && window.STANDINGS_DATA.season) || siteData.config.season,
        updatedAt: new Date().toISOString().slice(0, 10),
        columns: (window.STANDINGS_DATA && window.STANDINGS_DATA.columns) || ["Team", "Played", "Wins", "Losses", "Pins", "Points"],
        rows: collectRows()
      };
    }

    function repaintTable() {
      const wrap = document.getElementById("standings-table-wrap");
      if (!wrap) return;
      wrap.innerHTML = renderStandingsTable(currentData());
    }

    editor.addEventListener("input", repaintTable);
    editor.addEventListener("click", (event) => {
      const target = event.target;
      if (target.classList.contains("remove-row")) {
        target.closest(".editor-row").remove();
        repaintTable();
      }
    });

    document.getElementById("add-row").addEventListener("click", () => {
      const row = document.createElement("div");
      row.className = "editor-row";
      row.innerHTML = `
        <input name="team" value="" aria-label="Team name">
        <input name="played" type="number" value="0" aria-label="Played">
        <input name="wins" type="number" value="0" aria-label="Wins">
        <input name="losses" type="number" value="0" aria-label="Losses">
        <input name="pins" type="number" value="0" aria-label="Pins">
        <input name="points" type="number" value="0" aria-label="Points">
        <button class="button button-secondary remove-row" type="button">Remove</button>
      `;
      editor.appendChild(row);
    });

    document.getElementById("save-local").addEventListener("click", () => {
      const data = currentData();
      window.localStorage.setItem("apoel-standings", JSON.stringify(data));
      repaintTable();
      alert("Standings saved on this device.");
    });

    document.getElementById("reset-local").addEventListener("click", () => {
      window.localStorage.removeItem("apoel-standings");
      window.location.reload();
    });

    document.getElementById("export-json").addEventListener("click", async () => {
      const data = currentData();
      const payload = `window.STANDINGS_DATA = ${JSON.stringify(data, null, 2)};\n`;
      try {
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(payload);
          alert("Standings JSON copied to clipboard.");
        } else {
          const blob = new Blob([payload], { type: "text/javascript" });
          const url = URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = url;
          link.download = "standings.js";
          link.click();
          URL.revokeObjectURL(url);
        }
      } catch (error) {
        console.error(error);
        alert("Could not export automatically. Please copy it manually.");
      }
    });
  }
})();
