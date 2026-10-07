/* =====================================================================
   ESTUDIO PANA — interacción
   1) Escala el lienzo 1920x1080 para llenar la ventana
   2) Transición inicio -> servicios manejada por el scroll
   3) Morph por letra: Peridot -> PP Editorial Italic al pasar el cursor
   ===================================================================== */
(function () {
  "use strict";

  var stage    = document.getElementById("stage");
  var logo     = document.getElementById("logo");
  var cometLayers = Array.prototype.slice.call(document.querySelectorAll(".comet-layer"));
  var clOvals = Array.prototype.slice.call(document.querySelectorAll(".cl-oval"));
  var clWords = Array.prototype.slice.call(document.querySelectorAll(".cl-word"));
  var estudio  = document.getElementById("estudio");
  var creativo = document.getElementById("creativo");
  var screenEl = document.getElementById("screen");
  var svcTrack = document.getElementById("svcTrack");
  var projTrack= document.getElementById("projTrack");
  var contactTrack = document.getElementById("contactTrack");
  var ourwork  = document.getElementById("ourwork");
  var footnav  = document.getElementById("footnav");
  var projects = document.getElementById("projects");
  var credits  = document.getElementById("credits");
  var SCREEN_H = 460;                 // alto de la máscara (coincide con styles.css)

  var detail        = document.getElementById("detail");
  var detailMedia   = document.getElementById("detailMedia");
  var detailTitle   = document.getElementById("detailTitle");
  var detailClose   = document.getElementById("detailClose");
  var detailOpen    = false;
  var MEDIA = window.PROJECT_MEDIA || {};

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- utilidades ---------- */
  function clamp(v, a, b){ return v < a ? a : (v > b ? b : v); }
  function lerp(a, b, t){ return a + (b - a) * t; }
  function smoothstep(e0, e1, x){
    var t = clamp((x - e0) / (e1 - e0), 0, 1);
    return t * t * (3 - 2 * t);
  }

  /* ---------- 1) escala del lienzo ---------- */
  function fit(){
    var k = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
    stage.style.setProperty("--k", k);
  }

  /* ---------- 3) morph por letra (flip 3D principal <-> secundaria) ---------- */
  function splitLetters(el){
    var text = el.getAttribute("data-text") || el.textContent;
    el.textContent = "";
    el.classList.add("split");
    for (var i = 0; i < text.length; i++){
      var ch = text[i];
      if (ch === " "){
        var sp = document.createElement("span");
        sp.className = "ltr space";
        sp.innerHTML = "&nbsp;";
        el.appendChild(sp);
        continue;
      }
      var ltr   = document.createElement("span"); ltr.className = "ltr";
      var inner = document.createElement("span"); inner.className = "ltr__inner";
      var front = document.createElement("span"); front.className = "face front"; front.textContent = ch;
      var back  = document.createElement("span"); back.className  = "face back";  back.textContent  = ch.toLowerCase();
      inner.appendChild(front);
      inner.appendChild(back);
      ltr.appendChild(inner);
      el.appendChild(ltr);
    }
  }

  var morphEls = Array.prototype.slice.call(document.querySelectorAll(".morph"));
  morphEls.forEach(splitLetters);

  // hover por letra POR DELEGACIÓN -> funciona con letras dinámicas (proyectos)
  document.addEventListener("mouseover", function (e){
    var l = e.target.closest ? e.target.closest(".ltr:not(.space)") : null;
    if (l) l.classList.add("on");
  });
  document.addEventListener("mouseout", function (e){
    var l = e.target.closest ? e.target.closest(".ltr:not(.space)") : null;
    if (!l) return;
    var to = e.relatedTarget && e.relatedTarget.closest ? e.relatedTarget.closest(".ltr:not(.space)") : null;
    if (to !== l) l.classList.remove("on");
  });

  // ?hoverdemo=1 -> fuerza el flip en letras alternadas (para previsualizar/capturar)
  if (/[?&]hoverdemo=1/.test(location.search)){
    document.querySelectorAll(".ltr:not(.space)").forEach(function (l, i){
      if (i % 2 === 0) l.classList.add("on");
    });
  }

  // fija el ancho de cada letra (con la fuente Peridot) para que el cambio
  // a itálica NO empuje a las vecinas -> hover estable, sin saltos.
  function lockWidths(){
    document.querySelectorAll(".ltr:not(.space)").forEach(function (s){
      if (s.closest(".detail")) return;     // el detalle no está en el lienzo escalado
      var w = s.getBoundingClientRect().width;
      // el ancho se mide ya escalado por --k; lo normalizamos
      var k = parseFloat(getComputedStyle(stage).getPropertyValue("--k")) || 1;
      s.style.width = (w / k) + "px";
      s.style.textAlign = "center";
    });
  }
  // lock para textos morph FUERA del lienzo (detalle): fija cada letra al ancho
  // de su cara PRINCIPAL (Peridot), así la itálica no agranda la celda -> sin huecos.
  function lockPlainWidths(root){
    Array.prototype.forEach.call(root.querySelectorAll(".ltr:not(.space)"), function (s){
      var front = s.querySelector(".face.front");
      if (!front) return;
      s.style.width = front.getBoundingClientRect().width + "px";
      s.style.textAlign = "center";
    });
  }

  /* ---------- 2) navegación por SECCIONES (transición fluida) ----------
     Secciones: 0 = inicio · 1 = servicios · 2 = proyectos.
     Un gesto de scroll = avanzar/retroceder una sección; curP persigue al
     objetivo con easing suave -> transición elegante (no escalonada).
     ?p=0..2 fuerza un estado continuo (para previsualizar/capturar). */
  var SECTIONS = 4;                   // 0 inicio · 1 servicios · 2 proyectos · 3 contacto
  var targetSec = 0;
  var curP = 0;
  var forcedP = (function(){
    var m = /[?&]p=([0-9.]+)/.exec(location.search);
    return m ? clamp(parseFloat(m[1]), 0, SECTIONS - 1) : null;
  })();
  if (forcedP !== null){ curP = forcedP; targetSec = Math.round(forcedP); }

  // aplica el estado visual para un valor continuo p (0..2)
  function applyState(p){
    var t01 = clamp(p, 0, 1);          // inicio -> servicios
    var t12 = clamp(p - 1, 0, 1);      // servicios -> proyectos
    var t23 = clamp(p - 2, 0, 1);      // proyectos -> contacto
    var e01 = smoothstep(0, 1, t01);
    var e12 = smoothstep(0, 1, t12);
    var e23 = smoothstep(0, 1, t23);

    // logo: viaja de (centro,540,escala1) a (arriba,210,escala.62) en 0->1.
    // cometLoop suaviza --lcy y deja la cola; acá sólo fijamos el destino.
    targetY = lerp(540, 210, e01);
    logo.style.setProperty("--ls", lerp(1, 0.62, e01));

    // inicio (estudio / creativo) se desvanece
    var inicio = 1 - smoothstep(0, 0.55, t01);
    estudio.style.opacity = inicio;
    creativo.style.opacity = inicio;
    var iOn = inicio > 0.5 ? "auto" : "none";
    estudio.style.pointerEvents = iOn;
    creativo.style.pointerEvents = iOn;

    // SERVICIOS: sube desde abajo (0->1) y sale por arriba (1->2). SIN opacidad.
    var svcY = (p <= 1) ? lerp(SCREEN_H, 0, e01) : lerp(0, -SCREEN_H, e12);
    svcTrack.style.transform = "translateY(" + svcY + "px)";

    // PROYECTOS (créditos): suben (1->2) y salen hacia arriba (2->3).
    // La lista es más alta que la máscara -> al salir se desvanece (si no, loopea).
    var projY = (p <= 2) ? lerp(SCREEN_H, 0, e12) : lerp(0, -SCREEN_H, e23);
    projTrack.style.transform = "translateY(" + projY + "px)";
    projTrack.style.opacity = 1 - e23;

    // CONTACTO: sube desde abajo (2->3). SIN opacidad.
    if (contactTrack) contactTrack.style.transform = "translateY(" + lerp(SCREEN_H, 0, e23) + "px)";

    // nav "our work / contact": NO aparece en el inicio; entra recién en servicios
    if (footnav){
      var fnv = smoothstep(0.5, 1, t01);
      footnav.style.opacity = fnv;
      footnav.style.pointerEvents = fnv > 0.5 ? "auto" : "none";
    }

    // overlay de proyectos (miniatura): visible en proyectos, se va hacia contacto.
    // NO captura eventos, para que el hover llegue a los créditos de abajo.
    projects.style.opacity = e12 * (1 - e23);
    projects.style.pointerEvents = "none";
    projects.setAttribute("aria-hidden", (e12 > 0.5 && e23 < 0.5) ? "false" : "true");
    screenEl.setAttribute("aria-hidden", t01 > 0.5 ? "false" : "true");
  }

  // avanzar/retroceder de sección (con bloqueo para que 1 gesto = 1 paso)
  var navLock = 0;
  function go(dir){
    var now = (window.performance ? performance.now() : Date.now());
    if (now < navLock) return;
    var nt = clamp(targetSec + dir, 0, SECTIONS - 1);
    if (nt !== targetSec){
      targetSec = nt;
      lastScrollT = now;               // avisa al cometa que hay movimiento
      navLock = now + 620;             // ignora más input durante la transición
    }
  }

  // loop de navegación: curP persigue a targetSec con easing (elegante)
  function navLoop(){
    if (forcedP !== null){
      curP = forcedP;
    } else {
      curP += (targetSec - curP) * 0.075;
      if (Math.abs(targetSec - curP) < 0.0005) curP = targetSec;
      else lastScrollT = (window.performance ? performance.now() : Date.now()); // en transición
    }
    applyState(curP);
    requestAnimationFrame(navLoop);
  }
  requestAnimationFrame(navLoop);

  /* ---------- entrada: rueda / teclado / touch ---------- */
  window.addEventListener("wheel", function (e){
    if (detailOpen) return;                 // el detalle usa su propio scroll nativo
    e.preventDefault();
    if (Math.abs(e.deltaY) < 2) return;

    // en PROYECTOS (sección 2): la rueda hace SCROLL INTERNO de la lista.
    // Arriba del todo, un scroll hacia arriba vuelve a servicios.
    if (targetSec === 2 && curP > 1.6 && curP < 2.4){
      var now = (window.performance ? performance.now() : Date.now());
      userScrollT = now;
      var d = e.deltaY * 0.5;
      if (d < 0){                              // hacia arriba
        if (coff <= 0.5){ go(-1); return; }    // ya en el tope -> volver a servicios
        coff = Math.max(0, coff + d);
      } else {                                 // hacia abajo (circular)
        coff += d;
        if (setH) coff = coff % setH;
      }
      return;
    }

    go(e.deltaY > 0 ? 1 : -1);
  }, { passive: false });

  window.addEventListener("keydown", function (e){
    if (detailOpen){ if (e.key === "Escape") closeDetail(); return; }
    if (e.key === "ArrowDown" || e.key === "PageDown" || e.key === " "){ e.preventDefault(); go(1); }
    else if (e.key === "ArrowUp" || e.key === "PageUp"){ e.preventDefault(); go(-1); }
    else if (e.key === "Home"){ e.preventDefault(); targetSec = 0; }
    else if (e.key === "End"){ e.preventDefault(); targetSec = SECTIONS - 1; }
  });

  var touchY0 = null;
  window.addEventListener("touchstart", function (e){ touchY0 = e.touches[0].clientY; }, { passive: true });
  window.addEventListener("touchend", function (e){
    if (detailOpen || touchY0 == null) return;
    var dy = touchY0 - e.changedTouches[0].clientY;
    if (Math.abs(dy) > 40) go(dy > 0 ? 1 : -1);
    touchY0 = null;
  }, { passive: true });

  /* ---------- efecto COMETA (reemplaza el giro del óvalo) ----------
     - El logo viaja en Y según el scroll (targetY). curY lo persigue con easing.
     - Historial de curY: cada capa muestra una posición anterior -> al subir con
       el scroll, las capas viejas quedan ATRÁS (abajo) = cola de cometa. En reposo
       el historial converge y las capas se juntan (logo sólido).
     - En REPOSO, además, el ÓVALO oscila suave (con estela por el desfase de cada
       capa); la PALABRA queda FIJA. Al scrollear, la oscilación se apaga y óvalo +
       palabra viajan juntos. */
  var targetY = 540, curY = 540;
  var lastScrollT = -1e9;
  var histY = [];
  var idleF = 1;                              // 1 = quieto, 0 = moviéndose
  var N = cometLayers.length;
  // por capa (0 = cola más tenue ... N-1 = cabeza): retardo en frames y opacidad
  var LAG     = [30, 22, 15,  9,  4,  0];
  var OPACITY = [0.08, 0.16, 0.28, 0.46, 0.68, 1];
  var MAXH = 46;
  // giro 3D del óvalo (estela), sumado al efecto cometa. Lo maneja el scroll:
  // cada transición de sección = 360°, y en proyectos suma con el scroll interno.
  var curAngle = 0, histA = [];
  for (var a0 = 0; a0 < 90; a0++) histA.push(0);

  for (var i0 = 0; i0 < 46; i0++) histY.push(curY);   // precarga historial
  cometLayers.forEach(function (el, j){
    el.style.opacity = OPACITY[j] != null ? OPACITY[j] : 1;
  });

  function cometLoop(){
    var now = (window.performance ? performance.now() : Date.now());

    curY += (targetY - curY) * 0.18;                  // easing del viaje
    logo.style.setProperty("--lcy", curY + "px");
    histY.push(curY);
    if (histY.length > MAXH) histY.shift();

    // reposo si casi no hay movimiento y no scrolleó hace poco
    var moving = Math.abs(targetY - curY) > 0.4 || (now - lastScrollT < 160);
    idleF += ((moving ? 0 : 1) - idleF) * 0.08;       // transición suave
    var bobAmp = 5 * idleF;                            // amplitud de oscilación del óvalo

    // ángulo de giro: 360°/sección + scroll interno de proyectos. En reposo
    // vuelve al múltiplo de 360 más cercano (óvalo enmarcando "pana").
    var spinTarget = curP * 360 + coff * 0.6;
    var aTarget = (now - lastScrollT > 160) ? Math.round(curAngle / 360) * 360 : spinTarget;
    curAngle += (aTarget - curAngle) * 0.12;
    histA.push(curAngle); if (histA.length > 90) histA.shift();

    for (var j = 0; j < N; j++){
      var lag = LAG[j] != null ? LAG[j] : 0;
      var idx = histY.length - 1 - lag;
      var oldY = idx >= 0 ? histY[idx] : histY[0];
      var off  = oldY - curY;                          // cola: capas viejas quedan atrás
      cometLayers[j].style.transform = "translateY(" + off + "px)";

      // óvalo: oscila en reposo (estela) + GIRA en 3D (estela) al scrollear. Palabra: fija.
      var bob = bobAmp * Math.sin((now - lag * 16) / 500);
      var ai  = histA.length - 1 - lag;
      var ang = ai >= 0 ? histA[ai] : histA[0];
      clOvals[j].style.transform = "translateY(" + bob + "px) rotateY(" + ang + "deg)";
    }
    requestAnimationFrame(cometLoop);
  }
  requestAnimationFrame(cometLoop);

  /* ---------- proyectos: créditos en loop ---------- */
  // proyectos importados de Behance (brunopalmisciano): nombre + portada + URL.
  var PREV_DIR = "https://pana-estudio-creativo.netlify.app/assets/previews/behance/";
  var BE = "https://www.behance.net/gallery/";
  var PROJECTS = [
    { n:"PESQUERA CO",      img:"pesquera-co.png",      url:BE + "247209451/PESQUERA-CO" },
    { n:"LOGOFOLIO V.2",    img:"logofolio-v2.jpg",     url:BE + "247207229/LOGOFOLIO-V2" },
    { n:"LOGOFOLIO V.1",    img:"logofolio-v1.jpg",     url:BE + "247207111/LOGOFOLIO-V1" },
    { n:"CANTINA BERNARDO", img:"cantina-bernardo.png", url:BE + "237220743/CANTINA-BERNARDO" },
    { n:"FURIAS",           img:"furias.png",           url:BE + "247199731/FURIAS-WAREHOUSE" },
    { n:"RAZA ARGENTINA",   img:"raza-argentina.jpg",   url:BE + "236751421/Raza-Argentina" },
    { n:"BODEGON CO",       img:"bodegon-co.gif",       url:BE + "236718073/BODEGON-CO-Restaurant-Branding" },
    { n:"VIALMAQ",          img:"vialmaq.jpg",          url:BE + "229347939/VIALMAQ" },
    { n:"PLANTA BAJA",      img:"planta-baja.jpg",      url:BE + "182014105/Planta-Baja" }
  ];
  // el nombre va en un <span> ajustado al texto -> el hover (miniatura) sólo se
  // dispara sobre las LETRAS; el click abre la galería de Behance.
  function projHTML(p){
    var slug = p.img.replace(/\.[^.]+$/, "");   // "bodegon-co.gif" -> "bodegon-co"
    return '<div class="proj"><span class="proj__t" data-gif="' + p.img +
           '" data-name="' + p.n + '" data-url="' + p.url +
           '" data-slug="' + slug + '">' + p.n + '</span></div>';
  }
  if (credits){
    var setHTML = PROJECTS.map(projHTML).join("");
    credits.innerHTML = setHTML + setHTML;   // dos copias -> loop sin costura
    // efecto morph también en los nombres de proyecto (Peridot -> Editorial ital.)
    Array.prototype.forEach.call(credits.querySelectorAll(".proj__t"), splitLetters);
  }
  var setH = 0, coff = 0, cspeed = 0.55, creditsPaused = false, userScrollT = -1e9;
  function measureCredits(){ if (credits) setH = credits.scrollHeight / 2; }
  function creditsLoop(){
    // sólo corre cuando entramos a proyectos; fuera de ahí, coff=0 -> el track
    // queda trasladado por debajo de la máscara y NO se filtra en inicio/servicios.
    var active = curP > 1.35 && curP < 2.6;
    if (active){
      var now = (window.performance ? performance.now() : Date.now());
      // auto-roll suave, salvo que el cursor esté sobre una palabra o que el
      // usuario haya scrolleado la lista hace poco (scroll interno manual).
      if (setH && !creditsPaused && (now - userScrollT > 1400)){
        coff += cspeed;
        if (coff >= setH) coff -= setH;   // loop
      }
      credits.style.transform = "translateY(" + (-coff) + "px)";
    } else if (coff !== 0){
      coff = 0;
      credits.style.transform = "translateY(0)";
    }
    requestAnimationFrame(creditsLoop);
  }
  requestAnimationFrame(creditsLoop);

  /* ---------- HOVER del título: miniatura (gif) FLOTANTE encima de la lista ----
     Al pasar el cursor por un nombre: se PAUSA el loop y aparece el recuadro
     flotante (fade+scale) con el gif del proyecto, centrado sobre la lista.
     Al salir de la lista, se oculta y se retoma el scroll. */
  var hoverclip = document.getElementById("hoverclip");
  var hoverImg  = document.getElementById("hoverclip-img");
  var hoverVid  = document.getElementById("hoverclip-vid");
  var clipShown = false;
  var CLIP_OFF = 12;                 // separación del cursor (px de lienzo)
  var clipTimer = null, clipList = [], clipIdx = 0;
  var CLIP_MS = 300;                 // cada diapositiva dura 0.3s

  // posiciona la esquina sup-izq de la miniatura en el cursor. Convierte el
  // punto del viewport a coords del lienzo 1920x1080 (que está centrado y
  // escalado por --k).
  function placeClip(vx, vy){
    var k = parseFloat(getComputedStyle(stage).getPropertyValue("--k")) || 1;
    var sx = 960 + (vx - window.innerWidth  / 2) / k;
    var sy = 540 + (vy - window.innerHeight / 2) / k;
    hoverclip.style.left = (sx + CLIP_OFF) + "px";
    hoverclip.style.top  = (sy + CLIP_OFF) + "px";
  }
  // muestra una diapositiva (imagen o video) en el recuadro
  function renderClipItem(src){
    if (/\.mp4$/i.test(src)){
      hoverImg.style.display = "none";
      hoverVid.style.display = "block";
      if (hoverVid.getAttribute("src") !== src){ hoverVid.src = src; }
      var pr = hoverVid.play(); if (pr && pr.catch) pr.catch(function (){});
    } else {
      hoverVid.pause();
      hoverVid.style.display = "none";
      hoverImg.style.display = "block";
      hoverImg.src = src;
    }
  }
  function showClip(el, vx, vy){
    // arma el pase de diapositivas con los slides del proyecto
    var slug = el.getAttribute("data-slug");
    var list = (MEDIA[slug] || []).slice();
    if (!list.length) list = [PREV_DIR + el.getAttribute("data-gif")];   // fallback portada
    else list.forEach(function (s){ if (!/\.mp4$/i.test(s)){ var im = new Image(); im.src = s; } }); // precarga
    clipList = list; clipIdx = 0;
    renderClipItem(clipList[0]);
    clearInterval(clipTimer);
    if (clipList.length > 1){
      clipTimer = setInterval(function (){
        clipIdx = (clipIdx + 1) % clipList.length;
        renderClipItem(clipList[clipIdx]);
      }, CLIP_MS);
    }
    if (vx == null){ var r = el.getBoundingClientRect(); vx = r.left; vy = r.top; }
    placeClip(vx, vy);
    hoverclip.classList.add("show");
    hoverclip.setAttribute("aria-hidden", "false");
    clipShown = true;
    creditsPaused = true;
  }
  function hideClip(){
    clearInterval(clipTimer); clipTimer = null;
    hoverVid.pause();
    hoverclip.classList.remove("show");
    hoverclip.setAttribute("aria-hidden", "true");
    clipShown = false;
    creditsPaused = false;
  }
  function closestWord(node){
    while (node && node !== credits){
      if (node.classList && node.classList.contains("proj__t")) return node;
      node = node.parentNode;
    }
    return null;
  }
  if (credits){
    // hover SOBRE LA PALABRA (span ajustado al texto)
    credits.addEventListener("mouseover", function (e){
      var el = closestWord(e.target);
      if (el) showClip(el, e.clientX, e.clientY);
    });
    // la miniatura sigue al cursor mientras está sobre la palabra
    credits.addEventListener("mousemove", function (e){
      if (clipShown) placeClip(e.clientX, e.clientY);
    });
    // se cierra apenas el cursor sale de la palabra (aunque siga en la sección)
    credits.addEventListener("mouseout", function (e){
      var from = closestWord(e.target);
      if (!from) return;
      var to = closestWord(e.relatedTarget);
      if (!to) hideClip();        // si pasó directo a otra palabra, su mouseover la muestra
    });
    // click en el nombre -> abre la vista de detalle DENTRO de la página
    credits.addEventListener("click", function (e){
      var el = closestWord(e.target);
      if (el) openDetail(el.getAttribute("data-slug"), el.getAttribute("data-name"), el.getAttribute("data-url"));
    });
  }

  /* ---------- vista de detalle de proyecto (in-page) ---------- */
  function openDetail(slug, name, url){
    var list = MEDIA[slug] || [];
    var html = "";
    for (var i = 0; i < list.length; i++){
      var f = list[i];
      if (/\.mp4$/i.test(f)){
        html += '<video src="' + f + '" autoplay loop muted playsinline preload="metadata"></video>';
      } else {
        html += '<img src="' + f + '" alt="" loading="lazy">';
      }
    }
    detailMedia.innerHTML = html;
    // título con efecto morph (principal -> secundaria itálica)
    detailTitle.setAttribute("data-text", name || "");
    detailTitle.textContent = name || "";
    splitLetters(detailTitle);
    detail.scrollTop = 0;
    detail.classList.add("open");
    detail.setAttribute("aria-hidden", "false");
    detailOpen = true;
    lockPlainWidths(detail);       // título + "volver": ajusta el ancho de las letras
    hideClip();
  }
  function closeDetail(){
    detail.classList.remove("open");
    detail.setAttribute("aria-hidden", "true");
    detailOpen = false;
    setTimeout(function (){ if (!detailOpen) detailMedia.innerHTML = ""; }, 420);  // frena videos
  }
  if (detailClose) detailClose.addEventListener("click", closeDetail);
  // clic en el logo del detalle -> cierra el proyecto y vuelve al inicio
  var detailLogo = document.getElementById("detailLogo");
  if (detailLogo) detailLogo.addEventListener("click", function (){ closeDetail(); targetSec = 0; });

  /* ---------- logo del detalle: el óvalo GIRA (estela 3D) al scrollear ----------
     Mismo efecto que tenía el logo antes: cada pantalla scrolleada = 360°, con
     estela (cada capa muestra un ángulo anterior) y, al frenar, vuelve al óvalo
     que enmarca "pana" (múltiplo de 360 más cercano). La palabra queda fija. */
  var dlLayers = detail ? Array.prototype.slice.call(detail.querySelectorAll(".dl-layer")) : [];
  var dlOvals  = detail ? Array.prototype.slice.call(detail.querySelectorAll(".dl-oval")) : [];
  // SIN estela: sólo la cabeza + 2 ecos muy tenues y cortos (fade cometa mínimo).
  var DL_LAG = [0, 0, 0, 4, 2, 0];
  var DL_OP  = [0, 0, 0, 0.10, 0.22, 1];
  var dlHistA = []; for (var d0 = 0; d0 < 20; d0++) dlHistA.push(0);
  var dlAngle = 0, dlPrevSp = 0, dlLastScroll = -1e9;
  dlLayers.forEach(function (el, j){ el.style.opacity = DL_OP[j] != null ? DL_OP[j] : 1; });
  function detailComet(){
    var now = (window.performance ? performance.now() : Date.now());
    if (detailOpen && dlOvals.length){
      var sp = detail.scrollTop;
      var ch = detail.clientHeight || window.innerHeight || 1000;
      if (Math.abs(sp - dlPrevSp) > 0.5){ dlLastScroll = now; dlPrevSp = sp; }
      var idle = now - dlLastScroll > 140;
      // sólo GIRA el óvalo (rotateY) al scrollear; en reposo vuelve al óvalo inicial
      var aTarget = idle ? Math.round(dlAngle / 360) * 360 : (sp / ch) * 360;
      dlAngle += (aTarget - dlAngle) * 0.12;
      dlHistA.push(dlAngle); if (dlHistA.length > 20) dlHistA.shift();
      for (var j = 0; j < dlOvals.length; j++){
        var aIdx = dlHistA.length - 1 - DL_LAG[j];
        var ang = aIdx >= 0 ? dlHistA[aIdx] : dlHistA[0];
        dlOvals[j].style.transform = "rotateY(" + ang + "deg)";   // fade cometa mínimo
      }
    }
    requestAnimationFrame(detailComet);
  }
  requestAnimationFrame(detailComet);

  // ?detail=<slug> -> abre el detalle al cargar (previsualizar/capturar)
  var mDet = /[?&]detail=([a-z0-9-]+)/.exec(location.search);
  if (mDet){
    var pj = PROJECTS.filter(function (p){ return p.img.replace(/\.[^.]+$/, "") === mDet[1]; })[0];
    if (pj) openDetail(mDet[1], pj.n, pj.url);
  }

  // ?openproj=N / ?hoverproj=N -> fuerza la miniatura del proyecto N (para capturar)
  var mHov = /[?&](?:open|hover)proj=([0-9]+)/.exec(location.search);
  if (mHov && credits){
    var hIdx = parseInt(mHov[1], 10) || 0;
    var hEl  = credits.querySelectorAll(".proj__t")[hIdx];
    if (hEl) showClip(hEl);
  }

  // clic en "our work" -> transiciona a proyectos (sección 2)
  if (ourwork){
    ourwork.addEventListener("click", function (){ targetSec = 2; });
  }
  // clic en "contact" -> transiciona a la sección de contacto (sección 3)
  var contact = document.getElementById("contact");
  if (contact){
    contact.addEventListener("click", function (){ targetSec = 3; });
  }

  // clic en el LOGO: en el inicio baja a servicios; en cualquier otra sección vuelve al inicio
  if (logo){
    logo.addEventListener("click", function (){ targetSec = (curP < 0.5) ? 1 : 0; });
  }

  /* ---------- formulario de consulta (Netlify Forms, envío AJAX) ---------- */
  var contactForm = document.getElementById("contactForm");
  var cfOk = document.getElementById("cfOk");
  if (contactForm){
    contactForm.addEventListener("submit", function (e){
      e.preventDefault();
      var data = new URLSearchParams(new FormData(contactForm)).toString();
      fetch("/", { method:"POST", headers:{ "Content-Type":"application/x-www-form-urlencoded" }, body:data })
        .then(function (){ contactForm.reset(); if (cfOk) cfOk.style.display = "block"; })
        .catch(function (){ if (cfOk){ cfOk.textContent = "no se pudo enviar, escribinos a panaestudiocreativo@gmail.com"; cfOk.style.display = "block"; } });
    });
  }

  /* ---------- arranque ---------- */
  fit();
  applyState(curP);
  measureCredits();
  window.addEventListener("resize", function (){ fit(); applyState(curP); measureCredits(); });

  // medir anchos/altura una vez cargadas las fuentes reales
  if (document.fonts && document.fonts.ready){
    document.fonts.ready.then(function (){ fit(); lockWidths(); measureCredits(); });
  } else {
    window.addEventListener("load", function (){ fit(); lockWidths(); measureCredits(); });
  }
})();
