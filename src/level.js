function calculateXPProgress(birthDate) {
    const now = new Date();
    const currentYear = now.getFullYear();

    const lastBirthday = new Date(birthDate);
    lastBirthday.setFullYear(currentYear);
    if (now < lastBirthday) lastBirthday.setFullYear(currentYear - 1);

    const nextBirthday = new Date(lastBirthday);
    nextBirthday.setFullYear(lastBirthday.getFullYear() + 1);

    const total = nextBirthday - lastBirthday;
    const progress = now - lastBirthday;

    const percentage = (progress / total) * 100;
    return Math.min(Math.max(percentage, 0), 100);
}

export function generateLevel() {
    const birthDate = new Date('2004-09-29');
    const now = new Date();
    let age = now.getFullYear() - birthDate.getFullYear();

    const hadBirthdayThisYear =
        now.getMonth() > birthDate.getMonth() ||
        (now.getMonth() === birthDate.getMonth() && now.getDate() >= birthDate.getDate());

    if (!hadBirthdayThisYear) {
        age -= 1;
    }

    document.getElementById("level-value").textContent = age;

    const xpPercent = calculateXPProgress(birthDate);
    const xpBar = document.getElementById("xp-bar");
    xpBar.style.width = `${xpPercent.toFixed(2)}%`;
}