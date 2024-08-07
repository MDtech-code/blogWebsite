from transformers import pipeline
import warnings
# Suppress the specific FutureWarning
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers.tokenization_utils_base")
 # Load the zero-shot classification pipeline
classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli' ,clean_up_tokenization_spaces=True)

 # Define a comprehensive list of categories
labels = ["Sports", "Technology", "Health", "Entertainment", "Politics", "Business", "Education", "Travel", "Food", "Fashion", "Science", "Art", "Music"]

def predict_category(content):
     prediction = classifier(content, labels)
     return prediction['labels'][0]
    

# # Example usage
# content = "The latest advancements in lahore hiway hotel."
# category = predict_category(content)
# print(f"The predicted category is: {category}")