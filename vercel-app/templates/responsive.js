/* Enterprise Analytics — responsive navigation and Safari/iOS touch helpers.
 * No external libraries and no access to passwords, API keys or session data. */
(() => {
  "use strict";

  const $ = id => document.getElementById(id);
  const mobileQuery = window.matchMedia("(max-width: 960px)");
  const doc = document.documentElement;
  const sidebar = $("sidebar");
  const menuToggle = $("menuToggle");
  const overlay = $("mobileOverlay");
  const panels = [$("dashboardContent"), $("v2Module")].filter(Boolean);
  if (!sidebar || !menuToggle || !overlay) return;

  // app-shell is a stacking context (z-index:1). The backdrop was a sibling
  // of that context, making it sit ABOVE the menu despite menu z-index:120.
  // Put backdrop and drawer in the SAME context so the close button works.
  const appShell = document.querySelector(".app-shell");
  if (appShell && overlay.parentElement !== appShell) {
    appShell.insertBefore(overlay, appShell.firstChild);
  }

  const bottom = document.createElement("nav");
  bottom.className = "mobile-bottom-nav";
  bottom.id = "mobileBottomNav";
  bottom.setAttribute("aria-label", "Navegação rápida no celular");
  bottom.innerHTML = [
    ['overview', '▦', 'Início'],
    ['sales', '↗', 'Vendas'],
    ['finance', '◫', 'Finanças'],
    ['integrations', '⌁', 'Integrar'],
    ['menu', '☰', 'Menu']
  ].map(([key, symbol, label]) => (
    '<button type="button" data-mobile-id="' + key + '" aria-label="' +
    label + '" title="' + label + '"><span class="mobile-nav-icon" aria-hidden="true">' +
    symbol + '</span><span>' + label + '</span></button>'
  )).join("");
  document.body.appendChild(bottom);

  const closeButton = document.createElement("button");
  closeButton.type = "button";
  closeButton.className = "mobile-sidebar-close";
  closeButton.setAttribute("aria-label", "Fechar menu lateral");
  closeButton.textContent = "×";
  sidebar.prepend(closeButton);
  menuToggle.setAttribute("aria-controls", "sidebar");
  menuToggle.setAttribute("aria-expanded", "false");

  const tooltip = document.createElement("div");
  tooltip.id = "mobileChartTip";
  tooltip.className = "mobile-chart-tip";
  tooltip.setAttribute("role", "status");
  tooltip.setAttribute("aria-live", "polite");
  tooltip.hidden = true;
  document.body.appendChild(tooltip);

  let scrollBeforeMenu = 0;
  let wasLocked = false;
  let resetScroll = false;
  let viewportFrame = 0;
  let enhanceFrame = 0;
  let hideTooltipTimer = 0;

  function activePage() {
    if ($("integrationsNav")?.classList.contains("active")) return "integrations";
    return document.querySelector('.sidebar .nav-item[data-view].active')?.dataset.view || "overview";
  }

  function updateBottom() {
    const active = activePage();
    for (const button of bottom.querySelectorAll("button[data-mobile-id]")) {
      const selected = button.dataset.mobileId === active;
      button.classList.toggle("active", selected);
      if (selected) button.setAttribute("aria-current", "page");
      else button.removeAttribute("aria-current");
    }
  }

  function openMenu() {
    if (!mobileQuery.matches) return;
    sidebar.classList.add("open");
    overlay.hidden = false;
    updateMenuState();
    closeButton.focus({ preventScroll: true });
  }

  function closeMenu() {
    sidebar.classList.remove("open");
    overlay.hidden = true;
    updateMenuState();
  }

  function updateMenuState() {
    const show = mobileQuery.matches && sidebar.classList.contains("open");
    menuToggle.setAttribute("aria-expanded", String(show));
    if (show === wasLocked) return;

    if (show) {
      scrollBeforeMenu = window.scrollY || 0;
      document.body.style.top = "-" + scrollBeforeMenu + "px";
      document.body.classList.add("ea-menu-locked");
      wasLocked = true;
    } else {
      document.body.classList.remove("ea-menu-locked");
      document.body.style.removeProperty("top");
      wasLocked = false;
      const scrollTarget = resetScroll ? 0 : scrollBeforeMenu;
      resetScroll = false;
      window.scrollTo(0, scrollTarget);
    }
  }

  function useNavigation(key) {
    if (key === "menu") {
      openMenu();
      return;
    }
    let target = key === "integrations"
      ? $("integrationsNav")
      : document.querySelector('.sidebar button.nav-item[data-view="' + key + '"]');
    if (!target) {
      openMenu();
      return;
    }
    resetScroll = true;
    target.click();
    updateBottom();
    window.scrollTo(0, 0);
  }

  bottom.addEventListener("click", event => {
    const button = event.target.closest("[data-mobile-id]");
    if (!button) return;
    useNavigation(button.dataset.mobileId);
  });
  closeButton.addEventListener("click", () => {
    closeMenu();
    menuToggle.focus({ preventScroll: true });
  });

  // App.js owns sidebar toggle; observer synchronizes the scroll lock without
  // replacing or duplicating the app's original navigation listeners.
  sidebar.addEventListener("click", event => {
    if (event.target.closest('button.nav-item[data-view]') ||
        event.target.closest("#integrationsNav")) {
      resetScroll = true;
    }
  }, true);
  const sidebarObserver = new MutationObserver(() => {
    updateMenuState();
    updateBottom();
  });
  sidebarObserver.observe(sidebar, {
    attributes: true,
    attributeFilter: ["class", "aria-current"],
    subtree: true
  });

  function updateViewport() {
    viewportFrame = 0;
    const innerHeight = Math.max(200, window.innerHeight || 0);
    const visual = window.visualViewport;
    const isField = document.activeElement &&
      /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);
    const rawGap = visual
      ? innerHeight - visual.height - visual.offsetTop
      : 0;
    const keyboardHeight = (isField && rawGap > 110) ? Math.max(0, rawGap) : 0;
    const textField = isField && /^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName);
    const keyboardOpen = Boolean(isField && (
      textField || keyboardHeight > 110 ||
      (visual && visual.height < innerHeight * 0.78)
    ));
    doc.style.setProperty("--ea-visual-height", Math.round(innerHeight) + "px");
    doc.style.setProperty("--ea-keyboard-inset", Math.round(keyboardHeight) + "px");
    document.body.classList.toggle("ea-keyboard-open", keyboardOpen);
  }
  function scheduleViewport() {
    if (viewportFrame) return;
    viewportFrame = requestAnimationFrame(updateViewport);
  }
  window.addEventListener("resize", scheduleViewport, { passive: true });
  window.addEventListener("orientationchange", () => {
    closeMenu();
    scheduleViewport();
  }, { passive: true });
  window.visualViewport?.addEventListener("resize", scheduleViewport, { passive: true });
  window.visualViewport?.addEventListener("scroll", scheduleViewport, { passive: true });
  document.addEventListener("focusin", scheduleViewport);
  document.addEventListener("focusout", scheduleViewport);
  const breakpointChanged = () => {
    if (!mobileQuery.matches) closeMenu();
    updateBottom();
    scheduleViewport();
  };
  if (typeof mobileQuery.addEventListener === "function") {
    mobileQuery.addEventListener("change", breakpointChanged);
  } else if (typeof mobileQuery.addListener === "function") {
    mobileQuery.addListener(breakpointChanged);
  }
  scheduleViewport();

  function hideTip() {
    if (hideTooltipTimer) clearTimeout(hideTooltipTimer);
    hideTooltipTimer = 0;
    tooltip.hidden = true;
  }
  function showTip(node) {
    const value = node.dataset.tip || node.getAttribute("aria-label");
    if (!value) return;
    tooltip.textContent = value;
    tooltip.hidden = false;
    const rect = node.getBoundingClientRect();
    const w = tooltip.offsetWidth;
    const h = tooltip.offsetHeight;
    const left = Math.max(10, Math.min(window.innerWidth - w - 10, rect.left));
    const y = Math.max(12, Math.min(window.innerHeight - h - 18, rect.top - h - 9));
    tooltip.style.left = left + "px";
    tooltip.style.top = y + "px";
    hideTooltipTimer = setTimeout(hideTip, 4800);
  }
  document.addEventListener("click", event => {
    if (!mobileQuery.matches) return;
    const node = event.target.closest?.("[data-tip]");
    if (node) {
      hideTip();
      showTip(node);
    } else if (!event.target.closest?.("#mobileChartTip")) {
      hideTip();
    }
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape") {
      hideTip();
      if (sidebar.classList.contains("open")) closeMenu();
    }
  });
  window.addEventListener("scroll", hideTip, { passive: true });

  function enhanceMobileCharts() {
    enhanceFrame = 0;
    for (const panel of panels) {
      if (!panel) continue;
      for (const chart of panel.querySelectorAll(".v3-graph .chart-area")) {
        chart.setAttribute("role", "region");
        chart.setAttribute("aria-label", "Gráfico rolável horizontalmente para revelar datas e valores");
        chart.setAttribute("tabindex", "0");
      }
      for (const legacySvg of panel.querySelectorAll(".v2-panel > svg.v2-chart")) {
        if (legacySvg.parentElement?.classList.contains("ea-mobile-svg-scroll")) continue;
        const wrap = document.createElement("div");
        wrap.className = "ea-mobile-svg-scroll";
        wrap.setAttribute("role", "region");
        wrap.setAttribute("aria-label", "Gráfico com rolagem horizontal em telas pequenas");
        wrap.setAttribute("tabindex", "0");
        legacySvg.parentNode.insertBefore(wrap, legacySvg);
        wrap.appendChild(legacySvg);
      }
      for (const tabs of panel.querySelectorAll(".v2-tabs")) {
        tabs.setAttribute("aria-label", "Subabas: deslize lateralmente para ver mais opções");
        tabs.setAttribute("tabindex", "0");
        const active = tabs.querySelector(".v2-tab.active");
        if (mobileQuery.matches && active) {
          const centered = active.offsetLeft + active.offsetWidth / 2 - tabs.clientWidth / 2;
          tabs.scrollLeft = Math.max(0, centered);
        }
      }
    }
    updateBottom();
  }
  function scheduleEnhance() {
    if (enhanceFrame) return;
    enhanceFrame = requestAnimationFrame(enhanceMobileCharts);
  }
  for (const panel of panels) {
    const observer = new MutationObserver(scheduleEnhance);
    observer.observe(panel, { childList: true, subtree: true });
  }
  document.addEventListener("enterprise:rendered", scheduleEnhance);
  document.addEventListener("click", event => {
    const navTarget = event.target.closest?.('.sidebar button.nav-item[data-view], #integrationsNav');
    if (navTarget) requestAnimationFrame(updateBottom);
  });
  scheduleEnhance();
})();
