from deepagents.backends.filesystem import FilesystemBackend
from deepagents.backends.protocol import ExecuteResponse, SandboxBackendProtocol
import subprocess
import os

class LocalExecutionBackend(FilesystemBackend, SandboxBackendProtocol):
    """
    Extensions of FilesystemBackend that supports local command execution.
    This enables the 'execute' tool for the agent.
    """
    
    def execute(self, command: str) -> ExecuteResponse:
        """Execute a shell command locally."""
        try:
            # Prepare environment with current python path
            import sys
            env = os.environ.copy()
            current_python_dir = os.path.dirname(sys.executable)
            env["PATH"] = current_python_dir + os.pathsep + env.get("PATH", "")
            
            # Use shell=True to support pipes and shell features
            # Run in the configured root directory (cwd of the backend)
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.cwd,
                timeout=300,  # 5 minutes timeout
                env=env
            )
            
            output = process.stdout
            if process.stderr:
                output += "\nSTDERR:\n" + process.stderr
                
            return ExecuteResponse(
                output=output,
                exit_code=process.returncode,
                truncated=False
            )
        except subprocess.TimeoutExpired:
            return ExecuteResponse(
                output="Command execution timed out",
                exit_code=124,
                truncated=False
            )
        except Exception as e:
            return ExecuteResponse(
                output=f"Execution error: {str(e)}",
                exit_code=1,
                truncated=False
            )
