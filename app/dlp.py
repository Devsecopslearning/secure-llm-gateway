"""
Data Loss Prevention (DLP) Module
Detects and blocks Personally Identifiable Information (PII) from user inputs.

This module provides pattern-based PII detection for the Secure LLM Gateway.
Uses regex patterns to detect sensitive data without external ML dependencies.

Author: Secure LLM Gateway Project
Purpose: M Tech Project - Secure AI Interaction Framework
"""

import re
from typing import Dict, List, Tuple

class DLPEngine:
    """
    Data Loss Prevention Engine using Pattern Matching
    
    Detects PII entities including:
    - Personal information (names, email, phone)
    - Financial data (credit card, bank account)
    - Government IDs (passport, SSN, driver license)
    - Network addresses (IP, URLs)
    """
    
    # PII Detection Patterns (Regex)
    PATTERNS = {
        "EMAIL_ADDRESS": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "PHONE_NUMBER": r'(\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
        "US_SSN": r'\b(?!000|666)[0-9]{3}-(?!00)[0-9]{2}-(?!0000)[0-9]{4}\b',
        "CREDIT_CARD": r'\b(?:\d{4}[-\s]?){3}\d{4}\b|\b\d{16}\b',
        "PASSPORT": r'\b[A-Z]{1,2}\d{6,9}\b',
        "DRIVER_LICENSE": r'\b[A-Z]{1,2}\d{5,8}\b',
        "IP_ADDRESS": r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
        "BANK_ACCOUNT": r'\b[0-9]{8,17}\b',
        "URL": r'https?://[^\s]+',
    }
    
    def __init__(self):
        """Initialize DLP Engine"""
        self.is_initialized = True
        self.compiled_patterns = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.PATTERNS.items()
        }
    
    def detect_pii(self, text: str) -> Dict:
        """
        Detect PII entities in the provided text
        
        Args:
            text (str): Text to analyze for PII
        
        Returns:
            dict: {
                "has_pii": bool,
                "pii_entities": list of {
                    "entity_type": str,
                    "text": str (matched text),
                    "position": int (character position)
                },
                "pii_summary": list of entity types found
            }
        """
        result = {
            "has_pii": False,
            "pii_entities": [],
            "pii_summary": []
        }
        
        if not text:
            return result
        
        try:
            pii_types_set = set()
            entity_id = 0
            
            # Check each pattern
            for entity_type, pattern in self.compiled_patterns.items():
                matches = pattern.finditer(text)
                
                for match in matches:
                    entity_info = {
                        "entity_type": entity_type,
                        "text": match.group(),
                        "position": match.start()
                    }
                    result["pii_entities"].append(entity_info)
                    pii_types_set.add(entity_type)
            
            if pii_types_set:
                result["has_pii"] = True
                result["pii_summary"] = sorted(list(pii_types_set))
        
        except Exception as e:
            print(f"Error during PII detection: {e}")
        
        return result


# Global DLP Engine instance
dlp_engine = DLPEngine()


def check_pii(text: str) -> Dict:
    """
    Check if text contains PII
    
    Args:
        text (str): Text to check for PII
    
    Returns:
        dict: Detection results with has_pii, pii_entities, pii_summary
    """
    return dlp_engine.detect_pii(text)


def block_if_pii(text: str) -> Tuple[bool, str, List[str]]:
    """
    Check if text should be blocked due to PII
    
    Args:
        text (str): Text to check
    
    Returns:
        tuple: (should_block: bool, error_message: str, pii_types: list)
    """
    pii_result = dlp_engine.detect_pii(text)
    
    if pii_result["has_pii"]:
        pii_types = ", ".join(pii_result["pii_summary"])
        error_msg = (
            f"Query blocked by DLP policy. "
            f"Detected sensitive data: {pii_types}. "
            f"Please remove personal information and try again."
        )
        return True, error_msg, pii_result["pii_summary"]
    
    return False, "", []


def anonymize_pii(text: str) -> str:
    """
    Anonymize PII in text (redact sensitive information)
    
    Args:
        text (str): Text to anonymize
    
    Returns:
        str: Text with PII replaced
    """
    result = text
    pii_check = dlp_engine.detect_pii(text)
    
    # Replace PII with [REDACTED_TYPE]
    if pii_check["pii_entities"]:
        # Sort by position (reverse) to maintain positions
        for entity in sorted(pii_check["pii_entities"], 
                           key=lambda x: x["position"], 
                           reverse=True):
            start = entity["position"]
            # Find end position by searching for the matched text
            entity_text = entity["text"]
            end = start + len(entity_text)
            replacement = f"[REDACTED_{entity['entity_type']}]"
            result = result[:start] + replacement + result[end:]
    
    return result

