import json
import asyncio
import argparse
from pathlib import Path

# Need to ensure the app is in the Python path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.metrics.retrieval_metrics import RetrievalMetrics
from evaluation.metrics.answer_metrics import AnswerMetrics
from app.services.retrieval.retrieval_service import RetrievalService
from app.services.chat.chat_service import ChatService
from app.services.retrieval.context_builder import build_context

async def run_evaluation(dataset_path: str):
    print(f"Starting evaluation using dataset: {dataset_path}")
    
    with open(dataset_path, "r") as f:
        dataset = json.load(f)
        
    total_hit_rate = 0.0
    total_mrr = 0.0
    total_coverage = 0.0
    
    for idx, item in enumerate(dataset, 1):
        question = item["question"]
        expected_kws = item.get("expected_keywords", [])
        expected_types = item.get("expected_element_types", [])
        
        print(f"\n[{idx}/{len(dataset)}] Q: {question}")
        
        # 1. Retrieve
        results = await RetrievalService.retrieve(question=question)
        
        # 2. Evaluate Retrieval
        hit_rate = RetrievalMetrics.calculate_hit_rate(results, expected_types)
        mrr = RetrievalMetrics.calculate_mrr(results, expected_types)
        
        total_hit_rate += hit_rate
        total_mrr += mrr
        
        print(f"  Retrieval Hit Rate: {hit_rate}")
        print(f"  Retrieval MRR: {mrr:.2f}")
        
        # 3. Build Context (Simulating full pipeline, but we don't need actual Gemini generation for this basic runner without LLM API costs)
        # To avoid hitting Gemini for generation during simple CI runs, we might mock generation or just test context coverage.
        # Since generating answers costs API calls, we'll extract context text and check if it contains the keywords
        # as a proxy for "could the model answer it".
        context = build_context(results)
        coverage = AnswerMetrics.calculate_keyword_coverage(context, expected_kws)
        total_coverage += coverage
        
        print(f"  Context Keyword Coverage: {coverage * 100:.1f}%")
        
    print("\n" + "="*40)
    print("EVALUATION SUMMARY")
    print("="*40)
    print(f"Average Hit Rate:  {total_hit_rate / len(dataset):.2f}")
    print(f"Average MRR:       {total_mrr / len(dataset):.2f}")
    print(f"Average Context Keyword Coverage: {total_coverage / len(dataset) * 100:.1f}%")
    print("Note: Keyword matching is a simple development metric and is not a complete measure of answer correctness.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run S.A.V.I.O.R RAG Evaluation")
    parser.add_argument("--dataset", default="evaluation/datasets/sample_eval.json", help="Path to evaluation dataset")
    args = parser.parse_args()
    
    asyncio.run(run_evaluation(args.dataset))
