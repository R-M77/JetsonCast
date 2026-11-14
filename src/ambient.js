// Local Jetson customization. No external images, tracking, or network requests.
module.exports = () => {
    if (window.top !== window) return;
    const fs = require('fs');
    const path = require('path');
    const backgrounds = ['moonlit-meadow', 'aurora-lake', 'golden-coast', 'orbital-dawn'];
    const backgroundDir = path.join(process.env.JETSON_CAST_HOME, 'ambient');
    const rotationDelay = Math.max(30, Math.min(86400, Number(process.env.JETSON_CAST_ROTATION) || 300)) * 1000;
    const receiverName = process.env.JETSON_CAST_NAME || 'Jetson Cast';
    const funMode = process.env.JETSON_CAST_FUN_MODE === '1';
    const idleDelay = 90000;
    let lastActivity = Date.now() - 75000;
    let overlay;
    let art;
    let pet;
    let petOpen;
    let petBlink;
    let petActions;
    let lastPetAction = '';
    const petModes = ['walk-right', 'walk-left', 'peek-left', 'peek-right', 'peek-top', 'peek-bottom'];
    let petNext = 0;
    let petUntil = 0;
    let backgroundRequest = 0;
    let pendingArt;
    const clearPet = () => {
        if (!pet) return;
        pet.hidden = true;
        petOpen.removeAttribute('src');
        petBlink.removeAttribute('src');
        petActions.style.backgroundImage = '';
        petUntil = 0;
    };
    let backgroundIndex = 0;
    let backgroundStarted = 0;
    const hide = () => {
        if (!overlay || overlay.hidden) return;
        overlay.hidden = true;
        clearPet();
        petNext = 0;
        // Release the animated image during playback so it does no background decoding.
        art.removeAttribute('src');
        art.style.visibility = 'hidden';
        backgroundRequest++;
        if (pendingArt) pendingArt.removeAttribute('src');
        pendingArt = undefined;
        backgroundStarted = 0;
    };
    const loadBackground = () => {
        const request = ++backgroundRequest;
        try {
            const file = path.join(backgroundDir, backgrounds[backgroundIndex] + '.gif');
            const name = backgrounds[backgroundIndex];
            const next = document.createElement('img');
            next.className = 'ja-art'; next.alt = '';
            pendingArt = next;
            next.src = 'data:image/gif;base64,' + fs.readFileSync(file).toString('base64');
            // Keep the previous image visible until its replacement can paint.
            // A late decode must never restore artwork after casting has begun.
            next.decode().then(() => {
                if (request !== backgroundRequest || overlay.hidden) {
                    next.removeAttribute('src'); return;
                }
                art.replaceWith(next);
                art.removeAttribute('src');
                art = next;
                pendingArt = undefined;
                overlay.dataset.background = name;
            }).catch(() => {
                next.removeAttribute('src');
                if (pendingArt === next) pendingArt = undefined;
            });
        } catch (_) {
            console.warn('[Jetson Cast] Ambient background could not be loaded');
        }
        backgroundStarted = performance.now();
    };
    const reset = () => {
        lastActivity = Date.now();
        hide();
    };
    for (const event of ['keydown', 'pointerdown', 'pointermove', 'wheel', 'touchstart']) {
        window.addEventListener(event, reset, { capture: true, passive: true });
    }
    for (const event of ['play', 'playing', 'loadstart', 'seeking']) {
        document.addEventListener(event, event => {
            if (event.target instanceof HTMLMediaElement) reset();
        }, true);
    }
    function mount() {
        if (!document.body) return;
        const style = document.createElement('style');
        style.textContent = `
          #jetson-ambient[hidden] { display: none !important; }
          #jetson-ambient { position: fixed; inset: 0; z-index: 2147483646;
            overflow: hidden; color: #fff; background: #142636;
            font-family: Arial, sans-serif; cursor: none; isolation: isolate; }
          #jetson-ambient .ja-art { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; contain: paint; }
          #jetson-ambient .ja-shade { position: absolute; inset: 0; background: linear-gradient(180deg,rgba(5,16,27,.1),transparent 40%,rgba(5,16,27,.75)); }
          #jetson-ambient .ja-clock { position: absolute; top: 7%; right: 6%; text-align: right; text-shadow: 0 2px 24px #14263680; }
          #jetson-ambient .ja-time { font-size: clamp(48px,7vw,150px); font-weight: 300; letter-spacing: -.06em; font-variant-numeric: tabular-nums; }
          #jetson-ambient .ja-date { margin-top: 12px; font-size: clamp(16px,1.7vw,36px); opacity: .8; }
          #jetson-ambient .ja-copy { position: absolute; bottom: 8%; left: 6%; }
          #jetson-ambient .ja-name { font-size: clamp(32px,4vw,86px); font-weight: 400; letter-spacing: -.035em; margin: 0 0 18px; }
          #jetson-ambient .ja-instruction { font-size: clamp(17px,1.6vw,34px); opacity: .85; margin: 0; }
          #jetson-ambient .ja-pet[hidden] { display: none !important; }
          #jetson-ambient .ja-pet { position: absolute; bottom: 3px; left: var(--anchor,78%);
            height: clamp(96px,17vh,180px); aspect-ratio: 0.72; pointer-events: none;
            animation: ja-peek 15s ease-in-out both; }
          #jetson-ambient .ja-pet img { position: absolute; width: 100%; height: 100%; object-fit: contain; }
          #jetson-ambient .ja-pet-body { position: absolute; inset: 0; }
          #jetson-ambient .ja-pet-actions { display: none; position: absolute; inset: 0; background-size: 600% 100%; background-repeat: no-repeat; }
          #jetson-ambient .ja-pet[data-action^="walk"] { width: clamp(130px,18vh,194px); height: clamp(130px,18vh,194px); aspect-ratio: 1; bottom: 0; animation: ja-stroll 7s linear both; }
          #jetson-ambient .ja-pet[data-action^="walk"] img { display: none; }
          #jetson-ambient .ja-pet[data-action^="walk"] .ja-pet-actions { display: block;
            animation: ja-gait .6s steps(1,end) 8, ja-crouch .4s steps(1,end) 4.8s forwards, ja-air 1.8s steps(1,end) 5.2s forwards; }
          #jetson-ambient .ja-pet[data-action="walk-left"] .ja-pet-body { transform: scaleX(-1); }
          #jetson-ambient .ja-pet[data-action="peek-left"] { left: 0; bottom: auto; top: var(--anchor); animation: ja-left 15s ease-in-out both; }
          #jetson-ambient .ja-pet[data-action="peek-left"] .ja-pet-body { transform: rotate(90deg); }
          #jetson-ambient .ja-pet[data-action="peek-right"] { left: auto; right: 0; bottom: auto; top: var(--anchor); animation: ja-right 15s ease-in-out both; }
          #jetson-ambient .ja-pet[data-action="peek-right"] .ja-pet-body { transform: rotate(-90deg); }
          #jetson-ambient .ja-pet[data-action="peek-top"] { bottom: auto; top: 0; animation: ja-top 15s ease-in-out both; }
          #jetson-ambient .ja-pet[data-action="peek-top"] .ja-pet-body { transform: rotate(180deg); }
          @keyframes ja-gait { 0%,100% { background-position: 0% 0; } 25% { background-position: 20% 0; } 50% { background-position: 40% 0; } 75% { background-position: 60% 0; } }
          @keyframes ja-crouch { 0%,100% { background-position: 80% 0; } }
          @keyframes ja-air { 0%,100% { background-position: 100% 0; } }
          @keyframes ja-stroll {
            0% { transform: translate(0,110%); }
            8% { transform: translate(0,0); }
            68%,74% { transform: translate(var(--travel),0); }
            82% { transform: translate(var(--travel),-34%); }
            100% { transform: translate(var(--travel),125%); }
          }
          @keyframes ja-left { 0%,100% { transform: translateX(-150%); } 18%,76% { transform: translateX(-25%); } }
          @keyframes ja-right { 0%,100% { transform: translateX(150%); } 18%,76% { transform: translateX(25%); } }
          @keyframes ja-top { 0%,100% { transform: translateY(-115%); } 18%,76% { transform: translateY(-38%); } }
          #jetson-ambient .ja-pet-blink { animation: ja-blink 15s steps(1,end) both; }
          @keyframes ja-peek {
            0%,100% { transform: translateY(115%); }
            14%,30% { transform: translateY(35%); }
            43%,80% { transform: translateY(0); }
          }
          @keyframes ja-blink {
            0%,49%,51%,70%,72%,100% { opacity: 0; }
            49.5%,50.8%,70.5%,71.8% { opacity: 1; }
          }
          @media (prefers-reduced-motion: reduce) {
            #jetson-ambient .ja-pet { display: none; }
          }
        `;
        document.head.appendChild(style);
        overlay = document.createElement('div');
        overlay.id = 'jetson-ambient';
        overlay.hidden = true;
        overlay.setAttribute('aria-label', 'Jetson Cast ambient screen');
        art = document.createElement('img');
        art.className = 'ja-art'; art.alt = '';
        art.style.visibility = 'hidden';
        overlay.appendChild(art);
        const element = (tag, className, text, parent) => {
            const el = document.createElement(tag); el.className = className;
            if (text) el.textContent = text;
            (parent || overlay).appendChild(el); return el;
        };
        element('div', 'ja-shade');
        const clock = element('div', 'ja-clock');
        const time = element('div', 'ja-time', '', clock);
        const date = element('div', 'ja-date', '', clock);
        const copy = element('div', 'ja-copy');
        element('h1', 'ja-name', receiverName, copy);
        element('p', 'ja-instruction', 'Open YouTube on your phone · Tap Cast · Choose ' + receiverName, copy);
        if (funMode) {
            pet = element('div', 'ja-pet');
            pet.hidden = true;
            pet.setAttribute('aria-hidden', 'true');
            const petBody = element('div', 'ja-pet-body', '', pet);
            petOpen = element('img', 'ja-pet-open', '', petBody);
            petBlink = element('img', 'ja-pet-blink', '', petBody);
            petActions = element('div', 'ja-pet-actions', '', petBody);
            petOpen.alt = ''; petBlink.alt = '';
        }
        document.body.appendChild(overlay);
        setInterval(() => {
            const videos = [...document.querySelectorAll('video')];
            const playing = videos.some(v => !v.paused && !v.ended && v.readyState >= 2);
            if (playing) { reset(); return; }
            if (Date.now() - lastActivity < idleDelay) { hide(); return; }
            if (overlay.hidden) {
                loadBackground();
                overlay.hidden = false;
                petNext = performance.now() + 15000 + Math.random() * 10000;
            } else if (performance.now() - backgroundStarted >= rotationDelay) {
                backgroundIndex = (backgroundIndex + 1) % backgrounds.length;
                loadBackground();
            }
            if (!overlay.hidden) {
                const elapsed = performance.now();
                if (funMode && petUntil && elapsed >= petUntil) {
                    clearPet();
                    petNext = elapsed + 45000 + Math.random() * 30000;
                } else if (funMode && !petUntil && elapsed >= petNext) {
                    // Load only during a visit. Missing mascot artwork never affects casting.
                    petNext = elapsed + 90000;
                    try {
                        const available = petModes.filter(mode => mode !== lastPetAction);
                        const mode = available[Math.floor(Math.random() * available.length)];
                        lastPetAction = mode;
                        pet.dataset.action = mode;
                        const walking = mode.startsWith('walk');
                        const leftward = mode === 'walk-left';
                        const anchor = walking ? (leftward ? 80 : 60) :
                            mode === 'peek-top' ? 18 + Math.random() * 35 :
                            mode === 'peek-bottom' ? 65 + Math.random() * 20 : 35 + Math.random() * 24;
                        pet.style.setProperty('--anchor', anchor + '%');
                        pet.style.setProperty('--travel', (leftward ? -18 : 18) + 'vw');
                        if (walking) {
                            petActions.style.backgroundImage = 'url("data:image/png;base64,' + fs.readFileSync(path.join(backgroundDir, 'jet-actions.png')).toString('base64') + '")';
                        } else {
                            petOpen.src = 'data:image/png;base64,' + fs.readFileSync(path.join(backgroundDir, 'jet-open.png')).toString('base64');
                            petBlink.src = 'data:image/png;base64,' + fs.readFileSync(path.join(backgroundDir, 'jet-blink.png')).toString('base64');
                        }
                        pet.hidden = false;
                        petUntil = elapsed + 15000;
                    } catch (_) { clearPet(); }
                }
                const now = new Date();
                const clockText = now.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
                const dateText = now.toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' });
                if (time.textContent !== clockText) time.textContent = clockText;
                if (date.textContent !== dateText) date.textContent = dateText;
                // Very small periodic shift reduces static text wear without continuous animation.
                const shift = (Math.floor(now.getTime() / 60000) % 5 - 2) * 2;
                const transform = 'translate(' + shift + 'px,' + shift + 'px)';
                if (clock.style.transform !== transform) clock.style.transform = transform;
            }
        }, 1000);
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount, { once: true });
    else mount();
};
