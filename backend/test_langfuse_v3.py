#!/usr/bin/env python3
"""
Test LangFuse hierarchical tracing with the new v3 SDK.
"""

import asyncio
import time
from langfuse import observe, get_client

# Test the new @observe decorator approach
@observe(name="legal_document_analysis")
async def test_workflow():
    """Test workflow with hierarchical tracing."""
    print("Starting workflow...")
    
    # Simulate some workflow setup
    await asyncio.sleep(0.1)
    
    # Run agent tasks
    result1 = await test_text_extraction()
    result2 = await test_document_summarizer()
    result3 = await test_risk_assessment()
    result4 = await test_fraud_detection()
    result5 = await test_legal_advisor()
    result6 = await test_action_planner()
    
    print("Workflow completed!")
    return {
        "text_extraction": result1,
        "document_summarizer": result2,
        "risk_assessment": result3,
        "fraud_detection": result4,
        "legal_advisor": result5,
        "action_planner": result6
    }

@observe(name="text_extraction")
async def test_text_extraction():
    """Test text extraction agent."""
    print("  Running text extraction...")
    await asyncio.sleep(0.1)
    return "Text extracted successfully"

@observe(name="document_summarizer")
async def test_document_summarizer():
    """Test document summarizer agent."""
    print("  Running document summarizer...")
    await asyncio.sleep(0.1)
    return "Document summarized successfully"

@observe(name="risk_assessment")
async def test_risk_assessment():
    """Test risk assessment agent."""
    print("  Running risk assessment...")
    await asyncio.sleep(0.1)
    return "Risk assessment completed"

@observe(name="fraud_detection")
async def test_fraud_detection():
    """Test fraud detection agent."""
    print("  Running fraud detection...")
    await asyncio.sleep(0.1)
    return "Fraud detection completed"

@observe(name="legal_advisor")
async def test_legal_advisor():
    """Test legal advisor agent."""
    print("  Running legal advisor...")
    await asyncio.sleep(0.1)
    return "Legal advice generated"

@observe(name="action_planner")
async def test_action_planner():
    """Test action planner agent."""
    print("  Running action planner...")
    await asyncio.sleep(0.1)
    return "Action plan created"

async def main():
    """Main test function."""
    print("Testing LangFuse v3 hierarchical tracing...")
    
    # Run the workflow
    result = await test_workflow()
    print(f"Workflow result: {result}")
    
    # Flush events to LangFuse
    client = get_client()
    client.flush()
    print("LangFuse events flushed")

if __name__ == "__main__":
    asyncio.run(main())
