import streamlit as st
import pickle
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from streamlit_extras.add_vertical_space import add_vertical_space
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
import os



# Sidebar contents
with st.sidebar:
    st.title('🤗💬 LLM Chat App')
    st.markdown('''
    ## About
    This app is an LLM-powered chatbot built using:
    - [Streamlit](https://streamlit.io/)
    - [LangChain](https://python.langchain.com/)
    - [OpenAI](https://platform.openai.com/docs/models) LLM model
 
    ''')
    add_vertical_space(5)
    st.write('Made with ❤️ by [Ganesh Pasnurwar]')


load_dotenv()
def main():
    
    st.header("Chat with PDF")
   
    # upload a PDF file
    pdf = st.file_uploader("Upload your PDF", type='pdf')

    if pdf is not None:
        #read pdf file
        pdf_reader=PdfReader(pdf)
        #st.write(pdf_reader)

        text=""
        for page in pdf_reader.pages:
            text +=page.extract_text()
        #st.write(text)

        text_spliter=RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
            )
        chunks=text_spliter.split_text(text=text)
        #st.write(chunks)

        # # embeddings
        store_name = pdf.name[:-4]
        st.write(f'{store_name}')
        # st.write(chunks)
 
        if os.path.exists(f"{store_name}.pkl"):
            with open(f"{store_name}.pkl", "rb") as f:
                VectorStore = pickle.load(f)
            # st.write('Embeddings Loaded from the Disk')s
        else:
            embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
            VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
            with open(f"{store_name}.pkl", "wb") as f:
                pickle.dump(VectorStore, f)
        
        refresh_button = True
        while refresh_button:
            refresh_button=False
            

            # Accept user questions/query
            query = st.text_input("Ask questions about your PDF file:")
            # st.write(query)
    
            if query:
                docs = VectorStore.similarity_search(query=query, k=3)
    
                llm = OpenAI()
                chain = load_qa_chain(llm=llm, chain_type="stuff")
                with get_openai_callback() as cb:
                    response = chain.run(input_documents=docs, question=query)
                    print(cb)
                st.write(response)
            refresh_button = st.button("Refresh")

    




if __name__=="__main__":
    main()
