# ============================================
# 第一部分：匯入所需套件
# ============================================
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
import time

# ============================================
# 第二部分：設定 LLM 連線
# ============================================
# 這裡使用課程提供的 vLLM 伺服器
llm = ChatOpenAI(
    base_url="https://ws-02.wade0426.me/v1",  # 課程提供的 API 網址
    api_key="vllm-token",                      # API 金鑰（私架伺服器可隨便填）
    model="google/gemma-3-27b-it",             # 使用的模型
    temperature=0                              # 設為 0，輸出較穩定，方便觀察
)

# ============================================
# 第三部分：建立兩種風格的 Prompt Template
# ============================================

# LinkedIn 風格：專業、正式
linkedin_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一位 LinkedIn 專業人士，請用專業、正式的語氣撰寫一則關於指定主題的貼文，約 50 字，使用繁體中文。"),
    ("user", "{topic}")
])

# Instagram 風格：活潑、有 emoji 和 hashtag
instagram_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一位 IG 網紅，請用活潑、有趣的語氣撰寫一則關於指定主題的貼文，要有 emoji 和 hashtag，約 50 字，使用繁體中文。"),
    ("user", "{topic}")
])

# ============================================
# 第四部分：建立 Output Parser
# ============================================
# StrOutputParser 會把 LLM 的回應轉成純字串
parser = StrOutputParser()

# ============================================
# 第五部分：使用 LCEL 建立兩條 Chain
# ============================================
# Chain 的流程：Prompt → LLM → Parser
# 使用 | 符號串接（這就是 LCEL 語法）

linkedin_chain = linkedin_prompt | llm | parser
instagram_chain = instagram_prompt | llm | parser

# ============================================
# 第六部分：使用 RunnableParallel 平行執行
# ============================================
# RunnableParallel 會同時執行多個 Chain
# 結果會是一個字典：{"linkedin": "...", "instagram": "..."}

combined_chain = RunnableParallel(
    linkedin=linkedin_chain,
    instagram=instagram_chain
)

# ============================================
# 第七部分：主程式
# ============================================

# 讓使用者輸入主題
topic = input("輸入主題：")

# ---------- 流式輸出 ----------
print("\n" + "=" * 50)
print("📡 流式輸出（Streaming）")
print("=" * 50)

# .stream() 會逐步回傳結果，可以看到兩個 chain 交錯輸出
for chunk in combined_chain.stream({"topic": topic}):
    print(chunk)

# ---------- 批次處理 ----------
print("\n" + "=" * 50)
print("📦 批次處理（Batch）")
print("=" * 50)

# 記錄開始時間
start_time = time.time()


results = combined_chain.batch([{"topic": topic}])

# 計算耗時
elapsed_time = time.time() - start_time

# 輸出結果
print(f"⏱️ 耗時：{elapsed_time:.2f} 秒")
print("-" * 50)
print(f"【LinkedIn 專家說】：")
print(results[0]['linkedin'])
print("-" * 50)
print(f"【IG 網紅說】：")
print(results[0]['instagram'])
print("-" * 50)