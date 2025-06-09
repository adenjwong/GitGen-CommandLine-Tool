#!/usr/bin/env python3
import os
import json
import subprocess
import click
import openai

# Ensure your API key is set in the environment
openai.api_key = os.getenv("OPENAI_API_KEY")


def ask_llm(prompt: str) -> str:
    """
    Send a prompt to the LLM and return its response.
    """
    resp = openai.ChatCompletion.create(
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
    # Combine intent words into a sentence
    intent_text = " ".join(intent)

    # Build the LLM prompt
    prompt = (
        f"Translate this intent into sequential git steps as JSON schema:\n"
        f"`{{steps: [{{action: 'ask'|'run', cmd?: str, prompt?: str}}]}}`\n"
        f"Intent: \"{intent_text}\""
    )

    # Get JSON steps from the LLM
    raw_response = ask_llm(prompt)
    steps = json.loads(raw_response)

    # Process each step
    for step in steps.get("steps", []):
        action = step.get("action")
        if action == "ask":
            # Ask user for additional input
            answer = click.prompt(step.get("prompt", ""))
            step["answer"] = answer
        elif action == "run":
            # Replace placeholder with user answer if present
            cmd = step.get("cmd", "").replace('<user_input>', step.get("answer", ""))
            success, output = execute(cmd, dry_run)
            if not success:
                # On error, ask the LLM for a fix
                fix_prompt = (
                    f"I ran `{cmd}` and got an error:\n{output}\n"
                    "How can I fix this? Reply with a single git command."
                )
                fix_cmd = ask_llm(fix_prompt).strip()
                execute(fix_cmd, dry_run)

    click.echo("✅ Done!")


if __name__ == "__main__":
    main()
