"""
Guestbook multi-agent orchestration with small-step loops.

Roles:
- Controller: Python script (no LLM decision)
- guestbook-pm (kimi-k3): PRD, plan, analyze, finalize
- guestbook-coder (ornith): one small step per task
- guestbook-reviewer (kimi-k3): review one small change
- guestbook-tester (ornith): run tests and verify endpoints

Time limit: 2 hours.
"""

import os
import sys
import time
import signal
from datetime import datetime, timezone
from pathlib import Path

os.environ['OPENHANDS_SUPPRESS_BANNER'] = '1'

import openhands.tools
from openhands.sdk import LLM, Agent, Tool
from openhands.sdk.conversation.impl.local_conversation import LocalConversation
from openhands.sdk.subagent import load_project_agents, register_agent
from openhands.tools.task.manager import TaskManager

WORKSPACE = '/tmp/guestbook-demo'
KIMI_KEY = open('/workspace/kimi.md').read().strip()
TIME_LIMIT_SECONDS = 2 * 60 * 60
STEP_TIMEOUT_SECONDS = 180  # per subagent step


def log(msg: str):
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}", flush=True)


def make_kimi_llm(usage_id: str) -> LLM:
    return LLM(
        model='openai/kimi-k3',
        base_url='https://api.kimi.com/coding/v1',
        api_key=KIMI_KEY,
        usage_id=usage_id,
    )


def make_ornith_llm(usage_id: str) -> LLM:
    return LLM(
        model='openai/ornith:35b',
        base_url='http://192.168.18.2:8000/v1',
        api_key='not-required',
        usage_id=usage_id,
    )


def register_custom_agents():
    definitions = {d.name: d for d in load_project_agents(WORKSPACE)}

    def pm_factory(_llm: LLM) -> Agent:
        return Agent(
            llm=make_kimi_llm('guestbook-pm'),
            tools=[Tool(name=t) for t in definitions['guestbook-pm'].tools],
            system_prompt=definitions['guestbook-pm'].system_prompt,
        )

    def coder_factory(_llm: LLM) -> Agent:
        return Agent(
            llm=make_ornith_llm('guestbook-coder'),
            tools=[Tool(name=t) for t in definitions['guestbook-coder'].tools],
            system_prompt=definitions['guestbook-coder'].system_prompt,
        )

    def reviewer_factory(_llm: LLM) -> Agent:
        return Agent(
            llm=make_kimi_llm('guestbook-reviewer'),
            tools=[Tool(name=t) for t in definitions['guestbook-reviewer'].tools],
            system_prompt=definitions['guestbook-reviewer'].system_prompt,
        )

    def tester_factory(_llm: LLM) -> Agent:
        return Agent(
            llm=make_ornith_llm('guestbook-tester'),
            tools=[Tool(name=t) for t in definitions['guestbook-tester'].tools],
            system_prompt=definitions['guestbook-tester'].system_prompt,
        )

    for name, factory in [
        ('guestbook-pm', pm_factory),
        ('guestbook-coder', coder_factory),
        ('guestbook-reviewer', reviewer_factory),
        ('guestbook-tester', tester_factory),
    ]:
        register_agent(name=name, factory_func=factory, description=definitions[name])
        log(f'Registered subagent: {name}')


class TimeoutRunner:
    """Run a callable with a timeout using SIGALRM."""
    def __init__(self, timeout: int):
        self.timeout = timeout
        self.result = None
        self.error = None

    def _run(self, fn, *args, **kwargs):
        try:
            self.result = fn(*args, **kwargs)
        except Exception as e:
            self.error = e

    def run(self, fn, *args, **kwargs):
        def handler(signum, frame):
            raise TimeoutError(f'Step timed out after {self.timeout} seconds')

        old_handler = signal.signal(signal.SIGALRM, handler)
        signal.alarm(self.timeout)
        try:
            self._run(fn, *args, **kwargs)
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

        if self.error:
            raise self.error
        return self.result


