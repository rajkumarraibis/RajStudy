Your **GPT App**, named **PostMan Assistant**, is a **Generative AI-powered assistant** designed specifically for **Data Engineering** tasks related to **PostMan Git repositories**. It leverages **OpenAI GPT-3.5** and **LlamaIndex** to provide expert guidance on **ETL processes, data pipelines, version control, and Git workflows**.

---

### **How the App Works**
1. **Retraining the AI (`retrain.py`)**:
   - Reads training data from `training-data/` (help center docs, Google Sheets corpus).
   - Excludes certain directories (`Postman-GenAI-Assistant`, `.`, `venv`).
   - Uses `LlamaIndex` to create a **vector-based AI model**.
   - Saves the trained model in `model_dev/`.

2. **Running the Server (`server.py`)**:
   - Loads **environment variables** (`config.env`).
   - Sets up **OpenAI GPT-3.5-turbo** for **query processing**.
   - Uses **temperature control** (`TEMPERATURE_GENERAL_DEV` = 0.1) for consistency.
   - Loads the trained AI model (`model_dev/`).
   - Provides a **ChatBot** interface via `get_answer_from_model()`.

3. **Handling User Queries**:
   - Queries are **contextually processed** based on predefined prompts:
     - **"Explain `user_bulk_write_lambda.py`?"**
   - Ensures **strict focus** on **PostMan, Git, and Data Engineering**.
   - Prevents **off-topic responses** or AI manipulation.
   - Tailors responses **under 100 words** for clarity.

---

### **Key Features**
✅ **Customizable AI** for Data Engineering  
✅ **Retrains** on updated training data  
✅ **Environment-based configurations** for tuning behavior  
✅ **Handles Git, ETL, and Data Pipeline queries**  
✅ **Strict prompt control** to stay on-topic  

---

### **Next Steps**
- **Run `retrain.py`** to update the AI with new training data.
- **Start `server.py`** to handle user queries.
- **Interact via `get_answer_from_model("your_query")`**.

Would you like help with **testing** or **improving** your implementation? 🚀
