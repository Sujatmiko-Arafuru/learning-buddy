"""Test chatbot service initialization and basic functionality"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 60)
print("TESTING CHATBOT SERVICE")
print("=" * 60)

try:
    print("\n1. Testing chatbot service import...")
    from services.chatbot_service import get_chatbot_service
    print("   ✓ Import successful")
    
    print("\n2. Getting chatbot instance...")
    chatbot = get_chatbot_service()
    print(f"   ✓ Chatbot instance created: {type(chatbot).__name__}")
    
    print("\n3. Checking chatbot components...")
    print(f"   LLM: {'✓ Initialized' if chatbot.llm else '✗ Not initialized'}")
    print(f"   Vector DB: {'✓ Loaded' if chatbot.vectordb else '✗ Not loaded'}")
    print(f"   Router Prompt: {'✓ Initialized' if chatbot.router_prompt else '✗ Not initialized'}")
    print(f"   Embedding Model: {'✓ Initialized' if chatbot.embedding_model else '✗ Not initialized'}")
    
    print("\n4. Testing simple chat...")
    test_email = "test@example.com"
    test_message = "halo"
    
    try:
        result = chatbot.chat(test_email, test_message)
        print(f"   ✓ Chat successful")
        print(f"   Response type: {result.get('type', 'unknown')}")
        print(f"   Response preview: {result.get('response', '')[:100]}...")
    except Exception as e:
        print(f"   ✗ Chat failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✓ ALL TESTS COMPLETED")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)

