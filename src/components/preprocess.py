import os
import json
import random
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import streamlit as st
from datetime import datetime

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

file_path = os.path.join(os.getcwd(), "dataset", "all_docs.json")

RELATED_DOCUMENTS = ["2385", "3212", "3740", "3040", "3662", "4080", "1785", "3435", "1878", "1030", "1038", "3295"]
FALSE_LEADS = ["0926", "3630", "0783", "1088", "0383", "0129", "0639", "1671", "3231", "2287", "4293", "2395", "0499", "4312", "3232", "2243", "3665", "0878", "3375", "4156", "1482", "1594", "2696", "0432", "4314", "0008", "3563", "1750", "2900", "1243", "0274", "3772", "3874", "2664", "3237"]


def parse_date(date_str):
    return datetime.strptime(date_str.strip(), "%B %d, %Y")




with open(file_path, 'r') as json_file:
    data_dict = json.load(json_file)


# Ensure at least 100 documents are available
if len(data_dict) < 100:
    raise ValueError("Number of documents in 'all_docs.json' is less than 100.")



n = 100  # generating random numbers
RAND_DOCS = random.sample(list(data_dict.keys()), n - len(RELATED_DOCUMENTS))


temp_list = []

for doc_id, doc_str in data_dict.items():
    if doc_id in set(RELATED_DOCUMENTS + RAND_DOCS):
        lines = doc_str.split("\n")
        doc_title = lines[0]  # Assumes the title is the first line
        doc_date = lines[1]   # Assumes the date is the second line
        doc_content = "\n".join(lines[2:])
        
        temp_list.append({
            "original_id": doc_id,
            "title": doc_title,
            "date": doc_date,
            "content": doc_content
        })

sorted_list = sorted(temp_list, key=lambda x: parse_date(x['date']))


filtered_docs = ["VAST 2011 Mini-Challenge 3 Dataset"]
filtered_dict = {}


for index, doc in enumerate(sorted_list, start=1):
    filtered_dict[index] = {
        "title": doc['title'],
        "date": doc['date'],
        "content": doc['content']
    }

    doc_id_str = f"Document ID: {index}\n{doc['title']}\n{doc['date']}\n{doc['content']}"
    filtered_docs.append(doc_id_str)

print(f"Total Number of documents: {len(filtered_dict)}")


output_file = "./dataset/faiss_index_high.json"
with open(output_file, 'w') as json_out:
    json.dump(filtered_dict, json_out, indent=4)


# Assuming OPENAI_API_KEY is defined somewhere in your environment or code
db = FAISS.from_texts(
    filtered_docs, embedding=OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
)


# Save the db object to a file
db.save_local("./dataset/faiss_index_high")


