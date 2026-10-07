/* MDF Lexical Fields client-side search (generated).
 * Index data: assets/search-index.js (window.MDF_SEARCH_INDEX, works from file://)
 * backed by assets/search-index.json. Pipeline: lunr defaults minus the stemmer,
 * stop-word, and trimmer filters so accented source characters (á, ñ, é) survive
 * tokenization unchanged. */
(function () {
  "use strict";
  var input = document.getElementById("mdf-search");
  var box = document.getElementById("mdf-search-results");
  if (!input || !box) return;
  var index = null;
  var docs = {};

  function loadIndex() {
    if (typeof window.MDF_SEARCH_INDEX !== "undefined") {
      return Promise.resolve(window.MDF_SEARCH_INDEX);
    }
    return fetch("assets/search-index.json").then(function (r) { return r.json(); });
  }

  loadIndex()
    .then(function (data) {
      data.forEach(function (d) { docs[d.id] = d; });
      index = lunr(function () {
        this.pipeline.remove(lunr.stemmer);
        this.pipeline.remove(lunr.stopWordFilter);
        this.pipeline.remove(lunr.trimmer);
        this.ref("id");
        this.field("key", { boost: 10 });
        this.field("heading", { boost: 5 });
        this.field("text");
        data.forEach(function (d) { this.add(d); }, this);
      });
    })
    .catch(function () {
      box.hidden = false;
      box.textContent = "Search index unavailable.";
    });

  var timer = null;
  input.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(runSearch, 120);
  });

  function runSearch() {
    var query = input.value.trim();
    box.innerHTML = "";
    if (!query || !index) { box.hidden = true; return; }
    var hits;
    try { hits = index.search(query).slice(0, 25); } catch (err) { hits = []; }
    box.hidden = false;
    if (!hits.length) {
      var none = document.createElement("div");
      none.className = "search-empty";
      none.textContent = "No matches.";
      box.appendChild(none);
      return;
    }
    hits.forEach(function (hit) {
      var doc = docs[hit.ref];
      if (!doc) return;
      var link = document.createElement("a");
      link.href = doc.page + "#" + doc.anchor;
      var key = document.createElement("span");
      key.className = "hit-key";
      key.textContent = "\\" + doc.key;
      var heading = document.createElement("span");
      heading.className = "hit-heading";
      heading.textContent = doc.heading;
      link.appendChild(key);
      link.appendChild(heading);
      box.appendChild(link);
    });
  }

  document.addEventListener("click", function (event) {
    if (!box.contains(event.target) && event.target !== input) box.hidden = true;
  });
  input.addEventListener("keydown", function (event) {
    if (event.key === "Escape") { box.hidden = true; input.blur(); }
  });
})();
