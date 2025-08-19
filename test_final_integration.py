#!/usr/bin/env python3
"""
Final integration testing for Literate - Phase 7.4
Tests the complete system functionality across all components.
"""
import os
import sys
import subprocess
import time
from typing import List, Dict, Any
from llm_client import LLMClient
from object_manager import ObjectManager
from models import NarrativeObject
from tui_app import LiterateApp

class IntegrationTestSuite:
    """Comprehensive integration test suite for the complete system."""
    
    def __init__(self):
        self.test_results = []
        self.ollama_available = False
        self.openai_available = False
        self._check_providers()
    
    def _check_providers(self):
        """Check which LLM providers are available."""
        # Check Ollama
        try:
            client = LLMClient(provider="ollama")
            self.ollama_available = client.test_connection()
        except:
            pass
        
        # Check OpenAI
        try:
            if os.getenv("OPENAI_API_KEY"):
                client = LLMClient(provider="openai")
                self.openai_available = client.test_connection()
        except:
            pass
    
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result."""
        status = "✓ PASS" if passed else "✗ FAIL"
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"    {details}")
    
    def test_environment_setup(self) -> bool:
        """Test 1: Environment and dependencies."""
        print("\n=== Test 1: Environment Setup ===")
        
        # Check Python version
        if sys.version_info >= (3, 7):
            self.log_test("Python version >= 3.7", True, f"Python {sys.version}")
        else:
            self.log_test("Python version >= 3.7", False, f"Python {sys.version}")
            return False
        
        # Check required files
        required_files = ["main.py", "tui_app.py", "llm_client.py", "object_manager.py", 
                         "models.py", "requirements.txt", "README.md", "examples.md"]
        
        for file in required_files:
            if os.path.exists(file):
                self.log_test(f"File exists: {file}", True)
            else:
                self.log_test(f"File exists: {file}", False)
                return False
        
        # Check imports
        try:
            import requests
            import textual
            self.log_test("Core dependencies importable", True)
        except ImportError as e:
            self.log_test("Core dependencies importable", False, str(e))
            return False
        
        return True
    
    def test_llm_providers(self) -> bool:
        """Test 2: LLM Provider connectivity."""
        print("\n=== Test 2: LLM Provider Connectivity ===")
        
        at_least_one_working = False
        
        # Test Ollama
        if self.ollama_available:
            self.log_test("Ollama connection", True, "localhost:11434 accessible")
            at_least_one_working = True
        else:
            self.log_test("Ollama connection", False, "Server not accessible or model missing")
        
        # Test OpenAI
        if self.openai_available:
            self.log_test("OpenAI connection", True, "API key valid")
            at_least_one_working = True
        else:
            self.log_test("OpenAI connection", False, "API key missing or invalid")
        
        if not at_least_one_working:
            self.log_test("At least one provider working", False, "No LLM providers available")
            return False
        else:
            self.log_test("At least one provider working", True)
        
        return True
    
    def test_data_models(self) -> bool:
        """Test 3: Data models and object management."""
        print("\n=== Test 3: Data Models ===")
        
        try:
            # Test object creation
            from models import NarrativeObject, Relationship, ObjectCollection
            
            rel = Relationship("Bob", "friend")
            obj = NarrativeObject("Alice", "A person", [rel])
            self.log_test("Object creation", True)
            
            # Test collection
            collection = ObjectCollection()
            collection.add_or_update(obj)
            
            if len(collection.objects) == 1:
                self.log_test("Collection management", True)
            else:
                self.log_test("Collection management", False)
                return False
            
            # Test object manager
            manager = ObjectManager()
            test_response = '{"objects": [{"name": "Alice", "description": "A person", "relationships": []}]}'
            result = manager.process_text_update("Alice is here", test_response)
            
            if result["success"] and len(result["objects"]) == 1:
                self.log_test("Object manager processing", True)
            else:
                self.log_test("Object manager processing", False)
                return False
            
        except Exception as e:
            self.log_test("Data models", False, str(e))
            return False
        
        return True
    
    def test_llm_extraction(self) -> bool:
        """Test 4: LLM extraction functionality."""
        print("\n=== Test 4: LLM Extraction ===")
        
        test_text = "Alice met Bob at the coffee shop. They discussed their trip to Paris."
        
        # Test with available provider
        if self.ollama_available:
            try:
                client = LLMClient(provider="ollama")
                objects = client.extract_narrative_objects(test_text)
                
                if len(objects) > 0:
                    self.log_test("Ollama extraction", True, f"Extracted {len(objects)} objects")
                    
                    # Check for expected objects
                    object_names = [obj.name for obj in objects]
                    if any("Alice" in name or "Bob" in name for name in object_names):
                        self.log_test("Expected objects found", True)
                    else:
                        self.log_test("Expected objects found", False, f"Found: {object_names}")
                else:
                    self.log_test("Ollama extraction", False, "No objects extracted")
                    
            except Exception as e:
                self.log_test("Ollama extraction", False, str(e))
        
        if self.openai_available:
            try:
                client = LLMClient(provider="openai")
                objects = client.extract_narrative_objects(test_text)
                
                if len(objects) > 0:
                    self.log_test("OpenAI extraction", True, f"Extracted {len(objects)} objects")
                else:
                    self.log_test("OpenAI extraction", False, "No objects extracted")
                    
            except Exception as e:
                self.log_test("OpenAI extraction", False, str(e))
        
        return True
    
    def test_object_preservation(self) -> bool:
        """Test 5: Object preservation across updates."""
        print("\n=== Test 5: Object Preservation ===")
        
        try:
            manager = ObjectManager()
            
            # First update
            response1 = '{"objects": [{"name": "Alice", "description": "A person", "relationships": []}]}'
            result1 = manager.process_text_update("Alice is here", response1)
            
            # Second update with new object
            response2 = '{"objects": [{"name": "Bob", "description": "Another person", "relationships": []}]}'
            result2 = manager.process_text_update("Bob arrives", response2, preserve_existing=True)
            
            # Both objects should exist
            all_objects = manager.get_all_objects()
            object_names = [obj.name for obj in all_objects]
            
            if "Alice" in object_names and "Bob" in object_names:
                self.log_test("Object preservation", True, "Both Alice and Bob preserved")
            else:
                self.log_test("Object preservation", False, f"Objects: {object_names}")
                return False
            
        except Exception as e:
            self.log_test("Object preservation", False, str(e))
            return False
        
        return True
    
    def test_tui_creation(self) -> bool:
        """Test 6: TUI application creation."""
        print("\n=== Test 6: TUI Application ===")
        
        try:
            # Test Ollama TUI
            app_ollama = LiterateApp(llm_provider="ollama")
            self.log_test("TUI creation (Ollama)", True)
            
            # Test OpenAI TUI if available
            if os.getenv("OPENAI_API_KEY"):
                app_openai = LiterateApp(llm_provider="openai")
                self.log_test("TUI creation (OpenAI)", True)
            
            # Test provider assignment
            if app_ollama.llm_provider == "ollama":
                self.log_test("Provider assignment", True)
            else:
                self.log_test("Provider assignment", False)
                return False
            
        except Exception as e:
            self.log_test("TUI creation", False, str(e))
            return False
        
        return True
    
    def test_command_line_interface(self) -> bool:
        """Test 7: Command line interface."""
        print("\n=== Test 7: Command Line Interface ===")
        
        try:
            # Test help
            result = subprocess.run([sys.executable, "main.py", "--help"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and "--openai" in result.stdout:
                self.log_test("Command line help", True)
            else:
                self.log_test("Command line help", False, "Help not working or missing --openai")
                return False
            
        except Exception as e:
            self.log_test("Command line interface", False, str(e))
            return False
        
        return True
    
    def test_error_handling(self) -> bool:
        """Test 8: Error handling."""
        print("\n=== Test 8: Error Handling ===")
        
        try:
            # Test invalid provider
            try:
                client = LLMClient(provider="invalid")
                self.log_test("Invalid provider handling", False, "Should have raised error")
            except:
                self.log_test("Invalid provider handling", True)
            
            # Test missing API key for OpenAI
            old_key = os.environ.get("OPENAI_API_KEY")
            if old_key:
                del os.environ["OPENAI_API_KEY"]
            
            try:
                client = LLMClient(provider="openai")
                self.log_test("Missing API key handling", False, "Should have raised error")
            except ValueError:
                self.log_test("Missing API key handling", True)
            except Exception as e:
                self.log_test("Missing API key handling", False, f"Wrong error type: {e}")
            finally:
                if old_key:
                    os.environ["OPENAI_API_KEY"] = old_key
            
        except Exception as e:
            self.log_test("Error handling", False, str(e))
            return False
        
        return True
    
    def test_performance(self) -> bool:
        """Test 9: Basic performance."""
        print("\n=== Test 9: Performance ===")
        
        if not (self.ollama_available or self.openai_available):
            self.log_test("Performance test", False, "No LLM providers available")
            return False
        
        try:
            provider = "ollama" if self.ollama_available else "openai"
            client = LLMClient(provider=provider)
            
            # Test response time
            start_time = time.time()
            objects = client.extract_narrative_objects("Alice met Bob.")
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response_time < 30:  # Should complete within 30 seconds
                self.log_test("Response time", True, f"{response_time:.2f}s")
            else:
                self.log_test("Response time", False, f"{response_time:.2f}s (too slow)")
                return False
            
        except Exception as e:
            self.log_test("Performance test", False, str(e))
            return False
        
        return True
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests."""
        print("🧪 Starting Final Integration Test Suite for Literate")
        print("=" * 60)
        
        test_methods = [
            self.test_environment_setup,
            self.test_llm_providers,
            self.test_data_models,
            self.test_llm_extraction,
            self.test_object_preservation,
            self.test_tui_creation,
            self.test_command_line_interface,
            self.test_error_handling,
            self.test_performance
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                if test_method():
                    passed_tests += 1
            except Exception as e:
                print(f"✗ FAIL: {test_method.__name__} crashed: {e}")
        
        # Summary
        print("\n" + "=" * 60)
        print("🏁 FINAL INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.ollama_available:
            print("✓ Ollama provider available")
        else:
            print("⚠ Ollama provider not available")
        
        if self.openai_available:
            print("✓ OpenAI provider available")
        else:
            print("⚠ OpenAI provider not available")
        
        # Detailed results
        print("\nDetailed Results:")
        for result in self.test_results:
            status = "✓" if result["passed"] else "✗"
            print(f"  {status} {result['test']}")
            if result["details"]:
                print(f"    {result['details']}")
        
        # Overall assessment
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! System is ready for production.")
            return {"status": "success", "passed": passed_tests, "total": total_tests}
        elif passed_tests >= total_tests * 0.8:
            print("\n⚠️  Most tests passed. System is functional with minor issues.")
            return {"status": "partial", "passed": passed_tests, "total": total_tests}
        else:
            print("\n❌ Multiple test failures. System needs attention before deployment.")
            return {"status": "failure", "passed": passed_tests, "total": total_tests}

def main():
    """Run the integration test suite."""
    suite = IntegrationTestSuite()
    result = suite.run_all_tests()
    
    # Exit with appropriate code
    if result["status"] == "success":
        sys.exit(0)
    elif result["status"] == "partial":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()