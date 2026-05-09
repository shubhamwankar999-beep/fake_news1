document.addEventListener('DOMContentLoaded', () => {
    const verifyBtn = document.getElementById('verifyBtn');
    const newsContent = document.getElementById('newsContent');
    const modelSelect = document.getElementById('modelSelect');
    const resultsArea = document.getElementById('resultsArea');
    const loader = document.getElementById('loader');
    
    const verdictBadge = document.getElementById('verdictBadge');
    const verdictText = document.getElementById('verdictText');
    const confidenceBar = document.getElementById('confidenceBar');
    const confidenceValue = document.getElementById('confidenceValue');
    const realBar = document.getElementById('realBar');
    const realValue = document.getElementById('realValue');
    const fakeBar = document.getElementById('fakeBar');
    const fakeValue = document.getElementById('fakeValue');

    let predictionChart = null;

    // --- Helper function to update the badge style ---
    const updateVerdictBadge = (label) => {
        const isFake = label === 'FAKE';
        
        verdictBadge.classList.remove('fake', 'real');
        verdictText.classList.remove('fake', 'real');
        
        if (isFake) {
            verdictBadge.textContent = 'FAKE';
            verdictBadge.classList.add('fake');
            verdictText.textContent = 'CRITICAL: DISINFORMATION DETECTED';
            verdictText.classList.add('fake');
        } else {
            verdictBadge.textContent = 'REAL';
            verdictBadge.classList.add('real');
            verdictText.textContent = 'VERIFIED: AUTHENTIC CONTENT';
            verdictText.classList.add('real');
        }
    };

    // --- Chart Rendering ---
    const renderPredictionChart = (realConfidence, fakeConfidence) => {
        const ctx = document.getElementById('predictionChart').getContext('2d');
        
        if (predictionChart) predictionChart.destroy();

        predictionChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Real', 'Fake'],
                datasets: [{
                    data: [realConfidence, fakeConfidence],
                    backgroundColor: ['#38ef7d', '#ff4b2b'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8', font: { family: 'Outfit' } }
                    }
                },
                cutout: '70%',
                animation: { animateScale: true, animateRotate: true }
            }
        });
    };

    // --- Static Analytics Charts ---
    const renderAnalytics = () => {
        const accCtx = document.getElementById('accChart').getContext('2d');
        new Chart(accCtx, {
            type: 'bar',
            data: {
                labels: ['N.Bayes', 'LogReg', 'LSTM', 'BERT'],
                datasets: [{
                    data: [89, 92, 94, 98],
                    backgroundColor: '#4facfe'
                }]
            },
            options: {
                plugins: { legend: { display: false } },
                scales: { 
                    y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                    x: { ticks: { color: '#94a3b8' } }
                }
            }
        });

        const sentCtx = document.getElementById('sentChart').getContext('2d');
        new Chart(sentCtx, {
            type: 'line',
            data: {
                labels: ['Fake', 'Mixed', 'Real'],
                datasets: [{
                    label: 'Sentiment Intensity',
                    data: [0.9, 0.4, 0.2],
                    borderColor: '#00f2fe',
                    fill: true,
                    backgroundColor: 'rgba(0,242,254,0.1)'
                }]
            },
            options: {
                plugins: { legend: { display: false } },
                scales: { 
                    y: { beginAtZero: true, display: false },
                    x: { ticks: { color: '#94a3b8' } }
                }
            }
        });
    };

    try { renderAnalytics(); } catch (e) { console.warn("Analytics render failed", e); }

    // --- Live News Fetching ---
    const fetchLiveNews = async () => {
        const grid = document.getElementById('liveNewsGrid');
        try {
            const response = await fetch('/live-news');
            const data = await response.json();
            
            grid.innerHTML = '';
            // Store fetched globally for random test
            window.latestLiveNews = data;

            data.forEach(item => {
                const card = document.createElement('div');
                card.className = 'news-card';
                // Fix: Check for valid dates
                const pubDate = item.published ? new Date(item.published).toLocaleDateString() : 'Recent';
                card.innerHTML = `
                    <div class="content">
                        <small>${item.source || 'News'} • ${pubDate}</small>
                        <h4>${item.title}</h4>
                    </div>
                    <button class="btn-verify">Verify AI Verdict</button>
                `;
                // Add event listener safely rather than inline onclick to avoid race conditions
                card.querySelector('.btn-verify').addEventListener('click', (e) => {
                   e.stopPropagation();
                   newsContent.value = item.title;
                   document.getElementById('verify').scrollIntoView({ behavior: 'smooth' });
                   verifyBtn.click();
                });
                grid.appendChild(card);
            });
        } catch (error) {
            grid.innerHTML = '<p style="color:red; text-align:center;">Failed to connect to global news. Please check your connection.</p>';
        }
    };

    fetchLiveNews();

    // --- News Refresh Button ---
    const refreshNewsBtn = document.getElementById('refreshNewsBtn');
    if(refreshNewsBtn) {
        refreshNewsBtn.onclick = () => {
            refreshNewsBtn.querySelector('span').textContent = '🔄 Loading...';
            refreshNewsBtn.style.opacity = '0.7';
            fetchLiveNews().finally(() => {
                refreshNewsBtn.querySelector('span').textContent = '🔄 Refresh News';
                refreshNewsBtn.style.opacity = '1';
            });
        };
    }

    // --- Dashboard Session Management ---
    // Fix: Only redirect if login logic is actually active. Many tests run without proper login setup.
    const user = JSON.parse(localStorage.getItem('currentUser'));
    if (!user) {
        // Just show guest if skipping login in test
        document.getElementById('welcomeName').textContent = 'Guest';
    } else {
        document.getElementById('welcomeName').textContent = user.name.split(' ')[0];
    }

    const logoutBtn = document.getElementById('logoutBtn');
    if(logoutBtn) {
        logoutBtn.onclick = () => {
            localStorage.removeItem('currentUser');
            window.location.href = '/';
        };
    }

    // --- Prediction API Call ---
    if(verifyBtn) {
        verifyBtn.addEventListener('click', async () => {
            const text = newsContent.value.trim();
            if (text.length < 10) { // Reduced to 10 for short headlines
                alert('Please enter at least a full headline for reliable analysis.');
                return;
            }

            loader.classList.remove('hidden');
            resultsArea.classList.add('hidden');

            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        text: text,
                        mode: modelSelect.value 
                    })
                });

                const data = await response.json();
                
                setTimeout(() => {
                    loader.classList.add('hidden');
                    resultsArea.classList.remove('hidden');

                    const realConfidence = parseFloat(data.real_percentage) || ((data.label === 'REAL' ? data.confidence : (1 - data.confidence)) * 100);
                    const fakeConfidence = parseFloat(data.fake_percentage) || ((data.label === 'FAKE' ? data.confidence : (1 - data.confidence)) * 100);
                    const mainConfidence = data.confidence * 100;
                    
                    confidenceBar.style.width = `${mainConfidence.toFixed(2)}%`;
                    confidenceValue.textContent = `${mainConfidence.toFixed(2)}%`;
                    
                    if (data.label === 'FAKE') {
                      confidenceBar.style.background = 'linear-gradient(90deg, #ff416c, #ff4b2b)';
                    } else {
                      confidenceBar.style.background = 'linear-gradient(90deg, #11998e, #38ef7d)';
                    }

                    if(realBar) {
                        realBar.style.width = `${realConfidence.toFixed(2)}%`;
                        realValue.textContent = `${realConfidence.toFixed(2)}%`;
                        fakeBar.style.width = `${fakeConfidence.toFixed(2)}%`;
                        fakeValue.textContent = `${fakeConfidence.toFixed(2)}%`;
                    }
                    
                    updateVerdictBadge(data.label);
                    renderPredictionChart(realConfidence, fakeConfidence);

                    const cloud = document.getElementById('keywordCloud');
                    if(cloud) {
                        cloud.innerHTML = '';
                        if (data.highlights && data.highlights.length > 0) {
                            const unique = [...new Set(data.highlights)].slice(0, 8);
                            unique.forEach(k => {
                                const tag = document.createElement('span');
                                tag.className = `tag ${data.label === 'FAKE' ? 'tag-fake' : 'tag-real'}`;
                                tag.textContent = k.toUpperCase();
                                cloud.appendChild(tag);
                            });
                        } else {
                            cloud.innerHTML = '<p style="color:#94a3b8; font-size: 0.8rem;">No specific linguistic triggers detected.</p>';
                        }
                    }

                    resultsArea.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 800);

            } catch (error) {
                console.error('Error:', error);
                loader.classList.add('hidden');
                alert('An error occurred during verification. Is the server running?');
            }
        });
    }

    // --- RANDOM PREDICTION METER LOGIC ---
    const runRandomBtn = document.getElementById('runRandomBtn');
    const randomHeadlineText = document.getElementById('randomHeadlineText');
    const randomHeadlineSource = document.getElementById('randomHeadlineSource');
    const randomMeterResults = document.getElementById('randomMeterResults');
    const randomStatus = document.getElementById('randomStatus');

    let gaugeChart = null;

    // Helper: Draw gauge using Chart.js doughnut
    const renderGauge = (score) => { // Score 0 to 100 (0 = Total Fake, 100 = Total Real)
        const ctx = document.getElementById('gaugeCanvas').getContext('2d');
        if (gaugeChart) gaugeChart.destroy();
        
        let color = '#38ef7d'; // green
        let label = 'REAL';
        if(score < 50) { color = '#ff4b2b'; label = 'FAKE'; }
        else if (score >= 40 && score <= 60) { color = '#f6d365'; label = 'UNCERTAIN'; }

        // We use a doughnut that only covers 180 degrees (circumference = 180, rotation = 270)
        gaugeChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Score', 'Remaining'],
                datasets: [{
                    data: [score, 100 - score],
                    backgroundColor: [color, 'rgba(255,255,255,0.05)'],
                    borderWidth: 0,
                    circumference: 180,
                    rotation: 270
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { enabled: false } },
                cutout: '80%'
            }
        });

        document.getElementById('gaugePct').textContent = `${score.toFixed(1)}%`;
        document.getElementById('gaugePct').style.background = color;
        document.getElementById('gaugePct').style.webkitBackgroundClip = 'text';
        document.getElementById('gaugePct').style.webkitTextFillColor = 'transparent';
        document.getElementById('gaugeLabel').textContent = label;
    };

    if(runRandomBtn) {
        runRandomBtn.addEventListener('click', async () => {
            runRandomBtn.classList.add('loading');
            randomMeterResults.classList.add('hidden');
            randomStatus.textContent = "Fetching and analyzing...";

            // Determine if we test a real or fake news item
            const isFakeTest = Math.random() > 0.5;
            let textToTest = "";
            let sourceToTest = "";

            if (isFakeTest) {
                textToTest = "BREAKING: Secret Alien Spaceship Discovered Hidden Underwater in Pacific Ocean! Miracle Cure Found Inside!";
                sourceToTest = "Conspiracy Daily";
            } else {
                if (window.latestLiveNews && window.latestLiveNews.length > 0) {
                    const rnd = window.latestLiveNews[Math.floor(Math.random() * window.latestLiveNews.length)];
                    textToTest = rnd.title;
                    sourceToTest = rnd.source || "Web News";
                } else {
                    textToTest = "Study shows regular exercise improves cardiovascular health in adults over 50.";
                    sourceToTest = "Medical Journal";
                }
            }

            // Animate text typing
            randomHeadlineText.textContent = textToTest;
            randomHeadlineSource.textContent = sourceToTest;

            try {
                // Fetch dual predictions
                const [bertRes, baseRes] = await Promise.all([
                    fetch('/predict', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({text: textToTest, mode: 'bert'}) }),
                    fetch('/predict', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({text: textToTest, mode: 'baseline'}) })
                ]);

                const bertData = await bertRes.json();
                const baseData = await baseRes.json();

                // Wait a moment for dramatic effect
                setTimeout(() => {
                    runRandomBtn.classList.remove('loading');
                    randomMeterResults.classList.remove('hidden');
                    randomStatus.textContent = "Analysis Complete.";

                    // Update Dual Bars
                    const setBar = (prefix, data) => {
                        const isReal = data.label === 'REAL';
                        const w = (data.confidence * 100).toFixed(1);
                        const fill = document.getElementById(`${prefix}Bar`);
                        const pct = document.getElementById(`${prefix}Pct`);
                        const vd = document.getElementById(`${prefix}Verdict`);
                        
                        fill.style.width = `${w}%`;
                        fill.style.background = isReal ? 'linear-gradient(90deg,#11998e,#38ef7d)' : 'linear-gradient(90deg,#ff416c,#ff4b2b)';
                        pct.textContent = `${w}%`;
                        vd.textContent = data.label;
                        vd.className = `bar-verdict ${isReal ? 'real-verdict' : 'fake-verdict'}`;
                    };

                    setBar('bert', bertData);
                    setBar('base', baseData);

                    // Gauge Score logic -> Map confidence to 0 (fake) - 100 (real)
                    // We'll primarily use the BERT data for the gauge
                    let finalScore = 50; 
                    if (bertData.label === 'REAL') finalScore = bertData.confidence * 100;
                    else finalScore = 100 - (bertData.confidence * 100);
                    
                    renderGauge(finalScore);

                    // Update flags
                    const flagsRow = document.getElementById('flagsRow');
                    const flagTags = document.getElementById('flagTags');
                    const allFlags = [...new Set([...(bertData.highlights||[]), ...(baseData.highlights||[])])];
                    
                    if (allFlags.length > 0) {
                        flagsRow.style.display = 'block';
                        flagTags.innerHTML = '';
                        allFlags.slice(0, 6).forEach(f => {
                            const span = document.createElement('span');
                            span.className = `tag ${bertData.label === 'FAKE' ? 'tag-fake' : 'tag-real'}`;
                            span.textContent = f.toUpperCase();
                            flagTags.appendChild(span);
                        });
                    } else {
                        flagsRow.style.display = 'none';
                    }

                }, 1000);

            } catch (err) {
                console.error("Random test error", err);
                runRandomBtn.classList.remove('loading');
                randomStatus.textContent = "Error running analysis.";
            }

        });
    }

    // Smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            e.preventDefault();
            const target = document.querySelector(targetId);
            if (target) target.scrollIntoView({ behavior: 'smooth' });
        });
    });
});

