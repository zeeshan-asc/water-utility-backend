"""
AquaSentinel Backend API
CFO Command Intelligence API for Financial, Operational, Billing & Compliance Oversight
"""

import os
import logging
import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from flask import jsonify, request, g, send_from_directory
from flask_cors import CORS
from vanna.flask import VannaFlaskApp
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import core modules
from core.logging_utils import setup_logging
from core.custom_vanna import MyVanna
from routes.dashboard_routes import dashboard_bp

# Initialize logging
api_logger, data_logger = setup_logging()

# Initialize custom Vanna instance
vn = MyVanna(config={
    'model': 'gpt-4o-mini',
    'temperature': 0.7,
})

# Configure Flask app using VannaFlaskApp (runs on port 8084 by default)
app = VannaFlaskApp(
    vn=vn,
    allow_llm_to_see_data=True,
    followup_questions=False,
    debug=False,
    title="AquaSentinel AI",
    subtitle="Your AI-powered water utility copilot",
    logo="/assets/local/aquasentinel-logo.jpg",
)

# Access the underlying Flask app for custom routes
flask_app = app.flask_app
flask_app.config['JSON_SORT_KEYS'] = False

# Static directory
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

# Configure CORS to allow requests from all origins
CORS(flask_app, 
     origins="*", 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
     supports_credentials=False)

