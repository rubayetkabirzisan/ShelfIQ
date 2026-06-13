import requests
BASE = 'http://localhost:8000'
def test(name, r):
    status = 'PASS' if r.status_code < 400 else 'FAIL'
    print(f'[{status}] {name} ({r.status_code})')
r = requests.post(f'{BASE}/api/auth/login/', json={'username':'rep','password':'rep123'})
test('Login as rep', r)
rep_token = r.json()['access']
rep_h = {'Authorization': f'Bearer {rep_token}'}
r = requests.post(f'{BASE}/api/auth/login/', json={'username':'supervisor','password':'super123'})
test('Login as supervisor', r)
sup_token = r.json()['access']
sup_h = {'Authorization': f'Bearer {sup_token}'}
r = requests.get(f'{BASE}/api/visits/outlets/')
test('Get outlets (no auth)', r)
r = requests.get(f'{BASE}/api/auth/me/', headers=rep_h)
test('Get me (rep)', r)
r = requests.get(f'{BASE}/api/visits/', headers=rep_h)
test('List visits', r)
r = requests.get(f'{BASE}/api/visits/stats/', headers=sup_h)
test('Visit stats', r)
r = requests.post(f'{BASE}/api/fraud/check/', headers=rep_h, json={'visit_id':1})
test('Fraud check', r)
r = requests.get(f'{BASE}/api/fraud/logs/', headers=sup_h)
test('Fraud logs (supervisor)', r)
r = requests.get(f'{BASE}/api/fraud/logs/', headers=rep_h)
test('Fraud logs (rep) expect 403', r)
r = requests.get(f'{BASE}/api/analysis/', headers=sup_h)
test('Analysis list', r)
r = requests.post(f'{BASE}/api/chat/message/', headers=sup_h, json={'message':'How many outlets do we have?'})
test('RetailGPT chat', r)
if r.status_code == 201:
    print('     AI:', r.json()['response'][:100])
r = requests.get(f'{BASE}/api/chat/history/', headers=sup_h)
test('Chat history', r)
r = requests.post(f'{BASE}/api/chat/message/', headers=rep_h, json={'message':'test'})
test('Chat (rep) expect 403', r)
r = requests.get(f'{BASE}/api/observability/metrics/')
test('Observability metrics', r)
print()
print('Done.')
