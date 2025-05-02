import {projects} from './projects.js';
import {soundManager} from './sound.js';
import {generateProjectCards} from './ui.js';
import {loadBackground} from './background.js';
import {generateLevel} from './level.js';

document.addEventListener('DOMContentLoaded', () => {
    soundManager.init();

    if (localStorage.getItem('muted') === 'true') {
        soundManager.toggleMute();
    }

    generateLevel();
    generateProjectCards(projects, soundManager);
    loadBackground();

    const videos = document.querySelectorAll('.project-video');

    videos.forEach(video => {
        video.volume = 0.1;
    });
});