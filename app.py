import streamlit as st
import traceback
import sys
import io
import matplotlib.pyplot as plt
import importlib

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="GroundTruth",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STATE MANAGEMENT ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# Store BPMN as an image buffer (BytesIO), not a Figure object
if "bpmn_image" not in st.session_state:
    st.session_state.bpmn_image = None

if "delay_model_results" not in st.session_state:
    st.session_state.delay_model_results = {"run": False, "logs": "", "figures": []}


def navigate_to(page_name):
    st.session_state.current_page = page_name
    st.rerun()


# --- GLOBAL CACHING (SPEED BOOST) ---
@st.cache_resource
def get_chatbot_agent():
    # REMOVED TRY/EXCEPT so we can see the real error in the UI if it fails
    import Chatbot_neo4j as bot_module
    return bot_module


@st.cache_resource
def load_yolo_model():
    from ultralytics import YOLO
    return YOLO('./Object_detection/best.pt')


# =========================================================
# 🏠 DASHBOARD
# =========================================================
def show_home():
    st.title("✈️ GroundTruth Operations Hub")
    st.markdown("### Select a module to begin")
    st.divider()

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.subheader("🤖 Flight Assistant")
            st.markdown("**GraphRAG AI Agent** with Neo4j & LLaMa 3.")
            if st.button("Launch Assistant 🚀", use_container_width=True): navigate_to("Flight Assistant")

    with col2:
        with st.container(border=True):
            st.subheader("🛡️ Delay Risk Analysis")
            st.markdown("**Predictive Analytics** with Random Forest.")
            if st.button("Launch Risk Model 📊", use_container_width=True): navigate_to("Delay Prediction")

    with col3:
        with st.container(border=True):
            st.subheader("👁️ Turnaround Vision")
            st.markdown("**Computer Vision** (YOLOv8) for real-time tracking.")
            if st.button("Launch Vision AI 🎥", use_container_width=True): navigate_to("Turnaround Vision")

    with col4:
        with st.container(border=True):
            st.subheader("🗺️ Process Visualizer")
            st.markdown("**BPMN Visualization** for SOP compliance.")
            if st.button("View Process Map 📐", use_container_width=True): navigate_to("BPMN Visualizer")


# =========================================================
# 🤖 APP 1: CHATBOT
# =========================================================
def show_chatbot():
    st.button("← Back to Dashboard", on_click=navigate_to, args=("Home",))
    st.title("🤖 GroundTruth Assistant")

    try:
        bot_module = get_chatbot_agent()
    except Exception as e:
        st.error("❌ Critical Error Importing Chatbot")
        st.error(f"Error details: {e}")
        st.warning("Check your requirements.txt and Streamlit Secrets.")
        return

    if "messages" not in st.session_state: st.session_state.messages = []

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).markdown(msg["content"])

    if prompt := st.chat_input("Ask about a flight..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").markdown(prompt)

        with st.chat_message("assistant"):
            if hasattr(bot_module, 'agent_executor'):
                with st.spinner("Thinking..."):
                    try:
                        response = bot_module.agent_executor.invoke({"input": prompt})
                        st.markdown(response['output'])
                        st.session_state.messages.append({"role": "assistant", "content": response['output']})
                    except Exception as e:
                        st.error(f"Error: {e}")


# =========================================================
# 🛡️ APP 2: DELAY ML
# =========================================================
def show_delay_model():
    st.button("← Back to Dashboard", on_click=navigate_to, args=("Home",))
    st.title("🛡️ Delay Risk Analysis")

    try:
        import delay_ml
    except Exception as e:
        st.error(f"❌ Error loading 'delay_ml.py'")
        st.code(f"{e}")
        return

    # Check Cache
    if st.session_state.delay_model_results["run"]:
        st.success("Loaded from Cache")
        st.code(st.session_state.delay_model_results["logs"])
        for fig in st.session_state.delay_model_results["figures"]:
            st.pyplot(fig)
        if st.button("🔄 Re-run"):
            st.session_state.delay_model_results = {"run": False, "logs": "", "figures": []}
            st.rerun()
        return

    if st.button("🚀 Run Model Training"):
        captured_output = io.StringIO()
        figures_captured = []

        class StreamlitLogger:
            def write(self, msg): captured_output.write(msg)

            def flush(self): pass

        old_stdout = sys.stdout
        sys.stdout = StreamlitLogger()

        old_show = plt.show

        def new_show():
            fig = plt.gcf()
            st.pyplot(fig)
            figures_captured.append(fig)
            plt.figure()

        plt.show = new_show

        try:
            with st.spinner("Training..."):
                importlib.reload(delay_ml)
                delay_ml.main()

            st.session_state.delay_model_results = {
                "run": True,
                "logs": captured_output.getvalue(),
                "figures": figures_captured
            }
            st.success("Done!")
        except Exception as e:
            st.error(f"Runtime Error: {e}")
            st.code(traceback.format_exc())
        finally:
            sys.stdout = old_stdout
            plt.show = old_show


