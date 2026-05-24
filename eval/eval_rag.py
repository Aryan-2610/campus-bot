import os
import pandas as pd
import warnings
import json
from datasets import Dataset
from ragas import evaluate

# Resolved Ragas 1.0 Deprecation Imports
from ragas.metrics import faithfulness
from ragas.metrics.collections import (
    answer_relevancy,
    context_recall,
    context_precision
)

from engine import CampusBot
from dotenv import load_dotenv

# Suppress library warnings for a cleaner terminal output
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

load_dotenv()

# Absolute path provided by user
CSV_PATH = "/Users/aryangupta/college2/projects/campus-bot/campus-assistant/eval_data.csv"

def run_evaluation():
    # 1. Initialize CampusBot (No arguments to match your engine.py)
    print("--- Initializing CampusBot ---")
    bot = CampusBot()
    
    # 2. Verify CSV existence
    if not os.path.exists(CSV_PATH):
        print(f"Error: CSV not found at {CSV_PATH}")
        return

    # 3. Load the 50+ row dataset
    df_gold = pd.read_csv(CSV_PATH)
    questions, answers, contexts, ground_truths = [], [], [], []

    print(f"--- Running evaluation on {len(df_gold)} test cases ---")
    
    for i, row in df_gold.iterrows():
        query = row['Question']
        gt = row['Ground_Truth']
        
        print(f"[{i+1}/{len(df_gold)}] Processing Query...")
        
        # Get response from your existing bot logic
        # Your chat method returns a dictionary: {"answer": "...", "source_file": "..."}
        response = bot.chat(query)
        
        # Since we can't modify engine.py to return the retrieved context, 
        # we call your retriever directly for the evaluation metrics.
        # Ragas expects a list of strings for 'contexts'
        retrieved_docs = bot.retriever.get_fused_context([query])
        
        questions.append(query)
        answers.append(response.get("answer", "Error: No answer generated"))
        contexts.append([retrieved_docs])
        ground_truths.append(gt)

    # 4. Construct the Ragas Dataset
    eval_ds = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    })

    # 5. Execute Scientific Evaluation
    print("--- Calculating Scores with Gemini as Judge ---")
    # This will use your GOOGLE_API_KEY from .env
    result = evaluate(
        eval_ds,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_recall,
            context_precision
        ]
    )

    # 6. Display and Export
    print("\n" + "="*40)
    print("      CAMPUSBOT EVALUATION SUMMARY")
    print("="*40)
    print(result)
    
    report_file = os.path.join(os.path.dirname(CSV_PATH), "evaluation_results.csv")
    result.to_pandas().to_csv(report_file, index=False)
    print(f"\nDetailed report saved to: {report_file}")

if __name__ == "__main__":
    run_evaluation()