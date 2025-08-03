import requests
import sys
import json
from datetime import datetime

class NokodeAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.created_blueprint_id = None
        self.created_project_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        return success

    def test_get_agents(self):
        """Test getting all agents"""
        success, response = self.run_test(
            "Get All Agents",
            "GET", 
            "api/agents",
            200
        )
        if success and isinstance(response, list) and len(response) == 5:
            print(f"   Found {len(response)} agents as expected")
            # Test agent structure
            agent = response[0]
            required_fields = ['id', 'name', 'status', 'type', 'last_active']
            if all(field in agent for field in required_fields):
                print("   Agent structure is correct")
            else:
                print("   ⚠️  Agent structure missing required fields")
        return success

    def test_get_specific_agent(self):
        """Test getting specific agent"""
        success, response = self.run_test(
            "Get Specific Agent",
            "GET",
            "api/agents/1",
            200
        )
        if success and response.get('name') == 'FrontendAgent':
            print("   Correct agent retrieved")
        return success

    def test_update_agent_status(self):
        """Test updating agent status"""
        success, response = self.run_test(
            "Update Agent Status",
            "POST",
            "api/agents/1/status",
            200,
            data={"status": "busy"}
        )
        if success and response.get('status') == 'busy':
            print("   Agent status updated successfully")
        return success

    def test_get_blueprints(self):
        """Test getting all blueprints"""
        success, response = self.run_test(
            "Get All Blueprints",
            "GET",
            "api/blueprints", 
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} blueprints")
        return success

    def test_create_blueprint(self):
        """Test creating a new blueprint"""
        blueprint_data = {
            "name": "Test App",
            "description": "A test application blueprint",
            "components": [
                {"type": "header", "props": {"title": "Welcome"}},
                {"type": "button", "props": {"text": "Click me"}}
            ]
        }
        
        success, response = self.run_test(
            "Create Blueprint",
            "POST",
            "api/blueprints",
            200,
            data=blueprint_data
        )
        
        if success and 'id' in response:
            self.created_blueprint_id = response['id']
            print(f"   Blueprint created with ID: {self.created_blueprint_id}")
        return success

    def test_get_specific_blueprint(self):
        """Test getting specific blueprint"""
        if not self.created_blueprint_id:
            print("   ⚠️  No blueprint ID available, skipping test")
            return False
            
        success, response = self.run_test(
            "Get Specific Blueprint",
            "GET",
            f"api/blueprints/{self.created_blueprint_id}",
            200
        )
        
        if success and response.get('name') == 'Test App':
            print("   Correct blueprint retrieved")
        return success

    def test_generate_code(self):
        """Test code generation from blueprint"""
        if not self.created_blueprint_id:
            print("   ⚠️  No blueprint ID available, skipping test")
            return False
            
        # Test frontend code generation
        success_fe, response_fe = self.run_test(
            "Generate Frontend Code",
            "POST",
            "api/generate-code",
            200,
            data={"blueprint_id": self.created_blueprint_id, "target": "frontend"}
        )
        
        if success_fe and 'code' in response_fe and 'React' in response_fe['code']:
            print("   Frontend code generated successfully")
        
        # Test backend code generation
        success_be, response_be = self.run_test(
            "Generate Backend Code", 
            "POST",
            "api/generate-code",
            200,
            data={"blueprint_id": self.created_blueprint_id, "target": "backend"}
        )
        
        if success_be and 'code' in response_be and 'FastAPI' in response_be['code']:
            print("   Backend code generated successfully")
            
        return success_fe and success_be

    def test_get_projects(self):
        """Test getting all projects"""
        success, response = self.run_test(
            "Get All Projects",
            "GET",
            "api/projects",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} projects")
        return success

    def test_create_project(self):
        """Test creating a new project"""
        if not self.created_blueprint_id:
            print("   ⚠️  No blueprint ID available, skipping test")
            return False
            
        project_data = {
            "name": "Test Project",
            "blueprint_id": self.created_blueprint_id,
            "status": "active"
        }
        
        success, response = self.run_test(
            "Create Project",
            "POST",
            "api/projects",
            200,
            data=project_data
        )
        
        if success and 'id' in response:
            self.created_project_id = response['id']
            print(f"   Project created with ID: {self.created_project_id}")
        return success

    def test_get_analytics(self):
        """Test getting platform analytics"""
        success, response = self.run_test(
            "Get Analytics",
            "GET",
            "api/analytics",
            200
        )
        
        if success:
            expected_fields = ['total_agents', 'active_agents', 'total_blueprints', 'total_projects']
            if all(field in response for field in expected_fields):
                print("   Analytics data structure is correct")
                print(f"   Total agents: {response.get('total_agents')}")
                print(f"   Active agents: {response.get('active_agents')}")
            else:
                print("   ⚠️  Analytics missing some fields")
        return success

    def test_delete_blueprint(self):
        """Test deleting a blueprint"""
        if not self.created_blueprint_id:
            print("   ⚠️  No blueprint ID available, skipping test")
            return False
            
        success, response = self.run_test(
            "Delete Blueprint",
            "DELETE",
            f"api/blueprints/{self.created_blueprint_id}",
            200
        )
        
        if success and 'message' in response:
            print("   Blueprint deleted successfully")
        return success

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Nokode AgentOS API Tests")
        print("=" * 50)
        
        # Basic health and agent tests
        self.test_health_check()
        self.test_get_agents()
        self.test_get_specific_agent()
        self.test_update_agent_status()
        
        # Blueprint tests
        self.test_get_blueprints()
        self.test_create_blueprint()
        self.test_get_specific_blueprint()
        self.test_generate_code()
        
        # Project tests
        self.test_get_projects()
        self.test_create_project()
        
        # Analytics test
        self.test_get_analytics()
        
        # Cleanup
        self.test_delete_blueprint()
        
        # Print final results
        print("\n" + "=" * 50)
        print(f"📊 Final Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend API is working correctly.")
            return 0
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed.")
            return 1

def main():
    tester = NokodeAPITester("http://localhost:8001")
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())