#!/bin/bash

# Comprehensive testing script for Atlas-Chat application
# This script runs tests for all components and identifies issues

echo "Starting comprehensive testing process..."

# Create a test results directory
RESULTS_DIR="./test_results_$(date +%Y%m%d_%H%M%S)"
mkdir -p $RESULTS_DIR

echo "Created test results directory: $RESULTS_DIR"

# Function to log test results
log_test_result() {
        local test_name=$1
        local status=$2
        local details=$3

        echo "[$status] $test_name: $details" >>"$RESULTS_DIR/test_results.log"
        echo "[$status] $test_name: $details"
}

# Function to test backend API endpoints
test_backend_api() {
        echo "Testing backend API endpoints..."

        # Check if backend is running
        if ! curl -s http://localhost:8000/api/health >/dev/null; then
                log_test_result "Backend Health Check" "FAIL" "Backend is not running"
                return 1
        fi

        # Test authentication endpoints
        echo "Testing authentication endpoints..."
        AUTH_RESULT=$(curl -s -X POST http://localhost:8000/api/auth/token -H "Content-Type: application/json" -d '{"username":"test","password":"test"}')

        if [[ $AUTH_RESULT == *"error"* ]]; then
                log_test_result "Authentication API" "FAIL" "Authentication endpoint returned error"
        else
                log_test_result "Authentication API" "PASS" "Authentication endpoint working correctly"
        fi

        # Test code execution endpoints
        echo "Testing code execution endpoints..."
        CODE_RESULT=$(curl -s -X POST http://localhost:8000/api/code/execute -H "Content-Type: application/json" -d '{"code":"print(\"Hello, World!\")","language":"python"}')

        if [[ $CODE_RESULT == *"error"* ]]; then
                log_test_result "Code Execution API" "FAIL" "Code execution endpoint returned error"
        else
                log_test_result "Code Execution API" "PASS" "Code execution endpoint working correctly"
        fi

        # Test artifact endpoints
        echo "Testing artifact endpoints..."
        ARTIFACT_RESULT=$(curl -s -X GET http://localhost:8000/api/artifacts)

        if [[ $ARTIFACT_RESULT == *"error"* ]]; then
                log_test_result "Artifacts API" "FAIL" "Artifacts endpoint returned error"
        else
                log_test_result "Artifacts API" "PASS" "Artifacts endpoint working correctly"
        fi

        # Test team management endpoints
        echo "Testing team management endpoints..."
        TEAM_RESULT=$(curl -s -X GET http://localhost:8000/api/teams)

        if [[ $TEAM_RESULT == *"error"* ]]; then
                log_test_result "Teams API" "FAIL" "Teams endpoint returned error"
        else
                log_test_result "Teams API" "PASS" "Teams endpoint working correctly"
        fi
}

# Function to test E2B code interpreter
test_e2b_code_interpreter() {
        echo "Testing E2B code interpreter..."

        # Check if E2B code interpreter is running
        if ! curl -s http://localhost:8080/health >/dev/null; then
                log_test_result "E2B Code Interpreter Health Check" "FAIL" "E2B code interpreter is not running"
                return 1
        fi

        # Test Python code execution
        echo "Testing Python code execution..."
        PYTHON_RESULT=$(curl -s -X POST http://localhost:8080/execute -H "Content-Type: application/json" -d '{"code":"print(\"Hello, World!\")","language":"python"}')

        if [[ $PYTHON_RESULT == *"error"* ]]; then
                log_test_result "Python Code Execution" "FAIL" "Python code execution returned error"
        else
                log_test_result "Python Code Execution" "PASS" "Python code execution working correctly"
        fi

        # Test JavaScript code execution
        echo "Testing JavaScript code execution..."
        JS_RESULT=$(curl -s -X POST http://localhost:8080/execute -H "Content-Type: application/json" -d '{"code":"console.log(\"Hello, World!\")","language":"javascript"}')

        if [[ $JS_RESULT == *"error"* ]]; then
                log_test_result "JavaScript Code Execution" "FAIL" "JavaScript code execution returned error"
        else
                log_test_result "JavaScript Code Execution" "PASS" "JavaScript code execution working correctly"
        fi

        # Test artifact generation
        echo "Testing artifact generation..."
        ARTIFACT_RESULT=$(curl -s -X POST http://localhost:8080/execute -H "Content-Type: application/json" -d '{"code":"import matplotlib.pyplot as plt\nimport numpy as np\n\nx = np.linspace(0, 10, 100)\ny = np.sin(x)\n\nplt.figure()\nplt.plot(x, y)\nplt.savefig(\"sine_wave.png\")\nprint(\"Artifact generated\")","language":"python"}')

        if [[ $ARTIFACT_RESULT == *"error"* ]]; then
                log_test_result "Artifact Generation" "FAIL" "Artifact generation returned error"
        else
                log_test_result "Artifact Generation" "PASS" "Artifact generation working correctly"
        fi

        # Test timeout handling
        echo "Testing timeout handling..."
        TIMEOUT_RESULT=$(curl -s -X POST http://localhost:8080/execute -H "Content-Type: application/json" -d '{"code":"import time\nwhile True:\n    time.sleep(1)\n    print(\"Still running...\")","language":"python","timeout":5}')

        if [[ $TIMEOUT_RESULT == *"timeout"* ]]; then
                log_test_result "Timeout Handling" "PASS" "Timeout handling working correctly"
        else
                log_test_result "Timeout Handling" "FAIL" "Timeout handling not working correctly"
        fi
}

# Function to test frontend components
test_frontend_components() {
        echo "Testing frontend components..."

        # Check if frontend is running
        if ! curl -s http://localhost:3000 >/dev/null; then
                log_test_result "Frontend Health Check" "FAIL" "Frontend is not running"
                return 1
        fi

        # Use Cypress or similar for frontend testing
        # For now, we'll just output a message
        log_test_result "Frontend Components" "INFO" "Frontend testing requires Cypress or similar tool"
}

# Function to test OpenAI Agent SDK integration
test_openai_agent_sdk() {
        echo "Testing OpenAI Agent SDK integration..."

        # Check if backend is running
        if ! curl -s http://localhost:8000/api/health >/dev/null; then
                log_test_result "Backend Health Check" "FAIL" "Backend is not running"
                return 1
        fi

        # Test SDK executor
        echo "Testing SDK executor..."
        SDK_RESULT=$(curl -s -X POST http://localhost:8000/api/agent/execute -H "Content-Type: application/json" -d '{"prompt":"What is the capital of France?","executor":"sdk"}')

        if [[ $SDK_RESULT == *"error"* ]]; then
                log_test_result "SDK Executor" "FAIL" "SDK executor returned error"
        else
                log_test_result "SDK Executor" "PASS" "SDK executor working correctly"
        fi

        # Test tool registration
        echo "Testing tool registration..."
        TOOL_RESULT=$(curl -s -X POST http://localhost:8000/api/agent/tools -H "Content-Type: application/json" -d '{"name":"calculator","description":"Performs calculations","function":"calculate"}')

        if [[ $TOOL_RESULT == *"error"* ]]; then
                log_test_result "Tool Registration" "FAIL" "Tool registration returned error"
        else
                log_test_result "Tool Registration" "PASS" "Tool registration working correctly"
        fi
}

# Function to test agent delegation
test_agent_delegation() {
        echo "Testing agent delegation..."

        # Check if backend is running
        if ! curl -s http://localhost:8000/api/health >/dev/null; then
                log_test_result "Backend Health Check" "FAIL" "Backend is not running"
                return 1
        fi

        # Test team creation
        echo "Testing team creation..."
        TEAM_RESULT=$(curl -s -X POST http://localhost:8000/api/teams -H "Content-Type: application/json" -d '{"name":"Test Team","description":"A test team"}')

        if [[ $TEAM_RESULT == *"error"* ]]; then
                log_test_result "Team Creation" "FAIL" "Team creation returned error"
        else
                log_test_result "Team Creation" "PASS" "Team creation working correctly"
                
                # Extract team ID
                TEAM_ID=$(echo $TEAM_RESULT | grep -o '"id":"[^"]*' | cut -d'"' -f4)
                
                if [ -n "$TEAM_ID" ]; then
                        # Test agent addition
                        echo "Testing agent addition..."
                        AGENT_RESULT=$(curl -s -X POST http://localhost:8000/api/teams/$TEAM_ID/agents -H "Content-Type: application/json" -d '{"name":"Test Agent","role":"coder"}')
                        
                        if [[ $AGENT_RESULT == *"error"* ]]; then
                                log_test_result "Agent Addition" "FAIL" "Agent addition returned error"
                        else
                                log_test_result "Agent Addition" "PASS" "Agent addition working correctly"
                                
                                # Extract agent ID
                                AGENT_ID=$(echo $AGENT_RESULT | grep -o '"id":"[^"]*' | cut -d'"' -f4)
                                
                                if [ -n "$AGENT_ID" ]; then
                                        # Test task creation
                                        echo "Testing task creation..."
                                        TASK_RESULT=$(curl -s -X POST http://localhost:8000/api/teams/$TEAM_ID/tasks -H "Content-Type: application/json" -d "{\"title\":\"Test Task\",\"description\":\"A test task\",\"assigned_to\":\"$AGENT_ID\"}")
                                        
                                        if [[ $TASK_RESULT == *"error"* ]]; then
                                                log_test_result "Task Creation" "FAIL" "Task creation returned error"
                                        else
                                                log_test_result "Task Creation" "PASS" "Task creation working correctly"
                                        fi
                                else
                                        log_test_result "Agent ID Extraction" "FAIL" "Could not extract agent ID"
                                fi
                        fi
                else
                        log_test_result "Team ID Extraction" "FAIL" "Could not extract team ID"
                fi
        fi
}

# Function to test security features
test_security_features() {
        echo "Testing security features..."

        # Check if backend is running
        if ! curl -s http://localhost:8000/api/health >/dev/null; then
                log_test_result "Backend Health Check" "FAIL" "Backend is not running"
                return 1
        fi

        # Test authentication
        echo "Testing authentication..."
        AUTH_RESULT=$(curl -s -X POST http://localhost:8000/api/auth/token -H "Content-Type: application/json" -d '{"username":"test","password":"test"}')

        if [[ $AUTH_RESULT == *"error"* ]]; then
                log_test_result "Authentication" "FAIL" "Authentication returned error"
        else
                log_test_result "Authentication" "PASS" "Authentication working correctly"
                
                # Extract token
                TOKEN=$(echo $AUTH_RESULT | grep -o '"token":"[^"]*' | cut -d'"' -f4)
                
                if [ -n "$TOKEN" ]; then
                        # Test authorization
                        echo "Testing authorization..."
                        AUTH_RESULT=$(curl -s -X GET http://localhost:8000/api/users/me -H "Authorization: Bearer $TOKEN")
                        
                        if [[ $AUTH_RESULT == *"error"* ]]; then
                                log_test_result "Authorization" "FAIL" "Authorization returned error"
                        else
                                log_test_result "Authorization" "PASS" "Authorization working correctly"
                        fi
                        
                        # Test invalid token
                        echo "Testing invalid token..."
                        INVALID_RESULT=$(curl -s -X GET http://localhost:8000/api/users/me -H "Authorization: Bearer invalid_token")
                        
                        if [[ $INVALID_RESULT == *"error"* ]]; then
                                log_test_result "Invalid Token" "PASS" "Invalid token correctly rejected"
                        else
                                log_test_result "Invalid Token" "FAIL" "Invalid token not rejected"
                        fi
                else
                        log_test_result "Token Extraction" "FAIL" "Could not extract token"
                fi
        fi

        # Test input validation
        echo "Testing input validation..."
        VALIDATION_RESULT=$(curl -s -X POST http://localhost:8000/api/auth/token -H "Content-Type: application/json" -d '{"username":"<script>alert(1)</script>","password":"test"}')

        if [[ $VALIDATION_RESULT == *"error"* ]]; then
                log_test_result "Input Validation" "PASS" "Input validation correctly rejected malicious input"
        else
                log_test_result "Input Validation" "FAIL" "Input validation did not reject malicious input"
        fi
}

# Function to test performance
test_performance() {
        echo "Testing performance..."

        # Check if backend is running
        if ! curl -s http://localhost:8000/api/health >/dev/null; then
                log_test_result "Backend Health Check" "FAIL" "Backend is not running"
                return 1
        fi

        # Test response time
        echo "Testing response time..."
        START_TIME=$(date +%s.%N)
        curl -s http://localhost:8000/api/health >/dev/null
        END_TIME=$(date +%s.%N)
        RESPONSE_TIME=$(echo "$END_TIME - $START_TIME" | bc)

        if (( $(echo "$RESPONSE_TIME < 0.5" | bc -l) )); then
                log_test_result "Response Time" "PASS" "Response time is acceptable: ${RESPONSE_TIME}s"
        else
                log_test_result "Response Time" "FAIL" "Response time is too slow: ${RESPONSE_TIME}s"
        fi

        # Test concurrent requests
        echo "Testing concurrent requests..."
        START_TIME=$(date +%s.%N)
        for i in {1..10}; do
                curl -s http://localhost:8000/api/health >/dev/null &
        done
        wait
        END_TIME=$(date +%s.%N)
        CONCURRENT_TIME=$(echo "$END_TIME - $START_TIME" | bc)

        if (( $(echo "$CONCURRENT_TIME < 2.0" | bc -l) )); then
                log_test_result "Concurrent Requests" "PASS" "Concurrent request time is acceptable: ${CONCURRENT_TIME}s"
        else
                log_test_result "Concurrent Requests" "FAIL" "Concurrent request time is too slow: ${CONCURRENT_TIME}s"
        fi
}

# Function to create a test report
create_test_report() {
        echo "Creating test report..."

        # Count test results
        TOTAL_TESTS=$(grep -c "\[" "$RESULTS_DIR/test_results.log")
        PASSED_TESTS=$(grep -c "\[PASS\]" "$RESULTS_DIR/test_results.log")
        FAILED_TESTS=$(grep -c "\[FAIL\]" "$RESULTS_DIR/test_results.log")
        INFO_TESTS=$(grep -c "\[INFO\]" "$RESULTS_DIR/test_results.log")

        # Calculate pass rate
        PASS_RATE=$(echo "scale=2; $PASSED_TESTS * 100 / ($PASSED_TESTS + $FAILED_TESTS)" | bc)

        # Create HTML report
        HTML_REPORT="$RESULTS_DIR/test_report.html"

        echo "<!DOCTYPE html>" >$HTML_REPORT
        echo "<html>" >>$HTML_REPORT
        echo "<head>" >>$HTML_REPORT
        echo "  <title>Atlas-Chat Test Report</title>" >>$HTML_REPORT
        echo "  <style>" >>$HTML_REPORT
        echo "    body { font-family: Arial, sans-serif; margin: 20px; }" >>$HTML_REPORT
        echo "    h1 { color: #333; }" >>$HTML_REPORT
        echo "    .summary { margin: 20px 0; padding: 10px; background-color: #f5f5f5; border-radius: 5px; }" >>$HTML_REPORT
        echo "    .pass { color: green; }" >>$HTML_REPORT
        echo "    .fail { color: red; }" >>$HTML_REPORT
        echo "    .info { color: blue; }" >>$HTML_REPORT
        echo "    table { border-collapse: collapse; width: 100%; }" >>$HTML_REPORT
        echo "    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }" >>$HTML_REPORT
        echo "    th { background-color: #f2f2f2; }" >>$HTML_REPORT
        echo "    tr:nth-child(even) { background-color: #f9f9f9; }" >>$HTML_REPORT
        echo "  </style>" >>$HTML_REPORT
        echo "</head>" >>$HTML_REPORT
        echo "<body>" >>$HTML_REPORT
        echo "  <h1>Atlas-Chat Test Report</h1>" >>$HTML_REPORT
        echo "  <div class='summary'>" >>$HTML_REPORT
        echo "    <p><strong>Date:</strong> $(date)</p>" >>$HTML_REPORT
        echo "    <p><strong>Total Tests:</strong> $TOTAL_TESTS</p>" >>$HTML_REPORT
        echo "    <p><strong>Passed:</strong> <span class='pass'>$PASSED_TESTS</span></p>" >>$HTML_REPORT
        echo "    <p><strong>Failed:</strong> <span class='fail'>$FAILED_TESTS</span></p>" >>$HTML_REPORT
        echo "    <p><strong>Info:</strong> <span class='info'>$INFO_TESTS</span></p>" >>$HTML_REPORT
        echo "    <p><strong>Pass Rate:</strong> $PASS_RATE%</p>" >>$HTML_REPORT
        echo "  </div>" >>$HTML_REPORT
        echo "  <h2>Test Results</h2>" >>$HTML_REPORT
        echo "  <table>" >>$HTML_REPORT
        echo "    <tr><th>Status</th><th>Test</th><th>Details</th></tr>" >>$HTML_REPORT

        # Add test results to table
        while IFS= read -r line; do
                STATUS=$(echo $line | grep -o "\[.*\]" | tr -d '[]')
                TEST=$(echo $line | sed -E 's/\[.*\] ([^:]+):.*/\1/')
                DETAILS=$(echo $line | sed -E 's/\[.*\] [^:]+: (.*)/\1/')
                
                STATUS_CLASS="info"
                if [ "$STATUS" == "PASS" ]; then
                        STATUS_CLASS="pass"
                elif [ "$STATUS" == "FAIL" ]; then
                        STATUS_CLASS="fail"
                fi
                
                echo "    <tr><td class='$STATUS_CLASS'>$STATUS</td><td>$TEST</td><td>$DETAILS</td></tr>" >>$HTML_REPORT
        done < "$RESULTS_DIR/test_results.log"

        echo "  </table>" >>$HTML_REPORT
        echo "</body>" >>$HTML_REPORT
        echo "</html>" >>$HTML_REPORT

        echo "Test report created: $HTML_REPORT"
}

# Main execution
echo "Starting comprehensive testing process..."

# Run tests
test_backend_api
test_e2b_code_interpreter
test_frontend_components
test_openai_agent_sdk
test_agent_delegation
test_security_features
test_performance

# Create test report
create_test_report

echo "Testing completed. Results saved to: $RESULTS_DIR"
echo "Test report: $RESULTS_DIR/test_report.html"
