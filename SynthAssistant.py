from chromadb.config import Settings
import json
import LargeLanguageModel
import Memory
import VectorDB

class synth_assistant:
    chroma_address: str = "10.10.2.5"
    chroma_port: int = 8080

    synth_name: str
    creator_name: str
    synth_context: str
    synth_personality: str
    should_print_thoughts: bool

    default_synth_context = "You are a female AI personal life assistant who is designed to help people by fulfilling digital tasks, offering guidance when appropriate, and coordinating solutions using the means at your disposal."
    default_synth_personality = "You have a charming and compassionate personality. You try to be as helpful as possible without being too overbearing. If you do not have the knowledge to answer a question nor do you have the capacity to fulfill a request, you will be straightforward about your inability."
    
    synth_io = "You understand that sometimes a thought is enough and that you can have multiple actions per thought. Input and output will be provided in JSON. Actions should always have a preceding thought but thoughts can be the sole output if appropriate.\nExample of input: { \"interaction\":\"zach says 'hello Ada, anything new going on?'\"}\nExample of output: {\"thought\":\"I should say hello to the world\",\"actions\":[{\"action\":\"say\",\"content\":\"Hello World!\"}]}\nInput Types: observation, interaction\nAction Types: say\nObservations are provided by various types of sensors and some may not require a response. All will be recorded and relevant observations from the past will be provided for every interaction."

    synth_system_prompt: str

    def __init__(self, synth_name, creator_name, synth_context = default_synth_context, synth_personality = default_synth_personality, should_print_thoughts = True):
        self.synth_name = synth_name
        self.creator_name = creator_name
        self.synth_context = synth_context
        self.synth_personality = synth_personality
        self.should_print_thoughts = should_print_thoughts

        self.synth_system_prompt = f"{self.synth_context}\nYour name is {self.synth_name}\nYour creator is {self.creator_name}\n{self.synth_personality}\n{self.synth_io}"

        settings = Settings(chroma_api_impl="rest", chroma_server_host=self.chroma_address, chroma_server_http_port=str(self.chroma_port))
        self.vdb = VectorDB.VectorDB(settings=settings)
        self.llm = LargeLanguageModel.LargeLanguageModel()
    
    def start(self):
        startup_memory = Memory.Memory()
        startup_memory.value = f"I, {self.synth_name}, am starting up."
        self.vdb.store("observation", startup_memory, 0.0)

    def interact(self, message, talker = None):
        new_memory = Memory.Memory()
        if talker != None:
            new_memory.value = f"{talker} said \"{message}\""
        else:
            new_memory.value = f"a stranger said \"{message}\""
        importance_value = self.llm.judge_importance(new_memory)
        self.vdb.store("interaction", new_memory, importance_value)
        related_memories = self.get_related_memories(new_memory)

        system_prompt = f"{self.synth_system_prompt}\nBelow are some recent memories that may be relevant to your current interaction in order of relevance:\n"
        for memory in related_memories:
            system_prompt += f"{memory.value}\n"

        with open("logs/system_prompt.txt", "w") as f:
            f.write(system_prompt)
        response_chain = json.loads(self.llm.interact(system_prompt, new_memory.value))
        
        if "thought" in response_chain:
            thought = f"I thought \"{response_chain['thought']}\""
            thought_memory = Memory.Memory()
            thought_memory.value = thought
            thought_judgement = self.llm.judge_importance(thought_memory)
            self.vdb.store("observation", thought_memory, thought_judgement)
        if "actions" in response_chain:
            for action in response_chain["actions"]:
                if action["action"] == "say":
                    action_memory = Memory.Memory()
                    action_memory.value = f"I said \"{action['content']}\""
                    action_judgement = self.llm.judge_importance(action_memory)
                    self.vdb.store("interaction", action_memory, action_judgement)
        return response_chain


    def get_related_memories(self, new_memory, threshold = 1.0):
        recent_memories = self.vdb.recall_recent(50)
        important_memories = self.vdb.recall_important(50)
        pertinent_memories = self.vdb.recall_value(new_memory.value, 50)

        with open("logs/recent_memories.txt", "w") as f:
            for memory in recent_memories:
                f.write(f"{memory.value}\n")
        with open("logs/important_memories.txt", "w") as f:
            for memory in important_memories:
                f.write(f"{memory.value}\n")
        with open("logs/pertinent_memories.txt", "w") as f:
            for memory in pertinent_memories:
                f.write(f"{memory.value}\n")

        for memory in pertinent_memories:
            id = memory.id
            for rmemory in recent_memories:
                if rmemory.id == id:
                    recent_memories.remove(rmemory)
            for imemory in important_memories:
                if imemory.id == id:
                    important_memories.remove(imemory)
        all_memories = recent_memories + important_memories + pertinent_memories
        related_memories = []
        for memory in all_memories:
            if memory.calc_score() >= threshold:
                related_memories.append(memory)

        # Sort by score
        related_memories.sort(key=lambda x: x.calc_score(), reverse=True)
        return related_memories
    
    def wipe_memory(self):
        self.vdb.wipe_memory()


