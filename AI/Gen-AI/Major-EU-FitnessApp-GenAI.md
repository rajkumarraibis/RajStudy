### **🏋️ Freeletics Fitness Chatbot (GPT + Pinecone for RAG & Caching)**
This system is a **fitness assistant chatbot** for **Freeletics**, embedded inside their mobile app. It provides **AI-powered workout recommendations** and fitness guidance.  

The chatbot is:
- **Exposed to the Freeletics app via AWS Web Services**
- **Powered by OpenAI GPT-3.5**
- **Enhanced with Pinecone for RAG (Retrieval-Augmented Generation) & Prompt Caching**
- **Trained on Freeletics workout plans, exercise routines, and fitness guides**

---

## **🚀 How the Freeletics Chatbot Works**
### **1️⃣ User Interaction**
- Users **ask questions** via the **Freeletics mobile app**:
  - 🏃 *“What’s the best leg workout for strength?”*  
  - 💪 *“Suggest an exercise for fat loss.”*  
  - 🤸 *“How do I recover after an intense workout?”*  

### **2️⃣ AWS API Gateway & Lambda**
- The Freeletics app **sends the request** to an **AWS API Gateway**.
- **AWS Lambda** receives the request and calls the chatbot backend.

### **3️⃣ Prompt Caching (Using Pinecone)**
- If the **same question has been asked before**, the response is **instantly retrieved from cache**.
- If **no cached response is found**, the system proceeds to **retrieval (RAG).**

### **4️⃣ RAG (Retrieval-Augmented Generation)**
- **Encoding:** The question is converted into a **vector embedding** using OpenAI’s `text-embedding-ada-002`.
- **Vector Search:** Pinecone **retrieves relevant workout guides & exercises**.
- **Decoding:** The retrieved context is formatted into a **GPT-3.5 prompt**.

### **5️⃣ GPT Processing**
- GPT-3.5 **combines the user’s query with retrieved knowledge** to generate an answer.
- The response is **stored in Pinecone** to improve performance for future similar queries.

### **6️⃣ Response Delivery**
- The **AWS Lambda function sends the response** back to the Freeletics app.
- The user sees the **fitness recommendation or workout plan** inside the app.

---

## **🛠️ Components & Their Role**
| **Component** | **Purpose** |
|--------------|------------|
| **Freeletics App** | User interface for asking fitness-related questions |
| **AWS API Gateway** | Exposes the chatbot as a web service |
| **AWS Lambda** | Processes requests & queries the AI model |
| **Pinecone (Vector DB)** | Stores embeddings for **retrieval & caching** |
| **OpenAI GPT-3.5** | Generates fitness recommendations when retrieval alone isn’t enough |
| **LlamaIndex** | Manages embedding generation & document indexing |
| **FAISS/Pinecone Index** | Performs **similarity search** for RAG |
| **SimpleDirectoryReader** | Loads **workout plans & fitness guides** into vector storage |
| **OpenAI Embeddings (`text-embedding-ada-002`)** | Converts text into **vector embeddings** for retrieval |
| **Prompt Engineering (`server.py`)** | Dynamically constructs **input prompts** before querying GPT |
| **Cache Layer (`pinecone_index.upsert`)** | Stores previous answers to **avoid redundant API calls** |
| **Environment Config (`config.env`)** | Stores API keys, model settings, and temperature values |

---

## **📊 System Architecture (RAG + Caching + AWS)**
Here’s a **visual overview** of how the components interact:

```md
                        +-----------------------+
                        |   Freeletics App      |
                        |  (User Asks Query)    |
                        +-----------------------+
                                  |
                                  v
                        +-----------------------+
                        |  AWS API Gateway      |
                        +-----------------------+
                                  |
                                  v
                        +-----------------------+
                        |  AWS Lambda Function  |
                        +-----------------------+
                                  |
                        +-----------------------+
                        |   Check Cache (Pinecone)  |
                        +-----------------------+
                                  |
                     Yes /        |       \ No
                Cached Response?  |  
                     |            v
                     |    +-----------------------+
                     |    | Retrieve Context (RAG)|
                     |    +-----------------------+
                     |            |
                     |            v
                     |    +-----------------------+
                     |    |    Query GPT-3.5      |
                     |    +-----------------------+
                     |            |
                     |            v
                     |    +-----------------------+
                     |    |   Store in Cache      |
                     |    +-----------------------+
                     |            |
                     |            v
                     |    +-----------------------+
                     |    |  Return Response      |
                     |    +-----------------------+
                                  |
                                  v
                        +-----------------------+
                        |   Freeletics App UI   |
                        |  (Show AI Response)   |
                        +-----------------------+
```

---

## **📌 Where Encoding & Decoding Happens**
| **Process** | **Component Handling It** | **Description** |
|------------|-------------------------|----------------|
| **Encoding (User Query to Vector)** | `OpenAIEmbedding(model="text-embedding-ada-002")` | Converts the user’s question into a vector embedding |
| **Vector Search (Retrieval)** | `Pinecone Index` | Searches for relevant fitness content based on the encoded query |
| **Decoding (Vector to Context)** | `LlamaIndex retriever.retrieve()` | Retrieves and formats relevant workout/exercise data |
| **Prompt Engineering** | `server.py` | Constructs the GPT input prompt with retrieved fitness knowledge |
| **Decoding (GPT Output to Text)** | `GPT-3.5` | Generates a personalized workout suggestion |

---

## **🔥 Key Advantages of This Setup**
✅ **Provides dynamic workout recommendations** (RAG ensures up-to-date fitness guidance).  
✅ **Instant responses via caching** (reduces API costs & improves user experience).  
✅ **Optimized for Freeletics' app scalability** (AWS handles thousands of fitness queries efficiently).  
✅ **Can incorporate user progress tracking** (e.g., “Suggest an exercise based on my previous workouts”).  

---

## **⚡ Next Steps**
Would you like:
1️⃣ **To integrate user workout history for even better recommendations?**  
2️⃣ **An optimized architecture for AWS deployment?**  
3️⃣ **A fallback mechanism to prevent irrelevant responses?**  

Let me know how you'd like to proceed! 🚀
