import subprocess
import tempfile
import os
import sqlite3
from django.shortcuts import render

def run_code(request):
    code = ''
    output = ''
    language = 'python'

    if request.method == 'POST':

        action=request.POST.get('action')

        if action=='clear':
            return render(request,'editorapp/index.html',{
                'code':'',
                'output':'',
                'language':'python'
            })
        
        code = request.POST.get('code', '')
        language = request.POST.get('language', 'python')
        

        try:
            if language == 'python':
                result = subprocess.run(['python', '-c', code],
                                        capture_output=True, text=True, timeout=5)
                output = result.stdout or result.stderr

            elif language == 'javascript':
                result = subprocess.run(['node', '-e', code],
                                        capture_output=True, text=True, timeout=5)
                output = result.stdout or result.stderr

            elif language == 'java':
                with tempfile.TemporaryDirectory() as temp_dir:
                    java_file = os.path.join(temp_dir, 'Main.java')
                    with open(java_file, 'w') as f:
                        f.write(code)

                    compile_proc = subprocess.run(['javac', java_file],
                                                  capture_output=True, text=True, timeout=5)
                    if compile_proc.returncode != 0:
                        output = compile_proc.stderr
                    else:
                        run_proc = subprocess.run(['java', '-cp', temp_dir, 'Main'],
                                                  capture_output=True, text=True, timeout=5)
                        output = run_proc.stdout or run_proc.stderr

            elif language == 'sql':
                try:
                    conn = sqlite3.connect(':memory:')
                    cursor = conn.cursor()
                    cursor.executescript(code)
                    rows = cursor.fetchall()
                    output = '\n'.join(str(row) for row in rows) or 'SQL executed successfully.'
                except Exception as e:
                    output = str(e)
                finally:
                    conn.close()

            else:
                output = f"Unsupported language: {language}"

        except subprocess.TimeoutExpired:
            output = "Error: Code execution timed out."
        except Exception as e:
            output = f"Error: {str(e)}"
        
        
    
    return render(request, 'editorapp/index.html', {
        'code': code,
        'output': output,
        'language': language
    })