# Add additional CORS headers manually to ensure they're set
@flask_app.after_request
def after_request(response):
    """Add CORS headers to all responses"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept,Origin')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'false')
    return response

# Register AI blueprint FIRST (before dashboard) to ensure it's checked before VannaFlaskApp's catch-all
# Make vn available to the blueprint via app context
flask_app.vn = vn
from routes.ai_routes import ai_bp
flask_app.register_blueprint(ai_bp)

# Register dashboard blueprint
flask_app.register_blueprint(dashboard_bp)

# Add before_request handler to ensure our custom routes are matched before catch-all
@flask_app.before_request
def check_custom_routes():
    """
    Ensure custom routes are checked before catch-all.
    This handler runs before route matching, so we can't prevent catch-all matching here,
    but we can ensure our routes are registered correctly.
    """
    # This is just for logging - Flask will match routes correctly
    if request.path.startswith('/api/v0/ai/') or request.path.startswith('/api/v0/dashboard/'):
        # Check if route exists
        adapter = flask_app.url_map.bind_to_environ(request.environ)
        try:
            endpoint, args = adapter.match()
            # Route exists and will be matched
            pass
        except Exception:
            # Route doesn't exist - will fall through to catch-all
            pass

# Remove VannaFlaskApp's catch-all route completely from URL map
# We need to do this multiple times because Flask may recreate it
catch_all_removed = False
max_attempts = 5

for attempt in range(max_attempts):
    catch_all_rules = [r for r in list(flask_app.url_map.iter_rules()) 
                       if r.endpoint == 'catch_all' and '<path:catch_all>' in r.rule]
    
    if not catch_all_rules:
        break
    
    for rule in catch_all_rules:
        try:
            flask_app.url_map._rules.remove(rule)
            catch_all_removed = True
        except (ValueError, AttributeError):
            pass
    
    # Force URL map remap
    flask_app.url_map._remap = True

# Remove or override the view function
if 'catch_all' in flask_app.view_functions:
    if catch_all_removed:
        del flask_app.view_functions['catch_all']
        api_logger.info("Removed VannaFlaskApp catch-all route and view function")
    else:
        # If we can't remove the route, override the function to forward requests
        api_logger.warning("Could not remove catch-all route - overriding function to forward requests")
        def forward_catch_all(catch_all):
            from flask import request
            # Try to match the route manually
            full_path = f"/api/v0/{catch_all}"
            try:
                adapter = flask_app.url_map.bind_to_environ(request.environ)
                endpoint, args = adapter.match(full_path, method=request.method)
                if endpoint in flask_app.view_functions and endpoint != 'catch_all':
                    api_logger.info(f"Catch-all forwarding POST request to: {endpoint}")
                    view_func = flask_app.view_functions[endpoint]
                    return view_func(**args)
            except Exception as e:
                api_logger.debug(f"Route matching failed: {e}")
            # Fall through to our catch-all handler
            from flask import jsonify
            return jsonify({
                "type": "error",
                "error": f"Route /api/v0/{catch_all} not found"
            }), 404
        
        flask_app.view_functions['catch_all'] = forward_catch_all

# Register our own catch-all AFTER all specific routes
# This ensures Flask checks specific routes first
@flask_app.route("/api/v0/<path:catch_all>", methods=["GET", "POST", "PUT", "DELETE"], endpoint='api_catch_all')
def api_catch_all(catch_all):
    """
    Catch-all for unmatched /api/v0/* routes.
    Returns appropriate error message.
    """
    from flask import jsonify
    
    # Check if this looks like it should be one of our routes
    if catch_all.startswith('ai/') or catch_all.startswith('dashboard/'):
        return jsonify({
            "type": "error",
            "error": f"Route /api/v0/{catch_all} not found. Check route registration."
        }), 404
    
    # For other routes, return VannaFlaskApp-style error
    return jsonify({
        "type": "error",
        "error": "The rest of the API is not ported yet."
    }), 200

# Add request logging middleware with Request IDs
@flask_app.before_request
def log_request_info():
    """Log incoming API requests with detailed information and Request ID."""
    g.start_time = time.time()
    g.request_id = str(uuid.uuid4())
    
    api_logger.info(f"=== API REQUEST START ===")
    api_logger.info(f"Request ID: {g.request_id}")
    api_logger.info(f"Method: {request.method}")
    api_logger.info(f"URL: {request.url}")
    api_logger.info(f"Remote Address: {request.remote_addr}")
    api_logger.info(f"User Agent: {request.headers.get('User-Agent', 'Unknown')}")
    
    # Log query parameters
    if request.args:
        api_logger.info(f"Query Parameters: {dict(request.args)}")
    
    # Log request body for POST requests
    if request.method == 'POST' and request.is_json:
        try:
            body = request.get_json()
            api_logger.info(f"Request Body: {json.dumps(body, indent=2)}")
        except Exception as e:
            api_logger.warning(f"Could not parse request body: {e}")

@flask_app.after_request
def log_response_info(response):
    """Log API responses with detailed information and Request ID."""
    if hasattr(g, 'start_time') and hasattr(g, 'request_id'):
        duration = time.time() - g.start_time
        
        api_logger.info(f"=== API RESPONSE ===")
        api_logger.info(f"Request ID: {g.request_id}")
        api_logger.info(f"Status Code: {response.status_code}")
        api_logger.info(f"Response Time: {duration:.3f}s")
        api_logger.info(f"Content Length: {response.content_length or 'Unknown'}")
        
        # Include Request ID in response headers
        response.headers['X-Request-ID'] = g.request_id
        
        # Log response content for debugging (truncated)
        if response.is_json:
            try:
                response_data = response.get_json()
                if response_data:
                    # Truncate large responses for logging
                    response_str = json.dumps(response_data, indent=2)
                    if len(response_str) > 1000:
                        response_str = response_str[:1000] + "... [TRUNCATED]"
                    api_logger.info(f"Response Content: {response_str}")
            except Exception as e:
                api_logger.warning(f"Could not parse response content: {e}")
        
        api_logger.info(f"=== API REQUEST END ===")
    
    return response

# Serve static assets
@flask_app.route("/assets/local/<path:filename>")
def serve_local_asset(filename: str):
    """
    Serve custom static assets from the project's static directory.
    """
    return send_from_directory(str(STATIC_DIR), filename)

# Favicon route
@flask_app.route('/favicon.ico')
def favicon():
    """Serve custom favicon for browser tab."""
    return send_from_directory(
        str(STATIC_DIR),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

# API info endpoint (VannaFlaskApp uses "/" for UI)
@flask_app.route("/api/info")
def api_info():
    """API information endpoint"""
    return jsonify({
        "message": "AquaSentinel API",
        "version": "1.0.0",
        "endpoints": {
            "kpis": "/api/v0/dashboard/kpis",
            "revenue": "/api/v0/dashboard/revenue/summary",
            "revenue_trends": "/api/v0/dashboard/revenue/trends",
            "budget_variance": "/api/v0/dashboard/budget-variance",
            "ar_aging": "/api/v0/dashboard/ar-aging",
            "debt": "/api/v0/dashboard/debt",
            "alerts": "/api/v0/dashboard/alerts",
            "scenarios": "/api/v0/dashboard/scenarios",
            "vanna_ui": "/",  # VannaFlaskApp provides UI at root
            "vanna_api": "/api/v0/vanna"  # VannaFlaskApp API endpoints
        }
    })

# Health check endpoint
@flask_app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

# Generate Summary endpoint (custom POST endpoint)
@flask_app.route("/api/v0/vanna/generate_summary", methods=['POST'])
def custom_generate_summary():
    """
    Generate natural language summary from SQL query results.
    
    Request Body:
        {
            "question": "What was the total revenue in 2024?",
            "sql": "SELECT SUM(actual_revenue) FROM water_data WHERE year = 2024",
            "data": [...]  // Optional: pre-executed data
        }
    
    Returns:
        JSON response with summary text
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Request must be JSON'
            }), 400
        
        data = request.get_json()
        question = data.get('question', '').strip()
        sql = data.get('sql', '').strip()
        provided_data = data.get('data')
        
        api_logger.info(f"[{g.request_id}] Generate summary requested")
        api_logger.info(f"[{g.request_id}] Question: {question[:100] if question else 'N/A'}")
        api_logger.info(f"[{g.request_id}] SQL: {sql[:100] if sql else 'N/A'}")
        
        # If data is provided, use it directly
        if provided_data:
            import pandas as pd
            df = pd.DataFrame(provided_data)
            api_logger.info(f"[{g.request_id}] Using provided data: {len(df)} rows")
        elif sql:
            # Execute SQL to get data
            api_logger.info(f"[{g.request_id}] Executing SQL to get data...")
            df = vn.run_sql(sql)
        else:
            return jsonify({
                'success': False,
                'error': 'Either "sql" or "data" must be provided'
            }), 400
        
        if df is None or df.empty:
            return jsonify({
                'success': True,
                'summary': 'No data available to summarize.',
                'question': question,
                'row_count': 0
            }), 200
        
        # Generate summary
        api_logger.info(f"[{g.request_id}] Generating summary from {len(df)} rows...")
        summary = vn.generate_summary(question=question, df=df)
        
        api_logger.info(f"[{g.request_id}] Summary generated successfully")
        
        return jsonify({
            'success': True,
            'summary': summary,
            'question': question,
            'sql': sql if sql else None,
            'row_count': len(df),
            'column_count': len(df.columns)
        }), 200
        
    except Exception as e:
        api_logger.error(f"[{g.request_id}] Error generating summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to generate summary: {str(e)}'
        }), 500


# Expose Flask app for WSGI servers (gunicorn, etc.)
application = flask_app  # Standard WSGI application name

# Run the application (for local development only)
if __name__ == "__main__":
    api_logger.info("=== AQUASENTINEL API STARTING ===")
    api_logger.info("Starting AquaSentinel API with VannaFlaskApp...")
    api_logger.info("Application URL: http://localhost:8084")
    api_logger.info("Vanna UI: http://localhost:8084")
    api_logger.info("CORS: Enabled for all origins")
    api_logger.info("Logging: Comprehensive logging enabled")
    api_logger.info("Log files: logs/aquasentinel_api.log, logs/aquasentinel_data.log")
    api_logger.info("=== APPLICATION READY ===")
    
    print("Starting AquaSentinel API with VannaFlaskApp...")
    print("Your app is running at: http://localhost:8084")
    print("Vanna UI available at: http://localhost:8084")
    print("CORS: Enabled for all origins")
    print("Logging: Comprehensive logging enabled")
    print("Log files: logs/aquasentinel_api.log, logs/aquasentinel_data.log")
    
    # VannaFlaskApp runs on port 8084 by default
    app.run(host='0.0.0.0', port=8084, debug=False)

