import os
import json
import re
import time
import jsonlines
from code.utils.agent import Agent


class Agent:
    def __init__(self, model_name, name, temperature, sleep_time):
        self.model_name = model_name
        self.name = name
        self.temperature = temperature
        self.sleep_time = sleep_time
        self.memory_lst = []

    def set_meta_prompt(self, meta_prompt):
        self.memory_lst.append({"role": "system", "content": meta_prompt})

    def add_event(self, content):
        self.memory_lst.append({"role": "user", "content": content})

    def add_memory(self, content):
        self.memory_lst.append({"role": "assistant", "content": content})


class DebatePlayer(Agent):
    def __init__(self, model_name: str, name: str, temperature: float, sleep_time: float, max_tokens: int = None,
                 top_p: float = None) -> None:
        super(DebatePlayer, self).__init__(model_name, name, temperature, sleep_time)

        if model_name == "deepseek-reasoner":
            self.client = deepseek_client
        elif model_name == "gemini-2.0-flash-thinking-exp-01-21":  
            self.client = gemini_client
        elif model_name == "o1-2024-12-17":
            self.client = o1_client
        else:
            self.client = client  

        self.max_tokens = max_tokens
        self.top_p = top_p
        self.stats = {
            "calls": 0,  
            "runtime": 0.0,  
            "prompt_tokens": 0,  
            "completion_tokens": 0, 
            "total_tokens": 0  
        }

    def ask(self, messages):
        """Distribute requests"""

        if self.model_name == "deepseek-reasoner":
            return self.ask_deepseek(messages)
        else:
            return self.ask_openai(messages)

    def ask_openai(self, messages):
        """OpenAI / Gemini """

        start_time = time.time()
        print(f"🔍 [{self.name}] call {self.model_name}...")

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p if self.top_p is not None else 1.0,
                stream=False
            )

            content = response.choices[0].message.content
            end_time = time.time()
            duration = end_time - start_time

            self.stats["calls"] += 1
            self.stats["runtime"] += duration

            if response.usage:
                self.stats["prompt_tokens"] += response.usage.prompt_tokens
                self.stats["completion_tokens"] += response.usage.completion_tokens
                self.stats["total_tokens"] += response.usage.total_tokens

            print(f"💡 {self.model_name} response (time consuming {duration:.2f}s): {content[:50]}...")
            return content

        except Exception as e:
            print(f"❌ OpenAI API call failed: {e}")
            return ""

    def ask_deepseek(self, messages):
        """DeepSeek  API """
        
        print(f"🔍 [{self.name}] call DeepSeek-reasoner...")
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model="deepseek-reasoner",
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=False
            )

            content = response.choices[0].message.content
            reasoning_content = getattr(response.choices[0].message, 'reasoning_content', '')

            end_time = time.time()
            duration = end_time - start_time

            self.stats["calls"] += 1
            self.stats["runtime"] += duration

            if response.usage:
                self.stats["prompt_tokens"] += response.usage.prompt_tokens
                self.stats["completion_tokens"] += response.usage.completion_tokens
                self.stats["total_tokens"] += response.usage.total_tokens

            print(f"💡 DeepSeek inference completed (time consuming {duration:.2f}s)")
            return content

        except Exception as e:
            print(f"❌ DeepSeek API call failed: {e}")
            return ""


