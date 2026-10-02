from pathlib import Path

from orkunkaan_unal_tncgroup_51internationalprojecttrainingprogram_akillisatisdanismaniprojesi import create_app

root = Path(__file__).resolve().parents[1]
app = create_app('development', {
    'DATABASE_URL': str(root / 'work' / 'preview.db'),
    'AI_PROVIDER': 'demo', 'GROQ_API_KEY': '',
    'ADMIN_API_TOKEN': 'orkun-yerel-demo',
    'SECRET_KEY': 'local-preview-only-no-production-secrets',
    'RATE_LIMIT_PER_MINUTE': 500,
    'CORS_ORIGINS': ['http://127.0.0.1:5055'],
})
app.run(host='127.0.0.1', port=5055, debug=False, use_reloader=False)