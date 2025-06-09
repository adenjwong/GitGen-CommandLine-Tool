#!/usr/bin/env python3
import os
import json
import subprocess
import click
from openai import OpenAI

# Load and sanitize the API key (remove any non-ASCII characters)
raw_key = os.getenv("OPENAI_API_KEY", "") or ""
sanitized_key = ''.join(ch for ch in raw_key if ord(ch) < 128)
if not sanitized_key:
    click.echo("❌ No valid OPENAI_API_KEY found. Please set it in your environment.")
    exit(1)

# Instantiate the OpenAI client
client = OpenAI(api_key=sanitized_key)


def ask_llm(prompt: str) -> str:
    """
    Send a prompt to the LLM and return its response.
    """
    resp = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content


def execute(cmd: str, dry_run: bool = False) -> tuple[bool, str]:
    """
    Execute a shell command. Returns (success, output).
    """
    click.echo(f"$ {cmd}")
    if dry_run:
        return True, ""
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return (proc.returncode == 0, proc.stderr or proc.stdout)


@click.command()
@click.argument("intent", nargs=-1, required=True)
@click.option("--dry-run", is_flag=True, help="Show commands without executing them")
def main(intent: tuple[str, ...], dry_run: bool) -> None:
    """
    Translate natural-language INTENT into git commands and execute them.
    """
    intent_text = " ".join(intent)

    prompt = (
        f"Translate this intent into sequential git steps as JSON schema:\n"
        f"`{{steps: [{{action: 'ask'|'run', cmd?: str, prompt?: str}}]}}`\n"
        f"Intent: \"{intent_text}\""
    )

    raw_response = ask_llm(prompt)
    try:
        steps = json.loads(raw_response)
    except json.JSONDecodeError:
        click.echo("❌ Failed to parse JSON from LLM. Response was:")
        click.echo(raw_response)
        return

    for step in steps.get("steps", []):
        action = step.get("action")
        if action == "ask":
            answer = click.prompt(step.get("prompt", ""))
            step["answer"] = answer
        elif action == "run":
            cmd = step.get("cmd", "").replace("<user_input>", step.get("answer", ""))
            success, output = execute(cmd, dry_run)
            if not success:
                fix_prompt = (
                    f"I ran `{cmd}` and got an error:\n{output}\n"
                    "How can I fix this? Reply with a single git command."
                )
                fix_cmd = ask_llm(fix_prompt).strip()
                execute(fix_cmd, dry_run)

    click.echo("✅ Done!")


if __name__ == "__main__":
    main()
