# 🔧 Chatbot Formatting Troubleshooting

## 🐛 Common Issues & Solutions

### Issue 1: Response Still Uses Markdown (**bold**, ==heading==)

**Symptoms:**
```
**Pengenalan Python** ================== Python adalah...
```

**Root Cause:**
- LLM ignores formatting instructions
- Markdown symbols not removed in post-processing

**Solutions Applied:**

1. **Stronger Prompt** ✅
   ```python
   "JANGAN gunakan format markdown seperti **bold** atau ==heading=="
   "Gunakan plain text dengan struktur yang jelas"
   ```

2. **Aggressive Cleaning** ✅
   ```python
   # Remove **bold**
   response = re.sub(r'\*\*([^*]+)\*\*', r'\1', response)
   
   # Remove ==heading==
   response = re.sub(r'={2,}([^=]+)={2,}', r'\1', response)
   
   # Remove ### headers
   response = re.sub(r'^#{1,6}\s+', '', response, flags=re.MULTILINE)
   ```

---

### Issue 2: Duplicate Course IDs

**Symptoms:**
```
Belajar Dasar AI (Course Id: 1, 43, 46)
```

**Root Cause:**
- Vector DB returns multiple entries for same course
- LLM lists all IDs it finds

**Solutions Applied:**

1. **Reduced k parameter** ✅
   ```python
   search_kwargs = {"k": 20}  # Was 200
   ```

2. **ID Cleaning** ✅
   ```python
   def clean_course_ids(match):
       ids = re.findall(r'\d+', match.group(1))
       return f"(ID: {ids[0]})"  # Only first ID
   
   response = re.sub(r'\((?:Course Id|ID):\s*([0-9,\s]+)\)', clean_course_ids, response)
   ```

3. **Explicit Instruction** ✅
   ```python
   "HAPUS duplicate Course ID - hanya tampilkan 1 ID per course"
   ```

---

### Issue 3: Text Wall (No Structure)

**Symptoms:**
```
Untuk mempelajari AI, ada beberapa course yang dapat Anda pelajari. Berikut adalah beberapa course yang relevan: 1. Belajar...
```

**Root Cause:**
- LLM generates paragraph style
- No explicit format template

**Solutions Applied:**

1. **Example Format in Prompt** ✅
   ```python
   CONTOH FORMAT YANG BENAR:
   "Halo! Untuk mempelajari Python, berikut rekomendasinya:

   Course untuk Pemula:

   1. Memulai Pemrograman dengan Python (ID: 1)
      - Level: Dasar
      - Durasi: 10 jam
      - Belajar dasar-dasar Python dari nol
   ..."
   ```

2. **Strict Structure Rules** ✅
   ```python
   "Format course WAJIB seperti ini:
   
   Nama Course (ID: X)
   - Level: [Dasar/Pemula/Menengah/Mahir]
   - Durasi: [X] jam
   - [1 kalimat deskripsi singkat]"
   ```

---

### Issue 4: Response Too Long

**Symptoms:**
- 500+ words response
- User scrolls forever
- Information overload

**Solutions Applied:**

1. **Word Limit** ✅
   ```python
   "Response maksimal 250 kata"
   ```

2. **Item Limit** ✅
   ```python
   "MAKSIMAL 5 item per list"
   "Rekomendasi 3-4 course (MAKSIMAL 4!)"
   ```

3. **Reduced Context** ✅
   ```python
   search_kwargs = {"k": 20}  # Less context = shorter response
   ```

---

### Issue 5: Inconsistent Formatting

**Symptoms:**
- Mix of bullet styles (*, -, •)
- Inconsistent spacing
- Random formatting

**Solutions Applied:**

1. **Standardize Bullets** ✅
   ```python
   response = re.sub(r'^\s*[\*\-•➤→]\s+', '• ', response, flags=re.MULTILINE)
   ```

2. **Consistent Spacing** ✅
   ```python
   # Single space after periods
   response = re.sub(r'\.\s+', '. ', response)
   
   # Remove excessive newlines
   response = re.sub(r'\n{3,}', '\n\n', response)
   ```

---

## 🎯 Current Implementation Status

### ✅ Implemented Fixes:

1. **Stronger Prompts**
   - Explicit "NO MARKDOWN" instruction
   - Format example in prompt
   - Word and item limits

2. **Aggressive Post-Processing**
   - Remove markdown symbols
   - Clean duplicate IDs
   - Standardize formatting
   - Trim whitespace

3. **Reduced Context**
   - k = 20 (was 200)
   - Less noise in retrieval
   - More focused responses

4. **Category-Specific Instructions**
   - COURSE_INFO: Max 5-6 courses
   - LEARNING_PATH: Structured format
   - SKILL: Max 4 courses, 200 words
   - RECOMMENDATION: Max 5 courses

---

## 🧪 Testing Checklist

After implementing fixes, test with:

### Test 1: Python Question (SKILL)
```
User: "Apa itu Python?"

Expected:
- Plain text (no markdown)
- Single Course ID per course
- Max 4 courses
- < 200 words
- 1 follow-up question
```

### Test 2: Course List (COURSE_INFO)
```
User: "Sebutkan course untuk AI"

Expected:
- Max 5 courses
- Format: Name (ID: X)
- Level and duration listed
- Sorted by level
- < 250 words
```

