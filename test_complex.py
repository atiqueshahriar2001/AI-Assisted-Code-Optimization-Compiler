from backend.optimizer.engine import optimize_code

code = '''
int multiply_by_sum(int a, int b) {
    return a * b;
}

int main() {
    int sum = 0;
    int i;
    for (i = 1; i <= n; i++) {
        sum = sum + i;
    }
    
    int x = multiply_by_sum(5, 10);
    int arr[100];
    for (i = 0; i < 100; i++) {
        arr[i] = i * 2;
    }
    
    int temp = 10;
    temp = 20;
    
    return 0;
}
'''
result = optimize_code(code)
print('Optimized code:')
print(result['optimized_code'])
print()
print('Suggestions:', len(result['suggestions']))
for s in result['suggestions'][:5]:
    print('  -', s['title'])
print()
print('Score:', result['score'])