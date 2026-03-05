import platform
import subprocess
from rich.console import Console
from rich.panel import Panel
import os

console = Console()
current_path = os.getcwd()
operating_system = platform.system()

build_cmd = ("docker build -f dockerfile -t scrape .") 
run_cmd = ('echo "Don\'t know your OS"')
if operating_system == 'Linux' or operating_system == 'Darwin':
    run_cmd = (
        "docker run -it "
        "-p 6080:6080 "
        "-v $(pwd)/user_data:/app/user_data "
        "scrape:latest"
    )
elif operating_system == 'Windows':
    run_cmd = (
        'docker run -it -p 6080:6080 '
        f"-v {current_path}:/app/user_data "
        'scrape:latest'
    )

console.print(Panel(f"[cyan]{build_cmd}[/]", title="Building"))
build = subprocess.run(build_cmd, shell=True)

# Run (only if build succeeded)
if build.returncode == 0:
    console.print(Panel(f"[cyan]{run_cmd}[/]", title="Running"))
    subprocess.run(run_cmd, shell=True)
else:
    console.print(f"[red]Build failed with exit code {build.returncode}[/]")
