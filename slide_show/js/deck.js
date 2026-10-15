// Draws the "deploy route" across the top of every slide marked data-stop="N",
// then starts reveal.js. The route's progress bar animates from the previous
// stop to the current one each time a step slide comes into view.
(function () {
  const STOPS = ["VM", "Panel", "Database", "Python", "Code", "App server", "systemd", "Domain", "HTTPS", "Ship"];
  const last = STOPS.length - 1;

  document.querySelectorAll("section[data-stop]").forEach((section) => {
    const to = Number(section.dataset.stop);
    const from = Number(section.dataset.from || Math.max(1, to - 1));
    const route = document.createElement("div");
    route.className = "route";
    route.setAttribute("aria-hidden", "true");
    route.style.setProperty("--from", (from - 1) / last);
    route.style.setProperty("--to", (to - 1) / last);
    route.innerHTML =
      '<div class="route-track"><div class="route-fill"></div></div><ol>' +
      STOPS.map((name, i) => {
        const state = i + 1 < to ? "done" : i + 1 === to ? "current" : "";
        return `<li class="${state}" style="left:${(i / last) * 100}%"><span class="dot"></span><span class="lbl">${name}</span></li>`;
      }).join("") +
      "</ol>";
    (section.querySelector(".wrap") || section).prepend(route);
  });

  Reveal.initialize({
    width: 1600,
    height: 900,
    margin: 0.03,
    center: false,
    hash: true,
    slideNumber: "c/t",
    showSlideNumber: "speaker",
    transition: "fade",
    transitionSpeed: "default",
    backgroundTransition: "fade",
    controlsTutorial: false,
    plugins: [RevealNotes, RevealZoom, RevealHighlight],
  });
})();
