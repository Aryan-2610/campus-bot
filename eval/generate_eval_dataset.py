import pandas as pd
import time
import sys
import os

# 1. Path Fix: Ensure Python can find rag_engine.py in the parent folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag_engine import CampusRAGEngine

def generate_ragas_dataset():
    # Initialize the engine
    engine = CampusRAGEngine()
    
    # The 50 Curated Question & Ground Truth pairs
    qa_pairs = [
        # --- file1250.pdf (Holidays) ---
        {"question": "What is the date for Republic Day in 2026?", "ground_truth": "Republic Day is on January 26, 2026."},
        {"question": "When is Holi celebrated according to the 2026 calendar?", "ground_truth": "Holi is on March 04, 2026."},
        {"question": "What day of the week does Id-ul-Fitr fall on in 2026?", "ground_truth": "Id-ul-Fitr falls on a Saturday."},
        {"question": "When is Mahavir Jayanti in 2026?", "ground_truth": "Mahavir Jayanti is on March 31, 2026."},
        {"question": "What is the date for Good Friday in 2026?", "ground_truth": "Good Friday is on April 03, 2026."},
        {"question": "When is Buddha Purnima in 2026?", "ground_truth": "Buddha Purnima is on May 01, 2026."},
        {"question": "What date is Independence Day in 2026?", "ground_truth": "Independence Day is on August 15, 2026."},
        {"question": "When is Mahatma Gandhi's Birthday holiday in 2026?", "ground_truth": "Mahatma Gandhi's Birthday is on October 02, 2026."},
        {"question": "What date is Diwali in 2026?", "ground_truth": "Diwali (Deepavali) is on November 08, 2026."},
        {"question": "Who signed the holiday office order for 2026?", "ground_truth": "The holiday office order was signed by Binod Doley, Registrar."},

        # --- file0681.pdf (Academic Calendar) ---
        {"question": "When does the Orientation program for first-year students start for AY 2025-26?", "ground_truth": "The Orientation program starts from 28.07.2025 "},
        {"question": "When does teaching commence for 1st-year students in the Odd Semester of AY 2025-26?", "ground_truth": "Teaching commences for 1st-year students on 04.08.2025."},
        {"question": "When are the Mid Term Examinations for the Odd Semester 2025-26?", "ground_truth": "Mid Term Examinations begin on 22.09.2025."},
        {"question": "What are the dates for Arena '25-26 / Yuvaan '25-26?", "ground_truth": "Arena '25-26 / Yuvaan '25-26 is scheduled from 17.10.2025 to 19.10.2025."},
        {"question": "When do classes shift to Online Mode in the Odd Semester 2025-26?", "ground_truth": "Classes are in Online Mode from 20.10.2025 to 24.10.2025."},
        {"question": "When does teaching commence for the Even Semester of AY 2025-26?", "ground_truth": "Teaching commences on 01.01.2026."},
        {"question": "What are the dates for Techfest '26 / Engifest '26?", "ground_truth": "Techfest '26 / Engifest '26 is from 09.02.2026 to 15.02.2026."},
        {"question": "When is Aahvan 25-26?", "ground_truth": "Aahvan 25-26 is from 19.02.2026 to 21.02.2026."},
        {"question": "When is the summer vacation for AY 2025-26?", "ground_truth": "Summer vacation is from 01.06.2026 to 31.07.2026."},
        {"question": "Who is the Dean Academic (UG)?", "ground_truth": "Prof. Rajeshwari Pandey is the Dean Academic (UG)."},

        # --- Notice for M3 (Foreign Admissions) ---
        {"question": "Who is Mode 3 (M3) admission strictly for?", "ground_truth": "Mode 3 is strictly for foreign passport holders."},
        {"question": "What is the fee to submit the online registration form for M3 admission?", "ground_truth": "The fee is $50."},
        {"question": "What is the last date to submit the online application form for M3?", "ground_truth": "The last date is 17th July 2026."},
        {"question": "When is the tentative date of physical reporting at DTU for M3?", "ground_truth": "The tentative date is 3rd August 2026 onwards."},
        {"question": "What is the last date of registration for M3 candidates?", "ground_truth": "The last date of registration is 17th August 2026."},
        {"question": "Which bank should the M3 application fee be submitted to?", "ground_truth": "The fee should be submitted to the State Bank of India."},
        {"question": "What is the Bank Account Number for M3 fee submission?", "ground_truth": "The Bank Account Number is 37143752513."},
        {"question": "What is the IFSC code for the M3 fee payment?", "ground_truth": "The IFSC code is SBIN0010446."},
        {"question": "What is the Swift Code for international M3 payments?", "ground_truth": "The Swift Code is SBININBB776."},
        {"question": "Who is the beneficiary name for the M3 fee payment?", "ground_truth": "The beneficiary name is Registrar, DTU-International Affairs."},

        # --- 4.pdf (Placement Coordinators Rules) ---
        {"question": "What is the minimum CGPA required to apply for the Placement Coordinator role?", "ground_truth": "A CGPA of 7.0 or above is required."},
        {"question": "What are the 10th and 12th grade marks requirements for a Placement Coordinator?", "ground_truth": "A minimum of 70% marks in both 10th and 12th grade is required."},
        {"question": "Can a Placement Coordinator undertake a six-month internship if they secure a full-time job offer?", "ground_truth": "No, they will not be permitted to undertake a six-month internship."},
        {"question": "What is the tenure of Placement Coordinators?", "ground_truth": "The tenure is from January to December 2025."},
        {"question": "Does a Placement Coordinator need an NOC to apply for an off-campus job?", "ground_truth": "Yes, a PC must take NOC from T&P to apply for an off-campus job."},
        {"question": "Can a Placement Coordinator serve as a Class Representative?", "ground_truth": "No, a PC is not allowed to hold a position in any student body or society, including Class Representative."},
        {"question": "What happens if a PC joins an internship without prior permission from T&P?", "ground_truth": "It will result in disciplinary action against the concerned PC."},
        {"question": "Who is authorized to modify the rules for Placement Coordinators?", "ground_truth": "The Head of Training & Placement (HoD, T&P) is authorized to make decisions regarding modifications."},
        {"question": "Who is the Head of Training and Placement at DTU?", "ground_truth": "Prof. Anil Singh Parihar is the Head (Training and Placement)."},

        # --- Other Miscellaneous Notices (Fees, Faculty, R&D, Backlogs) ---
        {"question": "What is the extended last date for payment of the annual academic fee for AY 2025-26 without fine?", "ground_truth": "The last date has been extended till 04.09.2025."},
        {"question": "What is the balance academic fee amount for B.Tech 2nd year students admitted through Lateral Entry?", "ground_truth": "The balance fee is Rs. 1,52,700/-."},
        {"question": "What is the deadline for Lateral Entry students to pay their balance fee?", "ground_truth": "The deadline is latest by 30.08.2025."},
        {"question": "In whose favor should the Demand Draft be made for the Lateral Entry fee?", "ground_truth": "The Demand Draft should be in favor of Registrar, DTU."},
        {"question": "What event was postponed on September 3, 2025?", "ground_truth": "The Research and Innovation Excellence Award Ceremony was postponed."},
        {"question": "When was the Research and Innovation Excellence Award Ceremony originally scheduled?", "ground_truth": "It was originally scheduled to be held on 8th September, 2025."},
        {"question": "Who is the Dean of R&D?", "ground_truth": "Prof. Girish Kumar is the Dean (R&D)."},
        {"question": "What is the deadline for M.Tech backlog students to submit their Major Project report for the Even semester 2025-26?", "ground_truth": "The deadline is by 08th June, 2026."},
        {"question": "Who is the Dean of Acad. PG?", "ground_truth": "Prof. Rinku Sharma is the Dean (Acad. PG)."},
        {"question": "What is one parameter evaluated for the extension of Professor Emeritus or Adjunct Faculty?", "ground_truth": "Measurable contributions in areas such as industry networking, research collaborations, mentoring, or teaching responsibilities."},
        {"question": "Who must support the application for further extension of an Adjunct Faculty?", "ground_truth": "It must be supported by a self-appraisal report and the recommendations of the respective HoD."},
        {"question": "Who is the Registrar of DTU who signed the notification for faculty extension parameters?", "ground_truth": "Binod Doley signed the notification."}
    ]

    output_path = "bot_outputs.csv"
    start_index = 0

    # 3. Resume Logic: Check how many have already been processed
    if os.path.exists(output_path):
        try:
            existing_df = pd.read_csv(output_path)
            start_index = len(existing_df)
            print(f"🔄 Found existing progress: {start_index} questions already processed.")
        except Exception as e:
            print(f"⚠️ Error reading existing CSV, starting from scratch: {e}")
            start_index = 0

    if start_index >= len(qa_pairs):
        print("✅ All questions have already been processed!")
        return

    remaining_pairs = qa_pairs[start_index:]
    print(f"🚀 Starting Generation Pipeline for {len(remaining_pairs)} remaining queries...\n")
    
    batch_results = []
    batch_size = 10
    
    for i, pair in enumerate(remaining_pairs):
        global_idx = start_index + i + 1
        question = pair["question"]
        ground_truth = pair["ground_truth"]
        
        print(f"[{global_idx}/{len(qa_pairs)}] Processing: {question}")
        
        # Rate Limit Fix: Simple retry loop for API limits (429 errors)
        max_retries = 3
        success = False
        
        for attempt in range(max_retries):
            try:
                # Get the context and the answer from the engine
                raw_context = engine.retriever.get_fused_context([question])
                answer = engine.get_response(question)
                
                # Append the row data. RAGAS requires 'contexts' to be a list.
                batch_results.append({
                    "question": question,
                    "answer": answer,
                    "contexts": [raw_context], 
                    "ground_truth": ground_truth
                })
                
                success = True
                # Sleep to stay safely under the Gemini Free Tier limit (15 RPM)
                time.sleep(4.5) 
                break # Success, break out of the retry loop
                
            except Exception as e:
                if "429" in str(e) or "RESOURCE" in str(e):
                    print(f"   ⏳ Rate limit hit (Attempt {attempt+1}/{max_retries}). Pausing for 10 seconds...")
                    time.sleep(10)
                else:
                    print(f"   ❌ Unexpected error: {e}")
                    break

        if not success:
            print(f"\nHalting execution at question {global_idx} due to persistent errors.")
            print("You can swap your API key and run the script again. It will resume from here.")
            break

        # 4. Batch Saving Logic: Save every 10 items or at the end of the list
        if len(batch_results) >= batch_size or (i == len(remaining_pairs) - 1):
            df_batch = pd.DataFrame(batch_results)
            
            # If the file doesn't exist (first batch of first run), include headers
            # Otherwise, append without headers
            file_exists = os.path.exists(output_path)
            df_batch.to_csv(output_path, mode='a', header=not file_exists, index=False)
            
            print(f"   💾 Checkpoint reached: Saved {len(batch_results)} rows to {output_path}")
            batch_results = [] # Clear the batch queue

    print(f"\n🏁 Pipeline stopped. Current CSV has {len(pd.read_csv(output_path))} total rows.")

if __name__ == "__main__":
    generate_ragas_dataset()