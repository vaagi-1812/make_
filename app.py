import streamlit as st
import traceback
import sys
import io
import matplotlib.pyplot as plt
import importlib
import time

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Swissport AI Hub",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STATE MANAGEMENT ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# Initialize Session State for caching App 2 (ML) & App 4 (BPMN) results
if "delay_model_results" not in st.session_state:
    st.session_state.delay_model_results = {"run": False, "logs": "", "figures": []}

if "bpmn_figure" not in st.session_state:
    st.session_state.bpmn_figure = None


def navigate_to(page_name):
    st.session_state.current_page = page_name
    st.rerun()


# =========================================================
# 🏠 DASHBOARD HOME PAGE
# =========================================================
def show_home():
    st.title("✈️ Swissport AI Operations Hub")
    st.markdown("### Select a module to begin")
    st.markdown("---")

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.subheader("🤖 Flight Assistant")
            st.markdown("Generative AI Chatbot powered by Neo4j Knowledge Graph.")
            if st.button("Launch Assistant 🚀", use_container_width=True):
                navigate_to("Flight Assistant")

    with col2:
        with st.container(border=True):
            st.subheader("🛡️ Delay Risk Analysis")
            status = "✅ Ready" if st.session_state.delay_model_results["run"] else "⚠️ Not Run"
            st.markdown(f"Machine Learning model for delay prediction. Status: **{status}**")
            if st.button("Launch Risk Model 📊", use_container_width=True):
                navigate_to("Delay Prediction")

    with col3:
        with st.container(border=True):
            st.subheader("👁️ Turnaround Vision")
            st.markdown("Real-time Computer Vision analysis for turnaround phases.")
            if st.button("Launch Vision AI 🎥", use_container_width=True):
                navigate_to("Turnaround Vision")

    with col4:
        with st.container(border=True):
            st.subheader("🗺️ Process SOP Visualizer")
            status = "✅ Generated" if st.session_state.bpmn_figure else "⚠️ Not Generated"
            st.markdown(f"Interactive BPMN visualization. Status: **{status}**")
            if st.button("View Process Map 📐", use_container_width=True):
                navigate_to("BPMN Visualizer")


# =========================================================
# 🤖 MINI APP 1: CHATBOT
# =========================================================
def show_chatbot():
    st.button("← Back to Dashboard", on_click=navigate_to, args=("Home",))
    st.title("🤖 Graph-Augmented Flight Assistant")
    st.divider()

    try:
        import Chatbot_neo4j as bot_module
    except ImportError:
        st.error("Could not import 'Chatbot_neo4j.py'.")
        bot_module = None

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about a flight..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            if bot_module and hasattr(bot_module, 'agent_executor'):
                with st.spinner("Thinking..."):
                    try:
                        response = bot_module.agent_executor.invoke({"input": prompt})
                        answer = response['output']
                        message_placeholder.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.error("Agent not ready.")


# =========================================================
# 🛡️ MINI APP 2: DELAY ML (Optimized)
# =========================================================
def show_delay_model():
    st.button("← Back to Dashboard", on_click=navigate_to, args=("Home",))
    st.title("🛡️ Delay Risk Analysis")
    st.divider()

    # --- RENDER CACHED RESULTS IF AVAILABLE ---
    if st.session_state.delay_model_results["run"]:
        st.success("Analysis Loaded from Cache")
        st.code(st.session_state.delay_model_results["logs"])
        for fig in st.session_state.delay_model_results["figures"]:
            st.pyplot(fig)

        if st.button("🔄 Re-run Model"):
            st.session_state.delay_model_results = {"run": False, "logs": "", "figures": []}
            st.rerun()
        return

    # --- RUN NEW ANALYSIS ---
    if st.button("🚀 Run Model Training"):
        log_output = st.empty()
        captured_output = io.StringIO()
        figures_captured = []

        class StreamlitLogger:
            def write(self, message):
                captured_output.write(message)
                log_output.code(captured_output.getvalue(), language="text")

            def flush(self): pass

        original_stdout = sys.stdout
        original_show = plt.show

        try:
            import delay_ml
            sys.stdout = StreamlitLogger()

            # Patch plt.show to save the figure to session state instead of just clearing
            def streamlit_show():
                fig = plt.gcf()
                st.pyplot(fig)
                figures_captured.append(fig)  # Cache the figure object
                # We don't clear (clf) immediately so we can copy it,
                # but pyplot handles new figures automatically usually.
                # To be safe in loop:
                plt.figure()

            plt.show = streamlit_show

            with st.spinner("Processing Data..."):
                delay_ml.main()

            # Save to Session State
            st.session_state.delay_model_results["run"] = True
            st.session_state.delay_model_results["logs"] = captured_output.getvalue()
            st.session_state.delay_model_results["figures"] = figures_captured

            st.success("Done! Results cached.")

        except ImportError:
            st.error("Missing 'delay_ml.py'.")
        except Exception as e:
            st.error(f"Error: {e}")
            st.code(traceback.format_exc())
        finally:
            sys.stdout = original_stdout
            plt.show = original_show


