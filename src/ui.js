export function generateProjectCards(projects, soundManager) {
    const container = document.querySelector(".project-container");

    projects.forEach(project => {
        const card = document.createElement("div");
        card.className = "project-card";

        if (project.featured) {
            card.classList.add("featured");
            card.innerHTML += `
            <div class="featured-label">[ FEATURED ]</div>
          `;
        }

        const hasVideo = project.videoId && project.videoId.trim() !== "";
        const hasVideoFile = project.videoFile && project.videoFile.trim() !== "";
        const hasLinks = project.links && project.links.length > 0;
        const hasImage = project.image && project.image.trim() !== "";

        card.innerHTML += `
            <div class="project-info">
                <h3>${project.title}</h3>
                <p>${project.description}</p>
            </div>
            ${hasVideo ? `
            <iframe src="https://www.youtube.com/embed/${project.videoId}?rel=0&enablejsapi=1&controls=1" allowfullscreen></iframe>
            ` : hasVideoFile ? `
                <video controls class="project-video">
                    <source src="${project.videoFile}" type="video/mp4">
                    Your browser does not support the video.
                </video>
            ` : ''}
            ${hasImage ? `
                <img src="${project.image}" alt="${project.title} image">
            ` : ''}
            ${hasLinks ? `
                <div class="project-buttons">
                ${project.links.map(link => `<a href="${link.url}" target="_blank">${link.label}</a>`).join("")}
                </div>
            ` : ''}
            <div class="project-stats">
                ${project.stats.map(stat => `
                <div class="stat-bar">
                    <span>${stat.label}:</span>
                    <div class="bar-container">
                    <div class="bar-fill" style="width: ${stat.percentage}%"></div>
                    </div>
                </div>
                `).join("")}
            </div>
        `;

        container.appendChild(card);

        card.addEventListener('mouseenter', () => soundManager.play('hover'));
        card.querySelectorAll('.project-buttons a').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                soundManager.play('click');
                setTimeout(() => {
                    window.open(button.href, '_blank');
                }, 100);
            });
        });
    });
}