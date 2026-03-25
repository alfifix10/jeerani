// ========================================
// TrendScope - Main Application
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    initParticles();
    initNavbar();
    initStats();
    renderTrends();
    renderArticles();
    initAnalyzer();
    initFilters();
    initModal();
    duplicateTicker();
});

// ---- Particles Background ----
function initParticles() {
    const container = document.getElementById('particles');
    const colors = ['#fe2c55', '#25f4ee', '#fffc00', '#ffffff'];
    for (let i = 0; i < 30; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        const size = Math.random() * 6 + 2;
        p.style.width = size + 'px';
        p.style.height = size + 'px';
        p.style.left = Math.random() * 100 + '%';
        p.style.background = colors[Math.floor(Math.random() * colors.length)];
        p.style.animationDuration = (Math.random() * 20 + 15) + 's';
        p.style.animationDelay = (Math.random() * 10) + 's';
        container.appendChild(p);
    }
}

// ---- Navbar ----
function initNavbar() {
    const navbar = document.querySelector('.navbar');
    const toggle = document.getElementById('menuToggle');
    const links = document.querySelector('.nav-links');

    window.addEventListener('scroll', () => {
        navbar.classList.toggle('scrolled', window.scrollY > 50);
    });

    toggle.addEventListener('click', () => {
        links.classList.toggle('active');
    });

    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            links.classList.remove('active');
            document.querySelectorAll('.nav-links a').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });
}

// ---- Animated Stats ----
function initStats() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const nums = entry.target.querySelectorAll('.stat-number[data-target]');
                nums.forEach(num => animateNumber(num));
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    const statsContainer = document.querySelector('.hero-stats');
    if (statsContainer) observer.observe(statsContainer);
}

function animateNumber(el) {
    const target = parseInt(el.dataset.target);
    const duration = 2000;
    const start = performance.now();

    function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.floor(target * eased).toLocaleString('ar-EG');
        if (progress < 1) requestAnimationFrame(update);
        else el.textContent = target.toLocaleString('ar-EG') + '+';
    }
    requestAnimationFrame(update);
}

// ---- Render Trends ----
function renderTrends(filter = 'all') {
    const grid = document.getElementById('trendsGrid');
    grid.innerHTML = '';

    const filtered = filter === 'all'
        ? trendsData
        : trendsData.filter(t => t.category === filter);

    filtered.forEach((trend, i) => {
        const card = document.createElement('div');
        card.className = 'trend-card';
        card.style.animationDelay = (i * 0.1) + 's';
        card.innerHTML = `
            <div class="trend-card-header">
                <div class="trend-rank">${trend.rank}</div>
                <span class="trend-category">${trend.categoryLabel}</span>
            </div>
            <div class="trend-card-body">
                <h3>${trend.title}</h3>
                <p>${trend.description}</p>
            </div>
            <div class="trend-card-footer">
                <div class="trend-stats">
                    <span>&#128065; ${trend.views}</span>
                    <span>&#10084;&#65039; ${trend.likes}</span>
                    <span>&#128257; ${trend.shares}</span>
                </div>
                <span class="trend-growth ${trend.growthUp ? '' : 'down'}">${trend.growth}</span>
            </div>
        `;
        card.addEventListener('click', () => {
            document.getElementById('analyzerInput').value = trend.hashtag;
            document.getElementById('analyzer').scrollIntoView({ behavior: 'smooth' });
            setTimeout(() => document.getElementById('analyzeBtn').click(), 500);
        });
        grid.appendChild(card);
    });
}

// ---- Filters ----
function initFilters() {
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            renderTrends(tab.dataset.filter);
        });
    });
}

// ---- Render Articles ----
function renderArticles() {
    const grid = document.getElementById('articlesGrid');
    grid.innerHTML = '';

    articlesData.forEach((article, i) => {
        const card = document.createElement('div');
        card.className = 'article-card';
        card.style.animationDelay = (i * 0.1) + 's';
        card.innerHTML = `
            <div class="article-image">
                <div class="article-image-bg" style="background:${article.bgGradient}">${article.emoji}</div>
                <span class="article-badge">${article.category}</span>
            </div>
            <div class="article-body">
                <h3>${article.title}</h3>
                <p>${article.excerpt}</p>
                <div class="article-meta">
                    <span class="article-read-time">&#128214; ${article.readTime}</span>
                    <span>${article.date}</span>
                </div>
            </div>
        `;
        card.addEventListener('click', () => openArticle(article));
        grid.appendChild(card);
    });
}

