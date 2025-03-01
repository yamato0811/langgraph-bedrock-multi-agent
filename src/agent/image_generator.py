from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from agent.state import AgentState
from models.bedrock_img_gen_model import BedrockImageModel
from models.llm import LLM
from utils.img_util import convert_img_2_base64


class ImageGenerator:
    def __init__(self, llm: LLM, bedrock_image_model: BedrockImageModel) -> None:
        self.llm = llm
        self.bedrock_image_model = bedrock_image_model
        self.graph = self.build_graph()

    def build_graph(self) -> CompiledStateGraph:
        graph_builder = StateGraph(AgentState)
        graph_builder.add_node(self.create_image_generation_prompt)
        graph_builder.add_node(self.generate_image)

        graph_builder.set_entry_point("create_image_generation_prompt")
        graph_builder.add_edge("create_image_generation_prompt", "generate_image")
        graph_builder.set_finish_point("generate_image")

        return graph_builder.compile()

    def create_image_generation_prompt(self, state: AgentState) -> dict:
        response = self.llm(
            [
                (
                    "system",
                    "あなたは画像生成AI用のテキストプロンプトを作成する一流のプロンプトエンジニアです。",
                )
            ]
            + state["messages"]
            + [
                (
                    "human",
                    "画像の主題（ビジュアルコンセプト）を基に、画像生成AIに広告画像を生成させるための英語プロンプトを作成してください。結果のみ出力してください。",
                )
            ]
        )

        display_message_dict = {
            "role": "assistant",
            "title": "Image Generatorのプロンプト作成結果",
            "icon": "🖼️",
            "content": response.content,
        }

        return {
            "messages": response,
            "display_message_dict": display_message_dict,
        }

    def generate_image(self, state: AgentState) -> dict:
        response = self.bedrock_image_model(state["copy"], n=2)
        images = self.bedrock_image_model.extract_content(response)
        images_b64 = [convert_img_2_base64(image) for image in images]

        print(images_b64)

        return {
            "messages": response,
            "display_message_dict": None,
        }
