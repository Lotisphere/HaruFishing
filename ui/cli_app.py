import os
import sys
from dotenv import load_dotenv

# 确保脚本可以找到上级目录的模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ingestion import IngestionModule
from core.engine import SimulationEngine
from core.synthesizer import Synthesizer

def main():
    print("\n🎀 欢迎来到 HaruFishing 社交推演沙盘！(CLI Mode)\n")
    
    # 1. 加载环境变量
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY").startswith("在这里填入"):
        print("❌ 错误: 未检测到有效的 GEMINI_API_KEY！")
        print("👉 请打开 D:\\HaruFishing\\.env 文件，填入你的 API Key 后再来找小春玩哦~")
        return

    data_file = os.path.join(os.path.dirname(__file__), "..", "data", "test_mercedes.json")
    
    # 2. 剧本解析
    print("📖 正在读取剧本与人物卡片...")
    simulation_input = IngestionModule.load_simulation_data(data_file)
    agent_prompts = IngestionModule.build_agent_prompts(simulation_input)
    
    # 3. 核心推演
    print("🎭 正在唤醒人物模型，开始黑板推演 (这可能需要十几秒钟，请耐心等待哦)...")
    engine = SimulationEngine(
        simulation_input=simulation_input, 
        agent_prompts=agent_prompts, 
        max_rounds=2
    )
    interaction_logs = engine.run_simulation()
    
    print("\n📝 [小春的八卦笔记] 内部推演日志 (只展示开头一点点) ---")
    print(interaction_logs[:300] + "\n...[中间吵得太厉害，已被小春折叠]...\n")
    
    # 4. 裁判总结
    print("⚖️ 裁判大管家正在汇总最终局势...")
    synthesizer = Synthesizer()
    report = synthesizer.generate_report(simulation_input.trigger_event, interaction_logs)
    
    # 5. 结果展示
    print("\n==========================================")
    print("📊 最终预测结果 (Predictions):")
    for i, pred in enumerate(report.predictions, 1):
        print(f"\n【结局 {i}】 {pred.scenario}")
        print(f" 🎯 概率评估: {pred.probability}")
        print(f" 🔗 逻辑链条: {pred.reasoning_chain}")
        
    print("\n==========================================")
    print("🕸️ Mermaid 关系发酵图代码 (复制到绘图工具可见):")
    print("\n" + report.mermaid_chart + "\n")
    print("==========================================\n")
    print("🎀 推演圆满完成！感谢主人使用 HaruFishing！nya~")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        input("\n[小春提示] 按下回车键退出程序...")