class Debate:
    def __init__(self, model_name: str = '', temperature: float = 0, num_players: int = 3,
                 openai_api_key: str = None, config: dict = None, max_round: int = 2, sleep_time: float = 0):
        self.model_name = model_name
        self.temperature = temperature
        self.num_players = num_players
        self.config = config
        self.max_round = max_round
        self.sleep_time = sleep_time

        self.init_prompt()
        self.creat_agents()
        self.init_agents()

    def init_prompt(self):
        if "debate_topic" in self.config and "##debate_topic##" in self.config.get("key", ""):
            self.config["key"] = self.config["key"].replace("##debate_topic##", self.config["debate_topic"])

    def creat_agents(self):
        # Define three roles
        self.players = [
            DebatePlayer(model_name="o1-2024-12-17", name="validator", temperature=0.3, sleep_time=self.sleep_time,
                         max_tokens=8192),
            DebatePlayer(model_name="deepseek-reasoner", name="arbiter", temperature=0.3, sleep_time=self.sleep_time,
                         max_tokens=8192),
            DebatePlayer(model_name="gemini-2.0-flash-thinking-exp-01-21", name="defender", temperature=0.3, top_p=0.95,
                         sleep_time=self.sleep_time, max_tokens=8192)
        ]
        self.validator = self.players[0]
        self.arbiter = self.players[1]
        self.defender = self.players[2]

    def init_agents(self):
        # System Prompt
        self.validator.set_meta_prompt(self.config['validator_meta_prompt'])
        self.defender.set_meta_prompt(
            self.config['defender_meta_prompt']
                .replace("##issue##", self.config["issue"])
                .replace("##cot##", self.config["cot"])
        )
        self.arbiter.set_meta_prompt(self.config['arbiter_meta_prompt'])

        print(f"===== Debate Round-1 =====\n")
        # Validator turn 1
        self.validator.add_event(
            self.config['validator_first_prompt']
                .replace("##issue##", self.config["issue"])
                .replace("##cot##", self.config["cot"])
        )
        self.val_ans = self.validator.ask(self.validator.memory_lst)
        self.config['base_answer'] = self.val_ans

        # Defender turn 1
        self.defender.add_event(self.config['defender_prompt'].replace('##val_ans##', self.val_ans))
        self.def_ans = self.defender.ask(self.defender.memory_lst)
        self.defender.add_memory(self.def_ans)

        # Arbiter turn 1
        self.arbiter.add_event(
            self.config['arbiter_prompt']
                .replace('##val_ans##', self.val_ans)
                .replace('##def_ans##', self.def_ans)
                .replace('##round##', 'first')
        )
        self.arb_ans = self.arbiter.ask(self.arbiter.memory_lst)
        self.arbiter.add_memory(self.arb_ans)

        try:
            self.arb_ans = json.loads(self.arb_ans)
        except json.JSONDecodeError:
            self.arb_ans = {"debate_answer": ""}

    def round_dct(self, num: int):
        dct = {1: 'first', 2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth',
               6: 'sixth', 7: 'seventh', 8: 'eighth', 9: 'ninth', 10: 'tenth'}
        return dct.get(num, str(num))

    def get_all_stats(self):
        summary = {
            "total_calls": 0,
            "total_runtime": 0.0,
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0
        }
        agent_stats = {}

        for player in self.players:
            agent_stats[player.name] = player.stats.copy()
            agent_stats[player.name]["runtime"] = round(player.stats["runtime"], 4)

            summary["total_calls"] += player.stats["calls"]
            summary["total_runtime"] += player.stats["runtime"]
            summary["total_tokens"] += player.stats["total_tokens"]
            summary["prompt_tokens"] += player.stats["prompt_tokens"]
            summary["completion_tokens"] += player.stats["completion_tokens"]

        summary["total_runtime"] = round(summary["total_runtime"], 4)
        return summary, agent_stats

    def run(self):
        for round_idx in range(self.max_round - 1):
            print(f"===== Debate Round-{round_idx + 2} =====\n")

            # Validator
            self.validator.add_event(
                self.config['validator_prompt']
                    .replace("##issue##", self.config["issue"])
                    .replace("##cot##", self.config["cot"])
                    .replace("##def_ans##", self.def_ans)
            )
            self.val_ans = self.validator.ask(self.validator.memory_lst)
            self.validator.add_memory(self.val_ans)

            # Defender
            self.defender.add_event(self.config['defender_prompt'].replace('##val_ans##', self.val_ans))
            self.def_ans = self.defender.ask(self.defender.memory_lst)
            self.defender.add_memory(self.def_ans)

            # Arbiter
            self.arbiter.add_event(
                self.config['arbiter_prompt']
                    .replace('##val_ans##', self.val_ans)
                    .replace('##def_ans##', self.def_ans)
                    .replace('##round##', self.round_dct(round_idx + 2))
            )
            self.arb_ans = self.arbiter.ask(self.arbiter.memory_lst)
            self.arbiter.add_memory(self.arb_ans)

            try:
                self.arb_ans = json.loads(self.arb_ans)
            except json.JSONDecodeError:
                self.arb_ans = {"debate_answer": ""}

        # Final Decision
        print("===== Final Decision =====\n")
        self.arbiter.add_event(self.config['judge_prompt_last2'])
        self.final_ans = self.arbiter.ask(self.arbiter.memory_lst)
        self.arbiter.add_memory(self.final_ans)

        def clean_final_answer(final_ans):
            try:
                final_ans = re.sub(r"<think>.*?</think>", "", final_ans, flags=re.DOTALL).strip()
                json_match = re.search(r"```json\s*(\{.*?\})\s*```", final_ans, re.DOTALL)
                if json_match:
                    return json_match.group(1)
                elif final_ans.strip().startswith("{") and final_ans.strip().endswith("}"):
                    return final_ans
                return "{}"
            except:
                return "{}"

        self.final_ans_str = clean_final_answer(self.final_ans)
        try:
            self.final_ans_json = json.loads(self.final_ans_str)
        except json.JSONDecodeError:
            self.final_ans_json = {"debate_answer": "", "analysis": self.final_ans}

        self.config.update(self.final_ans_json)
        self.config['success'] = True
        self.config["final_judgment"] = self.final_ans_json


