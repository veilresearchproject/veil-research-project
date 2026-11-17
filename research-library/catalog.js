"use strict";

const search = document.getElementById("case-search");
const finding = document.getElementById("case-finding");
const results = document.getElementById("case-results");
const classifications = new Set(Array.from(finding.options, option => option.value).filter(Boolean));
const reportPath = /^(?:[a-zA-Z0-9_-]+\/)*[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)*\.pdf$/;

function approvedCase(record) {
  return record && record.status === "published" &&
    typeof record.id === "string" && /^VEIL-IR-\d{4}-\d{3}$/.test(record.id) &&
    typeof record.title === "string" && record.title.trim() &&
    typeof record.summary === "string" && classifications.has(record.classification) &&
    typeof record.publication_date === "string" && /^\d{4}-\d{2}-\d{2}$/.test(record.publication_date) &&
    typeof record.report_url === "string" && reportPath.test(record.report_url);
}

function card(record) {
  const article = document.createElement("article");
  article.className = "library-card";
  const heading = document.createElement("h3");
  const link = document.createElement("a");
  link.href = record.report_url;
  link.textContent = record.id + " · " + record.title;
  heading.append(link);
  const metadata = document.createElement("p");
  metadata.textContent = record.classification + " · Published " + record.publication_date;
  if (typeof record.review_version === "string" && record.review_version) {
    metadata.textContent += " · Version " + record.review_version;
  }
  const summary = document.createElement("p");
  summary.textContent = record.summary;
  article.append(heading, metadata, summary);
  return article;
}

async function loadCatalog() {
  results.textContent = "Loading catalog…";
  try {
    const response = await fetch("cases.json", { cache: "no-store" });
    if (!response.ok) throw Error("Catalog unavailable");
    const data = await response.json();
    if (data?.schema_version !== "1.0" || !Array.isArray(data.cases)) {
      throw Error("Invalid catalog");
    }
    const cases = data.cases.filter(approvedCase);
    function show() {
      const query = search.value.trim().toLowerCase();
      const matches = cases.filter(record => {
        const topics = Array.isArray(record.topics)
          ? record.topics.filter(topic => typeof topic === "string") : [];
        const text = [record.id, record.title, record.summary, ...topics].join(" ").toLowerCase();
        return (!finding.value || record.classification === finding.value) && text.includes(query);
      });
      const status = document.createElement("p");
      status.textContent = matches.length ? (
        matches.length === 1 ? "1 matching report." : matches.length + " matching reports."
      ) : (cases.length ? "No published cases match your filters." : "No VEIL investigation reports have been published yet.");
      results.replaceChildren(status, ...matches.map(card));
    }
    search.addEventListener("input", show);
    finding.addEventListener("change", show);
    show();
  } catch {
    results.textContent = "The case catalog is temporarily unavailable.";
  }
}

loadCatalog();
