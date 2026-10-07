/* ===== INTRO al scrollear (prueba): moiré / möbius sobre el óvalo de pana =====
   El primer scroll en el inicio NO va directo a servicios: maneja este efecto
   (scrubbeado, sigue al dedo/rueda). Al completarse, el óvalo se recompone y
   le pasa la posta a la transición de Bruno (cometa hacia arriba). */
(function(){
  var stage=document.getElementById("stage"), root=document.documentElement;
  var estudio=document.getElementById("estudio"), creativo=document.getElementById("creativo");
  var cv=document.createElement("canvas"); cv.id="introfx";
  cv.style.cssText="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;z-index:0";
  stage.insertBefore(cv, stage.firstChild);
  var ctx=cv.getContext("2d");
  // óvalo del logo en coords del lienzo 1920x1080
  var CX=960, CY=540, RX=88.3/262.16*360, RY=45.01/262.16*360, ROT=-3.96*Math.PI/180;

  var mode="moire";
  try{ mode=localStorage.getItem("pana-fx")||"moire"; }catch(e){}
  var q=new URLSearchParams(location.search).get("fx"); if(q) mode=q;
  var ST={a:0,ip:0,col:0,beat:1,on:false,mode:mode};
  window.panaFX={ state:ST, set:function(m){ mode=m; ST.mode=m; try{localStorage.setItem("pana-fx",m);}catch(e){} }, get:function(){ return mode; } };

  var ipT=0, ip=0, lastIn=0, swallowUntil=0, phase=0, mx=0, my=0, smx=0, smy=0;
  var dbg=new URLSearchParams(location.search).get("ip"); if(dbg){ ipT=ip=parseFloat(dbg); lastIn=1e12; }
  function now(){ return performance.now(); }
  function atHome(){ return parseFloat(estudio.style.opacity||"1")>0.98; }
  function clamp(v,a,b){ return v<a?a:v>b?b:v; }
  function ss(a,b,x){ var t=clamp((x-a)/(b-a),0,1); return t*t*(3-2*t); }

  window.addEventListener("wheel",function(e){
    if(mode==="none") return;
    if(document.querySelector(".detail.open")) return;
    var t=now();
    if(t<swallowUntil){ e.preventDefault(); e.stopImmediatePropagation(); return; }
    if(!atHome()) return;
    var d=e.deltaY; if(Math.abs(d)<1) return;
    if(d<0 && ipT<=0) return;                 // arriba en el inicio: nada
    e.preventDefault(); e.stopImmediatePropagation();
    ipT=clamp(ipT+d*0.0011,0,1); lastIn=t;
  },{capture:true,passive:false});
  window.addEventListener("keydown",function(e){
    if(mode==="none"||!atHome()||e.isTrusted===false) return;
    if(e.key==="ArrowDown"||e.key===" "||e.key==="PageDown"){ if(ip<0.999){ e.preventDefault(); e.stopImmediatePropagation(); ipT=1; lastIn=now()-2000; } }
  },true);
  window.addEventListener("mousemove",function(e){ mx=e.clientX/innerWidth-.5; my=e.clientY/innerHeight-.5; });

  function handoff(){
    window.dispatchEvent(new Event("pana-handoff"));
    swallowUntil=now()+900;                   // que la inercia del trackpad no saltee secciones
    window.dispatchEvent(new KeyboardEvent("keydown",{key:"ArrowDown",bubbles:true}));
    setTimeout(function(){ ipT=0; ip=0; },700);
  }

  function size(){
    var k=parseFloat(getComputedStyle(stage).getPropertyValue("--k"))||1, dpr=Math.min(devicePixelRatio||1,2);
    var w=Math.round(1920*k*dpr), h=Math.round(1080*k*dpr);
    if(cv.width!==w||cv.height!==h){ cv.width=w; cv.height=h; }
    ctx.setTransform(w/1920,0,0,h/1080,0,0);
  }

  function oval(cx,cy,s,rot){ ctx.beginPath(); ctx.ellipse(cx,cy,RX*s,RY*s,rot,0,Math.PI*2); ctx.stroke(); }

  function drawMoire(p,t){
    // op-art: anillos gruesos (línea = hueco) y dos capas en XOR -> donde se
    // cruzan se apagan. Los anillos nacen del óvalo como una onda expansiva.
    var build=ss(0,.72,p), col=ss(.72,1,p), a=build*(1-col);
    var pitch=0.26*(1-col*0.97)/(ST.note||1);                    // separación entre anillos (en escalas del óvalo)
    var front=1+ss(0,.5,build)*12*(1-col*0.9);      // hasta dónde llegó la onda
    var ph=phase%1;
    ctx.lineWidth=RY*pitch*1.05;                     // grosor ~ mitad del paso -> contraste máximo
    ctx.globalAlpha=Math.min(1,a*5);
    function set(cx,cy,rot,pt,phs){
      for(var i=0;;i++){ var s=1+(i+phs)*pt; if(s>front) break; oval(cx,cy,s,rot); }
    }
    set(CX,CY,ROT,pitch,ph);
    ctx.globalCompositeOperation="xor";
    var ox=(smx*220+Math.sin(t*.0006)*40)*a, oy=(smy*120+Math.cos(t*.0008)*18)*a;
    var r2=ROT+a*(0.06+smx*0.08)+Math.sin(t*.0003)*0.03*a;
    set(CX+ox,CY+oy,r2,pitch*(1+0.05*a),1-ph+0.18*a*Math.sin(t/1000*Math.PI*2*ST.beat));   // la capa B respira al ritmo del batido       // la segunda capa fluye al revés
    ctx.globalCompositeOperation="source-over";
    ctx.globalAlpha=1;
    // el óvalo del logo siempre nítido arriba
    ctx.lineWidth=3*360/262.16*0.9; oval(CX,CY,1,ROT);
    // agujero negro detrás de "pana" para que la palabra se lea
    ctx.save(); ctx.globalCompositeOperation="destination-out"; ctx.beginPath();
    ctx.ellipse(CX,CY,RX*0.96,RY*0.9,ROT,0,Math.PI*2); ctx.fill();
    ctx.restore();
  }

  function drawMobius(p,t){
    var build=ss(0,.72,p), col=ss(.72,1,p), a=build*(1-col);
    var S=1+a*2.6, W=a*95, tilt=a*1.05, spin=a*Math.PI*1.4+Math.sin(t*.0005)*0.15*a+smx*0.6*a, twist=phase*2.2;
    var f=1500, M=260;
    function P(u,v){
      var c=Math.cos(u), s=Math.sin(u);
      var x=RX*S*c, y=RY*S*s;                        // eje en el plano
      var nx=RY*c, ny=RX*s, nl=Math.hypot(nx,ny); nx/=nl; ny/=nl;   // normal hacia afuera
      var h=u/2+twist, cw=Math.cos(h)*v*W, sw=Math.sin(h)*v*W;
      x+=nx*cw; y+=ny*cw; var z=sw;
      // rotación del logo, inclinación y giro
      var x1=x*Math.cos(ROT)-y*Math.sin(ROT), y1=x*Math.sin(ROT)+y*Math.cos(ROT);
      var y2=y1*Math.cos(tilt)-z*Math.sin(tilt), z2=y1*Math.sin(tilt)+z*Math.cos(tilt);
      var x3=x1*Math.cos(spin)+z2*Math.sin(spin), z3=-x1*Math.sin(spin)+z2*Math.cos(spin);
      var k=f/(f+z3); return [CX+x3*k, CY+y2*k, z3];
    }
    ctx.lineWidth=1.6+a*0.8;
    for(var i=0;i<M;i++){
      var u=i/M*Math.PI*2, A=P(u,-1), B=P(u,1);
      ctx.globalAlpha=clamp(0.55-((A[2]+B[2])/2)/(RX*S*2+1)*0.45,0.12,1)*Math.min(1,a*4);
      ctx.beginPath(); ctx.moveTo(A[0],A[1]); ctx.lineTo(B[0],B[1]); ctx.stroke();
    }
    ctx.globalAlpha=1; ctx.lineWidth=3;
    [-1,1].forEach(function(v){ ctx.beginPath(); for(var j=0;j<=M*2;j++){ var q=P(j/M*Math.PI*2,v); j?ctx.lineTo(q[0],q[1]):ctx.moveTo(q[0],q[1]); } ctx.stroke(); });
  }

  function frame(t){
    size();
    var tt=now();
    if(!ST.playing && tt-lastIn>900 && ipT>0 && ipT<1) ipT = ipT>0.6 ? Math.min(1,ipT+0.02) : Math.max(0,ipT-0.015);
    var prev=ip; ip+=(ipT-ip)*0.09; if(Math.abs(ipT-ip)<0.0008) ip=ipT;
    phase+=0.004+Math.abs(ip-prev)*9;
    smx+=(mx-smx)*0.06; smy+=(my-smy)*0.06;
    ctx.clearRect(0,0,1920,1080);
    var on = ip>0.001 && atHome() && mode!=="none";
    document.body.classList.toggle("fx-on",on);
    var a=ss(0,.72,ip)*(1-ss(.72,1,ip));
    stage.style.setProperty("--fxa",on?a:0);
    ST.on=on; ST.a=on?a:0; ST.ip=ip; ST.col=ss(.72,1,ip); ST.mx=smx; ST.my=smy;
    ST.beat=0.7+ST.a*2.2+Math.hypot(smx,smy)*7;      // Hz del batido: el mouse desafina
    if(on){
      ctx.strokeStyle=getComputedStyle(root).getPropertyValue("--oval").trim()||"#f50000";
      if(mode==="moire") drawMoire(ip,t); else drawMobius(ip,t);
    }
    if(ip>=0.999 && ipT>=1 && atHome() && tt>swallowUntil) handoff();
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
