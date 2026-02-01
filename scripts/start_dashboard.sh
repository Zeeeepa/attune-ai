#!/bin/bash
# Start the Empathy Dashboard (standalone version - direct Redis access)

cd "$(dirname "$0")/.."

echo "🚀 Starting Empathy Dashboard (Standalone)..."
echo "📊 Dashboard will be available at: http://localhost:8000"
echo ""
echo "💡 This version reads directly from Redis"
echo "   Make sure Redis is populated: python scripts/populate_redis_direct.py"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python -c "from src.empathy_os.dashboard import run_standalone_dashboard; run_standalone_dashboard()"