// ---- Article Modal ----
function initModal() {
    const overlay = document.getElementById('articleModal');
    const closeBtn = document.getElementById('closeModal');

    closeBtn.addEventListener('click', () => overlay.classList.remove('active'));
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) overlay.classList.remove('active');
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') overlay.classList.remove('active');
    });
}

function openArticle(article) {
    const body = document.getElementById('modalBody');
    let html = `
        <h2 class="article-full-title">${article.content.title}</h2>
        <div class="article-full-meta">
            <span>&#128214; ${article.readTime}</span>
            <span>&#128197; ${article.date}</span>
            <span>&#127991;&#65039; ${article.category}</span>
        </div>
        <div class="article-full-content">
    `;

    article.content.sections.forEach(section => {
        html += `<h3>${section.heading}</h3><p>${section.text}</p>`;
        if (section.fact) {
            html += `<div class="fact-box">&#128161; حقيقة: ${section.fact}</div>`;
        }
    });

    html += '</div>';
    body.innerHTML = html;
    document.getElementById('articleModal').classList.add('active');
}

// ---- Analyzer ----
function initAnalyzer() {
    const input = document.getElementById('analyzerInput');
    const btn = document.getElementById('analyzeBtn');
    const btnText = btn.querySelector('span');
    const btnLoader = btn.querySelector('.btn-loader');

    btn.addEventListener('click', () => {
        const topic = input.value.trim();
        if (!topic) {
            input.style.borderColor = '#fe2c55';
            setTimeout(() => input.style.borderColor = '', 1500);
            return;
        }
        btnText.style.display = 'none';
        btnLoader.style.display = 'block';
        btn.disabled = true;

        setTimeout(() => {
            generateAnalysis(topic);
            btnText.style.display = '';
            btnLoader.style.display = 'none';
            btn.disabled = false;
        }, 2000);
    });

    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') btn.click();
    });

    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            input.value = chip.dataset.topic;
            btn.click();
        });
    });
}

