# cluster_faqs.py
import json
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import google.generativeai as genai

# ---------- CONFIG ----------
genai.configure(api_key="AIzaSyAKRCfxhvDWPe-wRwhy6Km52lhStBB3UBo")
MODEL = "models/gemini-1.5-flash"  # Gemini text model
EMBED_MODEL = "all-MiniLM-L6-v2"
N_CLUSTERS = 5   # adjust based on diversity of FAQs
# ----------------------------

faq_pairs = [
    {"question": "Can I apply for placement coordinator if my CGPA is below 6.0?",
     "answer": "To be eligible for the Placement Coordinator role, you need a minimum CGPA of 7.0 or above."},
    {"question": "What is the minimum CGPA requirement for placement coordinator?",
     "answer": "The minimum CGPA requirement to be eligible for the Placement Coordinator role is 7.0 or above."},
    {"question": "How much is the annual fee for 2nd-year lateral entry students?",
     "answer": "The annual academic fee for lateral entry students is Rs. 1,52,700."},
    {"question": "When is the last date to pay the academic fee without late fine?",
     "answer": "The last date for payment of the annual academic fee for the academic year 2025-26 without a fine has been extended to September 4, 2025."},
    {"question": "Is CGPA considered for eligibility in campus recruitment?",
     "answer": "Yes, students must have a CGPA of 7.0 or above to be eligible for campus recruitment."},
    {"question": "What are the eligibility criteria for campus placement?",
     "answer": "To be eligible for campus placements, you must be a pre-final year student with a CGPA of 7.0 or above, have no history of backlogs, and have secured a minimum of 70% in both 10th and 12th grades. Additionally, you must have a clean disciplinary record."},
    {"question": "What are the rules for applying as placement coordinator?",
     "answer": "To apply for the Placement Coordinator role, you must be a pre-final year student with a CGPA of 7.0 or above, no history of backlogs, and a minimum of 70% in both 10th and 12th grade. You must also have a clean disciplinary record."},
    {"question": "Is there any CGPA cutoff for placement coordinator eligibility?",
     "answer": "Yes, to be eligible for the Placement Coordinator role, you must have a CGPA of 7.0 or above."},
    {"question": "Is there any restriction on internships for placement coordinators?",
     "answer": "Yes, a Placement Coordinator must get prior permission from the Training and Placement department before joining an internship during the placement session. Also, if a PC secures a full-time job offer, they will not be permitted to undertake a six-month internship."},
    {"question": "Can I participate in placement if I have backlogs?",
     "answer": "As per the placement eligibility criteria, students with a history of backlogs are not eligible to apply for placements."},
    {"question": "Who is eligible for campus recruitment drive?",
     "answer": "To be eligible for the campus recruitment drive, you must be a pre-final year student with a CGPA of 7.0 or above, no history of backlogs, and a minimum of 70% in both 10th and 12th grade. Additionally, all students graduating in 2026 and 2027 must fill out the specified Google Form to participate."},
    {"question": "Are placement coordinators allowed to work off-campus?",
     "answer": "Yes, a Placement Coordinator must take a No Objection Certificate (NOC) from the Training and Placement department to apply for an off-campus job."},
    {"question": "When is the next convocation ceremony scheduled?",
     "answer": "The date for the next convocation ceremony has not been announced yet. It will be communicated soon."},
    {"question": "Has the research award ceremony been postponed?",
     "answer": "Yes, the Research and Innovation Excellence Award Ceremony scheduled for September 8th, 2025, has been postponed. The new date will be communicated soon."},
    {"question": "Last date to pay fee without fine?",
     "answer": "The last date for payment of the annual academic fee for the academic year 2025-26 without a fine has been extended to September 4, 2025."},
    {"question": "Google form submission deadline for placement registration?",
     "answer": "The notice states that in-person document verification for Placement Coordinator roles will begin on Monday, 8th September 2025. The submission deadline for the form would be before this date"},
    {"question": "When will the postponed award ceremony be rescheduled?",
     "answer": "The notice indicates that the next date for the award ceremony will be communicated soon."},
    {"question": "How are students informed about major academic event postponements?",
     "answer": "Major academic event postponements are communicated to students through official notices posted on the university notice boards."},
    {"question": "Where are official notices regarding upcoming academic events published?",
     "answer": "Official notices regarding upcoming academic events are published on the university notice boards."},
    {"question": "Who approves modifications to placement coordinator rules?",
     "answer": "The Head of Training & Placement is authorized to make decisions regarding any modifications to the rules for Placement Coordinators."},
    {"question": "What is the university's policy on student involvement with external job consultancy agencies?",
     "answer": "According to the university's policy, a Placement Coordinator must not be involved in external placement consultancies, agencies, or unauthorized job referrals."},
    {"question": "Which authority issues No Objection Certificates for off-campus job applications?",
     "answer": "The Department of Training and Placement (T&P) issues the No Objection Certificate (NOC) for off-campus job applications."}
]

# -------- Step 1: Embed questions --------
model = SentenceTransformer(EMBED_MODEL)
questions = [f["question"] for f in faq_pairs]
embeddings = model.encode(questions)

# -------- Step 2: Cluster with KMeans --------
kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
labels = kmeans.fit_predict(embeddings)

# -------- Step 3: Group by clusters --------
clusters = {}
for idx, label in enumerate(labels):
    clusters.setdefault(label, []).append(faq_pairs[idx])

# -------- Step 4: Send each cluster to Gemini --------
def summarize_cluster(cluster_items):
    prompt = f"""
You are given multiple FAQ question-answer pairs from a university administration.

Here are the pairs:
{json.dumps(cluster_items, indent=2)}

Your task:
•⁠  ⁠Identify the short category type (like "fees", "academic", "placement", "scholarship").
•⁠  ⁠Create one representative question (ques) that summarizes the group.
•⁠  ⁠Create one clear answer (ans) using the given answers.

IMPORTANT:
•⁠  ⁠Only output valid JSON.
•⁠  ⁠Format must be: {{"type": "...", "ques": "...", "ans": "..."}}.
•⁠  ⁠Do not add explanations or extra text outside JSON.
"""
    response = genai.GenerativeModel(MODEL).generate_content(prompt)

    raw_text = response.text.strip()

    if raw_text.startswith("⁠  "):
        raw_text = raw_text.strip("  ⁠json").strip("```")

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "type": "unknown",
            "ques": "Parsing error",
            "ans": raw_text
        }

# -------- Step 5: Collect summaries --------
cluster_summaries = []
for cluster_items in clusters.values():
    summary = summarize_cluster(cluster_items)
    cluster_summaries.append(summary)

# -------- Step 6: Save results --------
with open("clustered_faq.json", "w") as f:
    json.dump(cluster_summaries, f, indent=2)

print("✅ Clustered FAQ JSON saved as clustered_faq.json")