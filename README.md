# Interactive-Reading-Buddy-POC-

# 📖 Noory AI Interactive Reading Buddy (POC)

An interactive, AI-assisted Arabic reading companion designed for children aged 3–8 and their parents. This proof of concept demonstrates a seamless parent onboarding experience, child persona customization, and real-time voice evaluation aligned with teacher benchmark standards.

---

## 🌟 Key Features
- **High-Converting Parent Setup:** Emotional and trust-building onboarding with dynamic parent testimonials and background music.
- **Child Persona & Avatars:** Interactive child initialization with iconic hero avatars to reduce reading anxiety.
- **Real-Time Speech Evaluation:** Word-by-word phonetic matching in Arabic with clear visual feedback (Green/Red highlighting).
- **Teacher Benchmark Logic:** Automated evaluation adhering to the `Score > 6.0 = Success` threshold with instant professional narrator playback on `Try Again`.
- **End-of-Session Progress Report:** Summary card showing average fluency score and completed pages.
---
## 🚀 Quick Start & Local Installation

### Prerequisites
Make sure you have **Python 3.9+** installed on your system.

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/noory-reading-buddy-poc.git](https://github.com/YOUR_USERNAME/noory-reading-buddy-poc.git)
cd noory-reading-buddy-poc

### 2. Install Required Dependencies
pip install streamlit streamlit-mic-recorder

### 3. Add Background Music (Optional)Place your ahd_al_asdiqa.mp3 file directly in the project root directory. (If omitted, the app will automatically fall back to a serene online instrumental stream).4. Run the ApplicationBashstreamlit run app.py

The app will automatically open in your default browser at http://localhost:8501.🛠️ Tech StackFramework: Streamlit (Python)Audio & Speech Recognition: Web Speech API / streamlit-mic-recorderArabic Text Normalization & Scoring: Custom fuzzy string distance with diacritic (Tashkeel) removal and character standardization.
