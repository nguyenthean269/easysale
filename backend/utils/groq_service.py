import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import re
import time

class GroqChat:
    def __init__(self, model="llama-3.3-70b-versatile", max_tokens=1000, temperature=0.7, n=1, top_p=0.9, stream=False, max_history_length=10, response_format=None):
        # Load biến môi trường từ .env
        load_dotenv()
        self.api_key = os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError("❌ GROQ_API_KEY không được tìm thấy. Hãy kiểm tra lại tệp .env!")
        
        # Khởi tạo mô hình Llama từ Groq
        self.llm = ChatGroq(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            n=n,
            stream=stream,
            response_format=response_format
        )
        
        # Lưu trữ lịch sử hội thoại
        self.conversation_history = []
        self.max_history_length = max_history_length
    
    @staticmethod
    def load_prompt(path):
        """
        Đọc nội dung của tệp prompt.
        """
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    
    def chat(self, system_input, user_input):
        start = time.time()
        """
        Gửi câu hỏi đến Groq LLM và nhận phản hồi, duy trì lịch sử hội thoại với giới hạn.
        """
        # Thêm câu mới vào lịch sử hội thoại
        self.conversation_history.append(("user", user_input))
        
        # Giới hạn số lượng tin nhắn trong lịch sử
        if len(self.conversation_history) > self.max_history_length * 2:
            self.conversation_history = self.conversation_history[-self.max_history_length * 2:]

        messages = [("system", system_input)] + self.conversation_history
        
        try:
            response = self.llm.invoke(messages)
            self.conversation_history.append(("assistant", response.content))

            end = time.time()
            print(end - start)

            return GroqResponse(response.content)
        except Exception as e:
            return GroqResponse(f"❌ Lỗi từ Groq API: {e}")


    def chat_stream(self, system_input, user_input):
        """
        Trả về phản hồi từ Groq LLM dưới dạng stream.
        """
        self.conversation_history.append(("user", user_input))

        if len(self.conversation_history) > self.max_history_length * 2:
            self.conversation_history = self.conversation_history[-self.max_history_length * 2:]

        messages = [("system", system_input)] + self.conversation_history

        try:
            # 👇 Dùng stream thay vì invoke
            stream = self.llm.stream(messages)
            for chunk in stream:
                # chunk là BaseMessage => chunk.content là phần text
                yield chunk.content
        except Exception as e:
            yield f"\n❌ Lỗi khi stream từ Groq: {str(e)}"


    def clear_history(self):
        """
        Xóa lịch sử hội thoại.
        """
        self.conversation_history = []
    
class GroqResponse:
    def __init__(self, content):
        self.content = content
    
    def clean(self):
        """
        Loại bỏ khoảng trắng dư thừa từ response.
        """
        self.content = re.sub(r"<think>.*?</think>", "", self.content, flags=re.DOTALL)
        self.content = self.content.replace("```json", "").replace("```", "").replace("\xa0", " ").strip()
        return self.content
    
    def __str__(self):
        return self.content