if __name__ == '__main__':
    current_script_path = os.path.abspath(__file__).replace("\\", "/")
    MAD_path = current_script_path.rsplit("/", 1)[0]

    input_file = os.path.join(MAD_path, "input.josnl")
    output_file = os.path.join(MAD_path, "output.jsonl")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    config_path = f"{MAD_path}/code/utils/config4cot.json"
    if not os.path.exists(config_path):
        print(f"⚠️ Warning: Configuration file {config_path} not found. Using default empty configuration.")
        config_template = {
            "validator_meta_prompt": "You are a validator.",
            "defender_meta_prompt": "You are a defender.",
            "arbiter_meta_prompt": "You are an arbiter.",
            "validator_first_prompt": "Validate ##issue##",
            "defender_prompt": "Defend against ##val_ans##",
            "arbiter_prompt": "Judge ##val_ans## and ##def_ans##",
            "validator_prompt": "Validate again ##def_ans##",
            "judge_prompt_last2": "Final judgment"
        }
    else:
        config_template = json.load(open(config_path, "r", encoding='utf-8'))

    print(f"🚀 Processing begins, output to: {output_file}")

    with jsonlines.open(input_file, "r") as reader, jsonlines.open(output_file, "w") as writer:
        for entry in reader:
            loop_start_time = time.time()  

            question_id = entry.get("question_id", "unknown_id")
            issue = str(entry.get("input“, ”No problem description provided"))
            cot = str(entry.get("steps“, ”CoT process not provided"))
            code = entry.get("generate_results", "No code provided")

            if isinstance(code, list): code = "\n".join(code)

            print(f"\n----------------------------------------------------")
            print(f"Processing Question ID: {question_id}")

            config = config_template.copy()
            config['issue'] = issue
            config['cot'] = cot

            # Initialize and run the debate
            debate = Debate(num_players=3, openai_api_key=OPENAI_API_KEY, config=config, max_round=2, temperature=0, sleep_time=0)
            debate.run()

            # resluts
            final_result = debate.config.get("final_judgment", {})
            error_type = final_result.get("error_type", [])
            analysis = final_result.get("analysis", "No analysis provided")

            global_stats, agent_stats = debate.get_all_stats()
            loop_end_time = time.time()
            total_duration = loop_end_time - loop_start_time

    
            output_entry = {
                "question_id": question_id,
                "input": issue,
                "steps": cot,
                "generate_results": code,
                "error_type": error_type,
                "analysis": analysis,
                "global_stats": {
                    "wall_clock_time": round(total_duration, 2),  
                    "api_total_runtime_sum": global_stats["total_runtime"],  
                    "total_calls": global_stats["total_calls"],
                    "total_tokens": global_stats["total_tokens"],
                    "prompt_tokens": global_stats["prompt_tokens"],
                    "completion_tokens": global_stats["completion_tokens"]
                },

                "agent_stats": agent_stats
            }

            writer.write(output_entry)
            try:
                writer._fp.flush()
                os.fsync(writer._fp.fileno())  
            except AttributeError:
                pass  

            print(f"✅ Completed ID: {question_id} | Time taken: {total_duration:.2f}s | Token: {global_stats['total_tokens']}")

    print("\n✅ All tasks have been completed!")

    