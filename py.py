from flask import Flask, render_template_string, jsonify
import random
from datetime import datetime

app = Flask(__name__)

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ImpactMapper - Citizen Science for Societal Resilience</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #1a1a1a;
            overflow-x: hidden;
        }

        .hero {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
            color: white;
            padding: 80px 20px 120px;
            position: relative;
            overflow: hidden;
        }

        .hero::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><circle cx="2" cy="2" r="1" fill="rgba(255,255,255,0.1)"/></svg>');
            background-size: 50px 50px;
            opacity: 0.3;
            animation: float 20s infinite linear;
        }

        @keyframes float {
            from { transform: translateY(0); }
            to { transform: translateY(-100px); }
        }

        nav {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 0;
            position: relative;
            z-index: 10;
        }

        .logo {
            font-size: 28px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .logo-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #3b82f6, #06b6d4);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }

        .nav-links {
            display: flex;
            gap: 30px;
            list-style: none;
        }

        .nav-links a {
            color: white;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s;
            padding: 8px 16px;
            border-radius: 6px;
        }

        .nav-links a:hover {
            background: rgba(255,255,255,0.1);
            transform: translateY(-2px);
        }

        .hero-content {
            max-width: 1400px;
            margin: 80px auto 0;
            position: relative;
            z-index: 10;
        }

        h1 {
            font-size: 64px;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 24px;
            background: linear-gradient(135deg, #ffffff 0%, #94a3b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .mission {
            font-size: 22px;
            line-height: 1.6;
            margin-bottom: 40px;
            color: #cbd5e1;
            max-width: 800px;
        }

        .pillars {
            display: flex;
            gap: 20px;
            margin-bottom: 50px;
            flex-wrap: wrap;
        }

        .pillar {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            padding: 12px 24px;
            border-radius: 50px;
            font-weight: 600;
            font-size: 16px;
            border: 2px solid rgba(255,255,255,0.2);
            transition: all 0.3s;
        }

        .pillar:hover {
            background: rgba(255,255,255,0.2);
            transform: scale(1.05);
        }

        .cta-buttons {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }

        .btn {
            padding: 16px 32px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 18px;
            cursor: pointer;
            transition: all 0.3s;
            border: none;
            text-decoration: none;
            display: inline-block;
        }

        .btn-primary {
            background: linear-gradient(135deg, #3b82f6, #06b6d4);
            color: white;
            box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);
        }

        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(59, 130, 246, 0.4);
        }

        .btn-secondary {
            background: rgba(255,255,255,0.1);
            color: white;
            border: 2px solid rgba(255,255,255,0.3);
        }

        .btn-secondary:hover {
            background: rgba(255,255,255,0.2);
            transform: translateY(-3px);
        }

        .stats {
            background: white;
            padding: 60px 20px;
            margin-top: -60px;
            position: relative;
            z-index: 5;
        }

        .stats-container {
            max-width: 1400px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 40px;
            background: white;
            padding: 50px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        }

        .stat {
            text-align: center;
            padding: 20px;
            border-radius: 12px;
            transition: all 0.3s;
        }

        .stat:hover {
            transform: translateY(-5px);
            background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        }

        .stat-number {
            font-size: 48px;
            font-weight: 800;
            color: #0369a1;
            margin-bottom: 8px;
            font-variant-numeric: tabular-nums;
        }

        .stat-label {
            font-size: 16px;
            color: #64748b;
            font-weight: 500;
        }

        .features {
            padding: 100px 20px;
            background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
        }

        .features-container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .section-title {
            text-align: center;
            font-size: 48px;
            font-weight: 800;
            margin-bottom: 60px;
            color: #0f172a;
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 40px;
        }

        .feature-card {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.06);
            transition: all 0.4s;
            border: 2px solid transparent;
        }

        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 60px rgba(0,0,0,0.12);
            border-color: #3b82f6;
        }

        .feature-icon {
            width: 70px;
            height: 70px;
            background: linear-gradient(135deg, #3b82f6, #06b6d4);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            margin-bottom: 24px;
        }

        .feature-title {
            font-size: 26px;
            font-weight: 700;
            margin-bottom: 16px;
            color: #0f172a;
        }

        .feature-description {
            font-size: 16px;
            color: #475569;
            line-height: 1.7;
        }

        .audience {
            padding: 100px 20px;
            background: #0f172a;
            color: white;
        }

        .audience-container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .audience-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: center;
            margin-top: 50px;
        }

        .audience-tag {
            background: rgba(59, 130, 246, 0.2);
            border: 2px solid #3b82f6;
            padding: 20px 30px;
            border-radius: 50px;
            font-weight: 600;
            font-size: 18px;
            transition: all 0.3s;
        }

        .audience-tag:hover {
            background: #3b82f6;
            transform: scale(1.05);
        }

        .cta-section {
            padding: 100px 20px;
            background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
            color: white;
            text-align: center;
        }

        .cta-content {
            max-width: 800px;
            margin: 0 auto;
        }

        .cta-section h2 {
            font-size: 48px;
            font-weight: 800;
            margin-bottom: 24px;
        }

        .cta-section p {
            font-size: 20px;
            margin-bottom: 40px;
            opacity: 0.95;
        }

        footer {
            background: #0f172a;
            color: white;
            padding: 60px 20px 30px;
        }

        .footer-content {
            max-width: 1400px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 40px;
            margin-bottom: 40px;
        }

        .footer-section h3 {
            font-size: 20px;
            margin-bottom: 20px;
            color: #3b82f6;
        }

        .footer-section ul {
            list-style: none;
        }

        .footer-section ul li {
            margin-bottom: 12px;
        }

        .footer-section a {
            color: #cbd5e1;
            text-decoration: none;
            transition: color 0.3s;
        }

        .footer-section a:hover {
            color: #3b82f6;
        }

        .footer-bottom {
            max-width: 1400px;
            margin: 0 auto;
            padding-top: 30px;
            border-top: 1px solid rgba(255,255,255,0.1);
            text-align: center;
            color: #64748b;
        }

        @media (max-width: 768px) {
            h1 {
                font-size: 40px;
            }

            .mission {
                font-size: 18px;
            }

            .features-grid {
                grid-template-columns: 1fr;
            }

            .nav-links {
                display: none;
            }

            .stats-container {
                padding: 30px 20px;
            }
        }

        @keyframes countup {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .stat-number {
            animation: countup 0.8s ease-out;
        }
    </style>
</head>
<body>
    <section class="hero">
        <nav>
            <div class="logo">
                <div class="logo-icon">🗺️</div>
                ImpactMapper
            </div>
            <ul class="nav-links">
                <li><a href="#features">Features</a></li>
                <li><a href="#audience">Community</a></li>
                <li><a href="#data">Open Data</a></li>
                <li><a href="#about">About</a></li>
            </ul>
        </nav>

        <div class="hero-content">
            <h1>Citizen Science for<br>Societal Resilience</h1>
            <p class="mission">
                Fostering data-driven social impact and community resilience by connecting researchers, citizens, and policymakers through interactive platforms and verifiable, crowdsourced data.
            </p>

            <div class="pillars">
                <span class="pillar">🛡️ Resilience</span>
                <span class="pillar">📚 Education</span>
                <span class="pillar">🔍 Transparency</span>
            </div>

            <div class="cta-buttons">
                <a href="#features" class="btn btn-primary">Explore Platforms</a>
                <a href="#data" class="btn btn-secondary">Access Open Data</a>
            </div>
        </div>
    </section>

    <section class="stats">
        <div class="stats-container">
            <div class="stat">
                <div class="stat-number" id="stat-1">{{ stats.disaster_reports }}</div>
                <div class="stat-label">Validated Disaster Reports</div>
            </div>
            <div class="stat">
                <div class="stat-number" id="stat-2">{{ stats.citizen_scientists }}</div>
                <div class="stat-label">Active Citizen Scientists</div>
            </div>
            <div class="stat">
                <div class="stat-number" id="stat-3">{{ stats.certifications }}</div>
                <div class="stat-label">Digital Literacy Certifications</div>
            </div>
            <div class="stat">
                <div class="stat-number" id="stat-4">{{ stats.policies_analyzed }}</div>
                <div class="stat-label">Policies Analyzed</div>
            </div>
            <div class="stat">
                <div class="stat-number" id="stat-5">{{ stats.datasets }}</div>
                <div class="stat-label">Open Datasets Available</div>
            </div>
        </div>
    </section>

    <section class="features" id="features">
        <div class="features-container">
            <h2 class="section-title">Three Powerful Platforms</h2>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">🚨</div>
                    <h3 class="feature-title">Live Disaster Response Mapping</h3>
                    <p class="feature-description">
                        A dynamic map merging real-time crowdsourced reports verified by citizen scientists with high-resolution satellite imagery and official emergency data. Provides actionable intelligence for first responders during critical moments.
                    </p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">📱</div>
                    <h3 class="feature-title">DigiPath Learning Hub</h3>
                    <p class="feature-description">
                        An offline-first, gamified mobile application offering educational modules focused on digital literacy, financial inclusion, and basic health information designed specifically for underserved rural communities.
                    </p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3 class="feature-title">Policy Visualizer Dashboard</h3>
                    <p class="feature-description">
                        Transform complex Open Government Data into accessible insights. Visualize budget allocations, policy outcomes, and public service metrics through simplified graphs and regional comparisons to enhance accountability.
                    </p>
                </div>
            </div>
        </div>
    </section>

    <section class="audience" id="audience">
        <div class="audience-container">
            <h2 class="section-title">Join Our Global Community</h2>
            <div class="audience-grid">
                <div class="audience-tag">👥 Citizen Scientists</div>
                <div class="audience-tag">🏛️ NGOs & Aid Organizations</div>
                <div class="audience-tag">🏢 Local Government</div>
                <div class="audience-tag">📚 Rural Learners</div>
                <div class="audience-tag">🔬 Academic Researchers</div>
                <div class="audience-tag">⚖️ Policymakers</div>
            </div>
        </div>
    </section>

    <section class="cta-section" id="data">
        <div class="cta-content">
            <h2>Ready to Make an Impact?</h2>
            <p>Join thousands of citizens, researchers, and organizations using data to build more resilient communities.</p>
            <div class="cta-buttons" style="justify-content: center;">
                <a href="#" class="btn btn-secondary">Get Started</a>
                <a href="#" class="btn btn-primary" style="background: white; color: #3b82f6;">Download Data</a>
            </div>
        </div>
    </section>

    <footer>
        <div class="footer-content">
            <div class="footer-section">
                <h3>Platforms</h3>
                <ul>
                    <li><a href="#">Disaster Response Map</a></li>
                    <li><a href="#">DigiPath Learning Hub</a></li>
                    <li><a href="#">Policy Visualizer</a></li>
                </ul>
            </div>
            <div class="footer-section">
                <h3>Resources</h3>
                <ul>
                    <li><a href="#">Open Datasets</a></li>
                    <li><a href="#">API Documentation</a></li>
                    <li><a href="#">Research Papers</a></li>
                    <li><a href="#">Training Materials</a></li>
                </ul>
            </div>
            <div class="footer-section">
                <h3>Community</h3>
                <ul>
                    <li><a href="#">Become a Citizen Scientist</a></li>
                    <li><a href="#">Partner Organizations</a></li>
                    <li><a href="#">Success Stories</a></li>
                    <li><a href="#">Events & Workshops</a></li>
                </ul>
            </div>
            <div class="footer-section">
                <h3>About</h3>
                <ul>
                    <li><a href="#">Our Mission</a></li>
                    <li><a href="#">Technology Stack</a></li>
                    <li><a href="#">Contact Us</a></li>
                    <li><a href="#">Careers</a></li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; 2025 ImpactMapper. Empowering communities through open data and citizen science.</p>
        </div>
    </footer>

    <script>
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });

        const featureCards = document.querySelectorAll('.feature-card');
        featureCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-10px) scale(1.02)';
            });
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0) scale(1)';
            });
        });

        // Auto-refresh stats every 30 seconds
        setInterval(() => {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('stat-1').textContent = data.disaster_reports.toLocaleString();
                    document.getElementById('stat-2').textContent = data.citizen_scientists.toLocaleString();
                    document.getElementById('stat-3').textContent = data.certifications.toLocaleString();
                    document.getElementById('stat-4').textContent = data.policies_analyzed.toLocaleString();
                    document.getElementById('stat-5').textContent = data.datasets.toLocaleString();
                });
        }, 30000);
    </script>
