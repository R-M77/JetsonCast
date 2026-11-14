// Only local playback intent is shared; no video URLs, titles or account data.
module.exports = () => {
    if (window.top !== window || process.env.JETSON_CAST_INPUT_SWITCH !== '1') return;
    const fs = require('fs');
    const dir = require('path').join(process.env.JETSON_CAST_HOME, 'state');
    fs.mkdirSync(dir, { recursive: true, mode: 0o700 });
    let sequence = 0;
    let lastCommand = '';
    let lastIntent = 0;
    const emit = () => {
        const now = Date.now();
        if (now - lastIntent < 1200) return;
        lastIntent = now;
        const event = { id: `${process.pid}-${now}-${sequence++}`, at: now / 1000, action: 'play' };
        const temporary = dir + '/intent-' + require('crypto').randomUUID() + '.tmp';
        let created = false;
        try {
            fs.writeFileSync(temporary, JSON.stringify(event), { mode: 0o600, flag: 'wx' });
            created = true;
            fs.renameSync(temporary, dir + '/jetson-intent.json');
            created = false;
        } catch (error) { console.warn('[jetson-input] Could not report playback intent'); }
        finally { if (created) { try { fs.unlinkSync(temporary); } catch (_) {} } }
    };
    document.addEventListener('play', event => {
        if (event.target instanceof HTMLVideoElement) emit();
    }, true);
    setInterval(() => {
        try {
            const command = JSON.parse(fs.readFileSync(dir + '/jetson-command.json', 'utf8'));
            if (command.id === lastCommand) return;
            lastCommand = command.id;
            if (command.action === 'pause' && Date.now() / 1000 - command.at < 15) {
                for (const video of document.querySelectorAll('video')) if (!video.paused) video.pause();
            }
        } catch (_) { /* No command yet, or service is stopped. */ }
    }, 500);
};