class Controller:
    def __init__(self):
        self.start_time = time.time()
        self.parent_conv = self._create_parent_conversation()
        self.task_manager = TaskManager()
        self.iteration = 0
        self.step_results: list[tuple[str, str, str]] = []

    def _create_parent_conversation(self) -> LocalConversation:
        parent_agent = Agent(
            llm=make_kimi_llm('guestbook-parent'),
            tools=[],
            system_prompt='You are a parent conversation placeholder. Do nothing.',
        )
        return LocalConversation(
            agent=parent_agent,
            workspace=WORKSPACE,
            persistence_dir=f'/tmp/guestbook-demo/.subagents',
        )

    def remaining_seconds(self) -> float:
        return TIME_LIMIT_SECONDS - (time.time() - self.start_time)

    def _run_subagent(self, subagent_type: str, prompt: str) -> str:
        if self.remaining_seconds() <= 0:
            raise RuntimeError('Time limit reached')

        task = self.task_manager.start_task(
            prompt=prompt,
            subagent_type=subagent_type,
            conversation=self.parent_conv,
        )
        return task.result or task.error or 'No result returned'

    def run_subagent(self, subagent_type: str, prompt: str, timeout: int = STEP_TIMEOUT_SECONDS) -> str:
        """Run a subagent with timeout, retry once on failure."""
        runner = TimeoutRunner(timeout)
        try:
            result = runner.run(self._run_subagent, subagent_type, prompt)
            return result
        except Exception as e:
            log(f'{subagent_type} failed/timed out: {e}')
            # Retry once with a shorter prompt to unstuck the agent
            retry_prompt = f"""
The previous task failed or timed out. Please continue from where you left off.
You do not need to repeat work already completed. Just finish the current step.

Original task: {prompt}
"""
            try:
                return runner.run(self._run_subagent, subagent_type, retry_prompt)
            except Exception as e2:
                log(f'{subagent_type} retry also failed: {e2}')
                return f'FAILED: {e2}'

    def pm_create_prd_and_plan(self) -> str:
        log('PHASE: PM creates PRD and initial plan')
        prompt = """
Read `/tmp/guestbook-demo/project.md`.

Write two files:
1. `/tmp/guestbook-demo/pm-output/prd.md` - product requirements document (no scope changes).
2. `/tmp/guestbook-demo/pm-output/plan.md` - detailed execution plan.

The plan must follow this exact format, one step per line:

```
coder: <file> - <one-sentence instruction>
reviewer: <file> - review the above change
```

Steps should be small and sequential. Example order:
- package.json
- src/config/database.js
- src/models/Message.js
- src/routes/health.js
- src/routes/messages.js
- src/app.js
- src/server.js
- tests/app.test.js
- tester: all

After writing the files, return the full plan content.
"""
        return self.run_subagent('guestbook-pm', prompt, timeout=300)

    def coder_execute_step(self, step_number: int, instruction: str) -> str:
        log(f'STEP {step_number}: CODER -> {instruction}')
        prompt = f"""
Execute this single step from the guestbook plan.

Step number: {step_number}
Instruction: {instruction}

Work only in `/tmp/guestbook-demo`. Create or modify exactly the file(s) described.
Do not run full tests. If you need to run a quick syntax check, do so.
Report the exact file(s) changed and the result.
"""
        return self.run_subagent('guestbook-coder', prompt, timeout=STEP_TIMEOUT_SECONDS)

    def reviewer_review_step(self, step_number: int, instruction: str, coder_result: str) -> str:
        log(f'STEP {step_number}: REVIEWER -> {instruction}')
        prompt = f"""
Review this single step from the guestbook plan.

Step number: {step_number}
Plan instruction: {instruction}
Coder result: {coder_result}

Read the changed file(s). Check:
1. Does it match the plan instruction?
2. Is the syntax correct?
3. Is the style consistent?
4. Are there obvious bugs?

Write your review to `/tmp/guestbook-demo/review-output/step-{step_number}.md`.
If acceptable, include "APPROVED" in your response.
If not, list specific issues and suggested fixes.
"""
        return self.run_subagent('guestbook-reviewer', prompt, timeout=STEP_TIMEOUT_SECONDS)

    def tester_test_and_deploy(self) -> str:
        log('PHASE: TESTER -> run tests and deploy')
        prompt = """
Test and deploy the guestbook service in `/tmp/guestbook-demo`.

Steps:
1. If `node_modules` is missing, run `npm install`.
2. Run `npm test` and capture the full output.
3. If tests pass, start the server with `node src/server.js` in the background.
4. Wait briefly, then verify with curl:
   - GET http://localhost:6008/health
   - POST http://localhost:6008/messages with JSON { "author": "Alice", "content": "Hello" }
   - GET http://localhost:6008/messages
   - DELETE http://localhost:6008/messages/1
5. Write the full report to `/tmp/guestbook-demo/qa-output/qa-report.md`.

If anything fails, capture the error output and stop.
"""
        return self.run_subagent('guestbook-tester', prompt, timeout=400)

    def pm_analyze_and_replan(self, results: str) -> str:
        log('PHASE: PM analyzes and replans')
        prompt = f"""
You are the project manager. Review the recent execution results:

{results}

Current plan is at `/tmp/guestbook-demo/pm-output/plan.md`.

Do the following:
1. Read the current plan.
2. Mark completed steps by adding `[DONE]` at the end of the line.
3. If the project is not complete, add the remaining small steps needed.
4. If all steps are done and tests pass, write `/tmp/guestbook-demo/pm-output/final-report.md`.
5. Return the updated plan content and a brief assessment.

Scope must remain exactly as defined in `/tmp/guestbook-demo/project.md`. Do not add new features.
"""
        return self.run_subagent('guestbook-pm', prompt, timeout=300)

    def parse_plan(self, plan_text: str) -> list[tuple[int, str, str, str]]:
        """Parse plan lines into (step_number, step_type, target, instruction)."""
        steps = []
        step_no = 0
        for raw_line in plan_text.splitlines():
            line = raw_line.strip()
            if line.startswith(('coder:', 'reviewer:', 'tester:')):
                step_no += 1
                parts = line.split(':', 2)
                step_type = parts[0].strip()
                rest = parts[1].strip() if len(parts) > 1 else ''
                # Split on first dash or colon for target/instruction
                if ' - ' in rest:
                    target, instruction = rest.split(' - ', 1)
                elif ': ' in rest:
                    target, instruction = rest.split(': ', 1)
                else:
                    target, instruction = rest, rest
                steps.append((step_no, step_type, target.strip(), instruction.strip(), line))
        return steps

    def step_is_done(self, line: str) -> bool:
        return '[DONE]' in line

    def run(self):
        log('=== Guestbook Multi-Agent Orchestration Started ===')
        register_custom_agents()

        # Initial PRD and plan
        self.pm_create_prd_and_plan()

        max_loops = 5
        for loop in range(max_loops):
            if self.remaining_seconds() <= 300:
                log('Approaching time limit, stopping.')
                break

            self.iteration = loop + 1
            log(f'=== ITERATION {self.iteration} ===')

            plan_path = Path(f'{WORKSPACE}/pm-output/plan.md')
            if not plan_path.exists():
                raise RuntimeError('Plan file missing')
            plan_text = plan_path.read_text()

            steps = self.parse_plan(plan_text)
            if not steps:
                log('No actionable steps found in plan.')
                break

            loop_results = []
            for step_no, step_type, target, instruction, raw_line in steps:
                if self.remaining_seconds() <= 300:
                    log('Approaching time limit during steps, stopping.')
                    break

                if self.step_is_done(raw_line):
                    continue

                if step_type == 'coder':
                    result = self.coder_execute_step(step_no, f'{target} - {instruction}')
                    self.step_results.append((f'{step_no}', f'coder: {result}'))
                    loop_results.append(f'Step {step_no} (coder): {result}')

                elif step_type == 'reviewer':
                    last_coder = next(
                        (r for n, r in reversed(self.step_results) if n == str(step_no - 1) and r.startswith('coder')),
                        'No coder result'
                    )
                    result = self.reviewer_review_step(step_no, f'{target} - {instruction}', last_coder)
                    self.step_results.append((f'{step_no}', f'reviewer: {result}'))
                    loop_results.append(f'Step {step_no} (reviewer): {result}')

                elif step_type == 'tester':
                    result = self.tester_test_and_deploy()
                    self.step_results.append((f'{step_no}', f'tester: {result}'))
                    loop_results.append(f'Step {step_no} (tester): {result}')

            # PM analyzes and replans
            replan_result = self.pm_analyze_and_replan('\n'.join(loop_results))

            # Check if all steps are done
            updated_plan = Path(plan_path).read_text()
            all_done = all(
                self.step_is_done(line)
                for line in updated_plan.splitlines()
                if line.strip().startswith(('coder:', 'reviewer:', 'tester:'))
            )
            if all_done and 'final-report.md' in replan_result:
                log('All steps complete and final report written.')
                break

        log('=== Orchestration Finished ===')
        elapsed_min = (time.time() - self.start_time) / 60
        log(f'Elapsed: {elapsed_min:.1f} minutes')


def main():
    controller = Controller()
    try:
        controller.run()
    except Exception as e:
        log(f'ERROR: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
