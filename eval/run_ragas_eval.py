import os
import pandas as pd
import ast
from datasets import Dataset
from ragas import evaluate

# Use the legacy import to avoid the Ragas TypeError bug
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    answer_correctness
)
from dotenv import load_dotenv

# Vertex AI Imports (LLM only — embeddings run locally)
from langchain_google_vertexai import ChatVertexAI
from langchain_huggingface import HuggingFaceEmbeddings
from ragas.run_config import RunConfig

load_dotenv()

# If you downloaded the JSON key instead of using the gcloud CLI, uncomment the line below:
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

def run_ragas_evaluation():
    print("Loading generated dataset...")
    df = pd.read_csv("bot_outputs.csv")

    # Convert stringified lists back to python lists
    df['contexts'] = df['contexts'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    # Ensure correct columns exist
    required_columns = ['question', 'answer', 'contexts', 'ground_truth']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"CRITICAL ERROR: CSV missing column '{col}'.")

    eval_dataset = Dataset.from_pandas(df)

    # --- VERTEX AI INITIALIZATION (LLM ONLY) ---
    GCP_PROJECT_ID = "gen-lang-client-0845087562"
    GCP_LOCATION = "us-central1"

    print(f"Connecting to Vertex AI (Project: {GCP_PROJECT_ID})...")

    # LLM Initialization — still uses Gemini via Vertex
    gemini_llm = ChatVertexAI(
        model_name="gemini-2.5-flash",
        project=GCP_PROJECT_ID,
        location=GCP_LOCATION,
        max_retries=3
    )

    # --- EMBEDDINGS: LOCAL, NO API QUOTA ---
    print("Loading local embedding model (sentence-transformers)...")
    local_embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    metrics = [
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
        answer_correctness
    ]

    print("Running RAGAS evaluation (Free Trial Quota Optimized)...")

    # Throttled hard to avoid 429s on the Gemini LLM calls
    vertex_run_config = RunConfig(
        max_workers=1,      # sequential requests — safest for free-trial quota
        max_retries=8,      # more retries with backoff if a 429 slips through
        timeout=180
    )

    # Execute Evaluation
    result = evaluate(
        dataset=eval_dataset,
        metrics=metrics,
        llm=gemini_llm,
        embeddings=local_embeddings,
        run_config=vertex_run_config,
        raise_exceptions=True
    )

    # --- Export Detailed Results ---
    result_df = result.to_pandas()
    result_df.to_csv("ragas_detailed_results.csv", index=False)
    print("\nDetailed row-by-row metrics saved to: ragas_detailed_results.csv")

    # --- Export Summary Results ---
    # Computed directly from result_df to avoid relying on EvaluationResult.items(),
    # which was removed/changed in newer ragas versions.
    metric_names = [m.name for m in metrics]

    print("\nFinal Pipeline Averages")
    with open("ragas_final_results.txt", "w") as f:
        f.write("CampusBot - Final RAGAS Evaluation Averages (Vertex AI + Local Embeddings)\n")
        f.write("\n")
        for metric_name in metric_names:
            if metric_name in result_df.columns:
                score = result_df[metric_name].mean()
                formatted_line = f"{metric_name.replace('_', ' ').title()}: {score:.4f}"
                print(formatted_line)
                f.write(formatted_line + "\n")
            else:
                warning_line = f"Warning: '{metric_name}' not found in results columns."
                print(warning_line)
                f.write(warning_line + "\n")

    print("\nFinal averages saved to: ragas_final_results.txt")

if __name__ == "__main__":
    run_ragas_evaluation()