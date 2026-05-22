const formatPercent = (value) => {
  if (typeof value !== "number") return "--";
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
};

const toneClass = (value) => {
  if (typeof value !== "number") return "";
  return value >= 0 ? "positive" : "negative";
};

const setText = (id, value) => {
  document.getElementById(id).textContent = value;
};

const renderIndices = (indices) => {
  const tbody = document.getElementById("indices");
  tbody.innerHTML = "";

  indices.forEach((index) => {
    const row = document.createElement("tr");
    if (index.error) {
      row.innerHTML = `
        <td>${index.name}</td>
        <td colspan="5" class="muted">${index.error}</td>
      `;
      tbody.appendChild(row);
      return;
    }

    row.innerHTML = `
      <td>
        <strong>${index.name}</strong>
        <span>${index.ticker}</span>
      </td>
      <td>${index.close.toLocaleString()}</td>
      <td class="${toneClass(index.change_pct)}">${formatPercent(index.change_pct)}</td>
      <td class="${toneClass(index.change_5d)}">${formatPercent(index.change_5d)}</td>
      <td class="${toneClass(index.change_mtd)}">${formatPercent(index.change_mtd)}</td>
      <td>${index.low.toLocaleString()} - ${index.high.toLocaleString()}</td>
    `;
    tbody.appendChild(row);
  });
};

const renderNews = (items) => {
  const list = document.getElementById("news");
  list.innerHTML = "";

  items.forEach((item, index) => {
    const card = document.createElement("article");
    card.className = "news-card";
    card.innerHTML = `
      <div class="rank">${String(index + 1).padStart(2, "0")}</div>
      <div>
        <h3>${item.title}</h3>
        <p>${item.summary}</p>
        <div class="impact">
          <span>${item.impact}</span>
          <span>${item.reason}</span>
        </div>
      </div>
    `;
    list.appendChild(card);
  });
};

const renderReport = (report) => {
  setText("report-date", `${report.date} | 自动生成于 ${report.generated_at}`);
  setText("market-tone", report.market_overview.sentiment);
  setText("advancers", report.market_overview.advancers);
  setText("decliners", report.market_overview.decliners);
  setText("sources", report.sources.join(" / "));
  renderIndices(report.indices);
  renderNews(report.top_news);
};

fetch("./data/latest-report.json")
  .then((response) => {
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return response.json();
  })
  .then(renderReport)
  .catch((error) => {
    setText("report-date", "报告数据加载失败");
    setText("market-tone", error.message);
  });