# =========================================================
# 👁️ MINI APP 3: TURNAROUND VISION (Looping)
# =========================================================
def show_vision_app():
    st.button("← Back to Dashboard", on_click=navigate_to, args=("Home",))
    st.title("👁️ Computer Vision Turnaround Analysis")
    st.divider()

    try:
        import cv2
        from ultralytics import YOLO
    except ImportError:
        st.error("Missing libraries: `pip install opencv-python ultralytics`")
        return

    col_vid, col_stat = st.columns([0.7, 0.3])

    # Control logic
    if "vision_active" not in st.session_state:
        st.session_state.vision_active = False

    with col_vid:
        st.markdown("#### Video Feed")
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.button("▶️ Start Analysis"):
            st.session_state.vision_active = True
        if col_btn2.button("⏹️ Stop"):
            st.session_state.vision_active = False

        st_frame = st.empty()

    with col_stat:
        st.markdown("#### Live Phase Detection")
        status_placeholder = st.empty()

    if st.session_state.vision_active:
        video_path = './Object_detection/turnaround clip.mp4'
        model_path = './Object_detection/best.pt'

        try:
            model = YOLO(model_path)
            cap = cv2.VideoCapture(video_path)

            phases = {"DEBOARDING": False, "CLEANING": False, "BOARDING": False, "LUGGAGE": False}
            cleaning_count = 0

            while st.session_state.vision_active:
                success, frame = cap.read()

                # LOOPING LOGIC: If video ends, reset to frame 0
                if not success:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue

                results = model(frame, verbose=False)
                detected = [model.names[int(box.cls[0])] for box in results[0].boxes]

                # Logic
                if "cleaning_crew_vehicle" in detected:
                    cleaning_count += 1
                    phases["CLEANING"] = True
                if "luggage_vehicle" in detected:
                    phases["LUGGAGE"] = True
                if "bridge_connected" in detected:
                    if cleaning_count < 10:
                        phases["DEBOARDING"] = True
                    else:
                        phases["BOARDING"] = True

                # Display
                annotated = results[0].plot()
                st_frame.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), use_container_width=True)

                # Status
                status_txt = ""
                for p, active in phases.items():
                    color = "green" if active else "grey"
                    icon = "✅" if active else "⬜"
                    status_txt += f":{color}[{icon} **{p}**]\n\n"
                status_placeholder.markdown(status_txt)

            cap.release()

        except Exception as e:
            st.error(f"Error: {e}")


# =========================================================
# 🗺️ MINI APP 4: BPMN VISUALIZER (Optimized)
# =========================================================
def show_bpmn_app():
    st.button("← Back to Dashboard", on_click=navigate_to, args=("Home",))
    st.title("🗺️ SOP Process Visualization")
    st.divider()

    # --- RENDER CACHED FIGURE IF AVAILABLE ---
    if st.session_state.bpmn_figure:
        st.success("Loaded Process Map from Cache")
        st.pyplot(st.session_state.bpmn_figure)

        if st.button("🔄 Regenerate Diagram"):
            st.session_state.bpmn_figure = None
            st.rerun()
        return

    # --- GENERATE NEW DIAGRAM ---
    if st.button("📐 Generate Diagram"):
        original_show = plt.show
        try:
            def streamlit_show():
                fig = plt.gcf()
                st.pyplot(fig)
                # Store in session state
                st.session_state.bpmn_figure = fig
                plt.clf()

            plt.show = streamlit_show

            if 'bpmn_visualizer' in sys.modules:
                import bpmn_visualizer
                importlib.reload(bpmn_visualizer)
            else:
                import bpmn_visualizer

            st.success("Diagram Generated & Cached!")

        except ImportError:
            st.error("Missing 'bpmn_visualizer.py'. (Check spelling/underscores)")
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            plt.show = original_show


# =========================================================
# 🧭 MAIN ROUTERs
# =========================================================
if st.session_state.current_page == "Home":
    show_home()
elif st.session_state.current_page == "Flight Assistant":
    show_chatbot()
elif st.session_state.current_page == "Delay Prediction":
    show_delay_model()
elif st.session_state.current_page == "Turnaround Vision":
    show_vision_app()
elif st.session_state.current_page == "BPMN Visualizer":
    show_bpmn_app()