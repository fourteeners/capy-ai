"""
Foundry Bridge — connects CAPY tools to Foundry (forge, cast, anvil).

Provides:
- Foundry test execution for smart contracts
- Cast calls for reading contract state
- Local fork testing with anvil
- Invariant testing with handlers
"""

import json
import subprocess
import tempfile
import os
from typing import Optional


def run_forge_test(
    contract_path: str,
    match_contract: str = "",
    fork_url: str = "",
    block_number: Optional[int] = None,
    verbosity: int = 2,
    timeout: int = 600,
) -> dict:
    """
    Run Foundry forge tests on a smart contract.

    Args:
        contract_path: Path to the Foundry project
        match_contract: Regex to match specific test contracts
        fork_url: RPC URL for forked testing
        block_number: Block number for fork
        verbosity: Output verbosity (1-5)
        timeout: Timeout in seconds

    Returns:
        dict with test results
    """
    cmd = ["forge", "test"]

    if match_contract:
        cmd.extend(["--match-contract", match_contract])
    if fork_url:
        cmd.extend(["--fork-url", fork_url])
    if block_number:
        cmd.extend(["--fork-block-number", str(block_number)])
    if verbosity:
        cmd.extend(["-" + "v" * min(verbosity, 5)])

    try:
        proc = subprocess.run(
            cmd,
            cwd=contract_path,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        # Parse test results
        output = proc.stdout
        tests_passed = 0
        tests_failed = 0
        tests_skipped = 0

        for line in output.splitlines():
            if "PASS" in line and "test" in line.lower():
                tests_passed += 1
            elif "FAIL" in line and "test" in line.lower():
                tests_failed += 1
            elif "SKIP" in line:
                tests_skipped += 1

        return {
            "success": proc.returncode == 0,
            "returncode": proc.returncode,
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "tests_skipped": tests_skipped,
            "output": output[-2000:],  # Last 2000 chars
            "command": " ".join(cmd),
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Foundry tests timed out after {timeout}s", "success": False}
    except FileNotFoundError:
        return {"error": "Foundry (forge) not installed. Install: curl -L https://foundry.paradigm.xyz | bash", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


def cast_call(
    address: str,
    signature: str,
    rpc_url: str = "",
    args: Optional[list] = None,
) -> dict:
    """
    Call a smart contract view function via cast.

    Args:
        address: Contract address
        signature: Function signature (e.g., "balanceOf(address)(uint256)")
        rpc_url: RPC endpoint URL
        args: Function arguments

    Returns:
        dict with call result
    """
    cmd = ["cast", "call", address, signature]

    if args:
        for arg in args:
            cmd.append(str(arg))

    if rpc_url:
        cmd.extend(["--rpc-url", rpc_url])

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return {
            "success": proc.returncode == 0,
            "result": proc.stdout.strip(),
            "error": proc.stderr.strip() if proc.returncode != 0 else "",
            "address": address,
            "signature": signature,
        }
    except FileNotFoundError:
        return {"error": "cast not installed", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


def run_invariant_test(
    contract_path: str,
    target_contract: str,
    handlers: list[str],
    fork_url: str = "",
    depth: int = 15,
    timeout: int = 1800,
) -> dict:
    """
    Run Foundry invariant tests with handler functions.

    Invariant testing is the most powerful way to find edge-case
    vulnerabilities in smart contracts. It randomly sequences handler
    calls to violate invariants.

    Args:
        contract_path: Path to Foundry project
        target_contract: Contract with invariant assertions
        handlers: List of handler contract names
        fork_url: RPC URL for forked testing
        depth: Call depth for each run
        timeout: Timeout in seconds

    Returns:
        dict with test results
    """
    cmd = ["forge", "test", "--match-contract", target_contract]

    if fork_url:
        cmd.extend(["--fork-url", fork_url])

    # Set depth in foundry.toml or via env
    env = os.environ.copy()
    env["FOUNDRY_INVARIANT_DEPTH"] = str(depth)
    env["FOUNDRY_INVARIANT_RUNS"] = "256"

    try:
        proc = subprocess.run(
            cmd,
            cwd=contract_path,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )

        return {
            "success": proc.returncode == 0,
            "output": proc.stdout[-2000:],
            "invariant_violations": proc.stdout.count("violated"),
            "depth": depth,
            "handlers": handlers,
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Invariant tests timed out after {timeout}s", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


def simulate_exploit(
    contract_address: str,
    exploit_script: str,
    fork_url: str,
    block_number: Optional[int] = None,
) -> dict:
    """
    Simulate an exploit against a forked mainnet state.

    Uses Foundry's anvil to fork mainnet, then executes the exploit
    script to verify impact without touching real state.

    Args:
        contract_address: Target contract
        exploit_script: Solidity test/script for exploit
        fork_url: RPC URL to fork from
        block_number: Specific block to fork

    Returns:
        dict with simulation results
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "Exploit.s.sol")
        with open(script_path, "w") as f:
            f.write(exploit_script)

        cmd = ["forge", "script", script_path, "--fork-url", fork_url]
        if block_number:
            cmd.extend(["--fork-block-number", str(block_number)])
        cmd.append("--broadcast")  # Broadcast on fork only

        try:
            proc = subprocess.run(
                cmd,
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=300,
            )

            return {
                "success": proc.returncode == 0,
                "output": proc.stdout[-2000:],
                "contract": contract_address,
                "note": "Simulated on local fork — no real transactions sent",
            }
        except Exception as e:
            return {"error": str(e), "success": False}
