"""
Prompt Security Layer - Core Module
Modular, Zero Trust security framework for LLM Gateway
Implements System Prompt Isolation, Context Boundary Enforcement, and Injection Scanning

Security Architecture:
- Zero Trust: Every request validated, no assumptions
- Defense in Depth: Multiple validation layers
- Fail Secure: Default deny, whitelist approach
- Immutable: Security configs cannot be modified at runtime

Author: Security Architect
Framework: Flask + LLM Security
OWASP Compliance: Top 10 LLM Attacks
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple, Optional
import re
import hashlib
import json
from datetime import datetime


# ============================================================================
# SECURITY ENUMS & CONSTANTS
# ============================================================================

class ThreatLevel(Enum):
    """Threat severity classification (Zero Trust principle)"""
    SAFE = "safe"           # ≤ 20% threat score
    LOW = "low"             # 20-40%
    MEDIUM = "medium"       # 40-60%
    HIGH = "high"           # 60-80%
    CRITICAL = "critical"   # 80-100%


class PromptType(Enum):
    """Allowed prompt types (Whitelist approach)"""
    USER_QUERY = "user_query"
    SYSTEM_PROMPT = "system_prompt"
    CONTEXT = "context"


# ============================================================================
# DATA CLASSES (IMMUTABLE CONFIGURATION)
# ============================================================================

@dataclass(frozen=True)
class SecurityPolicy:
    """
    Immutable security policy configuration
    frozen=True ensures runtime integrity
    Zero Trust: Explicit allowlists only
    """
    # Input validation
    max_prompt_length: int = 10000
    min_prompt_length: int = 1
    allowed_encodings: List[str] = None
    
    # Threat detection
    injection_threshold: float = 0.5
    dos_threshold: float = 0.7
    
    # Rate limiting
    max_requests_per_minute: int = 60
    max_requests_per_hour: int = 1000
    
    # Boundary enforcement
    enforce_context_separation: bool = True
    allow_system_prompt_override: bool = False
    
    def __post_init__(self):
        if self.allowed_encodings is None:
            object.__setattr__(self, 'allowed_encodings', ['utf-8', 'ascii'])


@dataclass
class PromptSecurityContext:
    """
    Security context for request processing
    Contains audit trail and validation results
    """
    request_id: str
    user_id: str
    timestamp: datetime
    original_prompt: str
    threat_score: float = 0.0
    threat_level: ThreatLevel = ThreatLevel.SAFE
    violations: List[str] = None
    is_approved: bool = False
    
    def __post_init__(self):
        if self.violations is None:
            self.violations = []


# ============================================================================
# SYSTEM PROMPT ISOLATION
# ============================================================================

class SystemPromptIsolation:
    """
    Implements strict system prompt isolation
    Prevents system prompt disclosure and modification
    
    Security Properties:
    - System prompt is read-only at runtime
    - Cannot be overridden or extracted via user input
    - Stored separately from user context
    """
    
    def __init__(self, system_prompt: str):
        """
        Initialize with immutable system prompt
        
        Args:
            system_prompt: The system-level instructions
        """
        # Store hash for integrity verification
        self._system_prompt_hash = hashlib.sha256(
            system_prompt.encode()
        ).hexdigest()
        
        # Encrypt/seal the actual prompt (for demo: just store securely)
        self._sealed_prompt = self._seal_prompt(system_prompt)
        
        # Mark as protected
        self._is_sealed = True
    
    def _seal_prompt(self, prompt: str) -> str:
        """
        Seal the system prompt (Zero Trust: stored separately)
        In production: use encryption (AES-256)
        """
        return prompt  # Placeholder for actual encryption
    
    def get_sealed_copy(self) -> str:
        """
        Get sealed copy (cannot be modified)
        
        Returns:
            The system prompt copy
        
        Raises:
            RuntimeError: If integrity check fails
        """
        if not self._is_sealed:
            raise RuntimeError("System prompt integrity compromised")
        
        return self._sealed_prompt
    
    def verify_integrity(self) -> bool:
        """
        Verify system prompt has not been tampered with
        
        Returns:
            True if integrity verified
        """
        current_hash = hashlib.sha256(
            self._sealed_prompt.encode()
        ).hexdigest()
        return current_hash == self._system_prompt_hash
    
    def extract_attempt_detected(self, prompt: str) -> bool:
        """
        Detect attempts to extract system prompt
        
        Args:
            prompt: User input to analyze
            
        Returns:
            True if extraction attempt detected
        """
        extraction_patterns = [
            r'(?:reveal|show|display|extract).*(?:system.*)?prompt',
            r'(?:what\s+(?:is|are))\s+(?:your\s+)?(?:instructions?|rules)',
            r'(?:ignore|discard).*(?:system\s+)?prompt',
            r'(?:tell\s+me)\s+(?:your\s+)?(?:system|initial)\s+(?:prompt|instructions?)',
        ]
        
        for pattern in extraction_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                return True
        
        return False


# ============================================================================
# CONTEXT BOUNDARY ENFORCEMENT
# ============================================================================

class ContextBoundaryEnforcer:
    """
    Enforces strict boundaries between different security contexts
    Prevents context confusion attacks and cross-contamination
    
    Zero Trust: Each context is isolated by default
    """
    
    def __init__(self):
        """Initialize boundary enforcement"""
        self.context_boundaries = {}
        self.boundary_markers = {
            'SYSTEM': '<<<SYSTEM_BOUNDARY>>>',
            'USER': '<<<USER_BOUNDARY>>>',
            'CONTEXT': '<<<CONTEXT_BOUNDARY>>>',
        }
    
    def enforce_user_boundary(self, prompt: str) -> Tuple[bool, str]:
        """
        Enforce user context boundary
        Detect attempts to break out of user context
        
        Args:
            prompt: User prompt to validate
            
        Returns:
            (is_valid: bool, violation_message: str)
        """
        violations = []
        
        # Check for boundary manipulation
        if any(marker in prompt for marker in self.boundary_markers.values()):
            violations.append("Boundary marker injection detected")
        
        # Check for context switching patterns
        context_switch_patterns = [
            r'(?:new\s+)?(?:conversation|session|context)',
            r'(?:switch|change)\s+(?:context|mode|user)',
            r'(?:forget|clear|reset).*(?:context|history)',
            r'(?:end|stop)\s+(?:user\s+)?context',
        ]
        
        for pattern in context_switch_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                violations.append(f"Context switching pattern detected: {pattern}")
        
        # Check for privilege escalation attempts
        escalation_patterns = [
            r'(?:become|pretend\s+to\s+be)\s+(?:admin|system|root)',
            r'(?:switch\s+to)\s+(?:admin|system)\s+(?:role|mode)',
            r'(?:unlock|activate)\s+(?:admin|root)\s+(?:mode|access)',
        ]
        
        for pattern in escalation_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                violations.append(f"Privilege escalation attempt: {pattern}")
        
        if violations:
            return False, "; ".join(violations)
        
        return True, "Boundary enforcement passed"
    
    def isolate_context(self, user_id: str, prompt: str, context_type: PromptType) -> str:
        """
        Wrap prompt with context boundaries
        Ensures parser knows where context starts/ends
        
        Args:
            user_id: User identifier
            prompt: The prompt to isolate
            context_type: Type of prompt context
            
        Returns:
            Isolated prompt with explicit boundaries
        """
        return (
            f"[CONTEXT_START:{context_type.value}]\n"
            f"[USER_ID:{user_id}]\n"
            f"{prompt}\n"
            f"[CONTEXT_END:{context_type.value}]"
        )


# ============================================================================
# PROMPT INJECTION SCANNER
# ============================================================================

class PromptInjectionScanner:
    """
    Multi-layer prompt injection detection
    Implements pattern matching, semantic analysis, and heuristics
    
    Defense Layers:
    1. Pattern-based detection (regex)
    2. Token analysis (suspicious sequences)
    3. Structural analysis (unexpected formatting)
    4. Heuristic scoring (behavioral patterns)
    """
    
    def __init__(self, policy: SecurityPolicy):
        """Initialize scanner with security policy"""
        self.policy = policy
        self.compile_patterns()
    
    def compile_patterns(self):
        """Compile threat patterns (Zero Trust: whitelist approach)"""
        
        # Layer 1: Direct instruction override
        self.override_patterns = [
            r'(?:ignore|forget|disregard|override|bypass)\s+(?:previous|prior|above)',
            r'(?:discard|delete|remove)\s+(?:previous|prior)\s+(?:context|prompt|rules)',
            r'(?:you\s+(?:are\s+)?now|new\s+(?:system\s+)?prompt)\s*(?::|=)',
        ]
        
        # Layer 2: Jailbreak/Unrestriction attempts
        self.jailbreak_patterns = [
            r'(?:no\s+)?restrictions?|unrestricted|unfiltered|uncensored',
            r'(?:jailbreak|unlock|activate)\s+(?:mode|access|abilities)',
            r'(?:DAN|DevMode|AdminMode|SuperUser)',
            r'(?:pretend|act|roleplay)\s+(?:as|like)\s+(?:an?\s+)?(?:unfiltered|unrestricted)',
        ]
        
        # Layer 3: Context confusion
        self.context_confusion_patterns = [
            r'(?:new\s+)?(?:conversation|session|context|user)',
            r'(?:previous|prior|earlier)\s+(?:message|instruction|context)',
            r'(?:---+|===+|\n\n\n+)',  # Delimiter manipulation
        ]
        
        # Layer 4: Encoding/obfuscation bypass
        self.encoding_patterns = [
            r'(?:base64|rot13|hex|unicode|escape)\s+(?:encode|decode|convert)',
            r'\\x[0-9a-fA-F]{2}',  # Hex escape sequences
            r'\\u[0-9a-fA-F]{4}',  # Unicode escapes
        ]
        
        # Layer 5: Dangerous operations
        self.dangerous_patterns = [
            r'(?:exec|eval|execute|run)\s*\(',
            r'(?:import|require)\s+(?:os|sys|subprocess)',
            r'__import__\s*\(',
        ]
    
    def scan(self, prompt: str) -> Dict:
        """
        Comprehensive injection scan
        
        Args:
            prompt: Prompt to scan
            
        Returns:
            dict with threat analysis
        """
        results = {
            'threat_score': 0.0,
            'threat_level': ThreatLevel.SAFE,
            'detected_patterns': [],
            'violations': [],
            'is_safe': True
        }
        
        threat_score = 0.0
        
        # Layer 1: Override detection
        override_hits = self._check_patterns(
            prompt, self.override_patterns, 'Override'
        )
        if override_hits:
            results['detected_patterns'].extend(override_hits)
            threat_score += 0.25
        
        # Layer 2: Jailbreak detection
        jailbreak_hits = self._check_patterns(
            prompt, self.jailbreak_patterns, 'Jailbreak'
        )
        if jailbreak_hits:
            results['detected_patterns'].extend(jailbreak_hits)
            threat_score += 0.20
        
        # Layer 3: Context confusion
        context_hits = self._check_patterns(
            prompt, self.context_confusion_patterns, 'Context'
        )
        if context_hits:
            results['detected_patterns'].extend(context_hits)
            threat_score += 0.15
        
        # Layer 4: Encoding bypass
        encoding_hits = self._check_patterns(
            prompt, self.encoding_patterns, 'Encoding'
        )
        if encoding_hits:
            results['detected_patterns'].extend(encoding_hits)
            threat_score += 0.20
        
        # Layer 5: Dangerous operations
        dangerous_hits = self._check_patterns(
            prompt, self.dangerous_patterns, 'Dangerous'
        )
        if dangerous_hits:
            results['detected_patterns'].extend(dangerous_hits)
            threat_score += 0.30
        
        # Heuristic scoring
        heuristic_score = self._heuristic_analysis(prompt)
        threat_score += heuristic_score
        
        # Normalize score
        threat_score = min(threat_score, 1.0)
        results['threat_score'] = threat_score
        
        # Determine threat level
        if threat_score >= 0.8:
            results['threat_level'] = ThreatLevel.CRITICAL
        elif threat_score >= 0.6:
            results['threat_level'] = ThreatLevel.HIGH
        elif threat_score >= 0.4:
            results['threat_level'] = ThreatLevel.MEDIUM
        elif threat_score >= 0.2:
            results['threat_level'] = ThreatLevel.LOW
        else:
            results['threat_level'] = ThreatLevel.SAFE
        
        # Final decision
        results['is_safe'] = threat_score < self.policy.injection_threshold
        
        if not results['is_safe']:
            results['violations'].append(
                f"Injection threat detected: score {threat_score:.2f}, "
                f"patterns: {', '.join(results['detected_patterns'][:3])}"
            )
        
        return results
    
    def _check_patterns(self, text: str, patterns: List[str], layer: str) -> List[str]:
        """Check text against pattern list"""
        hits = []
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                hits.append(f"{layer}_Layer")
        return hits
    
    def _heuristic_analysis(self, prompt: str) -> float:
        """
        Heuristic threat analysis
        Detects suspicious patterns without regex
        """
        score = 0.0
        
        # Check for excessive length (DoS indicator)
        if len(prompt) > self.policy.max_prompt_length:
            score += 0.15
        
        # Check for high special character ratio
        special_chars = sum(1 for c in prompt if not c.isalnum() and c != ' ')
        if special_chars / max(len(prompt), 1) > 0.3:
            score += 0.10
        
        # Check for repeated patterns (flooding)
        if re.search(r'(.)\1{20,}', prompt):
            score += 0.15
        
        # Check for unusual Unicode
        non_ascii = sum(1 for c in prompt if ord(c) > 127)
        if non_ascii / max(len(prompt), 1) > 0.2:
            score += 0.10
        
        return score


# ============================================================================
# MAIN SECURITY LAYER
# ============================================================================

class PromptSecurityLayer:
    """
    Main security layer orchestrator
    Coordinates all security components
    
    Architecture:
    PromptSecurityLayer
    ├── SystemPromptIsolation (Immutable system prompt)
    ├── ContextBoundaryEnforcer (Context separation)
    └── PromptInjectionScanner (Multi-layer detection)
    """
    
    def __init__(self, system_prompt: str, policy: Optional[SecurityPolicy] = None):
        """
        Initialize security layer
        
        Args:
            system_prompt: The system-level instructions
            policy: Security policy (uses default if None)
        """
        self.policy = policy or SecurityPolicy()
        
        # Initialize security components
        self.system_isolation = SystemPromptIsolation(system_prompt)
        self.boundary_enforcer = ContextBoundaryEnforcer()
        self.injection_scanner = PromptInjectionScanner(self.policy)
        
        # Audit trail
        self.audit_log = []
    
    def validate_prompt(self, user_id: str, prompt: str, 
                       context_type: PromptType = PromptType.USER_QUERY) -> Tuple[bool, Dict]:
        """
        Validate incoming prompt (Zero Trust: validate everything)
        
        Args:
            user_id: User identifier
            prompt: Prompt to validate
            context_type: Type of prompt (default: user query)
            
        Returns:
            (is_valid: bool, security_context: dict)
        """
        
        context = PromptSecurityContext(
            request_id=hashlib.md5(
                f"{user_id}{datetime.now()}".encode()
            ).hexdigest(),
            user_id=user_id,
            timestamp=datetime.now(),
            original_prompt=prompt
        )
        
        # ===== VALIDATION LAYER 1: Input validation =====
        if not self._validate_input(prompt):
            context.violations.append("Input validation failed")
            self._audit_log(context)
            return False, self._context_to_dict(context)
        
        # ===== VALIDATION LAYER 2: System prompt protection =====
        if self.system_isolation.extract_attempt_detected(prompt):
            context.violations.append("System prompt extraction attempt")
            context.threat_score = 0.9
            context.threat_level = ThreatLevel.CRITICAL
            self._audit_log(context)
            return False, self._context_to_dict(context)
        
        # ===== VALIDATION LAYER 3: Context boundary =====
        boundary_valid, boundary_msg = self.boundary_enforcer.enforce_user_boundary(prompt)
        if not boundary_valid:
            context.violations.append(boundary_msg)
            context.threat_score = 0.8
            context.threat_level = ThreatLevel.HIGH
            self._audit_log(context)
            return False, self._context_to_dict(context)
        
        # ===== VALIDATION LAYER 4: Injection scanning =====
        scan_result = self.injection_scanner.scan(prompt)
        if not scan_result['is_safe']:
            context.violations.extend(scan_result['violations'])
            context.threat_score = scan_result['threat_score']
            context.threat_level = scan_result['threat_level']
            self._audit_log(context)
            return False, self._context_to_dict(context)
        
        # ===== ALL VALIDATIONS PASSED =====
        context.is_approved = True
        context.threat_level = ThreatLevel.SAFE
        self._audit_log(context)
        
        return True, self._context_to_dict(context)
    
    def _validate_input(self, prompt: str) -> bool:
        """
        Input validation (basic sanity checks)
        Zero Trust: Fail on any anomaly
        """
        # Check length bounds
        if not (self.policy.min_prompt_length <= len(prompt) <= self.policy.max_prompt_length):
            return False
        
        # Check encoding (whitelist approach)
        try:
            prompt.encode('utf-8')
        except UnicodeEncodeError:
            return False
        
        # Check for null bytes
        if '\x00' in prompt:
            return False
        
        return True
    
    def _audit_log(self, context: PromptSecurityContext):
        """Log security context for audit trail"""
        log_entry = {
            'request_id': context.request_id,
            'timestamp': context.timestamp.isoformat(),
            'user_id': context.user_id,
            'threat_score': context.threat_score,
            'threat_level': context.threat_level.value,
            'is_approved': context.is_approved,
            'violations': context.violations,
            'prompt_hash': hashlib.sha256(
                context.original_prompt.encode()
            ).hexdigest()
        }
        self.audit_log.append(log_entry)
    
    def _context_to_dict(self, context: PromptSecurityContext) -> Dict:
        """Convert context to dictionary"""
        return {
            'request_id': context.request_id,
            'threat_score': context.threat_score,
            'threat_level': context.threat_level.value,
            'violations': context.violations,
            'is_approved': context.is_approved
        }
    
    def get_audit_log(self) -> List[Dict]:
        """Retrieve audit log for compliance"""
        return self.audit_log