### Test 3: Recommendation (RECOMMENDATION)
```
User: "Saya mau belajar AI"

Expected:
- Max 5 recommendations
- Clear sections
- Reasoning for each
- Next steps
- Follow-up question
```

---

## 📊 Before vs After

### ❌ BEFORE (User's Screenshot):
```
**Pengenalan Python** ======================= Python adalah bahasa pemrograman tingkat tinggi yang mudah dipahami dan digunakan. Bahasa ini dikembangkan pada tahun 1991 oleh Guido van Rossum dan pertama kali dirilis pada tahun 1991. **Fitur Utama Python** ------------------ • Mudah dipahami dan digunakan, bahkan untuk pemula • Memiliki sintaks yang sederhana dan mudah dibaca • Dapat digunakan untuk berbagai keperluan... **Rekomendasi Course** -------------------- Berikut beberapa course yang dapat membantu Anda mempelajari Python: • **Memulai Pemrograman dengan Python** (ID: 1, Level: Dasar, Durasi: 10 jam) • Course ini membahas dasar-dasar pemrograman dengan Python... [continues for 500+ words]
```

**Problems:**
- ❌ Markdown symbols everywhere
- ❌ Decorative lines (====, ----)
- ❌ Too long
- ❌ Hard to read

---

### ✅ AFTER (Expected):
```
Halo! Python adalah bahasa pemrograman yang mudah dipelajari dan powerful untuk berbagai keperluan, mulai dari web development, data science, hingga machine learning.

Kegunaan Utama Python:
• Web development (Django, Flask)
• Data analysis (Pandas, NumPy)
• Machine Learning (scikit-learn, TensorFlow)
• Automation dan scripting

Course yang Saya Rekomendasikan:

1. Memulai Pemrograman dengan Python (ID: 1)
   - Level: Dasar
   - Durasi: 10 jam
   - Belajar fundamental Python dari nol

2. Belajar Machine Learning dengan Python (ID: 2)
   - Level: Menengah
   - Durasi: 20 jam
   - Terapkan Python untuk ML projects

3. Belajar Data Science dengan Python (ID: 3)
   - Level: Mahir
   - Durasi: 30 jam
   - Analisis data dengan Pandas dan NumPy

Rekomendasi:
Mulai dari course pertama untuk membangun fondasi yang kuat!

Apakah Anda sudah punya pengalaman programming sebelumnya?
```

**Improvements:**
- ✅ Plain text, no markdown
- ✅ Clean structure
- ✅ Single IDs
- ✅ Concise (< 250 words)
- ✅ Easy to read
- ✅ Actionable

---

## 🔍 Debugging Steps

If response still not formatted well:

### Step 1: Check Prompt
```python
# Print the actual prompt sent to LLM
print(f"PROMPT:\n{final_prompt}")
```

### Step 2: Check Raw Response
```python
# Before post-processing
print(f"RAW RESPONSE:\n{response.content}")
```

### Step 3: Check Formatted Response
```python
# After post-processing
print(f"FORMATTED:\n{formatted_response}")
```

### Step 4: Test Regex Patterns
```python
import re

test_text = "**Bold** text"
cleaned = re.sub(r'\*\*([^*]+)\*\*', r'\1', test_text)
print(cleaned)  # Should be: "Bold text"
```

---

## 🎛️ Tuning Parameters

### If Response Still Too Long:

1. **Reduce k further:**
   ```python
   search_kwargs = {"k": 10}  # Even less context
   ```

2. **Stricter word limit:**
   ```python
   "Response maksimal 150 kata"
   ```

3. **Fewer items:**
   ```python
   "MAKSIMAL 3 course"
   ```

### If Response Missing Info:

1. **Increase k slightly:**
   ```python
   search_kwargs = {"k": 30}
   ```

2. **Check filter:**
   ```python
   # Make sure relevant collections included
   search_kwargs["filter"] = {"source": {"$in": [...]}}
   ```

---

## 🚨 Emergency Fixes

### If LLM Still Ignores Instructions:

**Option 1: Add Penalty Statement**
```python
"PENTING: Jika Anda menggunakan markdown atau format yang salah, response akan ditolak!"
```

**Option 2: Temperature Adjustment**
```python
# Lower temperature = more deterministic
llm = ChatGroq(
    temperature=0.3,  # Was 0.7
    ...
)
```

**Option 3: Different Model**
```python
# Try different model
model_name="mixtral-8x7b-32768"  # Instead of llama-3.3-70b
```

---

## ✅ Verification

After restart, verify with:

```bash
# Test API
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "message": "Apa itu Python?"
  }'
```

**Expected JSON:**
```json
{
  "success": true,
  "data": {
    "response": "Halo! Python adalah...\n\nCourse yang Saya Rekomendasikan:\n\n1. ...",
    "type": "skill",
    "category": "SKILL"
  }
}
```

**Checklist:**
- [ ] No markdown symbols
- [ ] Single Course IDs
- [ ] Clean structure
- [ ] < 250 words
- [ ] Has follow-up question

---

## 📚 Resources

- **Prompt Engineering**: Make instructions explicit and mandatory
- **Regex Testing**: https://regex101.com/
- **LangChain Docs**: https://python.langchain.com/

---

**🎯 Summary:**

The fixes applied should significantly improve response formatting. If issues persist:
1. Check debug logs
2. Adjust k parameter
3. Modify temperature
4. Try different model

The combination of **stronger prompts** + **aggressive cleaning** should handle 95% of formatting issues!






