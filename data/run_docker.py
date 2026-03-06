import platform
import subprocess
from rich.console import Console
from rich.panel import Panel
import os

console = Console()
current_path = os.path.dirname(os.path.abspath(__file__))
operating_system = platform.system()

build_cmd = f"docker build -f {current_path}/dockerfile -t scrape {current_path}"
run_cmd = (
        "docker run -it "
        "-p 6080:6080 "
        f"-v {current_path}/user_data:/app/user_data "
        f"-v {current_path}/trump_truths_progress.csv:/app/trump_truths_progress.csv "
        f"-v {current_path}/last_id.txt:/app/last_id.txt "
        "scrape:latest"
        )

console.print(Panel(f"[cyan]{build_cmd}[/]", title="Building"))
build = subprocess.run(build_cmd, shell=True)


if build.returncode == 0:
    console.print(Panel(f"[cyan]{run_cmd}[/]", title="Running"))
    subprocess.run(run_cmd, shell=True)
else:
    console.print(f"[red]Build failed with exit code {build.returncode}[/]")
