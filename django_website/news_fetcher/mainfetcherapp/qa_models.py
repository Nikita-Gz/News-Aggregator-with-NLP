import transformers
from transformers import pipeline

qa_models = {
  0 : pipeline("question-answering", 'huggingface-course/bert-finetuned-squad'),
  1 : pipeline("question-answering", 'distilbert-base-cased-distilled-squad')
}