function generateAnalysis(topic) {
    const result = document.getElementById('analysisResult');
    result.style.display = 'block';

    const views = (Math.random() * 50 + 5).toFixed(1) + 'M';
    const growth = '+' + Math.floor(Math.random() * 500 + 50) + '%';

    document.getElementById('resultTitle').textContent = 'تحليل: ' + topic;
    document.getElementById('resultViews').textContent = '&#128065; ' + views + ' مشاهدة';
    document.getElementById('resultViews').innerHTML = '&#128065; ' + views + ' مشاهدة';
    document.getElementById('resultTrend').textContent = growth + ' نمو';

    drawChart(topic);
    generateInsights(topic);
    generateArticle(topic);

    result.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ---- Chart Drawing ----
function drawChart(topic) {
    const canvas = document.getElementById('trendChart');
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth * 2;
    canvas.height = 500;
    ctx.scale(2, 2);

    const w = canvas.offsetWidth;
    const h = 250;
    const padding = 40;
    const chartW = w - padding * 2;
    const chartH = h - padding * 2;

    ctx.clearRect(0, 0, w, h);

    // Generate data
    const days = 14;
    const data = [];
    let val = Math.random() * 20 + 10;
    for (let i = 0; i < days; i++) {
        val += (Math.random() - 0.3) * 15;
        val = Math.max(5, val);
        data.push(val);
    }
    // Make it trend upward
    data[days - 1] = Math.max(...data) * 1.2;
    data[days - 2] = Math.max(...data) * 0.9;

    const maxVal = Math.max(...data) * 1.1;

    // Grid lines
    ctx.strokeStyle = 'rgba(255,255,255,0.05)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
        const y = padding + (chartH / 4) * i;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(w - padding, y);
        ctx.stroke();
    }

    // Draw gradient area
    const gradient = ctx.createLinearGradient(0, padding, 0, h - padding);
    gradient.addColorStop(0, 'rgba(254, 44, 85, 0.3)');
    gradient.addColorStop(1, 'rgba(254, 44, 85, 0)');

    ctx.beginPath();
    ctx.moveTo(padding, h - padding);
    data.forEach((val, i) => {
        const x = padding + (chartW / (days - 1)) * i;
        const y = h - padding - (val / maxVal) * chartH;
        if (i === 0) ctx.lineTo(x, y);
        else {
            const prevX = padding + (chartW / (days - 1)) * (i - 1);
            const prevY = h - padding - (data[i - 1] / maxVal) * chartH;
            const cpX = (prevX + x) / 2;
            ctx.bezierCurveTo(cpX, prevY, cpX, y, x, y);
        }
    });
    ctx.lineTo(w - padding, h - padding);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();

    // Draw line
    ctx.beginPath();
    data.forEach((val, i) => {
        const x = padding + (chartW / (days - 1)) * i;
        const y = h - padding - (val / maxVal) * chartH;
        if (i === 0) ctx.moveTo(x, y);
        else {
            const prevX = padding + (chartW / (days - 1)) * (i - 1);
            const prevY = h - padding - (data[i - 1] / maxVal) * chartH;
            const cpX = (prevX + x) / 2;
            ctx.bezierCurveTo(cpX, prevY, cpX, y, x, y);
        }
    });
    ctx.strokeStyle = '#fe2c55';
    ctx.lineWidth = 3;
    ctx.stroke();

    // Draw dots
    data.forEach((val, i) => {
        const x = padding + (chartW / (days - 1)) * i;
        const y = h - padding - (val / maxVal) * chartH;
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#fe2c55';
        ctx.fill();
        ctx.strokeStyle = '#1a1a2e';
        ctx.lineWidth = 2;
        ctx.stroke();
    });

    // Labels
    ctx.fillStyle = 'rgba(255,255,255,0.4)';
    ctx.font = '11px Cairo';
    ctx.textAlign = 'center';
    const dayLabels = ['قبل 14 يوم', '', '', '', '', '', 'قبل أسبوع', '', '', '', '', '', '', 'اليوم'];
    dayLabels.forEach((label, i) => {
        if (label) {
            const x = padding + (chartW / (days - 1)) * i;
            ctx.fillText(label, x, h - 10);
        }
    });
}

// ---- Generate Insights ----
function generateInsights(topic) {
    const container = document.getElementById('insightsList');
    container.innerHTML = '';

    const templates = analysisTemplates.insights;
    const region = analysisTemplates.regions[Math.floor(Math.random() * analysisTemplates.regions.length)];
    const principle = analysisTemplates.principles[Math.floor(Math.random() * analysisTemplates.principles.length)];
    const warning = analysisTemplates.warnings[Math.floor(Math.random() * analysisTemplates.warnings.length)];
    const growth = Math.floor(Math.random() * 30 + 5);
    const amount = (Math.random() * 10 + 1).toFixed(1);

    templates.forEach(template => {
        const card = document.createElement('div');
        card.className = 'insight-card';
        const text = template.text
            .replace('{growth}', growth)
            .replace('{region}', region)
            .replace('{principle}', principle)
            .replace('{amount}', amount)
            .replace('{warning}', warning);

        card.innerHTML = `
            <div class="insight-icon">${template.icon}</div>
            <div>
                <h5>${template.title}</h5>
                <p>${text}</p>
            </div>
        `;
        container.appendChild(card);
    });
}

// ---- Generate Article ----
function generateArticle(topic) {
    const container = document.getElementById('generatedArticle');
    const template = analysisTemplates.articleTemplates[0];

    let html = `<p>${template.intro.replace('{topic}', topic)}</p>`;
    template.body.forEach(section => {
        html += section;
    });

    container.innerHTML = html;
}

// ---- Duplicate Ticker for seamless loop ----
function duplicateTicker() {
    const ticker = document.getElementById('tickerContent');
    ticker.innerHTML += ticker.innerHTML;
}