# =========================================================
# 👁️ APP 3: VISION (Optimization Fix)
# =========================================================
def show_vision_app():
    st.button("← Back to Dashboard", on_click=navigate_to, args=("Home",))
    st.title("GroundTruth Vision Analysis")

    try:
        import cv2
    except ImportError as e:
        st.error("❌ Library Import Error")
        st.code(f"Error details: {e}")
        return

    col_vid, col_stat = st.columns([0.7, 0.3])
    if "vision_active" not in st.session_state: st.session_state.vision_active = False

    with col_vid:
        c1, c2 = st.columns(2)
        if c1.button("▶️ Start"): st.session_state.vision_active = True
        if c2.button("⏹️ Stop"): st.session_state.vision_active = False
        st_frame = st.empty()

    # Place the status placeholder OUTSIDE the loop so it doesn't duplicate
    with col_stat:
        st.subheader("Live Phase Detection")
        status_placeholder = st.empty()

    if st.session_state.vision_active:
        try:
            model = load_yolo_model()
            video_path = './Object_detection/turnaround clip.mp4'
            cap = cv2.VideoCapture(video_path)

            if not cap.isOpened():
                st.error(f"❌ Could not find video at: {video_path}")
                st.info("Make sure you uploaded 'Object_detection/turnaround clip.mp4' to GitHub.")
                st.session_state.vision_active = False
                return

            phases = {"DEBOARDING": False, "CLEANING": False, "BOARDING": False, "LUGGAGE": False}
            count = 0
            frame_counter = 0

            while st.session_state.vision_active and cap.isOpened():
                success, frame = cap.read()
                if not success:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop video
                    continue

                # PERFORMANCE FIX: Only process every 3rd frame
                frame_counter += 1
                if frame_counter % 3 != 0:
                    continue

                results = model(frame, verbose=False)
                detected = [model.names[int(b.cls[0])] for b in results[0].boxes]

                if "cleaning_crew_vehicle" in detected:
                    count += 1
                    phases["CLEANING"] = True
                if "luggage_vehicle" in detected: phases["LUGGAGE"] = True
                if "bridge_connected" in detected:
                    if count < 10:
                        phases["DEBOARDING"] = True
                    else:
                        phases["BOARDING"] = True

                # Display Video
                frame_rgb = cv2.cvtColor(results[0].plot(), cv2.COLOR_BGR2RGB)
                st_frame.image(frame_rgb, use_container_width=True)

                # Update status (REPLACE text, don't append)
                status_text = ""
                for p, active in phases.items():
                    icon = "✅" if active else "⬜"
                    color = "green" if active else "grey"
                    status_text += f":{color}[{icon} **{p}**]\n\n"

                status_placeholder.markdown(status_text)

            cap.release()
        except Exception as e:
            st.error(f"Runtime Error: {e}")
            st.code(traceback.format_exc())
            st.session_state.vision_active = False


# =========================================================
# 🗺️ APP 4: BPMN (Image Caching Fix)
# =========================================================
def show_bpmn_app():
    st.button("← Back to Dashboard", on_click=navigate_to, args=("Home",))
    st.title("🗺️ GroundTruth Process Map")

    if st.session_state.bpmn_image is not None:
        st.success("Loaded from Cache")
        st.image(st.session_state.bpmn_image)
        if st.button("🔄 Regenerate"):
            st.session_state.bpmn_image = None
            st.rerun()
        return

    if st.button("📐 Generate Diagram"):
        original_show = plt.show
        try:
            def save_as_image():
                buf = io.BytesIO()
                plt.savefig(buf, format="png", bbox_inches='tight')
                buf.seek(0)
                st.session_state.bpmn_image = buf
                st.image(buf)
                plt.clf()

            plt.show = save_as_image

            if 'bpmn_visualizer' in sys.modules:
                import bpmn_visualizer
                importlib.reload(bpmn_visualizer)
            else:
                import bpmn_visualizer

        except Exception as e:
            st.error(f"Error: {e}")
            st.code(traceback.format_exc())
        finally:
            plt.show = original_show


# --- ROUTER ---
pages = {
    "Home": show_home,
    "Flight Assistant": show_chatbot,
    "Delay Prediction": show_delay_model,
    "Turnaround Vision": show_vision_app,
    "BPMN Visualizer": show_bpmn_app
}
pages[st.session_state.current_page]()