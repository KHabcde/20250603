from openai import OpenAI
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
from pywinauto.application import Application

# Load environment variables
load_dotenv()

# Get the OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY が設定されていません")

client = OpenAI(api_key=api_key)

#client = AzureOpenAI(
#    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#    api_version=os.getenv("OPENAI_API_VERSION"),
#    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
#)

def natural_to_macro(text: str) -> str:
    """
    Converts natural language text to macro syntax using OpenAI's ChatGPT API and appends the result to macro_syntax.txt.

    Args:
        text (str): The natural language command.

    Returns:
        str: The converted macro syntax.
    """
    try:
        # プロンプトテンプレートは直接文字列として定義
        # Format the template with the input text
        prompt = f"""
        以下の自然言語指示を、対応するマクロ構文に変換してください。
        自然言語指示: "{text}"
        マクロ構文のみを出力してください。
        出力には余計な記号や装飾を含めないでください。
        
        # 自然言語の例:
        # 「マウスカーソルを(100,200)に移動して」
        # マクロ構文の例:
        # move 100 200

        # 自然言語の例:
        # マウスカーソルをX方向に100,Y方向に200移動して
        # マクロ構文の例:
        # move_relative 100 200
        
        # 自然言語の例:
        # クリックして
        # マクロ構文の例:
        # click
        
        # 自然言語の例:
        # ダブルクリックして
        # マクロ構文の例:
        # doubleclick
        
        # 自然言語の例:
        # 0.5秒待機して
        # マクロ構文の例:
        # sleep 0.5
        
        # 自然言語の例:
        # キーワード「blue」を矩形領域(1000,1),(1900,500)の中から探してください
        # マクロ構文の例:
        # find_keyword_rectangleregion blue 1000 1 1900 500 
        
        # 自然言語の例:
        # 「c」とタイプしてください
        # マクロ構文の例:
        # type c
        
        # 自然言語の例:
        # 2値化反転を用いて、キーワード「blue」を矩形領域(1000,1),(1900,500)の中から探してください
        # マクロ構文の例:
        # find_keyword_rectangleregion_bitwise_invert blue 1000 1 1900 500 
        """
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0
            )  
        #response = client.chat.completions.create(
        #    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        #    messages=[
        #        {"role": "user", "content": prompt}
        #    ],
        #    temperature=0
        #    )
        if not response.choices or not response.choices[0].message.content.strip():
            raise ValueError("Empty response from the API.")

        macro_syntax = response.choices[0].message.content.strip()

        # Append the macro syntax to macro_syntax.txt
        with open("macro_syntax.txt", "a", encoding="utf-8") as output_file:
            output_file.write(macro_syntax + "\n")

        return macro_syntax
    except ValueError as ve:
        print(f"ValueError: {ve}")
        return "Error: Empty response from the API."
    except Exception as e:
        print(f"Error during API call: {e}")
        return "Error: API call failed."
