import requests

class AIClient:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.api_key = data_manager.data['ai']['api_key']
        self.api_url = data_manager.data['ai']['api_url']
        self.model = data_manager.data['ai']['model']
        self.show_text_response = data_manager.data['ai']['show_text_response']

    def ask_question(self, question):
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }

            data = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'user',
                        'content': question
                    }
                ],
                'temperature': 0.7,
                'max_tokens': 1000
            }

            print(f"🤖 Отправка запроса к AI...")
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content']
                print(f"✅ AI ответ получен!")
                return answer
            else:
                error_msg = f"❌ Ошибка API: {response.status_code} - {response.text}"
                print(error_msg)
                return error_msg

        except requests.exceptions.Timeout:
            return "❌ Таймаут запроса к AI. Попробуйте позже."
        except requests.exceptions.ConnectionError:
            return "❌ Ошибка подключения к AI сервису."
        except Exception as e:
            return f"❌ Неизвестная ошибка: {str(e)}"

    def chat_loop(self):
        print("\n" + "=" * 60)
        print("🤖 РЕЖИМ ИСКУССТВЕННОГО ИНТЕЛЛЕКТА")
        print("=" * 60)
        print(f"Модель: {self.model}")
        print("Введите ваш вопрос (или 'выход' для завершения):")
        print("=" * 60)

        while True:
            try:
                user_input = input("\n👤 Вы: ").strip()

                if user_input.lower() in ['выход', 'exit', 'quit']:
                    print("👋 Завершение чата...")
                    break

                if not user_input:
                    continue

                print("⏳ AI думает...")
                response = self.ask_question(user_input)

                print(f"\n🤖 AI: {response}")

            except KeyboardInterrupt:
                print("\n👋 Завершение чата...")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")