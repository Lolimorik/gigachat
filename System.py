import subprocess

result = subprocess.check_output("ls -l", shell=True, text=True)
