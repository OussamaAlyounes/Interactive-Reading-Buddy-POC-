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

## 🚀 Quick Start & How to Run

1. Clone or download this repository to your computer.
2. (Optional) Place your `ahd_al_asdiqa.mp3` background music file in the project folder.
3. Open your terminal in the project folder and run the following commands:

```bash
pip install streamlit streamlit-mic-recorder
streamlit run app.py
