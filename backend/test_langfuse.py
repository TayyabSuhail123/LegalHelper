#!/usr/bin/env python3
"""
Test script to verify LangFuse integration is working correctly.
"""

import sys
import os
import asyncio

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings
from app.core.langfuse_integration import initialize_langfuse, trace_workflow, trace_agent_decorator


async def test_langfuse_integration():
    """Test LangFuse integration."""
    print("🔍 Testing LangFuse Integration...")
    print(f"📊 LangFuse Host: {settings.langfuse_host}")
    print(f"🔑 Public Key Set: {'✅' if settings.langfuse_public_key else '❌'}")
    print(f"🔐 Secret Key Set: {'✅' if settings.langfuse_secret_key else '❌'}")
    
    # Test client initialization
    print("\n🚀 Initializing LangFuse client...")
    client = initialize_langfuse()
    
    if client:
        print("✅ LangFuse client initialized successfully!")
        
        # Test workflow tracing with hierarchical structure
        print("\n📈 Testing hierarchical workflow tracing...")
        try:
            async with trace_workflow("test_workflow", {"test": "data"}) as trace:
                print("✅ Main workflow trace created!")
                
                # Test that events can be logged to the workflow
                from app.core.langfuse_integration import log_workflow_event
                log_workflow_event("workflow_started", {"agents": ["test_agent"]})
                
                await asyncio.sleep(0.1)  # Simulate some work
                print("✅ Workflow events logged!")
                
        except Exception as e:
            print(f"❌ Workflow tracing failed: {e}")
            return False
            
        # Test agent decorator within workflow context
        print("\n🤖 Testing agent spans within workflow...")
        try:
            async with trace_workflow("test_workflow_with_agents", {"test": "hierarchical"}) as trace:
                
                @trace_agent_decorator("test_agent")
                async def test_agent_function(data):
                    await asyncio.sleep(0.1)  # Simulate work
                    return {"processed": data, "progress_percentage": 100}
                
                result = await test_agent_function({"input": "test"})
                print("✅ Agent span created within workflow!")
                print(f"📤 Result: {result}")
            
        except Exception as e:
            print(f"❌ Agent decorator failed: {e}")
            return False
            
        print("\n🎉 LangFuse integration is working correctly!")
        return True
        
    else:
        print("❌ LangFuse client failed to initialize")
        print("💡 Check your environment variables:")
        print("   - LANGFUSE_PUBLIC_KEY")
        print("   - LANGFUSE_SECRET_KEY")
        print("   - LANGFUSE_HOST")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_langfuse_integration())
    if success:
        print("\n✨ All tests passed! LangFuse is ready to trace your agents.")
    else:
        print("\n💥 Tests failed! Please check the configuration.")
        sys.exit(1)
