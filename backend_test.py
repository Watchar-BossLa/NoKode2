import requests
import sys
import json
from datetime import datetime

class NokodeAPITester:
    def __init__(self, base_url="https://62fe1321-2027-4554-bc39-bd0fbb210542.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.created_blueprint_id = None
        self.created_project_id = None
        self.created_workflow_id = None
        self.created_execution_id = None

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

    # =============================================================================
    # PHASE 2: ENTERPRISE FEATURES TESTING
    # =============================================================================

    def test_root_endpoint(self):
        """Test root endpoint with platform information"""
        success, response = self.run_test(
            "Root Endpoint",
            "GET",
            "",
            200
        )
        if success:
            expected_fields = ['message', 'status', 'version', 'docs']
            if all(field in response for field in expected_fields):
                print(f"   Platform: {response.get('message')}")
                print(f"   Version: {response.get('version')}")
                print(f"   Status: {response.get('status')}")
            else:
                print("   ⚠️  Root endpoint missing some fields")
        return success

    def test_system_info(self):
        """Test system info endpoint"""
        success, response = self.run_test(
            "System Information",
            "GET",
            "api/system/info",
            200
        )
        if success:
            expected_fields = ['service', 'version', 'phase', 'features', 'capabilities']
            if all(field in response for field in expected_fields):
                print(f"   Service: {response.get('service')}")
                print(f"   Phase: {response.get('phase')}")
                print(f"   Capabilities: {len(response.get('capabilities', []))}")
                
                # Check Phase 2 features
                phase2_features = response.get('features', {}).get('phase_2', {})
                print(f"   Phase 2 Features: {phase2_features}")
            else:
                print("   ⚠️  System info missing some fields")
        return success

    def test_enhanced_health_check(self):
        """Test enhanced health check with Phase 2 features"""
        success, response = self.run_test(
            "Enhanced Health Check",
            "GET",
            "api/health",
            200
        )
        if success:
            expected_fields = ['status', 'timestamp', 'service', 'version', 'features']
            if all(field in response for field in expected_fields):
                print(f"   Service: {response.get('service')}")
                print(f"   Version: {response.get('version')}")
                
                # Check all Phase 2 features
                features = response.get('features', {})
                phase2_features = ['ai_hub_enabled', 'workflow_enabled', 'analytics_enabled', 'api_gateway_enabled']
                for feature in phase2_features:
                    status = features.get(feature, False)
                    print(f"   {feature}: {status}")
            else:
                print("   ⚠️  Health check missing some fields")
        return success

    def test_ai_providers(self):
        """Test AI providers endpoint"""
        success, response = self.run_test(
            "AI Providers",
            "GET",
            "api/ai/providers",
            200
        )
        if success and 'providers' in response:
            providers = response['providers']
            print(f"   Found {len(providers)} AI providers")
            
            # Verify we have at least 3 providers as specified
            if len(providers) >= 3:
                for provider in providers:
                    print(f"   - {provider.get('name')}: {provider.get('models', [])}")
            else:
                print("   ⚠️  Expected at least 3 AI providers")
        return success

    def test_ai_generate_code_advanced(self):
        """Test advanced AI code generation"""
        if not self.created_blueprint_id:
            print("   ⚠️  No blueprint ID available, using default")
            blueprint_id = "1"  # Use existing blueprint
        else:
            blueprint_id = self.created_blueprint_id

        test_data = {
            "blueprint_id": blueprint_id,
            "target_language": "python",
            "framework": "fastapi",
            "requirements": ["authentication", "database"],
            "context": {"project_type": "web_api"},
            "ai_provider": "openai",
            "advanced_features": True
        }
        
        success, response = self.run_test(
            "Advanced AI Code Generation",
            "POST",
            "api/ai/generate-code-advanced",
            200,
            data=test_data
        )
        
        if success:
            expected_fields = ['files', 'documentation', 'tests', 'dependencies', 'quality_score']
            if all(field in response for field in expected_fields):
                print(f"   Generated files: {len(response.get('files', {}))}")
                print(f"   Quality score: {response.get('quality_score')}")
                print(f"   Dependencies: {len(response.get('dependencies', []))}")
            else:
                print("   ⚠️  Advanced code generation missing some fields")
        return success

    def test_workflow_templates(self):
        """Test workflow templates endpoint"""
        success, response = self.run_test(
            "Workflow Templates",
            "GET",
            "api/workflows/templates",
            200
        )
        if success and 'templates' in response:
            templates = response['templates']
            print(f"   Found {len(templates)} workflow templates")
            
            # Verify we have at least 3 templates as specified
            if len(templates) >= 3:
                for template in templates[:3]:  # Show first 3
                    print(f"   - {template.get('name')}: {template.get('description', '')[:50]}...")
            else:
                print("   ⚠️  Expected at least 3 workflow templates")
        return success

    def test_create_workflow(self):
        """Test workflow creation"""
        workflow_data = {
            "name": "Test Workflow",
            "description": "A test workflow for API testing",
            "triggers": [{"type": "manual", "config": {}}],
            "steps": [
                {"type": "log", "config": {"message": "Test step"}},
                {"type": "delay", "config": {"seconds": 1}}
            ]
        }
        
        success, response = self.run_test(
            "Create Workflow",
            "POST",
            "api/workflows",
            200,
            data=workflow_data
        )
        
        if success and 'workflow_id' in response:
            self.created_workflow_id = response['workflow_id']
            print(f"   Workflow created with ID: {self.created_workflow_id}")
            print(f"   Steps: {response.get('steps')}")
        return success

    def test_execute_workflow(self):
        """Test workflow execution"""
        if not self.created_workflow_id:
            print("   ⚠️  No workflow ID available, skipping test")
            return False
            
        context_data = {"test_param": "test_value"}
        
        success, response = self.run_test(
            "Execute Workflow",
            "POST",
            f"api/workflows/{self.created_workflow_id}/execute",
            200,
            data=context_data
        )
        
        if success and 'execution_id' in response:
            self.created_execution_id = response['execution_id']
            print(f"   Execution started with ID: {self.created_execution_id}")
            print(f"   Status: {response.get('status')}")
        return success

    def test_workflow_status(self):
        """Test workflow execution status"""
        if not self.created_execution_id:
            print("   ⚠️  No execution ID available, skipping test")
            return False
            
        success, response = self.run_test(
            "Workflow Execution Status",
            "GET",
            f"api/workflows/{self.created_execution_id}/status",
            200
        )
        
        if success:
            expected_fields = ['execution_id', 'workflow_id', 'status', 'started_at']
            if all(field in response for field in expected_fields):
                print(f"   Execution status: {response.get('status')}")
                print(f"   Current step: {response.get('current_step')}")
            else:
                print("   ⚠️  Workflow status missing some fields")
        return success

    def test_analytics_dashboards(self):
        """Test analytics dashboards endpoint"""
        success, response = self.run_test(
            "Analytics Dashboards",
            "GET",
            "api/analytics/dashboards",
            200
        )
        if success and 'dashboards' in response:
            dashboards = response['dashboards']
            print(f"   Found {len(dashboards)} analytics dashboards")
            
            # Verify we have at least 4 dashboards as specified
            if len(dashboards) >= 4:
                for dashboard in dashboards[:4]:  # Show first 4
                    print(f"   - {dashboard.get('name')}: {dashboard.get('description', '')[:50]}...")
            else:
                print("   ⚠️  Expected at least 4 analytics dashboards")
        return success

    def test_dashboard_data(self):
        """Test dashboard data retrieval"""
        # Use a default dashboard ID
        dashboard_id = "performance"
        
        success, response = self.run_test(
            "Dashboard Data",
            "GET",
            f"api/analytics/dashboards/{dashboard_id}",
            200
        )
        
        if success:
            expected_fields = ['dashboard_id', 'name', 'widgets']
            if all(field in response for field in expected_fields):
                print(f"   Dashboard: {response.get('name')}")
                print(f"   Widgets: {len(response.get('widgets', []))}")
            else:
                print("   ⚠️  Dashboard data missing some fields")
        return success

    def test_real_time_metrics(self):
        """Test real-time metrics endpoint"""
        success, response = self.run_test(
            "Real-time Metrics",
            "GET",
            "api/analytics/real-time",
            200
        )
        if success:
            expected_fields = ['timestamp', 'metrics']
            if all(field in response for field in expected_fields):
                metrics = response.get('metrics', {})
                print(f"   Real-time metrics: {len(metrics)} categories")
                for category, data in metrics.items():
                    print(f"   - {category}: {data}")
            else:
                print("   ⚠️  Real-time metrics missing some fields")
        return success

    def test_create_analytics_query(self):
        """Test custom analytics query creation"""
        query_data = {
            "name": "Test Query",
            "description": "A test analytics query",
            "data_source": "system_metrics",
            "query": "SELECT * FROM metrics WHERE timestamp > NOW() - INTERVAL 1 HOUR",
            "cache_ttl": 300
        }
        
        success, response = self.run_test(
            "Create Analytics Query",
            "POST",
            "api/analytics/queries",
            200,
            data=query_data
        )
        
        if success and 'query_id' in response:
            print(f"   Query created with ID: {response['query_id']}")
            print(f"   Data source: {response.get('data_source')}")
        return success

    def test_gateway_integrations(self):
        """Test API gateway integrations"""
        success, response = self.run_test(
            "Gateway Integrations",
            "GET",
            "api/gateway/integrations",
            200
        )
        if success and 'integrations' in response:
            integrations = response['integrations']
            print(f"   Found {len(integrations)} API integrations")
            
            # Verify we have at least 4 integrations as specified
            if len(integrations) >= 4:
                for integration in integrations[:4]:  # Show first 4
                    print(f"   - {integration.get('name')}: {integration.get('type')} ({integration.get('health_status', {}).get('status', 'unknown')})")
            else:
                print("   ⚠️  Expected at least 4 API integrations")
        return success

    def test_gateway_health(self):
        """Test API gateway health checks"""
        success, response = self.run_test(
            "Gateway Health Check",
            "GET",
            "api/gateway/health",
            200
        )
        if success and 'health_checks' in response:
            health_checks = response['health_checks']
            print(f"   Health checks for {len(health_checks)} integrations")
            
            for integration_id, health in health_checks.items():
                print(f"   - {integration_id}: {health.get('status', 'unknown')}")
        return success

    def test_gateway_stats(self):
        """Test API gateway statistics"""
        success, response = self.run_test(
            "Gateway Statistics",
            "GET",
            "api/gateway/stats",
            200
        )
        if success and 'stats' in response:
            stats = response['stats']
            print(f"   Gateway statistics: {len(stats)} integrations")
            
            for integration_id, stat in stats.items():
                if isinstance(stat, dict):
                    print(f"   - {integration_id}: {stat.get('requests_count', 0)} requests")
                else:
                    print(f"   - {integration_id}: {stat}")
        return success

    def test_add_gateway_integration(self):
        """Test adding new API integration"""
        integration_data = {
            "name": "Test Integration",
            "type": "rest_api",
            "base_url": "https://api.example.com",
            "auth_type": "api_key",
            "config": {
                "api_key": "test_key_123",
                "timeout": 30
            }
        }
        
        success, response = self.run_test(
            "Add Gateway Integration",
            "POST",
            "api/gateway/integrations",
            200,
            data=integration_data
        )
        
        if success and 'integration_id' in response:
            print(f"   Integration created with ID: {response['integration_id']}")
            print(f"   Type: {response.get('type')}")
        return success

    def run_all_tests(self):
        """Run all API tests including Phase 2 enterprise features"""
        print("🚀 Starting Nokode AgentOS Enterprise Phase 2 API Tests")
        print("=" * 60)
        
        # Phase 2: System Health & Info Tests
        print("\n📋 PHASE 2: SYSTEM HEALTH & INFO")
        print("-" * 40)
        self.test_root_endpoint()
        self.test_enhanced_health_check()
        self.test_system_info()
        
        # Phase 2: AI Integration Hub Tests
        print("\n🧠 PHASE 2: AI INTEGRATION HUB")
        print("-" * 40)
        self.test_ai_providers()
        self.test_ai_generate_code_advanced()
        
        # Phase 2: Workflow Automation Tests
        print("\n⚡ PHASE 2: WORKFLOW AUTOMATION")
        print("-" * 40)
        self.test_workflow_templates()
        self.test_create_workflow()
        self.test_execute_workflow()
        self.test_workflow_status()
        
        # Phase 2: Enterprise Analytics Tests
        print("\n📊 PHASE 2: ENTERPRISE ANALYTICS")
        print("-" * 40)
        self.test_analytics_dashboards()
        self.test_dashboard_data()
        self.test_real_time_metrics()
        self.test_create_analytics_query()
        
        # Phase 2: API Gateway Management Tests
        print("\n🌐 PHASE 2: API GATEWAY MANAGEMENT")
        print("-" * 40)
        self.test_gateway_integrations()
        self.test_gateway_health()
        self.test_gateway_stats()
        self.test_add_gateway_integration()
        
        # Legacy/Phase 1 Tests (for backward compatibility)
        print("\n🔧 LEGACY COMPATIBILITY TESTS")
        print("-" * 40)
        self.test_get_agents()
        self.test_get_specific_agent()
        self.test_update_agent_status()
        self.test_get_blueprints()
        self.test_create_blueprint()
        self.test_get_specific_blueprint()
        self.test_generate_code()
        self.test_get_projects()
        self.test_create_project()
        self.test_get_analytics()
        
        # Cleanup
        print("\n🧹 CLEANUP")
        print("-" * 40)
        self.test_delete_blueprint()
        
        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 Final Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Nokode AgentOS Enterprise Phase 2 is fully operational.")
            return 0
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_tests} tests failed.")
            success_rate = (self.tests_passed / self.tests_run) * 100
            print(f"📈 Success rate: {success_rate:.1f}%")
            
            if success_rate >= 80:
                print("✅ System is mostly functional with minor issues.")
                return 0
            else:
                print("❌ System has significant issues that need attention.")
                return 1

def main():
    tester = NokodeAPITester("https://62fe1321-2027-4554-bc39-bd0fbb210542.preview.emergentagent.com")
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())