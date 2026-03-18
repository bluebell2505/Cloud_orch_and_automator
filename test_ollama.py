import ollama

response = ollama.chat(
    model='mistral',
    messages=[{
        'role': 'user',
        'content': 'Reply with exactly: Mistral is working correctly!'
    }]
)

print(response['message']['content'])