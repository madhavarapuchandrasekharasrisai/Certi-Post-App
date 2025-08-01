import streamlit as st
import fitz  # PyMuPDF
import json
import pathlib
import base64
from streamlit_lottie import st_lottie
from openai import OpenAI
from io import BytesIO
import streamlit.components.v1 as components
from PIL import Image, ImageEnhance, ImageFilter

@st.cache_resource
def get_openai_client():
    return OpenAI(
        base_url=st.secrets["openai"]["base_url"],
        api_key=st.secrets["openai"]["api_key"]
    )

client = get_openai_client()

st.set_page_config(
    page_title="CertiPost — AI Content Generator for Certificates & Projects",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# Sidebar content (load conditionally)
def render_sidebar():
    st.markdown(
        '<h3 style="text-align: center; font-family:Segoe UI, Tahoma, Geneva, Verdana, sans-serif; color:#5c6bc0; font-size: 2rem; font-weight:700; letter-spacing:0.5px; margin-bottom:10px;">Certi Post</h3>',
        unsafe_allow_html=True)
    st.markdown('<p class="subheading">“Every certificate tells a story — we help you share it beautifully.”</p>',
                unsafe_allow_html=True)

    if st.button("🏠 Homepage"):
        st.session_state.page = "Homepage"
        st.rerun()

    lottie_ani = load_lottiefile("share with friends.json")
    if lottie_ani:
        st_lottie(lottie_ani, height=290, key="sidebar_animation", quality="high")
    else:
        st.warning("⚠ Failed to load animation.")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 1em;'>
        🐞 Found a bug? <a href='mailto:madhavarapuchandrasekhara@gmail.com?subject=Bug Report'>Email us</a> 
        or report it below
        </div>
        """,
        unsafe_allow_html=True
    )

    bug_txt = st.text_input("Quick bug report:",
                            placeholder="Briefly describe the issue...",
                            label_visibility="collapsed")
    if st.button("Report Bug"):
        if not bug_txt:
            st.error("Please Fill the Field, or Email us if you want to contact.")
        else:
            st.success("Bug Reported, Email us if you want to contact.")

# Enhanced CSS with better mobile responsiveness
st.markdown("""
<style>
    /* Global styles */
    body {
        background-color: #f8f9fa; /* Light white-blue background for minimalism */
    }
    .main {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 40vh; /* Minimum height for vertical centering, flexible for content */
        text-align: center;
        border-radius: 30px;
        padding: 15px; /* Decreased padding for smaller margins */
        box-sizing: border-box; /* Ensures padding is included in element dimensions */
        transition: padding 0.4s ease; /* Subtle transition for responsiveness */
    }
    /* Responsive adjustments (enhanced for mobiles) */
    @media (max-width: 768px) {
        .main {
            padding: 10px; /* Slightly more padding on mobile for better touch usability */
            min-height: auto; /* Flexible height on small screens */
        }
        .main-heading { font-size: 2rem; } /* Smaller heading for mobiles */
        .main-subheading { font-size: 1.1rem; margin-bottom: 30px; }
        .stButton > button {
            width: 100%; /* Full width for easy tapping */
            font-size: 1rem;
            padding: 12px 20px; /* Larger padding for touch */
            margin: 10px 0;
        }
        .upload-instruction { font-size: 1rem; }
        .uploader-container { padding: 15px; }
        .section-title { font-size: 1.6rem; }
        .stTextArea textarea { height: 300px !important; } /* Adjust text area height for mobile */
        img { max-width: 100% !important; height: auto; } /* Scale images to fit screen */
        /* Stack columns vertically on mobile */
        div[data-testid="column"] { width: 100% !important; margin-bottom: 10px; }
        /* Reduce animation durations for faster mobile performance */
        @keyframes fadeInDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } animation-duration: 0.5s; }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } animation-duration: 0.5s; }
        @keyframes slideInLeft { from { opacity: 0; transform: translateX(-30px); } to { opacity: 1; transform: translateX(0); } animation-duration: 0.5s; }
        @keyframes buttonPulse { animation-duration: 1.5s; } /* Shorter pulse */
        @keyframes subtleGradient { animation-duration: 5s; } /* Shorter gradient animation */
        /* Hide sidebar on mobile devices by default */
        section[data-testid="stSidebar"] {
            display: none !important; /* Completely hide the sidebar */
        }
        /* Adjust the main content to take full width since sidebar is hidden */
        div[data-testid="stAppViewContainer"] > div {
            width: 100% !important;
            margin-left: 0 !important;
        }
    }
    .main-heading {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 3rem;
        font-weight: 700;
        color: transparent;
        background: linear-gradient(135deg, #3f51b5 0%, #5c6bc0 100%);
        -webkit-background-clip: text;
        background-clip: text;
        letter-spacing: 1px;
        margin-bottom: 10px;
        animation: fadeInDown 1s ease-out;
    }
    .main-subheading {
        font-size: 1.5rem;
        color: #6c757d; /* Professional gray for subtitle */
        margin-bottom: 60px; /* Increased space below subheading */
        animation: fadeInUp 1s ease-out 0.3s;
        opacity: 0;
        animation-fill-mode: forwards;
    }
    /* Style for Streamlit buttons to match action-button class */
    .stButton > button {
        background-color: #5c6bc0; /* Professional blue */
        color: white;
        font-size: 1.2rem;
        font-weight: 600;
        padding: 15px 30px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        width: 100%; /* Full width within column */
        margin: 10px 5px; /* Spacing between buttons */
        animation: buttonPulse 2s infinite; /* Restored pulse animation for buttons */
    }
    .stButton > button:hover {
        background-color: #3f51b5; /* Darker blue on hover */
        transform: scale(1.05); /* Subtle scaling */
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15); /* Enhanced shadow */
    }
    /* Upgraded styles for upload instruction */
    .upload-instruction {
        font-weight: 700;
        font-size: 1.2rem; /* Slightly larger for emphasis */
        color: #333;
        text-align: center;
        margin-bottom: 20px;
        animation: fadeInUp 1s ease-out;
        background: linear-gradient(135deg, #3f51b5 0%, #5c6bc0 100%);
        -webkit-background-clip: text;
        background-clip: text;
        letter-spacing: 0.5px;
    }
    .uploader-container {
        border: 2px dashed #5c6bc0; /* Dashed border for visual appeal */
        border-radius: 10px;
        padding: 20px;
        background-color: #f8f9fa;
        transition: border-color 0.3s ease;
        animation: fadeIn 1.5s ease-in-out; /* Restored fade-in animation for uploader */
    }
    .uploader-container:hover {
        border-color: #3f51b5; /* Hover effect */
    }
    /* Section titles styling */
    .section-title {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 2rem;
        font-weight: 600;
        color: #3f51b5;
        text-align: center;
        margin-bottom: 20px;
        animation: slideInLeft 1s ease-out; /* Restored slide-in animation for titles */
    }
    /* Restored Animations */
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes buttonPulse {
        0% { box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
        50% { box-shadow: 0 4px 12px rgba(92, 107, 192, 0.3); }
        100% { box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
    }
    /* Restored Subtle background animation */
    .main {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        animation: subtleGradient 10s ease infinite;
    }
    @keyframes subtleGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    /* Existing CSS integrations */
    .subheading {
        text-align: center;
        font-size: 1.25rem;
        color: #666;
        margin-bottom: 10px;
        font-style: italic;
    }
    /* Small back button styling */
    .stButton > button[key="back_button"] {
        font-size: 0.85rem !important;
        padding: 5px 12px !important;
        width: auto !important;
        background-color: #f8f9fa !important;
        color: #3f51b5 !important;
        border: 1px solid #5c6bc0 !important;
        border-radius: 5px !important;
        box-shadow: none !important;
        margin: 10px 0 !important;
        transition: background-color 0.3s ease !important;
    }
    .stButton > button[key="back_button"]:hover {
        background-color: #e9ecef !important;
    }
</style>
""", unsafe_allow_html=True)

# Homepage content
if 'page' not in st.session_state:
    st.session_state.page = "Homepage"

if st.session_state.page == "Homepage":
    with st.sidebar:
        render_sidebar()
    st.markdown("""
    <div class="main">
        <h1 class="main-heading">🚀 CertiPost: AI Content Generator for Certifications & Projects</h1>
        <p class="main-subheading">Turn your certificates and project files into engaging LinkedIn posts and GitHub READMEs — effortlessly!</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✍ LinkedIn Post", key="linkedin_button"):
            st.session_state.page = "LinkedIn Post"
            st.rerun()
    with col2:
        if st.button("📘 GitHub ReadMe", key="github_button"):
            st.session_state.page = "GitHub Read Me"
            st.rerun()

else:
    with st.sidebar:
        render_sidebar()
    cols = st.columns([0.1, 0.6])
    with cols[0]:
        if st.button("← Back", key="back_button"):
            with st.spinner("Loading..."):
                st.session_state.page = "Homepage"
                st.rerun()
    option = st.session_state.page

    # Cached PDF functions
    @st.cache_data
    def extract_text_from_pdf(pdf_bytes):
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            st.error(f"Error extracting text from PDF: {e}")
            return ""

    @st.cache_data
    def convert_pdf_to_images(pdf_content: bytes):
        try:
            images = []
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            for page in doc:
                pix = page.get_pixmap(matrix=fitz.Matrix(4, 4))  # Higher zoom for quality
                img_data = pix.tobytes("png")
                images.append(img_data)
            return images
        except Exception as e:
            st.error(f"Error converting PDF: {e}")
            return []

    def get_image_download_button(img, filename):
        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue(), filename.replace(".jpg", ".png")

    def pil_to_base64(img):
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

    SUPPORTED_FILE_TYPES = [".py", ".txt", ".md", ".html", ".js", ".css", ".json", ".xml", ".yml", ".yaml",
                            ".java", ".c", ".cpp", ".cs", ".go", ".rb", ".php", ".ts", ".r", ".swift",
                            ".ipynb", ".sql", ".sh", ".bat", ".pl", ".scala", ".kt", ".dart",
                            ".tex", ".jsx", ".tsx", ".ini", ".cfg", ".conf", ".csv", ".log", ".rst", ".makefile",
                            ".groovy", ".erl", ".ex", ".exs", ".jl", ".lua", ".m", ".mm", ".ml", ".scm", ".clj", ".coffee",
                            ".asm", ".s", ".v", ".sv", ".vhd", ".vhdl", ".fs", ".fsi", ".fsharp", ".nix",
                            ".h", ".hpp", ".hxx", ".cuh", ".mli", ".eliom", ".pp", ".pas", ".adb", ".ads",
                            ".ps1", ".vue", ".handlebars", ".hbs", ".twig", ".liquid", ".mustache", ".pbix"]

    def copy_to_clipboard_button(text, key):
        escaped_text = text.replace(" ", " ").replace(" ", " ").replace(" ", " ").replace("  ", " ")
        components.html(f"""
            <textarea id='copy_target_{key}' style='display:none;'>{escaped_text}</textarea>
            <div style='display: flex; justify-content: center; align-items: center;'>
                <div style='position: relative;'>
                    <button onclick="navigator.clipboard.writeText(document.getElementById('copy_target_{key}').value).then(() => {{
                            const toast = document.createElement('div');
                            toast.innerText = '✅ Copied to Clipboard!';
                            toast.style.position = 'fixed';
                            toast.style.bottom = '20px';
                            toast.style.right = '20px';
                            toast.style.backgroundColor = '#28a745';
                            toast.style.color = 'white';
                            toast.style.padding = '10px 20px';
                            toast.style.borderRadius = '10px';
                            toast.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
                            toast.style.zIndex = 9999;
                            document.body.appendChild(toast);
                            setTimeout(() => toast.remove(), 2000);
                        }})"
                        style="
                            padding: 12px 24px;
                            background-color: #5c6bc0;
                            color: white;
                            border: none;
                            border-radius: 10px;
                            cursor: pointer;
                            font-weight: 600;
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                            transition: background-color 0.4s ease;
                        ">
                        📋 Copy to Clipboard
                    </button>
                </div>
            </div>
        """, height=150)

    @st.cache_data
    def calculate_certification_score(extracted_text):
        try:
            extracted_text = extracted_text.lower()
            high_value_keywords = {
                "aws": 90, "azure": 85, "google cloud": 80, "python": 75, "machine learning": 85,
                "data science": 80, "project management": 70, "pmp": 75, "agile": 70, "scrum": 70,
                "cybersecurity": 85, "cissp": 90, "devops": 80, "kubernetes": 75, "docker": 70
            }
            medium_value_keywords = {
                "java": 60, "javascript": 55, "web development": 50, "sql": 55, "marketing": 50,
                "graphic design": 45, "photoshop": 40, "excel": 45, "accounting": 50
            }
            score = 30
            for keyword, value in high_value_keywords.items():
                if keyword in extracted_text:
                    score = max(score, value)
                    break
            if score == 30:
                for keyword, value in medium_value_keywords.items():
                    if keyword in extracted_text:
                        score = max(score, value)
                        break
            if "2023" in extracted_text or "2024" in extracted_text or "2025" in extracted_text:
                score += 10
            elif "2020" in extracted_text or "2021" in extracted_text or "2022" in extracted_text:
                score += 5
            return min(score, 100)
        except Exception as e:
            st.error(f"Error calculating certification score: {e}")
            return 50

    if option == "LinkedIn Post":
        st.markdown('<h2 class="section-title">✍ Generate LinkedIn Post</h2>', unsafe_allow_html=True)
        st.markdown("""
        <div class="uploader-container">
            <p class="upload-instruction">📄 Upload your certificate PDF and watch it transform into a sleek " HD image " with a professionally written LinkedIn post — all in one click!</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)
        pdf_file = st.file_uploader(
            label="Upload your PDF certificate",
            type="pdf",
            label_visibility="hidden",
            help="Upload your PDF certificate here. Supported file size up to 10MB."
        )
        if pdf_file:
            # Enforce 10MB file size limit
            if len(pdf_file.getvalue()) > 10 * 1024 * 1024:
                st.error("File size exceeds 10MB limit. Please upload a smaller file.")
            else:
                # Detect file change for regeneration
                current_file_name = pdf_file.name
                if 'last_pdf_file' not in st.session_state:
                    st.session_state.last_pdf_file = ""
                if current_file_name != st.session_state.last_pdf_file:
                    if 'linkedin_post' in st.session_state:
                        del st.session_state.linkedin_post
                    if 'market_score' in st.session_state:
                        del st.session_state.market_score
                    st.session_state.last_pdf_file = current_file_name

                pdf_content = pdf_file.read()  # Read once for caching
                original_name = pathlib.Path(pdf_file.name).stem
                images = convert_pdf_to_images(pdf_content)
                base64_images = []

                if images:
                    for i, img_data in enumerate(images):
                        try:
                            img = Image.open(BytesIO(img_data))
                            img = img.filter(ImageFilter.SHARPEN)
                            enhancer = ImageEnhance.Contrast(img)
                            img = enhancer.enhance(1.3)
                            img_resized = img.copy()
                            img_resized.thumbnail((2048, 2048))  # Larger for quality
                            img_bytes, img_name = get_image_download_button(img_resized, f"{original_name}.png")
                            with st.container():
                                st.markdown(
                                    f"""
                                    <div style='text-align:center;'>
                                        <img src='data:image/png;base64,{base64.b64encode(img_bytes).decode()}' style='max-width: 512px; height: auto; display: block; margin: 0 auto; border-radius: 10px;' />
                                        <a href='data:image/png;base64,{base64.b64encode(img_bytes).decode()}' download='{img_name}' style='padding: 10px 10px; background-color: #5c6bc0;color: white;border: none;border-radius: 10px;cursor: pointer;font-weight: 600;box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);transition: background-color 0.4s ease;'>⬇ Download {img_name}</a>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                            base64_images.append(pil_to_base64(img_resized))
                        except Exception as e:
                            st.error(f"Error processing image {i + 1}: {e}")

                extracted_text = extract_text_from_pdf(pdf_content)

                if extracted_text.strip():
                    cols = st.columns([0.3, 0.8])  # Create 2 columns, left smaller than right
                    with cols[0]:
                        if st.button("🔄 Regenerate Post"):
                            if 'linkedin_post' in st.session_state:
                                del st.session_state['linkedin_post']
                            if 'market_score' in st.session_state:
                                del st.session_state['market_score']
                            st.rerun()

                    # Check if the post is already generated and stored in session state
                    if 'linkedin_post' not in st.session_state:
                        with st.spinner("Generating LinkedIn post..."):
                            try:
                                prompt_text = extracted_text[:1500]
                                prompt = f"""You are a LinkedIn content expert. Given a certificate's content, write a detailed, friendly, and professional LinkedIn post that includes: 1) A catchy title, 2) A celebratory statement, 3) 3–5 sentences on what was learned, 4) A ✅ bullet list of 4–6 key topics or skills, 5) A motivational paragraph, 6) A thank-you message, 7) 📜 Certification date, 8) 🔗 Credential verification if available, 9) A closing CTA, 10) 6–10 hashtags with 15–20 emojis throughout. Also add an inspiring learning quote.Do not say Here's your Read me or include any pre-text.\n\n{prompt_text}"""

                                response = client.chat.completions.create(
                                    extra_body={},
                                    model="mistralai/mixtral-8x7b-instruct",
                                    messages=[{"role": "user", "content": prompt}],
                                )

                                market_score = calculate_certification_score(extracted_text)
                                st.session_state.market_score = market_score  # Store score

                                linkedin_post = response.choices[0].message.content.strip()
                                st.session_state.linkedin_post = linkedin_post  # Store the generated post
                            except Exception as e:
                                st.error(f"OpenRouter API error: {e}")
                                st.session_state.linkedin_post = ""  # Fallback

                    # Display the stored post
                    linkedin_post = st.session_state.get('linkedin_post', "")
                    market_score = st.session_state.get('market_score', 50)

                    with st.container():
                        st.markdown(
                            f"<p style='font-weight:600; font-size: 1.8rem; color:#3f51b5;'>📊 Certificate Market Value Score: {market_score}/100</p>",
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            """
                            <p style='font-size: 0.9rem; color:#666;'>
                            This score delivers a data-driven evaluation of your certification's market demand and relevance, informed by key content analysis and issuance timeline to support informed career decisions.
                            It serves as a strategic tool to gauge competitive edge—consider leveraging it to prioritize skill development and networking opportunities.
                            </p>
                            """,
                            unsafe_allow_html=True,
                        )

                    if linkedin_post:
                        st.subheader("✍ Generated LinkedIn Post")
                        st.text_area("LinkedIn Post With Your Credentials.", linkedin_post, height=500)

                        cols = st.columns([1, 1])
                        with cols[0]:
                            copy_to_clipboard_button(linkedin_post, "linkedin")
                        with cols[1]:
                            linkedin_share_url = f"https://www.linkedin.com/shareArticle?mini=true&url=https://certipost.streamlit.app/&title=CertiPost%20Achievement&summary={linkedin_post[:300]}&source=LinkedIn"
                            components.html(
                                f"""
                                <div style='display: flex; justify-content: center; align-items: center;'>
                                    <a href='{linkedin_share_url}' target='_blank'>
                                        <button style="
                                            padding: 12px 24px;
                                            background-color: #0A66C2;
                                            color: white;
                                            border: none;
                                            border-radius: 10px;
                                            cursor: pointer;
                                            font-weight: 600;
                                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                            transition: background-color 0.4s ease;">
                                            🔗 Share on LinkedIn
                                        </button>
                                    </a>
                                </div>
                                """,
                                height=100,
                            )

                        col_preview, _ = st.columns([1, 1])
                        with col_preview:
                            if st.button("👀 Preview (See How It Looks Like)", key="preview_linkedin"):
                                st.markdown(linkedin_post, unsafe_allow_html=True)
                    else:
                        st.info("No post generated yet. Try regenerating or check your upload.")

    elif option == "GitHub Read Me":
        st.markdown('<h2 class="section-title">📘 Generate GitHub README</h2>', unsafe_allow_html=True)
        st.markdown("""
        <div class="uploader-container">
            <p class="upload-instruction">🗂️ Upload your " Main Project File " and get a clean, professional GitHub README — generated just for you in seconds! — all in one click!</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)
        file = st.file_uploader("GitHub Project",label_visibility="hidden",help=" Only Upload Main Project File to generate your README")
        if file:
            try:
                # Detect file change for regeneration
                current_file_name = file.name
                if 'last_github_file' not in st.session_state:
                    st.session_state.last_github_file = ""
                if current_file_name != st.session_state.last_github_file:
                    if 'readme_text' in st.session_state:
                        del st.session_state.readme_text
                    st.session_state.last_github_file = current_file_name

                file_text = file.read().decode("utf-8", errors="ignore")

                cols = st.columns([0.3, 0.8])
                with cols[0]:
                    if st.button("🔄 Regenerate README"):
                        if 'readme_text' in st.session_state:
                            del st.session_state.readme_text
                        st.rerun()

                if 'readme_text' not in st.session_state:
                    with st.spinner("Generating GitHub README..."):
                        prompt = f"You are a professional GitHub README writer. Write a clean, emoji-rich README.md in Markdown format based on this project.README sholud contain above 10,000 Characters.Follow this section order: 1) Title with emoji, 2) 📖 Overview, 3) 📸 Screenshot (self-upload later), 4) ✨ Features, 5) 💡 Enhancements, 6) 🛠 Technologies, 7) 🚀 Getting Started, 8) 🧑‍💻 Usage, 9) 🔄 Data Handling, 10) 📄 License, 11) 🙏 Acknowledgments. Use markdown syntax, proper formatting, 10–15 emojis, and triple backticks for code.Do not say Here's your Read me or include any pre-text.\n\n{file_text}"
                        response = client.chat.completions.create(
                            extra_body={},
                            model="mistralai/mixtral-8x7b-instruct",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        readme_text = response.choices[0].message.content.strip()
                        st.session_state.readme_text = readme_text  # Store the generated README

                readme_text = st.session_state.get('readme_text', "")
                if readme_text:
                    st.subheader("📘 Generated README.md")
                    st.text_area("README", readme_text, height=400, key="readme_area")

                    cols = st.columns([1, 1])
                    with cols[0]:
                        copy_to_clipboard_button(readme_text, "readme")
                    with cols[1]:
                        github_url = "https://github.com/new"
                        components.html(
                            f"""
                            <div style='display: flex; justify-content: center; align-items: center;'>
                                <a href='{github_url}' target='_blank'>
                                    <button style="
                                        padding: 12px 24px;
                                        background-color: #24292F;
                                        color: white;
                                        border: none;
                                        border-radius: 10px;
                                        cursor: pointer;
                                        font-weight: 600;
                                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                        transition: background-color 0.4s ease;">
                                        🚀 Upload to GitHub
                                    </button>
                                </a>
                            </div>
                            """,
                            height=100,
                        )

                    col1, _ = st.columns([1, 1])
                    with col1:
                        if st.button("👀 Preview (See How It Looks Like)"):
                            st.markdown(readme_text, unsafe_allow_html=True)
                else:
                    st.info("No README generated yet. Try regenerating or check your upload.")

            except Exception as e:
                st.error(f"API error: {e}")

    st.markdown("---", unsafe_allow_html=True)

st.markdown("<br><br>",unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; font-size: 0.9em; color: #888;'>
        Designed & Developed by <strong>Madhavarapu. Chandra Sekhara Sri Sai</strong><br>
        <em>✨ Responses generated by Mixtral AI.</em>
    </div>
    """, unsafe_allow_html=True)
