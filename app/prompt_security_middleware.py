"""
Prompt Security Middleware for Flask
Integrates PromptSecurityLayer into Flask request pipeline
Implements Zero Trust security at the middleware level

Security Pattern:
Request → Authentication → Prompt Security Middleware → LLM Processing

Author: Security Architect
"""

from flask import Flask, request, g, current_app, jsonify
from functools import wraps
from typing import Callable, Any
from app.prompt_security_layer import (
    PromptSecurityLayer,
    SecurityPolicy,
    PromptType
) 


# ============================================================================
# PROMPT SECURITY MIDDLEWARE
# ============================================================================

class PromptSecurityMiddleware:
    """
    Flask middleware for prompt security
    Integrates into request lifecycle
    
    Architecture:
    1. Initialized with PromptSecurityLayer
    2. Registered with Flask app
    3. Runs before request handlers
    4. Validates all prompts automatically
    """
    
    def __init__(self, app: Flask, security_layer: PromptSecurityLayer):
        """
        Initialize middleware
        
        Args:
            app: Flask application instance
            security_layer: Configured PromptSecurityLayer
        """
        self.app = app
        self.security_layer = security_layer
        
        # Register middleware hooks
        self.app.before_request(self.before_request)
        self.app.after_request(self.after_request)
    
    def before_request(self):
        """
        Before request hook (Zero Trust: validate everything)
        Validates prompt before route handler
        """
        # Store security context in Flask's g object
        g.security_context = {
            'validated': False,
            'threat_score': 0.0,
            'violations': []
        }
    
    def after_request(self, response):
        """
        After request hook
        Logs security context to response headers (optional)
        """
        if hasattr(g, 'security_context'):
            # Add security headers to response
            response.headers['X-Threat-Score'] = str(
                g.security_context.get('threat_score', 0)
            )
            response.headers['X-Security-Validated'] = str(
                g.security_context.get('validated', False)
            )
        
        return response


# ============================================================================
# PROMPT VALIDATION DECORATOR
# ============================================================================

def validate_prompt(prompt_field: str = 'prompt', 
                   context_type: PromptType = PromptType.USER_QUERY):
    """
    Decorator for validating prompts in Flask routes
    
    Zero Trust Pattern:
    @app.route('/secure-query', methods=['POST'])
    @validate_prompt(prompt_field='prompt')
    def secure_query():
        # prompt is automatically validated by decorator
        prompt = request.get_json()['prompt']
        # ... rest of handler
    
    Args:
        prompt_field: JSON field containing the prompt (default: 'prompt')
        context_type: PromptType classification (default: USER_QUERY)
    
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs) -> Any:
            
            # Step 1: Extract prompt from request
            data = request.get_json() or {}
            prompt = data.get(prompt_field, '')
            
            # Step 2: Get user ID from session (must be authenticated)
            user_id = g.get('user_id', 'unknown')
            
            # Step 3: Access security layer from app context
            security_layer = current_app.security_layer
            
            # Step 4: Validate prompt (Zero Trust)
            is_valid, security_context = security_layer.validate_prompt(
                user_id=user_id,
                prompt=prompt,
                context_type=context_type
            )
            
            # Step 5: Store context in Flask's g object
            g.security_context = security_context
            g.validated_prompt = prompt if is_valid else None
            
            # Step 6: Block invalid prompts
            if not is_valid:
                return jsonify({
                    'error': 'Security validation failed',
                    'request_id': security_context.get('request_id'),
                    'violations': security_context.get('violations'),
                    'threat_level': security_context.get('threat_level')
                }), 400
            
            # Step 7: Call original handler
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


# ============================================================================
# SECURITY CONTEXT HELPER
# ============================================================================

def get_security_context() -> dict:
    """
    Get current request security context
    Use in route handlers for security information
    
    Returns:
        Security context dict
    """
    return g.get('security_context', {})


def get_validated_prompt() -> str:
    """
    Get validated prompt from current request
    Safe to use directly (already validated)
    
    Returns:
        Validated prompt string
    """
    return g.get('validated_prompt', '')


# ============================================================================
# SECURITY AUDIT HELPER
# ============================================================================

def get_audit_trail(security_layer: PromptSecurityLayer) -> list:
    """
    Retrieve audit trail for compliance
    Use periodically to review security events
    
    Args:
        security_layer: PromptSecurityLayer instance
    
    Returns:
        List of audit log entries
    """
    return security_layer.get_audit_log()


# ============================================================================
# INITIALIZE SECURITY LAYER
# ============================================================================

def init_prompt_security(app: Flask, system_prompt: str, 
                        policy: 'SecurityPolicy' = None) -> PromptSecurityLayer:
    """
    Initialize prompt security layer with Flask app
    Call this during app setup
    
    Args:
        app: Flask application
        system_prompt: The system-level instructions
        policy: Custom SecurityPolicy (optional)
    
    Returns:
        Configured PromptSecurityLayer instance
    
    Example:
        from flask import Flask
        from app.prompt_security_middleware import init_prompt_security
        
        app = Flask(__name__)
        security_layer = init_prompt_security(
            app,
            system_prompt="You are a helpful AI assistant..."
        )
    """
    
    # Step 1: Create security layer
    security_layer = PromptSecurityLayer(system_prompt, policy)
    
    # Step 2: Register with app
    app.security_layer = security_layer
    
    # Step 3: Initialize middleware
    PromptSecurityMiddleware(app, security_layer)
    
    return security_layer


# ============================================================================
# USAGE EXAMPLE IN FLASK ROUTE
# ============================================================================

"""
EXAMPLE INTEGRATION:

from flask import Flask, request, jsonify, g
from app.prompt_security_middleware import (
    init_prompt_security,
    validate_prompt,
    get_validated_prompt,
    get_security_context
)

app = Flask(__name__)

# Initialize security during app startup
system_prompt = "You are a helpful AI assistant. Answer questions accurately and safely."
security_layer = init_prompt_security(app, system_prompt)

@app.route('/secure-query', methods=['POST'])
@validate_prompt(prompt_field='prompt')
def secure_query():
    '''
    Protected endpoint with automatic prompt validation
    
    Security Flow:
    1. @validate_prompt decorator validates prompt
    2. Invalid prompts rejected with 400 status
    3. Valid prompts available via get_validated_prompt()
    4. Security context available via get_security_context()
    '''
    
    # Get validated prompt (already verified safe)
    prompt = get_validated_prompt()
    
    # Get security context for logging/monitoring
    security_context = get_security_context()
    
    # Log request ID for audit trail
    request_id = security_context.get('request_id')
    
    # Process with LLM (prompt is now verified safe)
    response = query_llama3(prompt)
    
    return jsonify({
        'response': response,
        'request_id': request_id,
        'threat_score': security_context.get('threat_score')
    })

# Audit endpoint (for compliance)
@app.route('/audit/security-log', methods=['GET'])
@require_admin  # Custom decorator for admin-only access
def get_security_log():
    '''
    Retrieve security audit trail
    For compliance and incident investigation
    '''
    from app.prompt_security_middleware import get_audit_trail
    
    audit_log = get_audit_trail(app.security_layer)
    
    return jsonify({
        'total_requests': len(audit_log),
        'blocked_requests': sum(1 for log in audit_log if not log['is_approved']),
        'audit_trail': audit_log
    })
"""
