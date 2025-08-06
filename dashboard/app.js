async function loadData() {
    const res = await fetch('/data');
    const data = await res.json();

    const timeline = document.getElementById('timeline');
    timeline.innerHTML = '';
    data.reflections.forEach((r, i) => {
        const li = document.createElement('li');
        li.textContent = `${i + 1}. ${r.text} [${r.sentiment}] (${r.traits.join(', ')})`;
        timeline.appendChild(li);
    });

    document.getElementById('integrity').textContent = data.integrity_score;

    const cloud = document.getElementById('trait-cloud');
    cloud.innerHTML = '';
    Object.entries(data.trait_cloud).forEach(([trait, count]) => {
        const span = document.createElement('span');
        span.textContent = `${trait}(${count})`;
        cloud.appendChild(span);
    });

    document.getElementById('yield').textContent = data.vaultfire_yield;
}

document.addEventListener('DOMContentLoaded', loadData);
