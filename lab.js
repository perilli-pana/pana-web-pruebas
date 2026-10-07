(function(){
  var RED="#f50000", NAVY="#0a2a66", BLUE="#1530e6", CREAM="#f4f0e6";
  var P=[
    {n:"Original (Bruno)",          bg:"#000000", text:RED,  oval:RED,  word:RED},
    {n:"Blanco + rojo",             bg:"#ffffff", text:RED,  oval:RED,  word:RED},
    {n:"Americano: texto azul marino", bg:"#ffffff", text:NAVY, oval:RED, word:NAVY, alt:RED, sep:RED},
    {n:"Americano: texto rojo, logo azul", bg:"#ffffff", text:RED, oval:BLUE, word:BLUE, alt:BLUE, sep:BLUE},
    {n:"Racing: azul eléctrico",    bg:"#ffffff", text:BLUE, oval:RED,  word:BLUE, alt:RED, sep:RED, trail:RED},
    {n:"Bandera: filas alternadas", bg:"#ffffff", text:NAVY, oval:RED,  word:NAVY, alt:RED, sep:RED, rows:true},
    {n:"Crema vintage",             bg:CREAM,     text:NAVY, oval:RED,  word:NAVY, alt:RED, sep:RED},
    {n:"Fondo azul, texto blanco",  bg:NAVY,      text:"#ffffff", oval:RED, word:"#ffffff", alt:RED, sep:RED, trail:RED}
  ];
  var root=document.documentElement, cur={};
  function apply(p,i){
    cur=Object.assign({alt:p.text,sep:p.text,trail:p.text},p);
    root.style.setProperty("--bg",cur.bg); root.style.setProperty("--red",cur.text);
    ["oval","word","alt","sep","trail"].forEach(function(k){ root.style.setProperty("--"+k,cur[k]); });
    document.body.classList.toggle("alt-rows",!!cur.rows);
    btns.forEach(function(b,j){ b.classList.toggle("on",j===i); });
    ["bg","text","oval","word"].forEach(function(k){ inputs[k].value=cur[k]; });
    hex.textContent="fondo "+cur.bg+" · texto "+cur.text+" · óvalo "+cur.oval+" · pana "+cur.word;
    if(i>=0) try{ history.replaceState(null,"","#"+(i+1)); }catch(e){}
  }
  var box=document.createElement("div"); box.id="lab";
  box.innerHTML='<header>🎨 Pruebas de color <small>teclas 1–8 · ocultar ▾</small></header><div class="body"><div class="presets"></div>'+
    '<div class="pick"><label><input type="color" data-k="bg">fondo</label><label><input type="color" data-k="text">texto</label><label><input type="color" data-k="oval">óvalo</label><label><input type="color" data-k="word">pana</label></div>'+
    '<div class="fonts"><div class="t">estudio / creativo</div><button data-f="">Peridot (original)</button><button data-f="bold">Helvetica Bold</button><button data-f="cond">Helvetica Condensed</button><button data-f="reg">Helvetica Regular</button><button data-f="light">Helvetica Light</button></div>'+
    '<div class="fonts fx"><div class="t">efecto al scrollear (tecla M / B / 0)</div><button data-x="moire">Moiré</button><button data-x="mobius">Möbius</button><button data-x="none">Ninguno (Bruno)</button></div>'+
    '<div class="fonts salas"><div class="t">otras salas</div><button onclick="location.href=\'tv/\'">📺 Habitación con la TV</button></div>'+
    '<div class="hex"></div><div class="tip">Probá scrollear y pasar el mouse por las letras: la estela también cambia.</div></div>';
  document.body.appendChild(box);
  box.querySelector("header").onclick=function(){ box.classList.toggle("min"); };
  var list=box.querySelector(".presets"), hex=box.querySelector(".hex"), inputs={};
  var btns=P.map(function(p,i){
    var b=document.createElement("button"); b.className="p";
    b.innerHTML='<span class="k">'+(i+1)+'</span><span class="sw"><i style="background:'+p.bg+'"></i><i style="background:'+p.text+'"></i><i style="background:'+p.oval+'"></i></span>'+p.n;
    b.onclick=function(){ apply(p,i); }; list.appendChild(b); return b;
  });
  box.querySelectorAll("input").forEach(function(inp){
    inputs[inp.dataset.k]=inp;
    inp.oninput=function(){ var p=Object.assign({},cur); p[inp.dataset.k]=inp.value; if(inp.dataset.k==="text"){p.alt=p.alt===cur.text?inp.value:p.alt;} apply(p,-1); };
  });
  var fb=box.querySelectorAll(".fonts:not(.fx):not(.salas) button");
  function setFont(f){ if(f) document.body.dataset.sf=f; else delete document.body.dataset.sf; fb.forEach(function(b){ b.classList.toggle("on",b.dataset.f===f); }); try{ localStorage.setItem("pana-sf",f); }catch(e){} }
  fb.forEach(function(b){ b.onclick=function(){ setFont(b.dataset.f); }; });
  var sf=new URLSearchParams(location.search).get("sf"); if(sf===null){ sf=""; try{ sf=localStorage.getItem("pana-sf")||""; }catch(e){} } setFont(sf);
  var xb=box.querySelectorAll(".fx button");
  function setFx(m){ window.panaFX.set(m); xb.forEach(function(b){ b.classList.toggle("on",b.dataset.x===m); }); }
  xb.forEach(function(b){ b.onclick=function(){ setFx(b.dataset.x); }; });
  setFx(window.panaFX.get());
  addEventListener("keydown",function(e){ if(e.target.tagName==="INPUT"||e.target.tagName==="TEXTAREA")return; var m={m:"moire",b:"mobius","0":"none"}[e.key.toLowerCase()]; if(m) setFx(m); });
  box.addEventListener("wheel",function(e){ e.stopPropagation(); },true);
  addEventListener("keydown",function(e){ if(e.target.tagName==="INPUT"||e.target.tagName==="TEXTAREA")return; var n=+e.key; if(n>=1&&n<=P.length) apply(P[n-1],n-1); });
  var s=+(location.hash.slice(1)||1); apply(P[(s>=1&&s<=P.length?s:1)-1],(s>=1&&s<=P.length?s:1)-1);
  setTimeout(function(){ root.classList.add("ready"); },300);
})();
