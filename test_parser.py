# test_parser.py
import sys
sys.path.append('.')

sys.path.insert(0, 'log-collector')
from parser import process_log

# Simulated GitHub Actions failure log
FAKE_LOG = """
2024-01-15T10:23:41.123Z Run pip install -r requirements.txt
2024-01-15T10:23:41.200Z Collecting flask==2.0.0
2024-01-15T10:23:41.300Z Collecting requests
2024-01-15T10:23:42.100Z Successfully installed requests-2.28.0
2024-01-15T10:23:42.200Z Run python -m pytest tests/
2024-01-15T10:23:42.300Z ============================= test session starts ==============================
2024-01-15T10:23:42.400Z platform linux -- Python 3.11.0
2024-01-15T10:23:42.500Z collected 3 items
2024-01-15T10:23:43.100Z tests/test_app.py::test_home PASSED
2024-01-15T10:23:43.200Z tests/test_app.py::test_login PASSED
2024-01-15T10:23:43.300Z tests/test_app.py::test_payment FAILED
2024-01-15T10:23:43.400Z
2024-01-15T10:23:43.500Z ================================== FAILURES ===================================
2024-01-15T10:23:43.600Z _______________________ test_payment _______________________
2024-01-15T10:23:43.700Z
2024-01-15T10:23:43.800Z     def test_payment():
2024-01-15T10:23:43.900Z         response = client.post('/pay', json={'amount': 100})
2024-01-15T10:23:44.000Z >       assert response.status_code == 200
2024-01-15T10:23:44.100Z E       AssertionError: assert 500 == 200
2024-01-15T10:23:44.200Z E       where 500 = <Response [500]>.status_code
2024-01-15T10:23:44.300Z
2024-01-15T10:23:44.400Z tests/test_app.py:45: AssertionError
2024-01-15T10:23:44.500Z ============================== 1 failed in 3.24s ==============================
2024-01-15T10:23:44.600Z Error: Process completed with exit code 1.
"""

# Run the processor
result = process_log(FAKE_LOG)

print("=" * 60)
print(f"✅ Total lines in cleaned log : {result['total_lines']}")
print(f"✅ Lines in failure block     : {result['failure_lines']}")
print("=" * 60)
print("\n📋 EXTRACTED FAILURE BLOCK:\n")
print(result['failure_block'])