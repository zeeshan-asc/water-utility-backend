"""
AI Routes for Natural Language to SQL Queries.

This module provides endpoints for AI-powered natural language queries
using Vanna AI, OpenAI GPT-4o, and Pinecone vector store.
"""

import logging
from flask import Blueprint, request, jsonify, g, current_app

logger = logging.getLogger('vanna.api')

# Create Blueprint for AI routes
ai_bp = Blueprint('ai', __name__, url_prefix='/api/v0/ai')


def get_vanna_instance():
    """Get Vanna instance from Flask app context."""
    # Try to get from app context (set by VannaFlaskApp)
    if hasattr(current_app, 'vn'):
        return current_app.vn
    
    # Fallback: try to get from app's vanna instance
    # This will be set when we register the blueprint
    if hasattr(current_app, 'extensions') and 'vanna' in current_app.extensions:
        return current_app.extensions['vanna']
    
    # Last resort: import from app module
    try:
        from app import vn
        return vn
    except ImportError:
        logger.error("Could not get Vanna instance")
        raise RuntimeError("Vanna instance not available")


@ai_bp.route('/ask', methods=['POST'])
def ask_question():
    """
    Ask a natural language question and get SQL + results.
    
    Request Body:
        {
            "question": "What was the total revenue in 2024?",
            "run_sql": true  // Optional: whether to execute SQL and return data
        }
    
    Returns:
        JSON response with SQL query, data (if run_sql=true), and summary
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Request must be JSON'
            }), 400
        
        data = request.get_json()
        question = data.get('question', '').strip()
        run_sql = data.get('run_sql', True)
        history = data.get('history')
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        logger.info(f"[{g.request_id}] AI question received: '{question[:100]}...' with {len(history) if history else 0} context turns")
        
        # Get Vanna instance
        vanna = get_vanna_instance()
        
        # Generate SQL with allow_llm_to_see_data=True and history
        logger.info(f"[{g.request_id}] Generating SQL for question...")
        sql = vanna.generate_sql(question, allow_llm_to_see_data=True, history=history)
        
        response_data = {
            'success': True,
            'question': question,
            'sql': sql,
            'type': 'sql' if vanna._last_response_type == 'sql' else 'text'
        }
        
        # Execute SQL if requested and SQL was generated
        if run_sql:
            if vanna._last_response_type == 'sql' and sql:
                # We have SQL - execute it first, then generate summary
                try:
                    logger.info(f"[{g.request_id}] Executing SQL query...")
                    df = vanna.run_sql(sql)
                    
                    # Convert DataFrame to JSON
                    response_data['data'] = df.to_dict('records')
                    response_data['row_count'] = len(df)
                    response_data['column_count'] = len(df.columns)
                    
                    # Generate summary after SQL execution
                    try:
                        logger.info(f"[{g.request_id}] Generating summary after SQL execution...")
                        summary = vanna.generate_summary(question=question, df=df)
                        response_data['summary'] = summary
                    except Exception as e:
                        logger.warning(f"[{g.request_id}] Could not generate summary: {str(e)}")
                        response_data['summary'] = None
                        
                except Exception as e:
                    logger.error(f"[{g.request_id}] SQL execution failed: {str(e)}")
                    response_data['error'] = f"SQL execution failed: {str(e)}"
                    response_data['data'] = None
                    response_data['summary'] = None
            else:
                # No SQL generated (text response) - generate summary directly
                logger.info(f"[{g.request_id}] No SQL generated, generating summary directly...")
                response_data['text'] = sql
                response_data['data'] = None
                response_data['row_count'] = 0
                response_data['column_count'] = 0
                
                # Try to generate summary from question only
                try:
                    import pandas as pd
                    empty_df = pd.DataFrame()
                    logger.info(f"[{g.request_id}] Generating summary from question...")
                    summary = vanna.generate_summary(question=question, df=empty_df)
                    response_data['summary'] = summary
                except Exception as e:
                    logger.warning(f"[{g.request_id}] Could not generate summary: {str(e)}")
                    response_data['summary'] = None
        else:
            # SQL only mode - don't execute or generate summary
            if vanna._last_response_type == 'text':
                response_data['text'] = sql
                response_data['data'] = None
            else:
                response_data['data'] = None
        
        logger.info(f"[{g.request_id}] AI question processed successfully")
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"[{g.request_id}] Error in AI ask endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/generate-sql', methods=['GET', 'POST'])
def generate_sql():
    """
    Generate SQL from natural language question (without executing).
    
    GET: Query Parameters:
        question (str): Natural language question
    
    POST: Request Body:
        {"question": "Natural language question"}
        
    Returns:
        JSON response with SQL query only
    """
    try:
        # Support both GET (query params) and POST (JSON body)
        if request.method == 'POST':
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Request must be JSON'
                }), 400
            data = request.get_json()
            question = data.get('question', '').strip()
        else:
            question = request.args.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question parameter is required'
            }), 400
        
        # Get history if provided
        history = data.get('history') if request.method == 'POST' else None
        
        logger.info(f"[{g.request_id}] Generate SQL requested: '{question[:100]}...' with {len(history) if history else 0} context turns")
        
        # Get Vanna instance
        vanna = get_vanna_instance()
        
        # Generate SQL with allow_llm_to_see_data=True and history
        sql = vanna.generate_sql(question, allow_llm_to_see_data=True, history=history)
        
        # Also generate the "Contextual Understanding" question if history exists
        contextual_question = None
        if history and len(history) > 0:
            contextual_question = vanna.contextualize_question(question, history=history)
        
        return jsonify({
            'success': True,
            'question': question,
            'contextual_question': contextual_question,
            'sql': sql,
            'type': 'sql' if vanna._last_response_type == 'sql' else 'text'
        }), 200
        
    except Exception as e:
        logger.error(f"[{g.request_id}] Error in generate SQL endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/run-sql', methods=['POST'])
def run_sql():
    """
    Execute a SQL query and return results with optional summary generation.
    
    Request Body:
        {
            "sql": "SELECT * FROM water_data WHERE year = 2024",
            "question": "What was the total revenue in 2024?",  // Optional: for summary generation
            "generate_summary": true  // Optional: whether to generate summary (default: true)
        }
        
    Returns:
        JSON response with query results and summary (if requested)
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Request must be JSON'
            }), 400
        
        data = request.get_json()
        sql = data.get('sql', '').strip()
        question = data.get('question', '').strip()
        generate_summary = data.get('generate_summary', True)
        
        # If no SQL provided, check if we should generate summary directly
        if not sql:
            if question and generate_summary:
                logger.info(f"[{g.request_id}] No SQL provided, generating summary from question...")
                vanna = get_vanna_instance()
                try:
                    # Try to generate a summary from the question directly
                    # Create an empty DataFrame for summary generation
                    import pandas as pd
                    empty_df = pd.DataFrame()
                    summary = vanna.generate_summary(question=question, df=empty_df)
                    return jsonify({
                        'success': True,
                        'sql': None,
                        'type': 'text',
                        'question': question,
                        'data': None,
                        'row_count': 0,
                        'column_count': 0,
                        'summary': summary
                    }), 200
                except Exception as e:
                    logger.warning(f"[{g.request_id}] Could not generate summary without SQL: {str(e)}")
                    return jsonify({
                        'success': False,
                        'error': 'SQL query is required'
                    }), 400
            else:
                return jsonify({
                    'success': False,
                    'error': 'SQL query is required'
                }), 400
        
        logger.info(f"[{g.request_id}] Running SQL query: '{sql[:100]}...'")
        
        # Get Vanna instance
        vanna = get_vanna_instance()
        
        # Execute SQL
        df = vanna.run_sql(sql)
        
        response_data = {
            'success': True,
            'sql': sql,
            'data': df.to_dict('records'),
            'row_count': len(df),
            'column_count': len(df.columns)
        }
        
        # Generate summary if requested and question is provided
        if generate_summary and question:
            try:
                logger.info(f"[{g.request_id}] Generating summary after SQL execution...")
                summary = vanna.generate_summary(question=question, df=df)
                response_data['summary'] = summary
            except Exception as e:
                logger.warning(f"[{g.request_id}] Could not generate summary: {str(e)}")
                response_data['summary'] = None
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"[{g.request_id}] Error in run SQL endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ai_bp.route('/health', methods=['GET'])
def health_check():
    """
    Check AI service health.
    
    Returns:
        JSON response with service status
    """
    try:
        # Try to initialize Vanna to check if everything is configured
        vanna = get_vanna_instance()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'service': 'Vanna AI',
            'database': 'connected',
            'vector_store': 'connected'
        }), 200
        
    except Exception as e:
        logger.error(f"AI health check failed: {str(e)}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500

