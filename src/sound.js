export const soundManager = {
    muted: false,
    sounds: {
        hover: new Audio('Sounds/hover.mp3'),
        click: new Audio('Sounds/click.mp3')
    },
    init() {
        Object.values(this.sounds).forEach(sound => {
            sound.volume = 0.2;
            sound.load();
        });

        const muteBtn = document.getElementById('mute-btn');
        if (muteBtn) {
            muteBtn.addEventListener('click', () => this.toggleMute());
        }

        document.querySelectorAll('.control-btn').forEach(control => {
            control.addEventListener('mouseenter', () => this.play('hover'));
            control.addEventListener('click', (e) => {
                if (!control.id.includes('mute')) {
                    this.play('click');
                }
            });
        });
    },
    play(sound) {
        if (!this.muted && this.sounds[sound]) {
            this.sounds[sound].currentTime = 0;
            this.sounds[sound].play().catch(e => console.log("Sound playback prevented:", e));
        }
    },
    toggleMute() {
        this.muted = !this.muted;
        const icon = document.querySelector('.sound-icon');
        icon.textContent = this.muted ? '🔇' : '🔊';
        localStorage.setItem('muted', this.muted);
    }
};