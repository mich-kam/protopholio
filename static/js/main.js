(function () {
  "use strict";

  var doc = document.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Filet de sécurité : on NE coupe pas tout de suite le fallback du <head>.
  // Si une vieille version de ce fichier est en cache, les nouvelles classes
  // (.reveal-left, .stagger…) resteraient invisibles sans ce filet.
  var revealSelector = ".reveal, .reveal-left, .reveal-right, .reveal-scale, .stagger";
  function forceRevealAll() {
    $all(revealSelector).forEach(function (el) { el.classList.add("is-visible"); });
    $all(".code-line").forEach(function (el) { el.classList.add("is-on"); });
  }
  if (window.__revealFallback) clearTimeout(window.__revealFallback);
  window.__revealFallback = setTimeout(forceRevealAll, 3200);

  function $all(selector, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  // --- Thème clair / sombre (mémorisé dans localStorage) --------------------
  $all("[data-theme-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var isDark = doc.classList.toggle("dark");
      localStorage.setItem("theme", isDark ? "dark" : "light");
    });
  });

  // --- Menu mobile ----------------------------------------------------------
  var menuBtn = document.querySelector("[data-menu-toggle]");
  var menu = document.getElementById("mobile-menu");
  var iconOpen = menuBtn && menuBtn.querySelector("[data-icon-open]");
  var iconClose = menuBtn && menuBtn.querySelector("[data-icon-close]");
  function setMenu(open) {
    if (!menuBtn || !menu) return;
    menu.classList.toggle("hidden", !open);
    menuBtn.setAttribute("aria-expanded", String(open));
    menuBtn.setAttribute("aria-label", open ? (menuBtn.getAttribute("data-label-close") || "Fermer le menu") : (menuBtn.getAttribute("data-label-open") || "Ouvrir le menu"));
    if (iconOpen) iconOpen.classList.toggle("hidden", open);
    if (iconClose) iconClose.classList.toggle("hidden", !open);
    document.body.classList.toggle("nav-open", open);
    var header = document.querySelector("[data-site-header]");
    if (open && header) header.classList.remove("is-hidden");
  }
  if (menuBtn && menu) {
    menuBtn.addEventListener("click", function () {
      setMenu(menu.classList.contains("hidden"));
    });
    $all("a", menu).forEach(function (link) {
      link.addEventListener("click", function () { setMenu(false); });
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth >= 1024) setMenu(false);
    });
  }

  // --- Menus <details> : un seul ouvert, fermeture au clic extérieur / Échap ---
  document.addEventListener("click", function (e) {
    $all("details[data-dropdown][open]").forEach(function (d) {
      if (!d.contains(e.target)) d.removeAttribute("open");
    });
  });
  document.addEventListener("toggle", function (e) {
    var opened = e.target;
    if (!opened.matches || !opened.matches("details[data-dropdown]") || !opened.open) return;
    $all("details[data-dropdown][open]").forEach(function (other) {
      if (other !== opened) other.removeAttribute("open");
    });
  }, true);
  $all("details[data-dropdown] a").forEach(function (link) {
    link.addEventListener("click", function () {
      var parent = link.closest("details");
      if (parent) parent.removeAttribute("open");
    });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    $all("details[data-dropdown][open]").forEach(function (d) { d.removeAttribute("open"); });
    setMenu(false);
  });

  // --- Notifications (messages flash) ---------------------------------------
  $all("[data-flash]").forEach(function (flash) {
    var close = function () {
      flash.style.transition = "opacity .25s, transform .25s";
      flash.style.opacity = "0";
      flash.style.transform = "translateX(16px)";
      setTimeout(function () { flash.remove(); }, 260);
    };
    var btn = flash.querySelector("[data-flash-close]");
    if (btn) btn.addEventListener("click", close);
    setTimeout(close, 7000);
  });

  // --- Révélation au défilement (variants + stagger) -----------------------
  var reveals = $all(revealSelector);
  if (reveals.length) {
    if (!("IntersectionObserver" in window) || reduceMotion) {
      forceRevealAll();
    } else {
      var revealObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            revealObserver.unobserve(entry.target);
          }
        });
      }, { threshold: 0.08, rootMargin: "0px 0px -8% 0px" });
      reveals.forEach(function (el) { revealObserver.observe(el); });
      // Éléments déjà dans le viewport au chargement (hero, etc.)
      requestAnimationFrame(function () {
        reveals.forEach(function (el) {
          var rect = el.getBoundingClientRect();
          if (rect.top < window.innerHeight * 0.92 && rect.bottom > 0) {
            el.classList.add("is-visible");
            revealObserver.unobserve(el);
          }
        });
      });
    }
  }

  // --- Lignes de code du hero : apparition séquentielle ---------------------
  $all("[data-code-animate]").forEach(function (block) {
    var lines = $all(".code-line", block);
    if (!lines.length) return;
    if (reduceMotion) {
      lines.forEach(function (line) { line.classList.add("is-on"); });
      return;
    }
    var start = function () {
      lines.forEach(function (line, i) {
        line.style.setProperty("--line-d", (i * 90) + "ms");
        requestAnimationFrame(function () { line.classList.add("is-on"); });
      });
    };
    if ("IntersectionObserver" in window) {
      var codeObs = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            start();
            codeObs.unobserve(entry.target);
          }
        });
      }, { threshold: 0.25 });
      codeObs.observe(block);
    } else {
      start();
    }
  });

  // --- Boutons magnétiques (léger suivi du curseur) ---------------------------
  if (!reduceMotion && window.matchMedia("(pointer: fine)").matches) {
    $all("[data-magnetic]").forEach(function (btn) {
      btn.addEventListener("pointermove", function (e) {
        var rect = btn.getBoundingClientRect();
        var x = (e.clientX - rect.left - rect.width / 2) * 0.22;
        var y = (e.clientY - rect.top - rect.height / 2) * 0.22;
        btn.style.transform = "translate(" + x.toFixed(1) + "px, " + y.toFixed(1) + "px)";
      });
      btn.addEventListener("pointerleave", function () { btn.style.transform = ""; });
    });
  }

  // --- Parallaxe légère -----------------------------------------------------
  var parallaxEls = $all("[data-parallax]");
  if (parallaxEls.length && !reduceMotion) {
    var onScrollParallax = function () {
      var vh = window.innerHeight;
      parallaxEls.forEach(function (el) {
        var speed = parseFloat(el.getAttribute("data-parallax")) || 0.15;
        var rect = el.getBoundingClientRect();
        var mid = rect.top + rect.height / 2;
        var offset = (mid - vh / 2) * -speed;
        el.style.transform = "translate3d(0, " + offset.toFixed(1) + "px, 0)";
      });
    };
    window.addEventListener("scroll", onScrollParallax, { passive: true });
    onScrollParallax();
  }

  // --- Compteurs animés -------------------------------------------------------
  function animateCount(el) {
    var target = parseInt(el.getAttribute("data-count"), 10);
    if (isNaN(target)) return;
    if (reduceMotion || target === 0) { el.textContent = String(target); return; }
    var duration = 1200;
    var start = null;
    function step(ts) {
      if (start === null) start = ts;
      var progress = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = String(Math.round(target * eased));
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  var counters = $all("[data-count]");
  if (counters.length && "IntersectionObserver" in window) {
    var countObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCount(entry.target);
          countObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) {
      if (!reduceMotion) el.textContent = "0";
      countObserver.observe(el);
    });
  }

  // --- Scroll-spy : la section la plus haute encore au-dessus du repère ------
  var spyLinks = $all("a[data-spy]");
  var seenSpy = {};
  var spySections = [];
  spyLinks.forEach(function (link) {
    var id = link.getAttribute("data-spy");
    if (!id || seenSpy[id]) return;
    var section = document.getElementById(id);
    if (!section) return;
    seenSpy[id] = true;
    spySections.push(section);
  });
  spySections.sort(function (a, b) { return a.offsetTop - b.offsetTop; });
  var sectionLabel = document.querySelector("[data-nav-section]");
  function updateSpy() {
    if (!spySections.length) return;
    var marker = window.innerHeight * 0.34;
    var current = null;
    spySections.forEach(function (section) {
      if (section.getBoundingClientRect().top <= marker) current = section.id;
    });
    spyLinks.forEach(function (link) {
      var spy = link.getAttribute("data-spy");
      var isPage = link.hasAttribute("data-page-current");
      if (current && spy === current) link.setAttribute("aria-current", "true");
      else if (isPage && !current) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
    $all("details.nav-more").forEach(function (menu) {
      menu.classList.toggle("has-active", !!menu.querySelector('a[aria-current]:not([data-spy="accueil"])'));
    });
    if (sectionLabel) {
      var sample = current && document.querySelector('[data-spy="' + current + '"][data-label]');
      sectionLabel.textContent = sample ? sample.getAttribute("data-label") : "";
    }
  }

  // --- Barre de progression + bouton « retour en haut » + navbar intelligente -
  var progress = document.getElementById("scroll-progress");
  var toTop = document.querySelector("[data-back-to-top]");
  var header = document.querySelector("[data-site-header]");
  var lastScrollY = window.pageYOffset || 0;
  var ticking = false;
  function onScroll() {
    var scrollTop = window.pageYOffset || doc.scrollTop;
    var max = doc.scrollHeight - window.innerHeight;
    if (progress) progress.style.transform = "scaleX(" + (max > 0 ? Math.min(scrollTop / max, 1) : 0) + ")";
    if (toTop) {
      var show = scrollTop > 600;
      toTop.classList.toggle("opacity-0", !show);
      toTop.classList.toggle("pointer-events-none", !show);
      toTop.classList.toggle("translate-y-2", !show);
    }
    if (header) {
      var menuOpen = document.body.classList.contains("nav-open");
      var dropdownOpen = document.querySelector("details[data-dropdown][open]");
      var goingDown = scrollTop > lastScrollY + 6;
      var goingUp = scrollTop < lastScrollY - 6;
      header.classList.toggle("is-scrolled", scrollTop > 12);
      if (menuOpen || dropdownOpen || header.matches(":hover") || header.contains(document.activeElement)) {
        header.classList.remove("is-hidden");
      } else if (scrollTop < 80) header.classList.remove("is-hidden");
      else if (goingDown && scrollTop > 280) header.classList.add("is-hidden");
      else if (goingUp) header.classList.remove("is-hidden");
      lastScrollY = scrollTop;
    }
    updateSpy();
    ticking = false;
  }
  window.addEventListener("scroll", function () {
    if (!ticking) { ticking = true; requestAnimationFrame(onScroll); }
  }, { passive: true });
  onScroll();
  if (toTop) {
    toTop.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
    });
  }

  var headerEl = document.querySelector("[data-site-header]");
  if (headerEl) {
    headerEl.addEventListener("mouseenter", function () { headerEl.classList.remove("is-hidden"); });
    headerEl.addEventListener("focusin", function () { headerEl.classList.remove("is-hidden"); });
  }

  var clock = document.querySelector("[data-clock]");
  function tickClock() {
    if (!clock) return;
    var now = new Date();
    clock.dateTime = now.toISOString();
    clock.textContent = now.toLocaleTimeString(document.documentElement.lang || "fr", {
      hour: "2-digit",
      minute: "2-digit"
    });
  }
  tickClock();
  setInterval(tickClock, 30000);

  var hero = document.getElementById("accueil");
  if (hero && !reduceMotion && window.matchMedia("(pointer: fine)").matches) {
    hero.addEventListener("pointermove", function (e) {
      var rect = hero.getBoundingClientRect();
      hero.style.setProperty("--sx", (e.clientX - rect.left) + "px");
      hero.style.setProperty("--sy", (e.clientY - rect.top) + "px");
    });
  }

  // --- Afficher / masquer un mot de passe --------------------------------------
  $all("[data-toggle-password]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var input = btn.parentElement.querySelector("input");
      if (!input) return;
      var show = input.type === "password";
      input.type = show ? "text" : "password";
      btn.setAttribute(
        "aria-label",
        show
          ? (btn.getAttribute("data-label-hide") || "Masquer le mot de passe")
          : (btn.getAttribute("data-label-show") || "Afficher le mot de passe")
      );
      var eye = btn.querySelector("[data-eye]");
      var eyeOff = btn.querySelector("[data-eye-off]");
      if (eye) eye.classList.toggle("hidden", show);
      if (eyeOff) eyeOff.classList.toggle("hidden", !show);
    });
  });

  // --- Anti double-soumission des formulaires ---------------------------------
  $all("form[data-lock]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (form.dataset.submitting) { e.preventDefault(); return; }
      form.dataset.submitting = "1";
    });
  });
  // Retour arrière du navigateur (cache bfcache) : on réactive les formulaires.
  window.addEventListener("pageshow", function (e) {
    if (!e.persisted) return;
    $all("form[data-lock]").forEach(function (form) {
      delete form.dataset.submitting;
      $all('button[type="submit"]', form).forEach(function (b) {
        b.disabled = false;
        b.classList.remove("opacity-60", "cursor-wait");
      });
    });
  });

  // --- Filtres : soumission automatique au changement d'un <select> -----------
  $all("select[data-autosubmit]").forEach(function (select) {
    select.addEventListener("change", function () {
      if (select.form) select.form.requestSubmit();
    });
  });

  // --- Toasts légers (copie e-mail, confirmation…) ------------------------------
  var toastHost = document.getElementById("toast-host");
  function showToast(message) {
    if (!toastHost || !message) return;
    var el = document.createElement("div");
    el.className = "js-toast flex max-w-sm items-center gap-2 rounded-xl border border-emerald-200 bg-white px-4 py-3 text-sm font-medium text-slate-700 shadow-2xl dark:border-emerald-500/30 dark:bg-slate-900 dark:text-slate-200";
    el.setAttribute("role", "status");
    el.textContent = message;
    toastHost.appendChild(el);
    setTimeout(function () {
      el.style.transition = "opacity .25s, transform .25s";
      el.style.opacity = "0";
      el.style.transform = "translateY(8px)";
      setTimeout(function () { el.remove(); }, 260);
    }, 2400);
  }

  function copyText(text, onDone) {
    if (!text) return;
    var done = typeof onDone === "function" ? onDone : function () {};
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done).catch(function () {});
      return;
    }
    var tmp = document.createElement("input");
    tmp.value = text;
    document.body.appendChild(tmp);
    tmp.select();
    try { document.execCommand("copy"); done(); } catch (err) { /* ignoré */ }
    tmp.remove();
  }

  // --- Copier le lien de la page ------------------------------------------------
  $all("[data-copy-link]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var label = btn.querySelector("[data-copy-label]");
      var original = label ? label.textContent : "";
      copyText(window.location.href, function () {
        if (label) label.textContent = label.getAttribute("data-copied") || "Lien copié !";
        showToast(label && label.getAttribute("data-toast") ? label.getAttribute("data-toast") : "Lien copié !");
        setTimeout(function () { if (label) label.textContent = original; }, 2000);
      });
    });
  });

  // --- Copier un texte quelconque (e-mail, etc.) --------------------------------
  $all("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var value = btn.getAttribute("data-copy") || "";
      copyText(value, function () {
        showToast(btn.getAttribute("data-toast") || "Copié !");
      });
    });
  });

  // --- Effet « machine à écrire » : rôles qui défilent dans le hero ---------------
  // Le HTML contient déjà le premier rôle (visible sans JS) ; on l'efface puis on boucle.
  $all("[data-typewriter]").forEach(function (el) {
    var roles = (el.getAttribute("data-typewriter") || "").split("|").filter(Boolean);
    if (roles.length < 2 || reduceMotion) return;
    var index = 0;
    var chars = roles[0].length;
    var deleting = true;
    function tick() {
      var word = roles[index];
      if (deleting) {
        chars--;
        el.textContent = word.slice(0, Math.max(chars, 0));
        if (chars <= 0) {
          deleting = false;
          index = (index + 1) % roles.length;
          return setTimeout(tick, 380);
        }
        return setTimeout(tick, 32);
      }
      chars++;
      el.textContent = roles[index].slice(0, chars);
      if (chars >= roles[index].length) {
        deleting = true;
        return setTimeout(tick, 1900);
      }
      setTimeout(tick, 68);
    }
    setTimeout(tick, 2200);
  });

  // --- Halo lumineux qui suit le curseur sur les cartes ---------------------------
  if (!reduceMotion && window.matchMedia("(pointer: fine)").matches) {
    $all(".card-hover").forEach(function (card) {
      card.addEventListener("pointermove", function (e) {
        var rect = card.getBoundingClientRect();
        card.style.setProperty("--mx", e.clientX - rect.left + "px");
        card.style.setProperty("--my", e.clientY - rect.top + "px");
      });
    });
  }

  // --- Légère inclinaison 3D de la carte du hero au survol -------------------------
  if (!reduceMotion && window.matchMedia("(pointer: fine)").matches) {
    $all("[data-tilt]").forEach(function (el) {
      var zone = el.parentElement;
      zone.addEventListener("pointermove", function (e) {
        var rect = zone.getBoundingClientRect();
        var x = (e.clientX - rect.left) / rect.width - 0.5;
        var y = (e.clientY - rect.top) / rect.height - 0.5;
        el.style.transform = "perspective(1100px) rotateX(" + (-y * 7).toFixed(2) + "deg) rotateY(" + (x * 9).toFixed(2) + "deg)";
      });
      zone.addEventListener("pointerleave", function () { el.style.transform = ""; });
    });
  }

  // --- Palette de commandes (Ctrl/⌘ + K, ou « / ») ---------------------------------
  var palette = document.getElementById("cmdk");
  if (palette && typeof palette.showModal === "function") {
    var input = palette.querySelector("[data-cmdk-input]");
    var options = $all("[data-cmdk-option]", palette);
    var empty = palette.querySelector("[data-cmdk-empty]");
    var activeIndex = 0;

    function visibleOptions() {
      return options.filter(function (o) { return !o.closest("li").hidden; });
    }
    function setActive(index) {
      var list = visibleOptions();
      options.forEach(function (o) { o.setAttribute("aria-selected", "false"); });
      if (!list.length) return;
      activeIndex = (index + list.length) % list.length;
      list[activeIndex].setAttribute("aria-selected", "true");
      list[activeIndex].scrollIntoView({ block: "nearest" });
    }
    function filter() {
      var q = input.value.trim().toLowerCase();
      options.forEach(function (o) {
        var text = (o.textContent + " " + (o.getAttribute("data-keywords") || "")).toLowerCase();
        o.closest("li").hidden = q !== "" && text.indexOf(q) === -1;
      });
      $all("[data-cmdk-group]", palette).forEach(function (group) {
        var any = $all("li", group).some(function (li) { return !li.hidden; });
        group.hidden = !any;
      });
      var count = visibleOptions().length;
      if (empty) empty.hidden = count > 0;
      setActive(0);
    }
    function openPalette() {
      if (palette.open) return;
      input.value = "";
      filter();
      palette.showModal();
      input.focus();
    }
    function run(option) {
      if (!option) return;
      var action = option.getAttribute("data-cmdk-action");
      palette.close();
      if (action === "theme") {
        var isDark = doc.classList.toggle("dark");
        localStorage.setItem("theme", isDark ? "dark" : "light");
      } else if (action === "top") {
        window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
      } else if (option.href) {
        window.location.href = option.href;
      }
    }

    $all("[data-cmdk-open]").forEach(function (btn) { btn.addEventListener("click", openPalette); });
    document.addEventListener("keydown", function (e) {
      var typing = /^(INPUT|TEXTAREA|SELECT)$/.test((e.target.tagName || "")) || e.target.isContentEditable;
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        palette.open ? palette.close() : openPalette();
      } else if (e.key === "/" && !typing && !palette.open) {
        e.preventDefault();
        openPalette();
      }
    });
    input.addEventListener("input", filter);
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { e.preventDefault(); setActive(activeIndex + 1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); setActive(activeIndex - 1); }
      else if (e.key === "Enter") { e.preventDefault(); run(visibleOptions()[activeIndex]); }
    });
    options.forEach(function (option) {
      option.addEventListener("click", function (e) {
        if (option.getAttribute("data-cmdk-action")) e.preventDefault();
        run(option);
      });
      option.addEventListener("mousemove", function () {
        var i = visibleOptions().indexOf(option);
        if (i !== -1 && i !== activeIndex) setActive(i);
      });
    });
    // Un clic sur le fond assombri ferme la palette.
    palette.addEventListener("click", function (e) {
      if (e.target === palette) palette.close();
    });
  }

  // --- Réseau de nœuds animé (fond de la section cybersécurité) ---------------------
  // Purement décoratif. Pause automatique hors écran ; image fixe si « réduire les animations ».
  $all("canvas[data-network]").forEach(function (canvas) {
    var ctx = canvas.getContext("2d");
    if (!ctx) return;
    var section = canvas.closest("section") || canvas.parentElement;
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var width = 0, height = 0, nodes = [], frame = 0, mouse = null;
    var LINK = 130;

    function resize() {
      var rect = canvas.getBoundingClientRect();
      width = rect.width; height = rect.height;
      if (!width || !height) return;
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      var count = Math.max(18, Math.min(72, Math.round((width * height) / 15000)));
      nodes = [];
      for (var i = 0; i < count; i++) {
        nodes.push({
          x: Math.random() * width, y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.35, vy: (Math.random() - 0.5) * 0.35,
          r: 1 + Math.random() * 1.6
        });
      }
    }

    function draw(move) {
      ctx.clearRect(0, 0, width, height);
      var i, j, a, b, dx, dy, d;
      for (i = 0; i < nodes.length; i++) {
        a = nodes[i];
        if (move) {
          a.x += a.vx; a.y += a.vy;
          if (a.x < 0 || a.x > width) a.vx *= -1;
          if (a.y < 0 || a.y > height) a.vy *= -1;
        }
        ctx.beginPath();
        ctx.arc(a.x, a.y, a.r, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(52, 211, 153, 0.85)";
        ctx.fill();
        for (j = i + 1; j < nodes.length; j++) {
          b = nodes[j];
          dx = a.x - b.x; dy = a.y - b.y;
          d = Math.sqrt(dx * dx + dy * dy);
          if (d < LINK) {
            ctx.strokeStyle = "rgba(52, 211, 153, " + ((1 - d / LINK) * 0.32).toFixed(3) + ")";
            ctx.lineWidth = 1;
            ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
          }
        }
        if (mouse) {
          dx = a.x - mouse.x; dy = a.y - mouse.y;
          d = Math.sqrt(dx * dx + dy * dy);
          if (d < 170) {
            ctx.strokeStyle = "rgba(34, 211, 238, " + ((1 - d / 170) * 0.55).toFixed(3) + ")";
            ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(mouse.x, mouse.y); ctx.stroke();
          }
        }
      }
    }

    function loop() { draw(true); frame = requestAnimationFrame(loop); }
    function start() { if (!frame) frame = requestAnimationFrame(loop); }
    function stop() { cancelAnimationFrame(frame); frame = 0; }

    resize();
    var resizeTimer;
    window.addEventListener("resize", function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () { resize(); if (reduceMotion) draw(false); }, 150);
    });

    if (reduceMotion || !("IntersectionObserver" in window)) { draw(false); return; }

    section.addEventListener("pointermove", function (e) {
      var rect = canvas.getBoundingClientRect();
      mouse = { x: e.clientX - rect.left, y: e.clientY - rect.top };
    });
    section.addEventListener("pointerleave", function () { mouse = null; });
    new IntersectionObserver(function (entries) {
      entries[0].isIntersecting ? start() : stop();
    }).observe(section);
  });

  // --- Impression ---------------------------------------------------------------
  $all("[data-print]").forEach(function (btn) {
    btn.addEventListener("click", function () { window.print(); });
  });
  // Lien « ?print=1 » : ouvre directement la boîte de dialogue d'impression / d'enregistrement en PDF.
  if (new URLSearchParams(window.location.search).get("print") === "1" && document.querySelector("[data-print]")) {
    setTimeout(function () { window.print(); }, 800);
  }

  // --- Barres de compétences : remplissage au scroll ----------------------------
  var skillBars = $all("[data-skill-bar]");
  if (skillBars.length) {
    function fillBar(el) {
      var value = parseFloat(el.getAttribute("data-skill-bar"));
      if (isNaN(value)) return;
      el.style.setProperty("--skill", value + "%");
      el.classList.add("is-filled");
    }
    if (reduceMotion || !("IntersectionObserver" in window)) {
      skillBars.forEach(fillBar);
    } else {
      var skillObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          fillBar(entry.target);
          skillObserver.unobserve(entry.target);
        });
      }, { threshold: 0.35 });
      skillBars.forEach(function (el) { skillObserver.observe(el); });
    }
  }

  // --- Images : fondu quand elles sont chargées ---------------------------------
  $all("img.img-fade").forEach(function (img) {
    function mark() { img.classList.add("is-loaded"); }
    if (img.complete && img.naturalWidth) mark();
    else {
      img.addEventListener("load", mark);
      img.addEventListener("error", mark);
    }
  });

  // --- Lightbox pour les captures de projets / covers ---------------------------
  var lightbox = document.getElementById("lightbox");
  var lightboxImg = lightbox ? lightbox.querySelector("[data-lightbox-img]") : null;
  if (lightbox && lightboxImg && typeof lightbox.showModal === "function") {
    $all("[data-lightbox]").forEach(function (trigger) {
      trigger.addEventListener("click", function () {
        var src = trigger.getAttribute("data-lightbox");
        if (!src) return;
        lightboxImg.src = src;
        lightboxImg.alt = trigger.getAttribute("data-lightbox-alt") || "";
        lightbox.showModal();
      });
    });
    lightbox.addEventListener("click", function (e) {
      if (e.target === lightbox) lightbox.close();
    });
    lightbox.addEventListener("close", function () {
      lightboxImg.removeAttribute("src");
      lightboxImg.alt = "";
    });
  }

  // --- Flash d'ancre (arrivée sur #section) -------------------------------------
  function flashAnchor(id) {
    if (!id) return;
    var target = document.getElementById(id);
    if (!target) return;
    target.classList.remove("anchor-flash");
    // Force un reflow pour relancer l'animation si on reclique la même ancre.
    void target.offsetWidth;
    target.classList.add("anchor-flash");
    setTimeout(function () { target.classList.remove("anchor-flash"); }, 1000);
  }
  if (window.location.hash) {
    setTimeout(function () { flashAnchor(window.location.hash.slice(1)); }, 120);
  }
  window.addEventListener("hashchange", function () {
    flashAnchor((window.location.hash || "").slice(1));
  });

  // --- Sommaire d'article (h2 / h3) ---------------------------------------------
  var articleBody = document.querySelector("[data-article-body]");
  var tocBlocks = $all("[data-toc]");
  if (articleBody && tocBlocks.length) {
    var headings = $all("h2, h3", articleBody);
    if (headings.length >= 2) {
      function slugify(text, index) {
        var base = text.toLowerCase()
          .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
          .replace(/[^a-z0-9]+/g, "-")
          .replace(/(^-|-$)/g, "");
        return base || ("section-" + (index + 1));
      }
      var used = {};
      headings.forEach(function (heading, index) {
        if (!heading.id) {
          var id = slugify(heading.textContent || "", index);
          if (used[id]) id = id + "-" + (index + 1);
          used[id] = true;
          heading.id = id;
        }
        heading.style.scrollMarginTop = "6rem";
      });
      tocBlocks.forEach(function (nav) {
        var list = nav.querySelector("[data-toc-list]");
        if (!list) return;
        list.innerHTML = "";
        headings.forEach(function (heading) {
          var li = document.createElement("li");
          if (heading.tagName === "H3") li.style.paddingLeft = "0.85rem";
          var a = document.createElement("a");
          a.href = "#" + heading.id;
          a.textContent = heading.textContent;
          a.setAttribute("data-toc-link", heading.id);
          li.appendChild(a);
          list.appendChild(li);
        });
        nav.hidden = false;
      });
      if ("IntersectionObserver" in window) {
        var tocLinks = $all("[data-toc-link]");
        var tocObserver = new IntersectionObserver(function (entries) {
          entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            tocLinks.forEach(function (link) {
              var active = link.getAttribute("data-toc-link") === entry.target.id;
              if (active) link.setAttribute("aria-current", "true");
              else link.removeAttribute("aria-current");
            });
          });
        }, { rootMargin: "-20% 0px -65% 0px", threshold: 0 });
        headings.forEach(function (heading) { tocObserver.observe(heading); });
      }
    }
  }
})();