</body>
</html>
'''


class ImpactMapperData:
    """Data layer for ImpactMapper statistics and metrics"""
    
    def __init__(self):
        self.base_stats = {
            'disaster_reports': 12847,
            'citizen_scientists': 3521,
            'certifications': 8934,
            'policies_analyzed': 247,
            'datasets': 156
        }
    
    def get_live_stats(self):
        """Simulate live statistics with small random variations"""
        return {
            'disaster_reports': self.base_stats['disaster_reports'] + random.randint(0, 50),
            'citizen_scientists': self.base_stats['citizen_scientists'] + random.randint(0, 20),
            'certifications': self.base_stats['certifications'] + random.randint(0, 30),
            'policies_analyzed': self.base_stats['policies_analyzed'] + random.randint(0, 5),
            'datasets': self.base_stats['datasets'] + random.randint(0, 3)
        }


# Initialize data layer
data_layer = ImpactMapperData()


@app.route('/')
def index():
    """Main landing page"""
    stats = data_layer.get_live_stats()
    return render_template_string(HTML_TEMPLATE, stats=stats)


@app.route('/api/stats')
def api_stats():
    """API endpoint for live statistics"""
    return jsonify(data_layer.get_live_stats())


@app.route('/api/disaster-reports')
def api_disaster_reports():
    """API endpoint for disaster report data"""
    # Simulate disaster report data
    reports = [
        {
            'id': i,
            'location': f'Location {i}',
            'type': random.choice(['Flood', 'Earthquake', 'Fire', 'Storm']),
            'severity': random.choice(['Low', 'Medium', 'High', 'Critical']),
            'verified': random.choice([True, False]),
            'timestamp': datetime.now().isoformat()
        }
        for i in range(1, 11)
    ]
    return jsonify(reports)


@app.route('/api/certifications')
def api_certifications():
    """API endpoint for certification data"""
    certifications = {
        'total': data_layer.get_live_stats()['certifications'],
        'by_category': {
            'Digital Literacy': random.randint(3000, 4000),
            'Financial Inclusion': random.randint(2000, 3000),
            'Health Information': random.randint(2000, 2500)
        },
        'monthly_growth': random.randint(150, 250)
    }
    return jsonify(certifications)


@app.route('/api/policies')
def api_policies():
    """API endpoint for policy analysis data"""
    policies = [
        {
            'id': i,
            'title': f'Policy Initiative {i}',
            'category': random.choice(['Education', 'Healthcare', 'Infrastructure', 'Environment']),
            'budget': random.randint(1000000, 10000000),
            'impact_score': round(random.uniform(5.0, 9.5), 1),
            'region': random.choice(['North', 'South', 'East', 'West', 'Central'])
        }
        for i in range(1, 11)
    ]
    return jsonify(policies)


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'ImpactMapper API'
    })


if __name__ == '__main__':
    print("🗺️  ImpactMapper Server Starting...")
    print("📍 Access the application at: http://127.0.0.1:5000")
    print("📊 API Endpoints:")
    print("   - GET /api/stats - Live statistics")
    print("   - GET /api/disaster-reports - Disaster reports data")
    print("   - GET /api/certifications - Certification data")
    print("   - GET /api/policies - Policy analysis data")
    print("   - GET /health - Health check")
    print("\n🚀 Starting development server...\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)