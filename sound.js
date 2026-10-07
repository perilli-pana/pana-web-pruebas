/* ===== SONIDO (prueba) =====
   INTRO: un sinte grave que crece con la figura. El mouse lo toca:
        ← →  la nota (siempre dentro de Re menor)
        ↑ ↓  el filtro (arriba = brillante, abajo = sordo)
      Las dos capas del moiré son dos osciladores apenas desafinados: el batido
      que se oye es la misma interferencia que se ve.
 */
(function(){
  var ST=window.panaFX && window.panaFX.state; if(!ST) return;
  var ac=null, on=false, N=null, room=null, out=null, mx=0, my=.5, step=0;
  var NOTE_NAMES=["Re","Fa","Sol","La","Do","Re","Fa","Sol"];
  var btn=document.createElement("button"); btn.id="snd"; btn.textContent="🔇 activar sonido";
  document.body.appendChild(btn);
  btn.onclick=function(){ on=!on; ST.playing=on; if(on) start(); else if(ac) ac.suspend(); label(); };
  function label(){ btn.textContent = !on ? "🔇 activar sonido" : (ST.a>0.02 ? "🔊 "+NOTE_NAMES[step]+" · filtro "+Math.round((1-my)*100)+"%" : "🔊 sonido"); }

  function curve(k){ var n=1024,c=new Float32Array(n); for(var i=0;i<n;i++){ var x=i/(n-1)*2-1; c[i]=Math.tanh(x*k)/Math.tanh(k); } return c; }

  function start(){
    if(ac){ ac.resume(); return; }
    ac=new (window.AudioContext||window.webkitAudioContext)();
    // salida: compresión suave + un corte de agudos para que nada pinche
    var comp=ac.createDynamicsCompressor(); comp.threshold.value=-16; comp.ratio.value=3; comp.attack.value=.02; comp.release.value=.25;
    var shelf=ac.createBiquadFilter(); shelf.type="highshelf"; shelf.frequency.value=5000; shelf.gain.value=-6;
    out=ac.createGain(); out.gain.value=.9; out.connect(shelf); shelf.connect(comp); comp.connect(ac.destination);
    // sala estéreo, larga y oscura
    room=ac.createConvolver(); var L=ac.sampleRate*2.8, ir=ac.createBuffer(2,L,ac.sampleRate);
    for(var c=0;c<2;c++){ var d=ir.getChannelData(c), lp=0; for(var i=0;i<L;i++){ lp+=((Math.random()*2-1)-lp)*0.35; d[i]=lp*Math.pow(1-i/L,2.6); } }
    room.buffer=ir; var roomG=ac.createGain(); roomG.gain.value=.5; room.connect(roomG); roomG.connect(out);

    // --- sinte ---
    var master=ac.createGain(); master.gain.value=0;
    var lpf=ac.createBiquadFilter(); lpf.type="lowpass"; lpf.frequency.value=90; lpf.Q.value=7;
    var drive=ac.createWaveShaper(); drive.curve=curve(1.3); drive.oversample="4x";
    lpf.connect(drive); drive.connect(master); master.connect(out);
    var send=ac.createGain(); send.gain.value=.35; master.connect(send); send.connect(room);
    // eco ping-pong (corchea con puntillo a 80 bpm)
    var dl=ac.createDelay(2), dr=ac.createDelay(2), fbk=ac.createGain(), wet=ac.createGain(), mL=ac.createStereoPanner(), mR=ac.createStereoPanner(), dlp=ac.createBiquadFilter();
    dl.delayTime.value=dr.delayTime.value=.5625; fbk.gain.value=.38; wet.gain.value=.2; mL.pan.value=-.8; mR.pan.value=.8; dlp.type="lowpass"; dlp.frequency.value=1800;
    master.connect(dl); dl.connect(dlp); dlp.connect(mL); mL.connect(wet); dlp.connect(dr); dr.connect(mR); mR.connect(wet); dr.connect(fbk); fbk.connect(dl); wet.connect(out);
    // voces: sub al centro, sierras abiertas a los costados (estéreo ancho)
    function osc(type,mult,g,det,pan,dest){ var o=ac.createOscillator(), G=ac.createGain(), P=ac.createStereoPanner(); o.type=type; o.detune.value=det||0; G.gain.value=g; P.pan.value=pan||0; o.connect(G); G.connect(P); P.connect(dest||lpf); o.start(); return {o:o,m:mult}; }
    var V=[ osc("sine",.5,.7,0,0,master),
            osc("sawtooth",1,.2,-8,-.7), osc("sawtooth",1,.2,8,.7),
            osc("sawtooth",1,.2,0,0),
            osc("sawtooth",1.5,.1,5,-.35), osc("sawtooth",1.5,.1,-5,.35),
            osc("triangle",2.378,.07,0,0) ];
    // movimiento lento: chorus en las sierras y el filtro que respira
    var lfo=ac.createOscillator(), lg=ac.createGain(); lfo.frequency.value=.18; lg.gain.value=6; lfo.connect(lg); lg.connect(V[1].o.detune); lfo.start();
    var lfo2=ac.createOscillator(), lg2=ac.createGain(); lfo2.frequency.value=.23; lg2.gain.value=-6; lfo2.connect(lg2); lg2.connect(V[2].o.detune); lfo2.start();
    var lfo3=ac.createOscillator(), lg3=ac.createGain(); lfo3.frequency.value=.11; lg3.gain.value=60; lfo3.connect(lg3); lg3.connect(lpf.frequency); lfo3.start();
    N={master:master,lpf:lpf,V:V,B:V[3]};
    loop();
  }

  var SCALE=[0,3,5,7,10,12,15,17], ROOT=73.42;
  function loop(){
    if(!N) return;
    var t=ac.currentTime, a=on?ST.a:0;
    // nota con "histéresis": no titubea en el borde entre dos notas
    var pos=mx*SCALE.length;
    if(pos<step-0.15||pos>step+1.15) step=Math.max(0,Math.min(SCALE.length-1,Math.floor(pos)));
    var ratio=Math.pow(2,SCALE[step]/12); ST.note=ratio;
    var f=ROOT*ratio, drop=Math.pow(2,-ST.col*2/12);
    N.V.forEach(function(v){ v.o.frequency.setTargetAtTime(v===N.B? (f+ST.beat)*drop : f*v.m*drop, t, .07); });   // legato
    var open=Math.pow(1-my,1.7);
    N.lpf.frequency.setTargetAtTime(70+a*(110+open*3000),t,.06);
    N.master.gain.setTargetAtTime(Math.pow(a,1.3)*.45,t,.12);
    label();
    requestAnimationFrame(loop);
  }

  addEventListener("mousemove",function(e){ mx=e.clientX/innerWidth; my=e.clientY/innerHeight; });
})();
