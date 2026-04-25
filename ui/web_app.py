import os
import sys
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ingestion import IngestionModule
from core.engine import SimulationEngine
from core.synthesizer import Synthesizer
from utils.document_parser import extract_text_from_file

st.set_page_config(page_title="HaruFishing 社交沙盘", page_icon="🎀", layout="wide")

def render_knowledge_graph(nodes_data, edges_data):
    """使用 Pyvis 渲染动态力导向知识图谱"""
    import pyvis.network as net
    import tempfile
    
    g = net.Network(height='600px', width='100%', bgcolor='#ffffff', font_color='#333333', directed=True)
    g.barnes_hut(gravity=-3000, central_gravity=0.3, spring_length=150)
    
    color_map = {'Person': '#FF9999', 'Event': '#99CCFF', 'Action': '#99FF99', 'Emotion': '#FFCC99'}
    
    for node in nodes_data:
        group = node.group if node.group else 'Default'
        color = color_map.get(group, '#CCCCCC')
        shape = 'dot' if group == 'Person' else 'box'
        size = 25 if group == 'Person' else 15
        g.add_node(node.id, label=node.label, title=group, color=color, shape=shape, size=size)
        
    for edge in edges_data:
        g.add_edge(edge.source, edge.target, title=edge.label, label=edge.label, color='#888888')
        
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp:
        g.save_graph(tmp.name)
        with open(tmp.name, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
    components.html(html_content, height=620, scrolling=True)

def t(zh: str, en: str, ja: str = None) -> str:
    lang = st.session_state.get('ui_lang', '中文')
    if lang == '中文':
        return zh
    elif lang == 'English':
        return en
    else:
        return ja if ja else zh




def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Shippori+Mincho&display=swap');
    
    /* 全局字体更改为 ShipporiMincho */
    html, body, [class*="css"] {
        font-family: 'Shippori Mincho', serif !important;
    }

    /* 强制直角边框 */
    button, input, select, textarea, 
    div[data-baseweb], 
    div[data-testid="stExpander"] details, 
    div[data-testid="stFileUploader"] section,
    div[data-testid="stToast"] {
        border-radius: 0px !important;
    }
    
    /* 确认推演的主要按钮：白底黑字。强制所有子元素(如p标签)也是黑色 */
    button[kind="primary"], button[data-testid="baseButton-primary"] {
        background-color: #ffffff !important;
        border: 1px solid #ffffff !important;
    }
    button[kind="primary"] *, button[data-testid="baseButton-primary"] * {
        color: #000000 !important;
        font-weight: bold !important;
    }
    
    button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover {
        background-color: #cccccc !important;
        border-color: #cccccc !important;
    }
    button[kind="primary"]:hover *, button[data-testid="baseButton-primary"]:hover * {
        color: #000000 !important;
    }
    
    /* 极简黑白滚动条 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #000; 
    }
    ::-webkit-scrollbar-thumb {
        background: #555; 
        border-radius: 0px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #fff; 
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    inject_custom_css()

    # --- 侧边栏 ---
    with st.sidebar:
        st.session_state.ui_lang = st.radio("🌐 Language / 语言 / 言語", ["中文", "English", "日本語"], horizontal=True)
        st.header(t("⚙️ 引擎配置", "⚙️ Engine Config", "⚙️ エンジン設定"))
        
        load_dotenv(override=True)
        env_key = os.getenv("GEMINI_API_KEY")
        if env_key and env_key.startswith("在这里填入"):
            env_key = ""
            
        api_key_input = st.text_input(
            t("Gemini API Key (输入后请点击确认)", "Gemini API Key (Click confirm after input)", "Gemini API Key (入力後に確認をクリック)"), 
            type="password", 
            value=st.session_state.get("current_api_key", env_key or "")
        )
        
        if st.button(t("✔️ 确认 / 更新 Key", "✔️ Confirm / Update Key", "✔️ 確認 / 更新")):
            if api_key_input:
                st.session_state.current_api_key = api_key_input
                os.environ['GEMINI_API_KEY'] = api_key_input
                st.toast(t("API Key 已成功挂载！", "API Key successfully mounted!", "API Keyが正常に設定されました！"), icon="✅")
            else:
                st.toast(t("请输入 API Key 哦！", "Please input API Key!", "API Keyを入力してください！"), icon="⚠️")

        active_key = st.session_state.get("current_api_key") or env_key
        if active_key:
            os.environ['GEMINI_API_KEY'] = active_key
            masked_key = active_key[:6] + "..." + active_key[-4:] if len(active_key) > 10 else "***"
            
            if st.session_state.get("current_api_key"):
                st.success(t(f"✅ 使用手动输入的 Key: `{masked_key}`", f"✅ Using manual Key: `{masked_key}`", f"✅ 手動入力のKeyを使用中: `{masked_key}`"))
            else:
                st.success(t(f"✅ 使用本地 .env 的 Key: `{masked_key}`", f"✅ Using local .env Key: `{masked_key}`", f"✅ ローカル.envのKeyを使用中: `{masked_key}`"))
                
            if st.toggle(t("👁️ 显示完整的 API Key", "👁️ Show full API Key", "👁️ 完全なAPI Keyを表示")):
                st.code(active_key)
        else:
            st.warning(t("⚠️ 引擎处于离线状态，请填入 API Key", "⚠️ Engine offline, please input API Key", "⚠️ エンジンはオフラインです。API Keyを入力してください"))
            
        st.markdown("---")
        st.header(t("🧠 模型选择", "🧠 Model Selection", "🧠 モデル選択"))
        model_choice = st.selectbox(
            t("选择底层推演模型", "Select simulation model", "推論モデルを選択"),
            ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.1-pro-preview"],
            index=1,
            help=t("Flash 速度快；Pro 逻辑深。", "Flash is fast; Pro has deeper logic.", "Flashは高速、Proは深い論理的思考。")
        )
        os.environ['GEMINI_MODEL'] = model_choice

        st.markdown("---")
        st.header(t("📂 剧本注入", "📂 Scenario Injection", "📂 シナリオ注入"))
        
        data_mode = st.radio(t("选择剧本来源:", "Select scenario source:", "シナリオのソースを選択:"), [t("使用自带经典案例 (张三买奔驰)", "Use built-in classic case", "組み込みの定番ケースを使用 (張三、ベンツを買う)"), t("上传我自己的吃瓜文档", "Upload my own document", "自作のドキュメントをアップロード")])
        
        uploaded_file = None
        if data_mode == t("上传我自己的吃瓜文档", "Upload my own document", "自作のドキュメントをアップロード"):
            uploaded_file = st.file_uploader(
                t("拖拽上传文档 (支持 .txt, .pdf, .docx)", "Drag and drop document (supports .txt, .pdf, .docx)", "ドキュメントをドラッグ＆ドロップ (.txt, .pdf, .docx 対応)"), 
                type=['txt', 'pdf', 'docx']
            )
            if uploaded_file and st.session_state.get("last_uploaded_name") != uploaded_file.name:
                st.session_state.simulation_input = None 
                st.session_state.last_uploaded_name = uploaded_file.name
                st.info(t("检测到新文件，请点击右侧按钮进行解析。", "New file detected, please click the button on the right to parse.", "新しいファイルが検出されました。右側のボタンをクリックして解析してください。"))

    st.title(t("🎀 HaruFishing 微型群体智能沙盘 (完全体)", "🎀 HaruFishing Micro Swarm Intelligence Sandbox", "🎀 HaruFishing マイクロ群知能サンドボックス (完全体)"))
    st.markdown(t("上传剧情文档 (TXT/PDF/Word)，AI 将自动提炼角色恩怨并推演未来局势发酵！", "Upload a story document (TXT/PDF/Word), and AI will automatically extract character grievances and simulate future situations!", "ドキュメント(TXT/PDF/Word)をアップロードすると、AIがキャラクターの因縁を抽出し、今後の展開を予測します！"))
    
    if "simulation_input" not in st.session_state:
        st.session_state.simulation_input = None

    if data_mode == t("使用自带经典案例 (张三买奔驰)", "Use built-in classic case", "組み込みの定番ケースを使用 (張三、ベンツを買う)"):
        data_file = os.path.join(os.path.dirname(__file__), "..", "data", "test_mercedes.json")
        try:
            if st.session_state.simulation_input is None or st.session_state.get("is_custom_mode", False):
                st.session_state.simulation_input = IngestionModule.load_simulation_data(data_file)
                st.session_state.is_custom_mode = False 
        except Exception as e:
            st.error(f"{t('读取默认剧本失败:', 'Failed to read default scenario:', 'デフォルトシナリオの読み込みに失敗しました:')} {e}")
            return
            
    else:
        if uploaded_file and st.session_state.simulation_input is None:
            if st.button(t("🪄 开始解析文档并提取角色", "🪄 Start parsing document & extract characters", "🪄 ドキュメントを解析し、キャラクターを抽出"), type="primary"):
                if not os.environ.get("GEMINI_API_KEY"):
                    st.error(t("请先在左侧输入 API Key！", "Please input API Key in the sidebar first!", "まず左側にAPI Keyを入力してください！"))
                    return
                    
                with st.spinner(t("正在粉碎文档并喂给大模型提取角色设定...", "Processing document and extracting character settings via AI...", "ドキュメントを処理し、AIでキャラクター設定を抽出中...")):
                    try:
                        temp_path = os.path.join(os.path.dirname(__file__), "..", "data", f"temp_{uploaded_file.name}")
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        raw_text = extract_text_from_file(temp_path)
                        if not raw_text.strip():
                            st.error(t("文档内容为空或提取失败！", "Document is empty or extraction failed!", "ドキュメントが空であるか、抽出に失敗しました！"))
                            return
                            
                        simulation_input = IngestionModule.extract_from_document(raw_text)
                        st.session_state.is_custom_mode = True 
                        st.session_state.simulation_input = simulation_input
                        
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                            
                        st.rerun()
                    except Exception as e:
                        st.error(f"{t('解析失败:', 'Parsing failed:', '解析失敗:')} {e}")
                        
        elif not uploaded_file:
            st.session_state.simulation_input = None 
            st.info(t("👆 请先在左侧侧边栏上传一份剧情文档哦！", "👆 Please upload a story document in the sidebar first!", "👆 まず左側のサイドバーでシナリオドキュメントをアップロードしてください！"))
            return

    if st.session_state.simulation_input:
        sim_data = st.session_state.simulation_input
        
        if st.session_state.get("is_custom_mode", False):
            st.success(t("✅ 剧本提炼成功！请确认以下 AI 提取的角色卡片：", "✅ Scenario extracted! Please confirm the character cards:", "✅ シナリオの抽出に成功しました！以下のキャラクターカードを確認してください："))
        else:
            st.info(t("💡 当前使用的是自带的测试案例。如果你不想上传文件，可以直接点击推演看看效果哦！", "💡 Currently using the built-in test case. You can directly click simulate to see the result!", "💡 現在は組み込みのテストケースを使用しています。推論をクリックして結果を確認できます！"))
            
        st.info(f"**🔥 {t('核心触发事件', 'Core Trigger Event', 'コアイベント')}**: {sim_data.trigger_event}")
        cols = st.columns(len(sim_data.characters))
        for i, char in enumerate(sim_data.characters):
            with cols[i % len(cols)]:
                with st.expander(f"👤 {char.name}", expanded=True):
                    st.write(f"**{t('性格设定', 'Identity', '性格と背景')}**: {char.identity}")
                    st.write(f"**{t('人际关系', 'Relationships', '人間関係')}**:")
                    for target, relation in char.relationships.items():
                        st.write(f"- {t('对待', 'Towards', '対する態度')} {target}: {relation}")

        st.markdown("---")
        
        if st.button(t("🚀 角色确认无误，开启推演模拟 (Blackboard)", "🚀 Characters confirmed, Start Simulation (Blackboard)", "🚀 キャラクターを確認し、推論シミュレーションを開始 (Blackboard)"), type="primary"):
            if not os.environ.get("GEMINI_API_KEY"):
                st.error(t("请先在左侧输入 API Key！", "Please input API Key in the sidebar first!", "まず左側にAPI Keyを入力してください！"))
                return
                
            with st.status(t("🎬 正在进行沙盘推演...", "🎬 Running sandbox simulation...", "🎬 サンドボックス推論を実行中..."), expanded=True) as status:
                try:
                    st.write(t("1️⃣ 为角色注入灵魂...", "1️⃣ Injecting souls into characters...", "1️⃣ キャラクターに魂を注入中..."))
                    agent_prompts = IngestionModule.build_agent_prompts(sim_data)
                    
                    st.write(t("2️⃣ 黑板引擎启动，角色开始回合制心理博弈...", "2️⃣ Blackboard engine started, turn-based psychological games begin...", "2️⃣ 黒板エンジンが起動し、ターン制の心理戦が開始..."))
                    engine = SimulationEngine(
                        simulation_input=sim_data, 
                        agent_prompts=agent_prompts, 
                        max_rounds=2
                    )
                    
                    graph_placeholder = st.empty()
                    def update_graph_ui(nodes, edges):
                        with graph_placeholder.container():
                            render_knowledge_graph(nodes, edges)

                    interaction_logs, graph_nodes, graph_edges = engine.run_simulation(on_step_complete=update_graph_ui)
                    graph_placeholder.empty()
                    
                    with st.expander(t("📝 查看引擎内部未删减的原始撕逼日志", "📝 View raw, uncut interaction logs", "📝 エンジン内部の未編集の生ログを表示")):
                        st.text(interaction_logs)
                        
                    st.write(t("3️⃣ 裁判 Agent 介入，撰写推演报告并绘制逻辑图...", "3️⃣ Synthesizer Agent generating report & graph...", "3️⃣ 審判Agentが介入し、推論レポートと論理図を作成中..."))
                    synthesizer = Synthesizer()
                    report = synthesizer.generate_report(sim_data.trigger_event, interaction_logs)
                    
                    status.update(label=t("✅ 推演完美落幕！", "✅ Simulation complete!", "✅ 推論シミュレーションが完了しました！"), state="complete", expanded=False)
                    
                    st.subheader(t("📊 近期局势预测结局 (Predictions)", "📊 Near-term Situation Predictions", "📊 近い将来の状況予測 (Predictions)"))
                    for i, pred in enumerate(report.predictions, 1):
                        st.markdown(f"#### {t('结局', 'Outcome', '結末')} {i}: {pred.scenario}")
                        st.markdown(f"**🎯 {t('发生概率', 'Probability', '発生確率')}**: `{pred.probability}`")
                        st.markdown(f"**🔗 {t('逻辑链条', 'Reasoning Chain', '論理チェーン')}**: {pred.reasoning_chain}")
                        st.divider()
                        
                    st.subheader(t("🕸️ 动态知识图谱 (力导向图)", "🕸️ Dynamic Knowledge Graph (Force-Directed)", "🕸️ 動的ナレッジグラフ (フォース・ディレクテッド)"))
                    st.caption(t("✨ 提示：你可以用鼠标自由拖拽节点，或者滚动鼠标滚轮缩放画布哦！", "✨ Tip: You can drag nodes or use the mouse wheel to zoom!", "✨ ヒント：マウスでノードをドラッグしたり、スクロールでズームできます！"))
                    try:
                        render_knowledge_graph(graph_nodes, graph_edges)
                        with st.expander(t("查看图谱节点原始数据", "View raw graph node data", "グラフノードの生データを表示")):
                            st.json({"nodes": [n.model_dump() for n in graph_nodes], "edges": [e.model_dump() for e in graph_edges]})
                    except Exception as graph_e:
                        st.warning(f"{t('图谱渲染失败，可能是大模型返回的节点有误:', 'Graph rendering failed:', 'グラフのレンダリングに失敗しました:')} {graph_e}")
                except Exception as e:
                    status.update(label=t("❌ 推演过程发生错误", "❌ Simulation error occurred", "❌ 推論プロセスでエラーが発生しました"), state="error")
                    st.error(f"{t('详细报错信息:', 'Error details:', 'エラーの詳細:')} {e}")

            # --- 页面底部装饰 ---
    st.markdown("---")
    img_path = os.path.join(os.path.dirname(__file__), "..", "assets", "harufishing_webfront.png")
    if os.path.exists(img_path):
        import base64
        with open(img_path, 'rb') as f:
            base64_img = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <style>
        .full-bleed-img {{
            width: 100vw;
            position: relative;
            left: 50%;
            right: 50%;
            margin-left: -50vw;
            margin-right: -50vw;
            display: block;
            object-fit: cover;
        }}
        </style>
        <img src="data:image/png;base64,{base64_img}" class="full-bleed-img" />
        <div style='text-align: center; color: gray; margin-top: 15px;'>{t('🎀 HaruFishing - 社交宇宙身边的预言家', '🎀 HaruFishing - The Prophet of Your Social Universe', '🎀 HaruFishing - ソーシャルユニバースの預言者')}</div>
        """, unsafe_allow_html=True)
if __name__ == "__main__":
    main()





